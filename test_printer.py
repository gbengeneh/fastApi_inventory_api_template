import requests

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBpbnZlbnRvcnkuY29tIiwiZXhwIjoxNzYxOTQ1MTI1fQ.SEz9yvhqnZDRGBY2-cSWZRNPWV43OsnY3FmKk6XyTR0'
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/printer-settings/', json={
    'outlet_id': 1,
    'printer_type': 'thermal',
    'printer_name': 'Test Printer',
    'is_default': True,
    'settings': '{"paper_size": "80mm"}'
}, headers=headers)
print(response.status_code, response.text)
