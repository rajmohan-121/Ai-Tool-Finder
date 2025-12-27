import requests

BASE_URL = "http://127.0.0.1:8080"


# ---------------- HELPERS ---------------- #

def get_admin_token():
    response = requests.post(
        f"{BASE_URL}/admin/login",
        data={
            "username": "Team3",   # admin email / username
            "password": "Team3"    # admin password
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


# ---------------- TESTS ---------------- #

def test_add_tool():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "PyTest Tool",
        "use_case": "Testing API",
        "category": "Testing",
        "pricing": "Free"
    }

    response = requests.post(
        f"{BASE_URL}/admin/tools",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "PyTest Tool"
    assert data["pricing"] == "Free"


def test_get_tools():
    response = requests.get(f"{BASE_URL}/tools")

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)
