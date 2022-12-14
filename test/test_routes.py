import requests
import json
import uuid
from api import ADMIN_ROLE_UUID, USER_ROLE_UUID, APPLICATION_URL


CONTENT_TYPE = "application/json"
API_KEY = "TBD"
VALID_HEADERS = {"Content-Type": CONTENT_TYPE, "x-api-key": API_KEY}

USER_ROLES_URL = APPLICATION_URL + "/users/roles"
USERS_URL = APPLICATION_URL + "/users"
USERS_LOGIN_URL = APPLICATION_URL + "/users/login"
USER_ID_URL = APPLICATION_URL + "/users/{}"
USER_FAVORITES_URL = APPLICATION_URL + "/users/{}/favorite"
USER_REGISTRATIONS_URL = APPLICATION_URL + "/users/{}/registration"
USER_SUGGESTIONS_URL = APPLICATION_URL + "/users/{}/suggestion"

EVENTS_URL = APPLICATION_URL + "/events"
EVENT_ID_URL = APPLICATION_URL + "/events/{}"
EVENT_METRICS_URL = APPLICATION_URL + "/events/{}/metrics"
EVENTS_REGISTRATION_URL = APPLICATION_URL + "/events/registration"
EVENT_REGISTRATION_REMOVAL_URL = APPLICATION_URL + "/events/{}/registration/{}"
EVENTS_FAVORITE_URL = APPLICATION_URL + "/events/favorite"
EVENT_FAVORITE_REMOVAL_URL = APPLICATION_URL + "/events/{}/favorite/{}"
EVENTS_SHARE_URL = APPLICATION_URL + "/events/share"

USER_UUID = str(uuid.uuid4())
EVENT_UUID = str(uuid.uuid4())
ADMIN_UUID = str(uuid.uuid4())


def test_user_role_creation():
    request = requests.post(
        USER_ROLES_URL,
        json={"id": USER_ROLE_UUID, "role_name": "User"},
        headers=VALID_HEADERS,
        verify=False,
    )
    request = requests.post(
        USER_ROLES_URL,
        json={"id": ADMIN_ROLE_UUID, "role_name": "Admin"},
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 2
    assert response_body["role_name"] == "Admin"
    assert response_body["id"] == ADMIN_ROLE_UUID


def test_user_roles():
    request = requests.get(USER_ROLES_URL, headers=VALID_HEADERS, verify=False)
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 2
    assert response_body[0]["role_name"] == "User"
    assert response_body[1]["role_name"] == "Admin"


def test_user_creation():
    request = requests.post(
        USERS_URL,
        json={
            "id": USER_UUID,
            "username": "test person",
            "password": "test",
            "user_role_id": USER_ROLE_UUID,
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_role_id"] == USER_ROLE_UUID
    assert response_body["id"] == USER_UUID
    assert response_body["username"] == "test person"


def test_user_login():
    request = requests.post(
        USERS_LOGIN_URL,
        json={
            "username": "Test Person",
            "password": "test",
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_role_id"] == USER_ROLE_UUID
    assert response_body["id"] == USER_UUID
    assert response_body["username"] == "test person"


def test_get_all_users():
    request = requests.get(
        USERS_URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 1
    assert response_body[0]["user_role_id"] == USER_ROLE_UUID
    assert response_body[0]["id"] == USER_UUID
    assert response_body[0]["username"] == "test person"


def test_get_single_user():
    URL = USER_ID_URL.format(USER_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_role_id"] == USER_ROLE_UUID
    assert response_body["id"] == USER_UUID
    assert response_body["username"] == "test person"


def test_create_event():
    request = requests.post(
        EVENTS_URL,
        json={
            "id": EVENT_UUID,
            "description": "test event",
            "category": "science and technology",
            "location": "bu met",
            "cost": "free",
            "start_time": "some date format",
            "end_time": "some other date",
            "event_link": "some url",
            "create_user_id": USER_UUID,
            "update_time": "now",
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 10
    assert response_body["create_user_id"] == USER_UUID
    assert response_body["id"] == EVENT_UUID
    assert response_body["description"] == "test event"


def test_get_events():
    request = requests.get(
        EVENTS_URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 1
    assert len(response_body[0].keys()) == 10
    assert response_body[0]["create_user_id"] == USER_UUID
    assert response_body[0]["id"] == EVENT_UUID
    assert response_body[0]["description"] == "test event"


def test_get_single_event():
    URL = EVENT_ID_URL.format(EVENT_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 10
    assert response_body["create_user_id"] == USER_UUID
    assert response_body["id"] == EVENT_UUID
    assert response_body["description"] == "test event"


def test_update_single_event():
    URL = EVENT_ID_URL.format(EVENT_UUID)
    request = requests.post(
        URL,
        json={
            "user_id": USER_UUID,
            "description": "test event UPDATED",
            "category": "science and technology",
            "location": "bu met",
            "cost": "free",
            "start_time": "some date format",
            "end_time": "some other date",
            "event_link": "some url",
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 10
    assert response_body["create_user_id"] == USER_UUID
    assert response_body["id"] == EVENT_UUID
    assert response_body["description"] == "test event UPDATED"


def test_event_registration():
    request = requests.post(
        EVENTS_REGISTRATION_URL,
        json={
            "user_id": USER_UUID,
            "event_id": EVENT_UUID,
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_id"] == USER_UUID
    assert response_body["event_id"] == EVENT_UUID


def test_event_favorite():
    request = requests.post(
        EVENTS_FAVORITE_URL,
        json={
            "user_id": USER_UUID,
            "event_id": EVENT_UUID,
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_id"] == USER_UUID
    assert response_body["event_id"] == EVENT_UUID


def test_user_registrations():
    URL = USER_REGISTRATIONS_URL.format(USER_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 1
    assert response_body[0]["create_user_id"] == USER_UUID
    assert response_body[0]["id"] == EVENT_UUID
    assert response_body[0]["description"] == "test event UPDATED"


def test_user_favorites():
    URL = USER_FAVORITES_URL.format(USER_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 1
    assert response_body[0]["create_user_id"] == USER_UUID
    assert response_body[0]["id"] == EVENT_UUID
    assert response_body[0]["description"] == "test event UPDATED"


def test_user_suggestions():
    URL = USER_SUGGESTIONS_URL.format(USER_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 0


def test_event_share():
    request = requests.post(
        EVENTS_SHARE_URL,
        json={
            "event_id": EVENT_UUID,
            "user_id": USER_UUID,
            "to": "isea.sender@gmail.com",
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 4
    assert response_body["event_id"] == EVENT_UUID
    assert response_body["user_id"] == USER_UUID
    assert response_body["to"] == "isea.sender@gmail.com"


def test_event_metrics():
    URL = EVENT_METRICS_URL.format(EVENT_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 4
    assert response_body["registrations"] == 1
    assert response_body["favorites"] == 1
    assert response_body["favorites"] == 1


def test_remove_event_registration():
    URL = EVENT_REGISTRATION_REMOVAL_URL.format(EVENT_UUID, USER_UUID)
    request = requests.post(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_id"] == USER_UUID
    assert response_body["event_id"] == EVENT_UUID

    URL = USER_REGISTRATIONS_URL.format(USER_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 0


def test_remove_event_favorite():
    URL = EVENT_FAVORITE_REMOVAL_URL.format(EVENT_UUID, USER_UUID)
    request = requests.post(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_id"] == USER_UUID
    assert response_body["event_id"] == EVENT_UUID

    URL = USER_FAVORITES_URL.format(USER_UUID)
    request = requests.get(
        URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 0


def test_user_delete():
    user_id = "23456"
    requests.post(
        USERS_URL,
        json={
            "id": user_id,
            "username": "test delete",
            "password": "test",
            "user_role_id": USER_ROLE_UUID,
        },
        headers=VALID_HEADERS,
        verify=False,
    )

    requests.post(
        USERS_URL,
        json={
            "id": ADMIN_UUID,
            "username": "test admin",
            "password": "test",
            "user_role_id": ADMIN_ROLE_UUID,
        },
        headers=VALID_HEADERS,
        verify=False,
    )

    request = requests.delete(
        USERS_URL,
        json={
            "user_id": user_id,
            "requester_id": ADMIN_UUID,
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 3
    assert response_body["user_role_id"] == USER_ROLE_UUID
    assert response_body["id"] == user_id
    assert response_body["username"] == "test delete"

    request = requests.get(
        USERS_URL,
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body) == 2
    assert response_body[0]["user_role_id"] == USER_ROLE_UUID
    assert response_body[0]["id"] == USER_UUID
    assert response_body[0]["username"] == "test person"
    assert response_body[1]["user_role_id"] == ADMIN_ROLE_UUID
    assert response_body[1]["id"] == ADMIN_UUID
    assert response_body[1]["username"] == "test admin"


def test_delete_event():
    request = requests.delete(
        EVENTS_URL,
        json={
            "event_id": EVENT_UUID,
            "requester_id": ADMIN_UUID,
        },
        headers=VALID_HEADERS,
        verify=False,
    )
    response_body = json.loads(request.text)

    assert request.status_code == 200
    assert len(response_body.keys()) == 10
    assert response_body["create_user_id"] == USER_UUID
    assert response_body["id"] == EVENT_UUID
    assert response_body["description"] == "test event UPDATED"
