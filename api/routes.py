from flask import jsonify, request
from api.models import *
from api import app, local_environment, db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError


CONTENT_TYPE = {"ContentType": "application/json"}
BAD_REQUEST = {"error": "bad request"}


@app.route("/", methods=["GET"])
def check_active():
    return jsonify({"active": True})


@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.query(User).filter(User.canceled == 0).all()
    return users_schema.dump(users), 200, CONTENT_TYPE


@app.route("/users/<id>", methods=["GET"])
def get_user(id: str):
    try:
        user = db.session.query(User).filter(User.id == id).one()
        return users_schema.dump(user), 200, CONTENT_TYPE
    except NoResultFound:
        return (
            jsonify({"error": "user not found"}),
            404,
            CONTENT_TYPE,
        )
    except MultipleResultsFound:
        return (
            jsonify({"error": "critical error"}),
            500,
            CONTENT_TYPE,
        )


@app.route("/users", methods=["POST"])
def create_user():
    try:
        user = user_schema.loads(request)
        exists = (
            db.session.query(User.id).filter_by(username=user.username).first()
            is not None
        )

        if exists:
            return (
                jsonify({"error": "username not available"}),
                200,
                CONTENT_TYPE,
            )

        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 200, CONTENT_TYPE

    except ValidationError:
        return (
            jsonify(BAD_REQUEST),
            400,
            CONTENT_TYPE,
        )

    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(BAD_REQUEST),
            400,
            CONTENT_TYPE,
        )


@app.route("/users/<id>/favorites", methods=["GET"])
def get_user_favorites(id: str):
    favorites = (
        db.session.query(EventFavorite.event_id)
        .filter(EventFavorite.user_id == id)
        .all()
    )
    events = db.session.query(Event).filter(Event.id.in_(favorites)).all()
    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/users/<id>/registration", methods=["GET"])
def get_user_registration(id: str):
    registration = (
        db.session.query(EventRegistration.event_id)
        .filter(EventRegistration.user_id == id)
        .all()
    )
    events = db.session.query(Event).filter(Event.id.in_(registration)).all()
    return users_schem.dump(events), 200, CONTENT_TYPE


@app.route("/events", methods=["GET"])
def get_events():
    events = db.session.query(Event).filter(Event.canceled == 0).all()
    return events_schema.dump(events), 200, CONTENT_TYPE


@app.route("/events", methods=["POST"])
def create_event():
    try:
        user = user_schema.loads(request)
        exists = (
            db.session.query(User.id).filter_by(username=user.username).first()
            is not None
        )

        if exists:
            return (
                jsonify({"error": "event already exists"}),
                200,
                CONTENT_TYPE,
            )

        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 200, CONTENT_TYPE

    except ValidationError:
        return (
            jsonify(BAD_REQUEST),
            400,
            CONTENT_TYPE,
        )

    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(BAD_REQUEST),
            400,
            CONTENT_TYPE,
        )


@app.route("/events/<id>", methods=["GET"])
def get_event(id: str):
    try:
        event = db.session.query(Event).filter(Event.id == id).one()
        return event_schema.dump(event), 200, CONTENT_TYPE
    except NoResultFound:
        return (jsonify({"error": "event not found"}), 404, CONTENT_TYPE)
    except MultipleResultsFound:
        return (
            jsonify({"error": "critical error"}),
            500,
            CONTENT_TYPE,
        )


@app.route("/events/registration", methods=["POST"])
def event_registration():
    try:
        registration = event_registration_schema.loads(request)
        exists = (
            db.session.query(EventRegistration.id).filter_by(id=registration.id).first()
            is not None
        )

        if exists:
            registration.canceled = 0
            db.session.commit()
        else:
            db.session.add(registration)
            db.session.commit()

        return (
            event_registration_schema.dump(registration),
            200,
            CONTENT_TYPE,
        )
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(BAD_REQUEST),
            400,
            CONTENT_TYPE,
        )


@app.route("/events/registration/<id>", methods=["POST"])
def remove_user_registration(id: str):
    try:
        registration = (
            db.session.query(EventRegistration).filter(EventRegistration.id == id).one()
        )
        registration.canceled = 1
        return registrationschema.dump(favorite), 200, CONTENT_TYPE
    except NoResultFound:
        return (
            jsonify({"error": "user not found"}),
            404,
            CONTENT_TYPE,
        )
    except MultipleResultsFound:
        return (
            jsonify({"error": "critical error"}),
            500,
            CONTENT_TYPE,
        )


@app.route("/events/favorite", methods=["POST"])
def event_favorite():
    try:
        favorite = event_favorites_schema.loads(request)
        exists = (
            db.session.query(EventFavorite.id).filter_by(id=favorite.id).first()
            is not None
        )

        if exists:
            favorite.canceled = 0
            db.session.commit()
        else:
            db.session.add(favorite)
            db.session.commit()

        return (
            event_favorite_schema.dump(favorite),
            200,
            CONTENT_TYPE,
        )
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(BAD_REQUEST),
            400,
            CONTENT_TYPE,
        )


@app.route("/events/favorite/<id>", methods=["POST"])
def remove_user_favorite(id: str):
    try:
        favorite = db.session.query(EventFavorite).filter(EventFavorite.id == id).one()
        favorite.canceled = 1
        return favorite_schema.dump(favorite), 200, CONTENT_TYPE
    except NoResultFound:
        return (
            jsonify({"error": "user not found"}),
            404,
            CONTENT_TYPE,
        )
    except MultipleResultsFound:
        return (
            jsonify({"error": "critical error"}),
            500,
            CONTENT_TYPE,
        )


@app.route("/events/share", methods=["POST"])
def event_share():
    try:
        share = event_share.loads(request)
        db.session.add(share)
        db.session.commit()
        return (
            event_share_schema.dump(favorite),
            200,
            CONTENT_TYPE,
        )
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(BAD_REQUEST),
            400,
            CONTENT_TYPE,
        )
