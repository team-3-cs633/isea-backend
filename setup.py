import os
from dotenv import load_dotenv
import requests
import json
import uuid


load_dotenv("./src/api/.env")


CONTENT_TYPE = "application/json"
API_KEY = "TBD"
VALID_HEADERS = {"Content-Type": CONTENT_TYPE, "x-api-key": API_KEY}
USER_ROLES_URL = "http://127.0.0.1:5555/users/roles"
USERS_URL = "http://127.0.0.1:5555/users"
EVENTS_URL = "http://127.0.0.1:5555/events"
USER_ROLE_UUID = os.getenv("USER_ROLE_UUID")
ADMIN_ROLE_UUID = os.getenv("ADMIN_ROLE_UUID")
COORDINATOR_ROLE_UUID = os.getenv("COORDINATOR_ROLE_UUID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
COORDINATOR_USERNAME = os.getenv("COORDINATOR_USERNAME")
COORDINATOR_PASSWORD = os.getenv("COORDINATOR_PASSWORD")


def load_user_roles():
    """
    Create the user roles with defined role ids.
    This is for managing user access on the frontend
    while not using cookies.

    """

    # Create Admin
    requests.post(
        USER_ROLES_URL,
        json={"id": ADMIN_ROLE_UUID, "role_name": "Admin"},
        headers=VALID_HEADERS,
    )

    # Create Coordinator
    requests.post(
        USER_ROLES_URL,
        json={"id": COORDINATOR_ROLE_UUID, "role_name": "Event Coordinator"},
        headers=VALID_HEADERS,
    )

    # Create Users
    requests.post(
        USER_ROLES_URL,
        json={"id": USER_ROLE_UUID, "role_name": "User"},
        headers=VALID_HEADERS,
    )


def load_default_users():
    """
    Create the default admin account.
    This also creates a coordinator user for testing purposes.

    """

    # Create Admin
    requests.post(
        USERS_URL,
        json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "user_role_id": ADMIN_ROLE_UUID,
        },
        headers=VALID_HEADERS,
    )

    # Create Coordinator
    requests.post(
        USERS_URL,
        json={
            "username": COORDINATOR_USERNAME,
            "password": COORDINATOR_PASSWORD,
            "user_role_id": COORDINATOR_ROLE_UUID,
        },
        headers=VALID_HEADERS,
    )


if __name__ == "__main__":
    load_user_roles()
    load_default_users()
