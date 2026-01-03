import requests

BASE_URL = "http://127.0.0.1:8080"


# ---------------- HELPERS ---------------- #

def get_admin_token():
    response = requests.post(
        f"{BASE_URL}/admin/login",
        data={
            "username": "Team3",
            "password": "Team3"
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def create_tool(token):
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(
        f"{BASE_URL}/admin/tools",
        json={
            "name": "Review Tool",
            "use_case": "Testing reviews",
            "category": "Testing",
            "pricing": "Free"
        },
        headers=headers
    )

    assert response.status_code == 200, response.text
    return response.json()["id"]


def submit_review(tool_id):
    response = requests.post(
        f"{BASE_URL}/review",
        json={
            "tool_id": tool_id,
            "rating": 5,
            "comment": "Test review"
        }
    )
    assert response.status_code == 200, response.text


# ---------------- TESTS ---------------- #

def test_submit_review():
    token = get_admin_token()
    tool_id = create_tool(token)

    response = requests.post(
        f"{BASE_URL}/review",
        json={
            "tool_id": tool_id,
            "rating": 5,
            "comment": "Test review"
        }
    )

    assert response.status_code == 200, response.text
    assert "waiting for admin approval" in response.json()["message"].lower()


def test_get_reviews():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/admin/reviews",
        headers=headers
    )

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_approve_review():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure at least one pending review exists
    tool_id = create_tool(token)
    submit_review(tool_id)

    reviews_response = requests.get(
        f"{BASE_URL}/admin/reviews",
        headers=headers
    )
    assert reviews_response.status_code == 200, reviews_response.text

    reviews = reviews_response.json()
    pending = [r for r in reviews if r["status"] == "Pending"]
    assert len(pending) > 0, "No pending reviews to approve"

    review_id = pending[0]["id"]

    response = requests.put(
        f"{BASE_URL}/admin/reviews/{review_id}/approve",
        headers=headers
    )

    assert response.status_code == 200, response.text
    assert "approved" in response.json()["message"].lower()

