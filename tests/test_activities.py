from urllib.parse import quote
import pytest

from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_flow(client):
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # signup
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # confirm present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # duplicate signup should fail
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 400

    # remove participant
    resp = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # removing again should fail
    resp = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert resp.status_code == 400


def test_activity_not_found(client):
    bad_activity = "NonExistingActivity"
    email = "noone@example.com"

    resp = client.post(f"/activities/{quote(bad_activity)}/signup?email={quote(email)}")
    assert resp.status_code == 404

    resp = client.delete(f"/activities/{quote(bad_activity)}/participants?email={quote(email)}")
    assert resp.status_code == 404
