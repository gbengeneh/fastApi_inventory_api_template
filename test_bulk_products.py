import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    login_data = {
        "email": "admin@inventory.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/token", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_bulk_products(token):
    headers = {"Authorization": f"Bearer {token}"}

    # 20 realistic bulk products data (tax_rate in decimal 0-1, optional)
    bulk_products = [
        {"name": "Apple iPhone 14", "category_id": 1, "unit_id": 1, "cost_price": 700.0, "selling_price": 999.0, "stock_quantity": 50, "reorder_level": 10, "tax_rate": 0.08},
        {"name": "Samsung Galaxy S23", "category_id": 1, "unit_id": 1, "cost_price": 650.0, "selling_price": 899.0, "stock_quantity": 40, "reorder_level": 8, "tax_rate": 0.08},
        {"name": "Nike Air Max Shoes", "category_id": 2, "unit_id": 2, "cost_price": 80.0, "selling_price": 120.0, "stock_quantity": 100, "reorder_level": 20},
        {"name": "Adidas Ultraboost", "category_id": 2, "unit_id": 2, "cost_price": 90.0, "selling_price": 140.0, "stock_quantity": 80, "reorder_level": 15, "tax_rate": 0.1},
        {"name": "Dell XPS 13 Laptop", "category_id": 1, "unit_id": 1, "cost_price": 800.0, "selling_price": 1200.0, "stock_quantity": 30, "reorder_level": 5, "tax_rate": 0.07},
        {"name": "HP Pavilion Desktop", "category_id": 1, "unit_id": 1, "cost_price": 500.0, "selling_price": 750.0, "stock_quantity": 25, "reorder_level": 5},
        {"name": "Coca-Cola 2L Bottle", "category_id": 3, "unit_id": 3, "cost_price": 1.5, "selling_price": 2.5, "stock_quantity": 200, "reorder_level": 50, "tax_rate": 0.05},
        {"name": "Pepsi 2L Bottle", "category_id": 3, "unit_id": 3, "cost_price": 1.4, "selling_price": 2.4, "stock_quantity": 180, "reorder_level": 40},
        {"name": "Whole Wheat Bread", "category_id": 4, "unit_id": 4, "cost_price": 2.0, "selling_price": 3.5, "stock_quantity": 150, "reorder_level": 30, "tax_rate": 0.02},
        {"name": "White Rice 5kg", "category_id": 4, "unit_id": 5, "cost_price": 8.0, "selling_price": 12.0, "stock_quantity": 100, "reorder_level": 20},
        {"name": "Chicken Breast 1kg", "category_id": 4, "unit_id": 5, "cost_price": 6.0, "selling_price": 10.0, "stock_quantity": 80, "reorder_level": 15, "tax_rate": 0.05},
        {"name": "Beef Steak 1kg", "category_id": 4, "unit_id": 5, "cost_price": 12.0, "selling_price": 18.0, "stock_quantity": 60, "reorder_level": 10},
        {"name": "Milk 1L Carton", "category_id": 3, "unit_id": 3, "cost_price": 1.2, "selling_price": 2.0, "stock_quantity": 120, "reorder_level": 25, "tax_rate": 0.03},
        {"name": "Orange Juice 1L", "category_id": 3, "unit_id": 3, "cost_price": 2.5, "selling_price": 4.0, "stock_quantity": 90, "reorder_level": 18},
        {"name": "Toothpaste Colgate", "category_id": 5, "unit_id": 6, "cost_price": 1.0, "selling_price": 2.5, "stock_quantity": 200, "reorder_level": 40, "tax_rate": 0.08},
        {"name": "Shampoo Head & Shoulders", "category_id": 5, "unit_id": 6, "cost_price": 3.0, "selling_price": 5.0, "stock_quantity": 150, "reorder_level": 30},
        {"name": "Notebook A4 100 pages", "category_id": 6, "unit_id": 7, "cost_price": 1.5, "selling_price": 3.0, "stock_quantity": 300, "reorder_level": 50, "tax_rate": 0.05},
        {"name": "Pen Parker", "category_id": 6, "unit_id": 7, "cost_price": 2.0, "selling_price": 4.0, "stock_quantity": 250, "reorder_level": 40},
        {"name": "T-Shirt Cotton", "category_id": 2, "unit_id": 2, "cost_price": 5.0, "selling_price": 15.0, "stock_quantity": 150, "reorder_level": 30, "tax_rate": 0.1},
        {"name": "Jeans Levi's", "category_id": 2, "unit_id": 2, "cost_price": 20.0, "selling_price": 50.0, "stock_quantity": 100, "reorder_level": 20}
    ]

    response = requests.post(f"{BASE_URL}/api/products/bulk/", json=bulk_products, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        created_products = response.json()
        print(f"Successfully created {len(created_products)} products")
        for product in created_products:
            print(f"- {product['name']} (ID: {product['id']})")
    else:
        print("Bulk creation failed")

if __name__ == "__main__":
    token = login()
    if token:
        test_bulk_products(token)
    else:
        print("Cannot proceed without authentication")
