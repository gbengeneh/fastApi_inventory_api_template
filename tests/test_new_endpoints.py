import requests
import json
import time

BASE_URL = "http://localhost:8000"

def get_token():
    login_data = {
        "email": "admin@inventory.com",  # Assuming admin user exists
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/token", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get token")

def test_printer_settings(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Create a printer setting
    setting_data = {
        "outlet_id": 1,  # Assuming outlet exists
        "printer_type": "thermal",
        "printer_name": "Test Printer",
        "is_default": True,
        "settings": '{"paper_size": "80mm"}'
    }
    response = requests.post(f"{BASE_URL}/api/printer-settings/", json=setting_data, headers=headers)
    assert response.status_code == 200
    setting_id = response.json()["id"]
    print("✓ Created printer setting")

    # Get printer settings
    response = requests.get(f"{BASE_URL}/api/printer-settings/", headers=headers)
    assert response.status_code == 200
    print("✓ Retrieved printer settings")

    # Update printer setting
    update_data = {"printer_name": "Updated Printer"}
    response = requests.put(f"{BASE_URL}/api/printer-settings/{setting_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    print("✓ Updated printer setting")

    # Get default printer
    response = requests.get(f"{BASE_URL}/outlets/1/default-printer?printer_type=thermal", headers=headers)
    assert response.status_code == 200
    print("✓ Retrieved default printer")

    return setting_id

def test_invoice_templates(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Create an invoice template
    template_data = {
        "outlet_id": 1,
        "name": "Test Template",
        "header_text": "Invoice Header",
        "footer_text": "Thank you!",
        "is_default": True
    }
    response = requests.post(f"{BASE_URL}/api/invoice-templates/", json=template_data, headers=headers)
    assert response.status_code == 200
    template_id = response.json()["id"]
    print("✓ Created invoice template")

    # Get invoice templates
    response = requests.get(f"{BASE_URL}/api/invoice-templates/", headers=headers)
    assert response.status_code == 200
    print("✓ Retrieved invoice templates")

    # Update invoice template
    update_data = {"header_text": "Updated Header"}
    response = requests.put(f"{BASE_URL}/api/invoice-templates/{template_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    print("✓ Updated invoice template")

    # Get default template
    response = requests.get(f"{BASE_URL}/api/outlets/1/default-template", headers=headers)
    assert response.status_code == 200
    print("✓ Retrieved default template")

    return template_id

def test_installed_printers(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/printers/installed", headers=headers)
    assert response.status_code == 200
    printers = response.json()["printers"]
    print(f"✓ Retrieved installed printers: {len(printers)} found")
    return printers

def test_sales_invoice(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Create a payment first
    payment_data = {
        "payment_ref": "PAY-TEST-001",
        "related_type": "sale",
        "related_id": 1,  # Will be updated after sale creation
        "amount": 10.0,
        "amount_tendered": 15.0,  # Cash payment with change
        "method": "cash",
        "user_id": 3,
        "outlet_id": 1
    }
    response = requests.post(f"{BASE_URL}/api/payments/", json=payment_data, headers=headers)
    if response.status_code == 200:
        payment_id = response.json()["id"]
        print("✓ Created payment for sale")
    else:
        print(f"⚠ Payment creation failed: {response.status_code} - {response.text}")
        return None

    # Create a sale with payment_id
    sale_data = {
        "outlet_id": 1,
        "cashier_station_id": 1,
        "user_id": 3,
        "payment_id": payment_id,
        "total_amount": 10.0,
        "discount": 0.0,
        "tax": 0.0,
        "payment_status": "paid",
        "sale_type": "cash",
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "selling_price": 10.0,
                "cost_price": 5.0
            }
        ]
    }
    # Note: pos_id was removed from the schema, so this should work now
    response = requests.post(f"{BASE_URL}/api/sales/", json=sale_data, headers=headers)
    if response.status_code == 200:
        sale_id = response.json()["id"]
        print("✓ Created sale for testing invoice")
    else:
        print(f"⚠ Sale creation failed: {response.status_code} - {response.text}")
        return None

    # Generate invoice
    response = requests.get(f"{BASE_URL}/api/sales/{sale_id}/invoice", headers=headers)
    if response.status_code == 200:
        print("✓ Generated invoice")
    else:
        print(f"⚠ Invoice generation failed: {response.status_code} - {response.text}")
        print(f"Response content: {response.text}")

    # Print invoice (should now work with PDF fallback)
    response = requests.post(f"{BASE_URL}/api/sales/{sale_id}/print", headers=headers)
    if response.status_code == 200:
        print("✓ Printed invoice (PDF fallback)")
    else:
        print(f"⚠ Print invoice failed: {response.status_code} - {response.text}")

    return sale_id

def test_sale_payments(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Create a payment first
    payment_data = {
        "payment_ref": f"PAY-TEST-{int(time.time())}",
        "related_type": "sale",
        "related_id": 1,
        "amount": 20.0,
        "method": "card",
        "user_id": 3,
        "outlet_id": 1
    }
    response = requests.post(f"{BASE_URL}/api/payments/", json=payment_data, headers=headers)
    assert response.status_code == 200
    payment_id = response.json()["id"]
    print("✓ Created payment for sale payment test")

    # Create a sale
    sale_data = {
        "outlet_id": 1,
        "cashier_station_id": 1,
        "user_id": 3,
        "total_amount": 20.0,
        "discount": 0.0,
        "tax": 0.0,
        "payment_status": "paid",
        "sale_type": "card",
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "selling_price": 10.0,
                "cost_price": 5.0
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/api/sales/", json=sale_data, headers=headers)
    assert response.status_code == 200
    sale_id = response.json()["id"]
    print("✓ Created sale for sale payment test")

    # Create sale payment
    sale_payment_data = {
        "sale_id": sale_id,
        "payment_id": payment_id,
        "amount": 20.0
    }
    response = requests.post(f"{BASE_URL}/api/sales/{sale_id}/payments/", json=sale_payment_data, headers=headers)
    assert response.status_code == 200
    sale_payment_id = response.json()["id"]
    print("✓ Created sale payment")

    # Get sale payments
    response = requests.get(f"{BASE_URL}/api/sales/{sale_id}/payments/", headers=headers)
    assert response.status_code == 200
    payments = response.json()
    assert len(payments) > 0
    print("✓ Retrieved sale payments")

    # Delete sale payment
    response = requests.delete(f"{BASE_URL}/api/sales/{sale_id}/payments/{payment_id}", headers=headers)
    assert response.status_code == 200
    print("✓ Deleted sale payment")

def test_purchase_creation(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Get initial product state
    response = requests.get(f"{BASE_URL}/api/products/1", headers=headers)
    assert response.status_code == 200
    initial_product = response.json()
    initial_stock = initial_product["stock_quantity"]

    # Create purchase with final selling_price (calculated on frontend)
    purchase_data = {
        "supplier_id": 1,  # Assuming supplier exists
        "outlet_id": 1,
        "total_amount": 50.0,  # 10 * 5.0
        "payment_status": "paid",
        "invoice_number": f"PUR-TEST-{int(time.time())}",
        "created_by": 3,  # Assuming user exists
        "items": [
            {
                "product_id": 1,
                "quantity": 10,
                "cost_price": 5.0,
                "markup_percentage": 20.0,  # Still included for record keeping
                "selling_price": 6.0  # Final price calculated on frontend
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/api/purchases/", json=purchase_data, headers=headers)
    assert response.status_code == 200
    purchase_id = response.json()["id"]
    print("✓ Created purchase with final selling price")

    # Verify product updates
    response = requests.get(f"{BASE_URL}/api/products/1", headers=headers)
    assert response.status_code == 200
    updated_product = response.json()

    assert updated_product["cost_price"] == 5.0
    assert updated_product["selling_price"] == 6.0  # Should match the provided selling_price
    assert updated_product["stock_quantity"] == initial_stock + 10
    print("✓ Verified product selling price and stock quantity updates")

    return purchase_id

if __name__ == "__main__":
    try:
        token = get_token()
        test_printer_settings(token)
        test_invoice_templates(token)
        printers = test_installed_printers(token)
        test_sales_invoice(token)
        test_sale_payments(token)
        test_purchase_creation(token)
        print("\n🎉 All new endpoint tests completed!")
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
