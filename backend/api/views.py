# api/views.py
import os
from datetime import datetime

import gspread
import requests
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
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
        self.docs_service = None
        self.drive_service = None
        self._init_google_services()

    def _get_gemini_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY no encontrada")
            return None
        return genai.Client(api_key=api_key)

    def _init_google_services(self):
        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-service-v2.json"
            scope = [
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/drive",
                "https://spreadsheets.google.com/feeds",
            ]
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            self.docs_service = build("docs", "v1", credentials=creds)
            self.drive_service = build("drive", "v3", credentials=creds)
            print("✅ Servicios Google Docs y Drive inicializados")
        except Exception as e:
            print(f"❌ Error inicializando servicios Google: {e}")

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

        # Polen profesional y detallado
        pollen_report = self._get_pollen_level(ciudad)

        pronostico_ia = self._generate_gemini_forecast(
            nombre_completo, ciudad, alergias, nivel_riesgo, pollen_report
        )

        self._save_to_google_sheets(data, nombre_completo, nivel_riesgo, alergias)

        pdf_path, doc_url = self._create_and_export_pdf(
            nombre_completo,
            ciudad,
            nivel_riesgo,
            pollen_report,
            pronostico_ia,
            alergias,
        )

        self._log_registration(
            nombre_completo, data, alergias, nivel_riesgo, pollen_report, pronostico_ia
        )

        return Response(
            {
                "message": "¡Registro exitoso! Se ha generado tu pronóstico personalizado.",
                "nombre_completo": nombre_completo,
                "email": data.get("email"),
                "ciudad": ciudad,
                "nivel_riesgo": nivel_riesgo,
                "polen_actual": pollen_report,
                "pronostico": pronostico_ia[:300] + "..."
                if len(pronostico_ia) > 300
                else pronostico_ia,
                "documento_url": doc_url,
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_pollen_level(self, ciudad: str) -> str:
        """Devuelve informe profesional y detallado del polen"""
        try:
            city_coords = {
                "Madrid": (40.4168, -3.7038),
                "Barcelona": (41.3851, 2.1734),
                "Valencia": (39.4699, -0.3763),
                "Sevilla": (37.3891, -5.9845),
                "Bilbao": (43.2630, -2.9350),
            }
            lat, lon = city_coords.get(ciudad, (40.4168, -3.7038))

            url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality?"
                f"latitude={lat}&longitude={lon}&"
                f"current=grass_pollen,alder_pollen,birch_pollen,mugwort_pollen,olive_pollen,ragweed_pollen"
            )
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                current = response.json().get("current", {})

                pollen_info = {
                    "Gramíneas": current.get("grass_pollen", 0),
                    "Abedul": current.get("birch_pollen", 0),
                    "Olivo": current.get("olive_pollen", 0),
                    "Artemisa": current.get("mugwort_pollen", 0),
                    "Aliso": current.get("alder_pollen", 0),
                    "Ambrosía": current.get("ragweed_pollen", 0),
                }

                total = sum(pollen_info.values())
                overall_level = (
                    "Alto" if total > 80 else "Moderado" if total > 30 else "Bajo"
                )

                # Resumen profesional
                details = [
                    f"{name}: {value}"
                    for name, value in pollen_info.items()
                    if value > 0
                ]
                report = f"{overall_level} (Total: {total}) — {' | '.join(details)}"

                print(f"DEBUG - Polen profesional: {report}")
                return report

        except Exception as e:
            print(f"Error Open-Meteo: {e}")

        return "Datos de polen no disponibles en este momento"

    def _generate_gemini_forecast(
        self,
        nombre: str,
        ciudad: str,
        alergias: list,
        nivel_riesgo: str,
        pollen_report: str,
    ) -> str:
        if not self.gemini_client:
            return "Pronóstico no disponible."

        prompt = f"""
        Eres un alergólogo experto y comunicador claro.
        Redacta un pronóstico semanal profesional, empático y útil de máximo 150 palabras.

        Usuario: {nombre}
        Ciudad: {ciudad}
        Alergias declaradas: {", ".join(alergias)}
        Nivel de riesgo: {nivel_riesgo}
        Situación actual del polen: {pollen_report}

        Incluye recomendaciones prácticas y termina con un mensaje motivador.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error Gemini: {e}")
            return "No se pudo generar el pronóstico personalizado en este momento."

    def _create_and_export_pdf(
        self, nombre_completo, ciudad, nivel_riesgo, pollen_report, pronostico, alergias
    ):
        """Versión optimizada: copia, rellena, genera PDF y borra inmediatamente"""
        if not self.docs_service or not self.drive_service:
            print("❌ Servicios Google Docs no inicializados")
            return None, None

        try:
            TEMPLATE_DOCUMENT_ID = (
                "1JPAOXkWmxGA3ogwGOuI62-0JO5HlyiieehfXW4FGdlI"  # Tu ID
            )

            # 1. Copiar plantilla
            copy_title = f"Pronóstico - {nombre_completo} - {datetime.now().strftime('%Y-%m-%d')}"
            drive_response = (
                self.drive_service.files()
                .copy(fileId=TEMPLATE_DOCUMENT_ID, body={"name": copy_title})
                .execute()
            )
            document_id = drive_response.get("id")

            print(f"✅ Plantilla copiada temporalmente (ID: {document_id})")

            # 2. Rellenar plantilla
            requests_list = [
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{fecha}}"},
                        "replaceText": datetime.now().strftime("%d de %B de %Y"),
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{nombre}}"},
                        "replaceText": nombre_completo,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{ciudad}}"},
                        "replaceText": ciudad,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{nivel_riesgo}}"},
                        "replaceText": nivel_riesgo,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{polen_actual}}"},
                        "replaceText": pollen_report,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{pronostico}}"},
                        "replaceText": pronostico,
                    }
                },
            ]

            self.docs_service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests_list}
            ).execute()

            # 3. Exportar a PDF
            pdf_filename = f"pronostico_{nombre_completo.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            request = self.drive_service.files().export_media(
                fileId=document_id, mimeType="application/pdf"
            )

            with open(pdf_filename, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

            print(f"✅ PDF generado correctamente: {pdf_filename}")

            # 4. Borrar el documento temporal para no consumir quota
            try:
                self.drive_service.files().delete(fileId=document_id).execute()
                print("🗑️ Documento temporal eliminado automáticamente")
            except:
                pass

            return (
                pdf_filename,
                f"https://docs.google.com/document/d/{document_id}/edit",
            )

        except Exception as e:
            print(f"❌ Error creando PDF: {type(e).__name__} - {e}")
            return None, None

    def _save_to_google_sheets(
        self, data: dict, nombre_completo: str, nivel_riesgo: str, alergias: list
    ):
        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-service-v2.json"
            if not os.path.exists(creds_path):
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
            print(f"❌ Error Sheets: {e}")

    def _log_registration(
        self, nombre_completo, data, alergias, nivel_riesgo, pollen_report, pronostico
    ):
        print("\n=== NUEVO REGISTRO EN tualergiahoy.com ===")
        print(f"Nombre completo : {nombre_completo}")
        print(f"Email           : {data.get('email')}")
        print(f"Ciudad          : {data.get('ciudad')}")
        print(f"Alergias        : {alergias}")
        print(f"Nivel de riesgo : {nivel_riesgo}")
        print(f"Polen actual    : {pollen_report}")
        print(f"Pronóstico IA   : {pronostico[:150]}...")
        print("=" * 70)
