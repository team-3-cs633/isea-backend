from api import db, ma
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import uuid
import re


def generate_id() -> str:
    """
    Generate the id for the tables.
    Create a UUID and remove the "-"

    The UUID is used to prevent easy access to other user
    data since we are not implementing significant user data controls

    Returns:
        str: a uuid with "-" removed
    """
    return re.sub("-", "", str(uuid.uuid4()))


class UserRole(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    role_name = db.Column(db.String, unique=True, nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)


class UserRoleSchema(ma.Schema):
    class Meta:
        fields = ("id", "role_name")


user_role_schema = UserRoleSchema()
user_roles_schema = UserRoleSchema(many=True)


class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    username = db.Column(db.String, unique=True, nullable=False)
    user_role_id = db.Column(db.String, ForeignKey(UserRole.id), nullable=False)
    password = db.Column(db.String, nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    user_role = relationship(UserRole)


class UserInputSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "user_role_id", "password")


user_input_schema = UserInputSchema()
user_inputs_schema = UserInputSchema(many=True)


class UserOutputSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "user_role_id")


user_output_schema = UserOutputSchema()
user_outputs_schema = UserOutputSchema(many=True)


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
        )


event_schema = EventSchema()
events_schema = EventSchema(many=True)


class EventUpdateFormSchema(ma.Schema):
    class Meta:
        fields = (
            "user_id",
            "description",
            "category",
            "location",
            "cost",
            "start_time",
            "end_time",
            "event_link",
        )


event_update_form_schema = EventUpdateFormSchema()


class EventRegistration(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_id)
    event_id = db.Column(db.String, ForeignKey(Event.id), nullable=False)
    user_id = db.Column(db.String, ForeignKey(User.id), nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    event = relationship(Event)
    user = relationship(User)


class EventRegistrationSchema(ma.Schema):
    class Meta:
        fields = ("id", "event_id", "user_id")


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
        fields = ("id", "event_id", "user_id")


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
