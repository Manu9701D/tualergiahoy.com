# api/views.py
import os
from datetime import datetime

import gspread
import requests
from google.oauth2.service_account import Credentials
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer


class RegisterView(APIView):
    """Vista principal para el registro de usuarios en tualergiahoy.com"""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        nombre_completo = f"{data['nombre']} {data['apellidos']}"
        alergias = data.get("alergias", [])
        ciudad = data.get("ciudad", "Madrid")

        # Calcular nivel de riesgo
        num_alergias = len([a for a in alergias if str(a).lower() != "ninguna"])
        nivel_riesgo = (
            "alto" if num_alergias >= 3 else "medio" if num_alergias >= 2 else "bajo"
        )

        # Consultar polen actual con Open-Meteo
        pollen_level = self._get_pollen_level(ciudad)

        # Guardar en Google Sheets
        self._save_to_google_sheets(data, nombre_completo, nivel_riesgo, alergias)

        # Log en consola (para desarrollo)
        self._log_registration(nombre_completo, data, nivel_riesgo, pollen_level)

        # Respuesta al frontend
        return Response(
            {
                "message": "¡Registro exitoso! Bienvenido a tualergiahoy.com",
                "nombre_completo": nombre_completo,
                "email": data.get("email"),
                "ciudad": ciudad,
                "nivel_riesgo": nivel_riesgo,
                "polen_actual": pollen_level,
                "alergias": alergias,
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_pollen_level(self, ciudad: str) -> str:
        """Consulta la API de Open-Meteo y devuelve el nivel de polen."""
        try:
            city_coords = {
                "Madrid": (40.4168, -3.7038),
                "Barcelona": (41.3851, 2.1734),
                "Valencia": (39.4699, -0.3763),
                "Sevilla": (37.3891, -5.9845),
                "Bilbao": (43.2630, -2.9350),
                "Zaragoza": (41.6488, -0.8891),
            }
            lat, lon = city_coords.get(ciudad, (40.4168, -3.7038))

            url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pollen_grass,pollen_tree,pollen_weed"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                current = response.json().get("current", {})
                pollen_sum = (
                    current.get("pollen_grass", 0)
                    + current.get("pollen_tree", 0)
                    + current.get("pollen_weed", 0)
                )
                return (
                    "Alto"
                    if pollen_sum > 50
                    else "Moderado"
                    if pollen_sum > 20
                    else "Bajo"
                )
        except Exception as e:
            print(f"Error Open-Meteo: {e}")

        return "No disponible"

    def _save_to_google_sheets(
        self, data: dict, nombre_completo: str, nivel_riesgo: str, alergias: list
    ):
        """Guarda el registro en Google Sheets."""
        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-493508-5cb178e0f4a0.json"

            if not os.path.exists(creds_path):
                print(f"❌ No se encontró el archivo de credenciales: {creds_path}")
                return

            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
            ]

            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)

            spreadsheet = client.open("tualergiahoy_registros")
            sheet = spreadsheet.sheet1

            sheet.append_row(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    nombre_completo,
                    data["nombre"],
                    data["apellidos"],
                    str(data["fecha_nacimiento"]),
                    data.get("ciudad", ""),
                    nivel_riesgo,
                    ", ".join(alergias),
                    data["email"],
                    data.get("nivel_sensibilidad", "medio"),
                ]
            )

            print("✅ Registro guardado correctamente en Google Sheets")

        except Exception as e:
            print(f"❌ Error al guardar en Google Sheets: {type(e).__name__} - {e}")

    def _log_registration(
        self, nombre_completo: str, data: dict, nivel_riesgo: str, pollen_level: str
    ):
        """Imprime información útil en consola durante desarrollo."""
        print("\n=== NUEVO REGISTRO EN tualergiahoy.com ===")
        print(f"Nombre completo : {nombre_completo}")
        print(f"Email           : {data.get('email')}")
        print(f"Ciudad          : {data.get('ciudad')}")
        print(f"Alergias        : {data.get('alergias')}")
        print(f"Nivel de riesgo : {nivel_riesgo}")
        print(f"Polen actual    : {pollen_level}")
        print("=" * 60)
