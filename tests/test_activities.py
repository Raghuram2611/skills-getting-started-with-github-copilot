from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect a dictionary of activities
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_and_unregister_flow():
    activity = "Basketball Team"
    email = "testuser@example.com"

    # Ensure the email is not already in participants
    activities[activity]["participants"] = [p for p in activities[activity]["participants"] if p != email]

    # Signup should succeed
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # Now the participant should be present in the activity
    get_resp = client.get("/activities")
    participants = get_resp.json()[activity]["participants"]
    assert email in participants

    # Duplicate signup should fail with 400
    dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert dup.status_code == 400

    # Unregister should succeed
    unreg = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert unreg.status_code == 200
    assert "Unregistered" in unreg.json().get("message", "")

    # Verify participant no longer present
    get_resp = client.get("/activities")
    participants = get_resp.json()[activity]["participants"]
    assert email not in participants

    # Unregistering a non-existent participant should be 404
    notfound = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert notfound.status_code == 404


def test_activity_not_found():
    # Signup for nonexistent activity
    resp = client.post("/activities/NotAnActivity/signup?email=foo@example.com")
    assert resp.status_code == 404

    # Unregister for nonexistent activity
    resp = client.delete("/activities/NotAnActivity/unregister?email=foo@example.com")
    assert resp.status_code == 404
