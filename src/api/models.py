from api import db, ma, USER_ROLE_UUID
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
    """
    Class that represents the user role table.

        Attributes:
            id: the primary key represented as a UUID
            role_name: a unique name for the user role
            canceled: 1 if canceled 0 if not
    """

    id = db.Column(db.String, primary_key=True, default=USER_ROLE_UUID)
    role_name = db.Column(db.String, unique=True, nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)


class UserRoleSchema(ma.Schema):
    """
    Class that represents the user role schema.

        Used for serialization and deserialization of objects
        and for validating the data from requests
    """

    class Meta:
        fields = ("id", "role_name")


user_role_schema = UserRoleSchema()
user_roles_schema = UserRoleSchema(many=True)


class User(db.Model):
    """
    Class that represents the user table.

        Attributes:
            id: the primary key represented as a UUID
            username: a unique name for the user
            user_role_id: the id of the role associated with the user
            password: the hashed password of the user
            canceled: 1 if canceled 0 if not
    """

    id = db.Column(db.String, primary_key=True, default=generate_id)
    username = db.Column(db.String, unique=True, nullable=False)
    user_role_id = db.Column(
        db.String, ForeignKey(UserRole.id), nullable=False, default=USER_ROLE_UUID
    )
    password = db.Column(db.String, nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    user_role = relationship(UserRole)


class UserInputSchema(ma.Schema):
    """
    Class that represents the user input schema.

        Used for serialization and deserialization of objects
        and for validating the data from user creation requests
    """

    class Meta:
        fields = ("id", "username", "user_role_id", "password")


user_input_schema = UserInputSchema()
user_inputs_schema = UserInputSchema(many=True)


class UserOutputSchema(ma.Schema):
    """
    Class that represents the user output schema.

        Used specifying the data to return in a request
        associated with a user
    """

    class Meta:
        fields = ("id", "username", "user_role_id")


user_output_schema = UserOutputSchema()
user_outputs_schema = UserOutputSchema(many=True)


class Event(db.Model):
    """
    Class that represents the user role table.

        Attributes:
            id: the primary key represented as a UUID
            description: the event description, described what the event is about
            category: the event category, used for filtering results
            location: the specific location of the event
            cost: the cost of the event
            start_time: the start time and date of the event with the local timezone
            end_time: the end time and date of the event with the local timezone
            event_link: a url that links to more information about the event
            create_user_id: the id of the user that created the event
            update_time: the last time of update associated with the event row
            canceled: 1 if canceled 0 if not
    """

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
    """
    Class that represents the event schema.

        Used for serialization and deserialization of objects
        and for validating the data from event requests
    """

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
    """
    Class that represents the event update schema.

        Used for serialization and deserialization of objects
        and for validating the data from event update requests
    """

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
    """
    Class that represents the event registration table.

        Attributes:
            id: the primary key represented as a UUID
            event_id: the id of the event the user is being registered to
            user_id: the id of the user that is registering to the event
            canceled: 1 if canceled 0 if not
    """

    id = db.Column(db.String, primary_key=True, default=generate_id)
    event_id = db.Column(db.String, ForeignKey(Event.id), nullable=False)
    user_id = db.Column(db.String, ForeignKey(User.id), nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    event = relationship(Event)
    user = relationship(User)


class EventRegistrationSchema(ma.Schema):
    """
    Class that represents the event registration schema.

        Used for serialization and deserialization of objects
        and for validating the data from event registration requests
    """

    class Meta:
        fields = ("id", "event_id", "user_id")


event_registration_schema = EventRegistrationSchema()
event_registrations_schema = EventRegistrationSchema(many=True)


class EventFavorite(db.Model):
    """
    Class that represents the event favorite table.

        Attributes:
            id: the primary key represented as a UUID
            event_id: the id of the event the user is favoriting
            user_id: the id of the user that is favoriting the event
            canceled: 1 if canceled 0 if not
    """

    id = db.Column(db.String, primary_key=True, default=generate_id)
    event_id = db.Column(db.String, ForeignKey(Event.id), nullable=False)
    user_id = db.Column(db.String, ForeignKey(User.id), nullable=False)
    canceled = db.Column(db.Integer, nullable=False, default=0)

    event = relationship(Event)
    user = relationship(User)


class EventFavoriteSchema(ma.Schema):
    """
    Class that represents the event favorite schema.

        Used for serialization and deserialization of objects
        and for validating the data from event favorite requests
    """

    class Meta:
        fields = ("id", "event_id", "user_id")


event_favorite_schema = EventFavoriteSchema()
event_favorites_schema = EventFavoriteSchema(many=True)


class EventShare(db.Model):
    """
    Class that represents the event share table.

        Attributes:
            id: the primary key represented as a UUID
            event_id: the id of the event that was shared
    """

    id = db.Column(db.String, primary_key=True, default=generate_id)
    event_id = db.Column(db.String, ForeignKey(Event.id), nullable=False)

    event = relationship(Event)


class EventShareSchema(ma.Schema):
    """
    Class that represents the event share schema.

        Used for serialization and deserialization of objects
        and for validating the data from event share requests
    """

    class Meta:
        fields = ("id", "event_id")


event_share_schema = EventShareSchema()
event_shares_schema = EventShareSchema(many=True)


db.create_all()
