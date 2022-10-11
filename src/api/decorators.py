from functools import wraps
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError
from api.constants import (
    NOT_FOUND_ERROR,
    CRITICAL_ERROR,
    CONTENT_TYPE,
    BAD_REQUEST_ERROR,
)


def one_result(func):
    """
    Decorator for requests that require only one result.

    This is a wrapper around route functions that need to
    validate that only one result exists when executing a query
    """

    @wraps(func)
    def call_inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except NoResultFound:
            return (
                jsonify(NOT_FOUND_ERROR),
                404,
                CONTENT_TYPE,
            )
        except MultipleResultsFound:
            return (
                jsonify(CRITICAL_ERROR),
                500,
                CONTENT_TYPE,
            )

    return call_inner


def valid_result(func):
    """
    Decorator for requests that need to validate data.

    This is a wrapper around route functions that need to
    validate data of a request.

    This data validation can be:
    - A validation error caused when loading a particular marshmallow schema
    - An integrity error caused by an issue with a database action
    that requires a rollback
    """

    @wraps(func)
    def call_inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except ValidationError:
            return (
                jsonify(BAD_REQUEST_ERROR),
                400,
                CONTENT_TYPE,
            )

        except IntegrityError:
            db.session.rollback()
            return (
                jsonify(BAD_REQUEST_ERROR),
                400,
                CONTENT_TYPE,
            )

    return call_inner
