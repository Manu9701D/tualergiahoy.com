# test_register.py
import json

import requests

url = "http://127.0.0.1:8000/api/register/"

payload = {
    "nombre": "Juan",
    "apellidos": "Pérez García",
    "fecha_nacimiento": "1995-06-15",
    "ciudad": "Madrid",
    "alergias": ["polen", "gramíneas", "ácaros"],
    "email": "juan@example.com",
    "password": "123456",
    "nivel_sensibilidad": "alto",
}

headers = {"Content-Type": "application/json; charset=utf-8"}

response = requests.post(url, json=payload, headers=headers)

print("Status Code:", response.status_code)
print("Respuesta:")
print(response.json())
