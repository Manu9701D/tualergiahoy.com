# test_register.py
import json
from datetime import datetime

import requests

BASE_URL = "http://127.0.0.1:8000/api/register/"

# Lista de usuarios para probar la aplicación a fondo
test_users = [
    {
        "nombre": "Juan",
        "apellidos": "Pérez García",
        "fecha_nacimiento": "1995-06-15",
        "ciudad": "Madrid",
        "alergias": ["polen", "gramíneas", "ácaros"],
        "email": "juan.perez@gmail.com",
        "password": "123456",
        "nivel_sensibilidad": "alto",
    },
    {
        "nombre": "María",
        "apellidos": "López Fernández",
        "fecha_nacimiento": "1988-03-22",
        "ciudad": "Barcelona",
        "alergias": ["olivo", "gramíneas"],
        "email": "maria.lopez@gmail.com",
        "password": "123456",
        "nivel_sensibilidad": "medio",
    },
    {
        "nombre": "Carlos",
        "apellidos": "Rodríguez Soto",
        "fecha_nacimiento": "2001-11-05",
        "ciudad": "Valencia",
        "alergias": ["ácaros", "polen"],
        "email": "carlos.rodriguez@hotmail.com",
        "password": "123456",
        "nivel_sensibilidad": "bajo",
    },
    {
        "nombre": "Laura",
        "apellidos": "Martínez Ruiz",
        "fecha_nacimiento": "1992-07-30",
        "ciudad": "Sevilla",
        "alergias": ["gramíneas", "olivo", "ácaros", "ambrosía"],
        "email": "laura.martinez@yahoo.com",
        "password": "123456",
        "nivel_sensibilidad": "alto",
    },
    {
        "nombre": "Diego",
        "apellidos": "Gómez Navarro",
        "fecha_nacimiento": "1997-04-12",
        "ciudad": "Bilbao",
        "alergias": ["ninguna"],
        "email": "diego.gomez@gmail.com",
        "password": "123456",
        "nivel_sensibilidad": "bajo",
    },
]

print("🚀 Iniciando pruebas múltiples de registro...\n")
print("=" * 80)

for i, user in enumerate(test_users, 1):
    print(f"\n📋 Prueba {i}/5 - Registrando: {user['nombre']} {user['apellidos']}")
    print(f"   Ciudad: {user['ciudad']} | Email: {user['email']}")

    try:
        response = requests.post(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            json=user,
            timeout=15,
        )

        print(f"   Status Code: {response.status_code}")

        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ Registro exitoso")
            print(f"   Mensaje: {result.get('message')}")
            print(f"   PDF generado: {result.get('pdf_generado', 'No disponible')}")
            print(f"   Email enviado: {result.get('email_enviado', 'No disponible')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detalle: {error_detail}")
            except:
                print(f"   Respuesta: {response.text[:300]}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

    print("-" * 60)

print("\n✅ Pruebas múltiples finalizadas.")
print("Revisa la consola del servidor Django para ver los logs detallados.")
print("Revisa tu bandeja de entrada / Spam para comprobar los correos recibidos.")
