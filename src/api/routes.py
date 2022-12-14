import json
import uuid
import ssl
import smtplib
import urllib.parse
from email.message import EmailMessage
from flask import jsonify, request
from api.models import *
from api.decorators import one_result, valid_result
from api.constants import (
    NOT_FOUND_ERROR,
    CONTENT_TYPE,
    ALREADY_EXISTS_ERROR,
    LOGIN_ERROR,
    BAD_REQUEST_ERROR,
)
from api import (
    app,
    db,
    ADMIN_ROLE_UUID,
    EMAIL_USERNAME,
    EMAIL_PASSWORD,
    APPLICATION_URL,
)
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


@app.route("/", methods=["GET"])
def check_active():
    """Return true when the server is running and active."""
    return jsonify({"active": True})


@app.route("/users/roles", methods=["GET"])
def get_user_roles():
    """
    Get the available user roles in the system.

    Returns:
        a list of user role data, status code, content type
    """
    user_roles = db.session.query(UserRole).filter(UserRole.canceled == 0).all()
    return user_roles_schema.dump(user_roles), 200, CONTENT_TYPE


@app.route("/users/roles", methods=["POST"])
@valid_result
def create_user_role():
    """
    Create a new user role.

    payload: json {
        "role_name": str,
    }

    Returns:
        created user role data, status code, content type
    """
    user_role = user_role_schema.loads(json.dumps(request.json))
    exists = (
        db.session.query(UserRole.id)
        .filter_by(role_name=user_role["role_name"])
        .first()
        is not None
    )

    if exists:
        error = ALREADY_EXISTS_ERROR["error"].format("User Role")
        return (
            jsonify({"error": error}),
            400,
            CONTENT_TYPE,
        )

    new_user_role = UserRole(**user_role)
    db.session.add(new_user_role)
    db.session.commit()
    return user_role_schema.dump(new_user_role), 200, CONTENT_TYPE


@app.route("/users", methods=["GET"])
def get_users():
    """
    Get the active users in the system.

    Returns:
        a list of user data, status code, content type
    """
    users = (
        db.session.query(User)
        .join(UserRole, User.user_role_id == UserRole.id)
        .add_entity(UserRole)
        .filter(User.canceled == 0)
        .all()
    )
    user_data = []

    for user in users:
        user_data.append(
            {
                "id": user[0].id,
                "username": user[0].username,
                "user_role_id": user[0].user_role_id,
                "role_name": user[1].role_name,
            }
        )

    return user_outputs_schema.dump(user_data), 200, CONTENT_TYPE


@app.route("/users/<id>", methods=["GET"])
@one_result
def get_user(id: str):
    """
    Get the data of the specified user.

    Args:
        id: the id of the user to lookup

    Returns:
        a list of user role data, status code, content type
    """
    user = db.session.query(User).filter(User.id == id).one()
    return user_output_schema.dump(user), 200, CONTENT_TYPE


@app.route("/users", methods=["POST"])
@valid_result
def create_user():
    """
    Create a new user.

    payload: json {
        "username": str,
        "user_role_id: str,
        "password": str
    }

    Returns:
        created user data, status code, content type
    """
    user = user_input_schema.loads(json.dumps(request.json))
    user["username"] = user["username"].lower()

    exists = (
        db.session.query(User.id).filter_by(username=user["username"]).first()
        is not None
    )

    if exists:
        error = ALREADY_EXISTS_ERROR["error"].format("User")
        return (
            jsonify({"error": error}),
            200,
            CONTENT_TYPE,
        )

    ph = PasswordHasher()
    user["password"] = ph.hash(user["password"])

    new_user = User(**user)
    db.session.add(new_user)
    db.session.commit()
    return user_output_schema.dump(new_user), 200, CONTENT_TYPE


@app.route("/users", methods=["DELETE"])
@valid_result
def delete_user():
    """
    Delete a user.

    The requester must be an ADMIN

    payload: json {
        "user_id": str,
        "requester_id": str,
    }

    Returns:
        the deleted user data, status code, content type
    """

    user = db.session.query(User).filter_by(id=request.json["user_id"]).one_or_none()

    requester = (
        db.session.query(User)
        .filter_by(id=request.json["requester_id"], user_role_id=ADMIN_ROLE_UUID)
        .one_or_none()
    )

    if user and requester:
        user.canceled = 1
        db.session.commit()
        return user_output_schema.dump(user), 200, CONTENT_TYPE

    return (
        jsonify({"error": BAD_REQUEST_ERROR}),
        400,
        CONTENT_TYPE,
    )


@app.route("/users/login", methods=["POST"])
@valid_result
def user_login():
    """
    Login a new user.

    payload: json {
        "username": str,
        "password": str
    }

    Returns:
        logged in user data, status code, content type
    """
    ph = PasswordHasher()
    default = ph.hash(str(uuid.uuid4()))

    user = user_input_schema.loads(json.dumps(request.json))
    user["username"] = user["username"].lower()

    login_user = (
        db.session.query(User)
        .filter_by(username=user["username"], canceled=0)
        .one_or_none()
    )

    if not login_user:
        try:
            ph.verify(default, user["password"])
        except VerifyMismatchError:
            return jsonify(LOGIN_ERROR), 400, CONTENT_TYPE

    try:
        ph.verify(login_user.password, user["password"])
        return user_output_schema.dump(login_user), 200, CONTENT_TYPE
    except VerifyMismatchError:
        return jsonify(LOGIN_ERROR), 400, CONTENT_TYPE


@app.route("/users/<id>/favorite", methods=["GET"])
def get_user_favorites(id: str):
    """
    Get the favorite events of the specified user.

    Args:
        id: the id of the user to get the favorites of

    Returns
        a list of event data, status code, content type
    """
    favorite = (
        db.session.query(EventFavorite.event_id).filter_by(user_id=id, canceled=0).all()
    )
    favorites = [result[0] for result in favorite]
    events = (
        db.session.query(Event)
        .filter(and_(Event.id.in_(favorites), Event.canceled == 0))
        .all()
    )
    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/users/<id>/registration", methods=["GET"])
def get_user_registration(id: str):
    """
    Get the registered events of the specified user.

    Args:
        id: the id of the user to get the registrations of

    Returns:
        a list of event data, status code, content type
    """
    registration = (
        db.session.query(EventRegistration.event_id)
        .filter_by(user_id=id, canceled=0)
        .all()
    )
    registrations = [result[0] for result in registration]
    events = (
        db.session.query(Event)
        .filter(and_(Event.id.in_(registrations), Event.canceled == 0))
        .all()
    )
    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/users/<id>/suggestion", methods=["GET"])
def get_user_suggestions(id: str):
    """
    Get the suggested events of the specified user.

    Args:
        id: the id of the user to get the favorites of

    Returns:
        a list of event data, status code, content type
    """

    # Get registered events
    registration = (
        db.session.query(EventRegistration.event_id)
        .filter_by(user_id=id, canceled=0)
        .all()
    )
    registrations = [result[0] for result in registration]
    registered_events = (
        db.session.query(Event).filter(Event.id.in_(registrations)).all()
    )

    # Get favorite events
    favorite = (
        db.session.query(EventFavorite.event_id).filter_by(user_id=id, canceled=0).all()
    )
    favorites = [result[0] for result in favorite]
    favorite_events = db.session.query(Event).filter(Event.id.in_(favorites)).all()

    # Setup query data
    # Get all current categories
    all_events = registered_events + favorite_events
    categories = [event.category for event in all_events]

    # Get Ids to ignore
    # events the user already knows about should not be suggested to them
    ids_to_ignore = registrations + favorites

    # Get Suggested Events
    events = (
        db.session.query(Event)
        .filter(
            and_(
                Event.id.notin_(ids_to_ignore),
                Event.category.in_(categories),
                Event.canceled == 0,
            )
        )
        .all()
    )

    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/events", methods=["GET"])
def get_events():
    """
    Get a list of all valid events.

    Returns:
        a list of event data, status code, content type
    """
    events = db.session.query(Event).filter(Event.canceled == 0).all()
    sorted_events = sorted(events, key=lambda event: event.start_time)
    return events_schema.dump(sorted_events), 200, CONTENT_TYPE


@app.route("/events", methods=["POST"])
@valid_result
def create_event():
    """
    Create an event.

    payload: json {
        "description": str,
        "category": str,
        "location": str,
        "cost": str,
        "start_time": str,
        "end_time": str,
        "event_link": str,
        "create_user_id": str,
        "update_time": str,
    }

    Returns:
        created event data, status code, content type
    """
    event = event_schema.loads(json.dumps(request.json))
    exists = (
        db.session.query(Event.description)
        .filter_by(description=event["description"])
        .first()
        is not None
    )

    if exists:
        error = ALREADY_EXISTS_ERROR["error"].format("Event")
        return (
            jsonify({"error": error}),
            400,
            CONTENT_TYPE,
        )

    new_event = Event(**event)
    db.session.add(new_event)
    db.session.commit()
    return event_schema.dump(new_event), 200, CONTENT_TYPE


@app.route("/events", methods=["DELETE"])
@valid_result
def delete_event():
    """
    Delete an event.

    The requester must either be the event creator or an ADMIN

    payload: json {
        "event_id": str,
        "requester_id": str,
    }

    Returns:
        the deleted event data, status code, content type
    """

    event = db.session.query(Event).filter_by(id=request.json["event_id"]).one_or_none()

    if event and request.json["requester_id"] == event.create_user_id:
        requester = True

    else:
        requester = (
            db.session.query(User)
            .filter_by(id=request.json["requester_id"], user_role_id=ADMIN_ROLE_UUID)
            .one_or_none()
        )

    if event and requester:
        event.canceled = 1
        db.session.commit()
        return event_schema.dump(event), 200, CONTENT_TYPE

    return (
        jsonify({"error": BAD_REQUEST_ERROR}),
        400,
        CONTENT_TYPE,
    )


@app.route("/events/<id>", methods=["GET"])
@one_result
def get_event(id: str):
    """
    Get the data of the specified event id.

    Args:
        id: the id of the user to get the events of

    Returns:
        event data, status code, content type
    """
    event = db.session.query(Event).filter(Event.id == id).one()
    return event_schema.dump(event), 200, CONTENT_TYPE


@app.route("/events/<id>", methods=["POST"])
def update_event(id: str):
    """
    Update the data associated with the specified event id.

    The user_id in the request must match the create_user_id of
    the event

    Args:
        id: the id of the event to update

    payload: json {
        "user_id": str,
        "description": str,
        "category": str,
        "location": str,
        "cost": str,
        "start_time": str,
        "end_time": str,
        "event_link": str,
    }

    Returns:
        updated event data, status code, content type
    """
    try:
        update_request = event_update_form_schema.loads(json.dumps(request.json))
        event = db.session.query(Event).filter(Event.id == id).one()

        if event.create_user_id == update_request["user_id"]:
            for attr, value in update_request.items():
                if attr != "user_id":
                    setattr(event, attr, value)

            db.session.commit()
        return event_schema.dump(event), 200, CONTENT_TYPE
    except NoResultFound:
        return NOT_FOUND_ERROR, 404, CONTENT_TYPE
    except MultipleResultsFound:
        return (
            jsonify(CRITICAL_ERROR),
            500,
            CONTENT_TYPE,
        )
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(BAD_REQUEST_ERROR),
            400,
            CONTENT_TYPE,
        )


@app.route("/events/<id>/metrics", methods=["GET"])
@one_result
def get_event_metrics(id: str):
    """
    Get the metrics of the specified event id.

    Args:
        id: the id of the event to get the metric of

    Returns:
        event metric data, status code, content type
    """
    event = db.session.query(Event).filter(Event.id == id).one()
    registrations = (
        db.session.query(func.count(EventRegistration.id))
        .filter_by(event_id=id, canceled=0)
        .scalar()
    )
    favorites = (
        db.session.query(func.count(EventFavorite.id))
        .filter_by(event_id=id, canceled=0)
        .scalar()
    )
    shares = (
        db.session.query(func.count(EventShare.id))
        .filter(EventShare.event_id == id)
        .scalar()
    )

    popularity_score = (registrations * 0.8) + (favorites * 0.15) + (shares * 0.05)

    metrics = {
        "registrations": registrations,
        "favorites": favorites,
        "shares": shares,
        "popularity_score": popularity_score,
    }

    return jsonify(metrics), 200, CONTENT_TYPE


@app.route("/events/registration", methods=["POST"])
@valid_result
def event_registration():
    """
    Register a user for an event.

    payload: json {
        "event_id": str,
        "user_id": str,
    }

    Returns:
        event registration data, status code, content type
    """
    registration = event_registration_schema.loads(json.dumps(request.json))
    event_registration = (
        db.session.query(EventRegistration)
        .filter_by(user_id=registration["user_id"], event_id=registration["event_id"])
        .first()
    )

    if event_registration:
        event_registration.canceled = 0

    else:
        event_registration = EventRegistration(**registration)
        db.session.add(event_registration)

    db.session.commit()

    return (
        event_registration_schema.dump(event_registration),
        200,
        CONTENT_TYPE,
    )


@app.route("/events/<event_id>/registration/<user_id>", methods=["POST"])
@one_result
def remove_user_registration(event_id: str, user_id: str):
    """
    Unregister a user from the specified event.

    Args:
        event_id: the id of the event to unregister from
        user_id: the id of the user to unregister

    Returns:
        event registration data, status code, content type
    """
    registration = (
        db.session.query(EventRegistration)
        .filter_by(
            event_id=event_id,
            user_id=user_id,
        )
        .one()
    )
    registration.canceled = 1
    db.session.commit()
    return event_registration_schema.dump(registration), 200, CONTENT_TYPE


@app.route("/events/favorite", methods=["POST"])
@valid_result
def event_favorite():
    """
    Create a favorite record for a specific user and event.

    payload: json {
        "user_id": str,
        "event_id": str,
    }

    Returns:
        event favorite data, status code, content type
    """
    favorite = event_favorite_schema.loads(json.dumps(request.json))
    event_favorite = (
        db.session.query(EventFavorite)
        .filter_by(user_id=favorite["user_id"], event_id=favorite["event_id"])
        .first()
    )

    if event_favorite:
        event_favorite.canceled = 0

    else:
        event_favorite = EventFavorite(**favorite)
        db.session.add(event_favorite)

    db.session.commit()

    return (
        event_favorite_schema.dump(event_favorite),
        200,
        CONTENT_TYPE,
    )


@app.route("/events/<event_id>/favorite/<user_id>", methods=["POST"])
def remove_user_favorite(event_id: str, user_id: str):
    """
    Unfavorite an event of the specified user.

    Args:
        event_id: the id of the event to unfavorite
        user_id: the id of the user to unfavoirte

    Returns:
        event favorite data, status code, content type
    """
    favorite = (
        db.session.query(EventFavorite)
        .filter_by(event_id=event_id, user_id=user_id)
        .one()
    )
    favorite.canceled = 1
    db.session.commit()
    return event_favorite_schema.dump(favorite), 200, CONTENT_TYPE


@app.route("/events/share", methods=["POST"])
@valid_result
def event_share():
    """
    Store the event that was shared.

    payload: json {
        "event_id": str,
    }

    Returns:
        share data, status code, content type
    """
    share = event_share_schema.loads(json.dumps(request.json))
    new_share = EventShare(**share)

    event = db.session.query(Event).filter(Event.id == new_share.event_id).one_or_none()
    user = db.session.query(User).filter(User.id == new_share.user_id).one_or_none()

    if user and event:
        body = f"""
        Hello {new_share.to}! \n
        {user.username} thinks you might be interested in an event:
        Event: {event.description}
        Category: {event.category}
        Location: {event.location}
        Cost: {event.cost}\n

        If you are interested, come to {urllib.parse.urlparse(APPLICATION_URL).hostname} and search for the event above.
        We look forward to seeing you!

        Kindly,
        ISEA
        """

        email = EmailMessage()
        email["From"] = EMAIL_USERNAME
        email["To"] = new_share.to
        email["Subject"] = "ISEA event you might be interested in!"
        email.set_content(body)

        sent = False

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", port=465, context=ssl.create_default_context()
        ) as smtp:
            smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_USERNAME, new_share.to, email.as_string())
            sent = True

        if sent:
            db.session.add(new_share)
            db.session.commit()

            return (
                event_share_schema.dump(new_share),
                200,
                CONTENT_TYPE,
            )

    return (
        jsonify(BAD_REQUEST_ERROR),
        400,
        CONTENT_TYPE,
    )
