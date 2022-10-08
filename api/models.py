from api import db, ma
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import uuid
import re


def generate_id():
    return re.sub("-", "", str(uuid.uuid4()))


class UserRole(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    role_name = db.Column(db.String, unique=True, nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)


class UserRoleSchema(ma.Schema):
    class Meta:
        fields = ("id", "role_name", "canceled")


user_role_schema = UserRoleSchema()
user_roles_schema = UserRoleSchema(many=True)


class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    username = db.Column(db.String, unique=True, nullable=False)
    user_role_id = db.Column(db.String, ForeignKey(UserRole.id), nullable=False)
    password = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    user_role = relationship(UserRole)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "user_role_id", "canceled")


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Event(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    description = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    cost = db.Column(db.String, nullable=False)
    start_time = db.Column(db.String, nullable=False)
    end_time = db.Column(db.String, nullable=False)
    event_link = db.Column(db.String, nullable=True)
    create_user_id = db.Column(db.String, ForeignKey(User.id), nullable=False)
    update_time = db.Column(db.String, nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    user = relationship(User)


class EventSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "description",
            "category",
            "location",
            "cost",
            "start_time",
            "end_time",
            "event_link",
            "create_user_id",
            "update_time",
            "canceled",
        )


event_schema = EventSchema()
events_schema = EventSchema(many=True)


class EventRegistration(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    event_id = db.Column(db.String, ForeignKey(Event.id), nullable=False)
    user_id = db.Column(db.String, ForeignKey(User.id), nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    event = relationship(Event)
    user = relationship(User)


class EventRegistrationSchema(ma.Schema):
    class Meta:
        fields = ("id", "event_id", "user_id", "canceled")


event_registration_schema = EventRegistrationSchema()
event_registrations_schema = EventRegistrationSchema(many=True)


class EventFavorite(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    event_id = db.Column(db.String, ForeignKey(Event.id), nullable=False)
    user_id = db.Column(db.String, ForeignKey(User.id), nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    event = relationship(Event)
    user = relationship(User)


class EventFavoriteSchema(ma.Schema):
    class Meta:
        fields = ("id", "event_id", "user_id", "canceled")


event_favorite_schema = EventFavoriteSchema()
event_favorites_schema = EventFavoriteSchema(many=True)


class EventShare(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    event_id = db.Column(db.String, ForeignKey(Event.id), nullable=False)

    event = relationship(Event)


class EventShareSchema(ma.Schema):
    class Meta:
        fields = ("id", "event_id")


event_share_schema = EventShareSchema()
event_shares_schema = EventShareSchema(many=True)


db.create_all()
