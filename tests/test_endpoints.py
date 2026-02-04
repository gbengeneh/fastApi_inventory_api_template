import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Inventory POS backend running!"}
    print("✓ Root endpoint test passed")

def test_register_user():
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass",
        "role": "admin"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    # Allow 200 or 400 (if already registered)
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        assert "email" in response.json()
    print("✓ User registration test passed")
    return response.json() if response.status_code == 200 else None

def test_login():
    login_data = {
        "email": "test@example.com",
        "password": "testpass"
    }
    response = requests.post(f"{BASE_URL}/api/auth/token", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    print("✓ Login test passed")
    return response.json()["access_token"]

def test_get_me(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    print("✓ Get current user test passed")

def test_create_category(token):
    headers = {"Authorization": f"Bearer {token}"}
    category_data = {"name": "Test Category", "description": "A test category"}
    response = requests.post(f"{BASE_URL}/api/categories/", json=category_data, headers=headers)
    print(f"Category creation response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Category"
    print("✓ Create category test passed")
    return response.json()["id"]

def test_get_categories(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/categories/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("✓ Get categories test passed")

def test_create_product(token, category_id):
    headers = {"Authorization": f"Bearer {token}"}
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "cost_price": 10.0,
        "selling_price": 15.0,
        "category_id": category_id,
        "unit_id": 1  # Assuming unit exists
    }
    response = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"
    print("✓ Create product test passed")

def test_get_products(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("✓ Get products test passed")

if __name__ == "__main__":
    try:
        test_root()
        user = test_register_user()
        token = test_login()
        test_get_me(token)
        category_id = test_create_category(token)
        test_get_categories(token)
        test_create_product(token, category_id)
        test_get_products(token)
        print("\n🎉 All endpoint tests passed!")
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
