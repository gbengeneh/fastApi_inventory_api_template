import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    print("Testing auth flow...")

    # Step 1: Login
    login_data = {
        "email": "admin@inventory.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/token", json=login_data)
    print(f"Login response status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print("✓ Login successful")
        print(f"Access token: {access_token[:50]}...")
        print(f"Refresh token: {refresh_token[:50]}...")
    else:
        print(f"✗ Login failed: {response.text}")
        return

    # Step 2: Test protected endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
    print(f"Protected endpoint response status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Protected endpoint accessible")
    else:
        print(f"✗ Protected endpoint failed: {response.text}")

    # Step 3: Test refresh token
    response = requests.post(f"{BASE_URL}/api/auth/refresh?refresh_token={refresh_token}")
    print(f"Refresh response status: {response.status_code}")
    if response.status_code == 200:
        new_tokens = response.json()
        new_access_token = new_tokens["access_token"]
        new_refresh_token = new_tokens["refresh_token"]
        print("✓ Refresh successful")
        print(f"New access token: {new_access_token[:50]}...")
        print(f"New refresh token: {new_refresh_token[:50]}...")
    else:
        print(f"✗ Refresh failed: {response.text}")
        return

    # Step 4: Test with new access token
    headers = {"Authorization": f"Bearer {new_access_token}"}
    response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
    print(f"New access token test status: {response.status_code}")
    if response.status_code == 200:
        print("✓ New access token works")
    else:
        print(f"✗ New access token failed: {response.text}")

    # Step 5: Test /me endpoint
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"/me endpoint test status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✓ /me endpoint works - User: {user_data['name']} ({user_data['email']})")
    else:
        print(f"✗ /me endpoint failed: {response.text}")

if __name__ == "__main__":
    test_auth_flow()
