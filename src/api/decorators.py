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
