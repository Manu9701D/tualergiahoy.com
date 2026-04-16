# api/views.py
import os
from datetime import datetime

import gspread
import requests
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer

load_dotenv()


class RegisterView(APIView):
    """Vista principal del registro para tualergiahoy.com"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini_client = self._get_gemini_client()

    def _get_gemini_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  WARNING: GEMINI_API_KEY no encontrada en el archivo .env")
            return None
        return genai.Client(api_key=api_key)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        nombre_completo = f"{data['nombre']} {data['apellidos']}"
        alergias = data.get("alergias", [])
        ciudad = data.get("ciudad", "Madrid")

        num_alergias = len([a for a in alergias if str(a).lower() != "ninguna"])
        nivel_riesgo = (
            "alto" if num_alergias >= 3 else "medio" if num_alergias >= 2 else "bajo"
        )

        # Consultar polen con Open-Meteo (parámetros CORRECTOS)
        pollen_level = self._get_pollen_level(ciudad)

        # Generar pronóstico con Gemini
        pronostico_ia = self._generate_gemini_forecast(
            nombre_completo, ciudad, alergias, nivel_riesgo, pollen_level
        )

        # Guardar en Google Sheets
        self._save_to_google_sheets(data, nombre_completo, nivel_riesgo, alergias)

        self._log_registration(
            nombre_completo, data, alergias, nivel_riesgo, pollen_level, pronostico_ia
        )

        return Response(
            {
                "message": "¡Registro exitoso! Bienvenido a tualergiahoy.com",
                "nombre_completo": nombre_completo,
                "email": data.get("email"),
                "ciudad": ciudad,
                "nivel_riesgo": nivel_riesgo,
                "polen_actual": pollen_level,
                "pronostico": pronostico_ia[:300] + "..."
                if len(pronostico_ia) > 300
                else pronostico_ia,
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_pollen_level(self, ciudad: str) -> str:
        """Consulta Open-Meteo con los parámetros CORRECTOS de polen"""
        try:
            city_coords = {
                "Madrid": (40.4168, -3.7038),
                "Barcelona": (41.3851, 2.1734),
                "Valencia": (39.4699, -0.3763),
                "Sevilla": (37.3891, -5.9845),
                "Bilbao": (43.2630, -2.9350),
            }
            lat, lon = city_coords.get(ciudad, (40.4168, -3.7038))

            # Parámetros CORRECTOS de polen en Open-Meteo 2026
            url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality?"
                f"latitude={lat}&longitude={lon}&"
                f"current=grass_pollen,alder_pollen,birch_pollen,mugwort_pollen,olive_pollen,ragweed_pollen"
            )
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                current = response.json().get("current", {})
                pollen_sum = sum(
                    current.get(k, 0)
                    for k in [
                        "grass_pollen",
                        "alder_pollen",
                        "birch_pollen",
                        "mugwort_pollen",
                        "olive_pollen",
                        "ragweed_pollen",
                    ]
                )
                print(
                    f"DEBUG - Polen sumado: {pollen_sum}"
                )  # ← para ver los datos reales
                if pollen_sum > 50:
                    return "Alto"
                elif pollen_sum > 20:
                    return "Moderado"
                else:
                    return "Bajo"

        except Exception as e:
            print(f"Error Open-Meteo: {e}")

        return "No disponible"

    # Resto de funciones sin cambios (mantén las que ya tenías)
    def _generate_gemini_forecast(
        self,
        nombre: str,
        ciudad: str,
        alergias: list,
        nivel_riesgo: str,
        pollen_level: str,
    ) -> str:
        if not self.gemini_client:
            return "No se pudo generar el pronóstico (falta configuración de Gemini)."

        prompt = f"""
        Eres un experto en alergias y bienestar respiratorio.
        Redacta un mensaje positivo, empático y práctico de máximo 130 palabras para esta semana.

        Usuario: {nombre}
        Ciudad: {ciudad}
        Alergias: {", ".join(alergias)}
        Nivel de riesgo: {nivel_riesgo}
        Nivel de polen actual: {pollen_level}

        El texto debe ser motivador, incluir 1 o 2 consejos útiles y terminar con una frase positiva.
        Escríbelo en español natural y cercano.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error al llamar a Gemini: {e}")
            return "No se pudo generar el pronóstico personalizado en este momento."

    def _save_to_google_sheets(
        self, data: dict, nombre_completo: str, nivel_riesgo: str, alergias: list
    ):
        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-493508-5cb178e0f4a0.json"
            if not os.path.exists(creds_path):
                print("❌ No se encontró el archivo de credenciales")
                return

            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
            ]
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)

            sheet = client.open("tualergiahoy_registros").sheet1
            sheet.append_row(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    nombre_completo,
                    data.get("nombre", ""),
                    data.get("apellidos", ""),
                    str(data.get("fecha_nacimiento", "")),
                    data.get("ciudad", ""),
                    nivel_riesgo,
                    ", ".join(alergias),
                    data.get("email", ""),
                    data.get("nivel_sensibilidad", "medio"),
                ]
            )
            print("✅ Registro guardado en Google Sheets")
        except Exception as e:
            print(f"❌ Error Google Sheets: {type(e).__name__} - {e}")

    def _log_registration(
        self,
        nombre_completo: str,
        data: dict,
        alergias: list,
        nivel_riesgo: str,
        pollen_level: str,
        pronostico: str,
    ):
        print("\n=== NUEVO REGISTRO EN tualergiahoy.com ===")
        print(f"Nombre completo : {nombre_completo}")
        print(f"Email           : {data.get('email')}")
        print(f"Ciudad          : {data.get('ciudad')}")
        print(f"Alergias        : {alergias}")
        print(f"Nivel de riesgo : {nivel_riesgo}")
        print(f"Polen actual    : {pollen_level}")
        print(f"Pronóstico IA   : {pronostico[:150]}...")
        print("=" * 70)
