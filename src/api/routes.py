import json
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
from api import app, local_environment, db
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError
from argon2 import PasswordHasher


@app.route("/", methods=["GET"])
def check_active():
    return jsonify({"active": True})


@app.route("/users/roles", methods=["GET"])
def get_user_roles():
    user_roles = db.session.query(UserRole).filter(UserRole.canceled == 0).all()
    return user_roles_schema.dump(user_roles), 200, CONTENT_TYPE


@app.route("/users/roles", methods=["POST"])
@valid_result
def create_user_role():
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
            jsonify(error),
            200,
            CONTENT_TYPE,
        )
    new_user_role = UserRole(**user_role)
    db.session.add(new_user_role)
    db.session.commit()
    return user_role_schema.dump(new_user_role), 200, CONTENT_TYPE


@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.query(User).filter(User.canceled == 0).all()
    return user_outputs_schema.dump(users), 200, CONTENT_TYPE


@app.route("/users/<id>", methods=["GET"])
@one_result
def get_user(id: str):
    user = db.session.query(User).filter(User.id == id).one()
    return user_output_schema.dump(user), 200, CONTENT_TYPE


@app.route("/users", methods=["POST"])
@valid_result
def create_user():
    user = user_input_schema.loads(json.dumps(request.json))
    exists = (
        db.session.query(User.id).filter_by(username=user["username"]).first()
        is not None
    )

    if exists:
        error = ALREADY_EXISTS_ERROR["error"].format("User")
        return (
            jsonify(error),
            200,
            CONTENT_TYPE,
        )

    ph = PasswordHasher()
    user["password"] = ph.hash(user["password"])

    new_user = User(**user)
    db.session.add(new_user)
    db.session.commit()
    return user_output_schema.dump(new_user), 200, CONTENT_TYPE


@app.route("/users/login", methods=["POST"])
@valid_result
def user_login():
    ph = PasswordHasher()
    user = user_input_schema.loads(json.dumps(request.json))
    login_user = (
        db.session.query(User).filter_by(username=user["username"]).one_or_none()
    )

    if not login_user:
        ph.verify("VERIFY_NOTHING", user["password"])
    elif login_user and ph.verify(login_user.password, user["password"]):
        return user_output_schema.dump(login_user), 200, CONTENT_TYPE

    return jsonify(LOGIN_ERROR), 200, CONTENT_TYPE


@app.route("/users/<id>/favorite", methods=["GET"])
def get_user_favorites(id: str):
    favorite = (
        db.session.query(EventFavorite.event_id).filter_by(user_id=id, canceled=0).all()
    )
    favorites = [result[0] for result in favorite]
    events = db.session.query(Event).filter(Event.id.in_(favorites)).all()
    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/users/<id>/registration", methods=["GET"])
def get_user_registration(id: str):
    registration = (
        db.session.query(EventRegistration.event_id)
        .filter_by(user_id=id, canceled=0)
        .all()
    )
    registrations = [result[0] for result in registration]
    events = db.session.query(Event).filter(Event.id.in_(registrations)).all()
    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/events", methods=["GET"])
def get_events():
    events = db.session.query(Event).filter(Event.canceled == 0).all()
    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/events", methods=["POST"])
@valid_result
def create_event():
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
            jsonify(error),
            200,
            CONTENT_TYPE,
        )
    new_event = Event(**event)
    db.session.add(new_event)
    db.session.commit()
    return event_schema.dump(new_event), 200, CONTENT_TYPE


@app.route("/events/<id>", methods=["GET"])
@one_result
def get_event(id: str):
    event = db.session.query(Event).filter(Event.id == id).one()
    return event_schema.dump(event), 200, CONTENT_TYPE


@app.route("/events/<id>", methods=["POST"])
def update_event(id: str):
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
    share = event_share_schema.loads(json.dumps(request.json))
    new_share = EventShare(**share)
    db.session.add(new_share)
    db.session.commit()

    return (
        event_share_schema.dump(new_share),
        200,
        CONTENT_TYPE,
    )
