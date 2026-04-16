# api/views.py
import os
from datetime import datetime

import gspread
import requests
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
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
            print("⚠️ WARNING: GEMINI_API_KEY no encontrada")
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

        pollen_report = self._get_pollen_level(ciudad)

        if pollen_report.startswith("ERROR:"):
            return Response(
                {"error": pollen_report.replace("ERROR: ", ""), "field": "ciudad"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pronostico_ia = self._generate_gemini_forecast(
            nombre_completo, ciudad, alergias, nivel_riesgo, pollen_report
        )

        self._save_to_google_sheets(data, nombre_completo, nivel_riesgo, alergias)

        pdf_path = self._generate_pdf_direct(
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
                "pdf_generado": pdf_path,
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_pollen_level(self, ciudad: str) -> str:
        """Versión dinámica: busca cualquier ciudad y devuelve error si no la encuentra"""
        if not ciudad or not ciudad.strip():
            return "ERROR: El campo 'ciudad' es obligatorio."

        ciudad = ciudad.strip()

        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es&format=json"
            geo_response = requests.get(geo_url, timeout=8)

            if geo_response.status_code != 200 or not geo_response.json().get(
                "results"
            ):
                return f"ERROR: No se encontraron datos para la ciudad '{ciudad}'. Por favor, verifica el nombre."

            result = geo_response.json()["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]
            ciudad_encontrada = result.get("name", ciudad)

            print(f"✅ Ciudad encontrada: {ciudad_encontrada} ({lat}, {lon})")

            pollen_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=grass_pollen,alder_pollen,birch_pollen,mugwort_pollen,olive_pollen,ragweed_pollen"
            response = requests.get(pollen_url, timeout=10)

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
                overall = "Alto" if total > 80 else "Moderado" if total > 30 else "Bajo"
                details = [
                    f"{name}: {value}"
                    for name, value in pollen_info.items()
                    if value > 5
                ]
                return f"{overall} (Total: {total}) — {' | '.join(details)}"

        except Exception as e:
            print(f"Error al consultar polen para '{ciudad}': {e}")

        return f"ERROR: No se pudieron obtener datos de polen para '{ciudad}'. Inténtalo de nuevo más tarde."

    def _generate_gemini_forecast(
        self,
        nombre: str,
        ciudad: str,
        alergias: list,
        nivel_riesgo: str,
        pollen_report: str,
    ) -> str:
        if not self.gemini_client:
            return "Pronóstico no disponible en este momento."

        prompt = f"""
        Eres un experto en alergología. Redacta un pronóstico semanal claro, empático y profesional de máximo 150 palabras.

        Usuario: {nombre}
        Ciudad: {ciudad}
        Alergias: {", ".join(alergias)}
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
            return "No se pudo generar el pronóstico personalizado."

    def _generate_pdf_direct(
        self, nombre_completo, ciudad, nivel_riesgo, pollen_report, pronostico, alergias
    ):
        """Genera PDF con logo a la derecha del título"""
        try:
            pdf_filename = f"pronostico_{nombre_completo.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

            doc = SimpleDocTemplate(
                pdf_filename,
                pagesize=A4,
                rightMargin=2.5 * cm,
                leftMargin=2.5 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "Title",
                parent=styles["Heading1"],
                fontSize=22,
                spaceAfter=8,
                alignment=0,
                textColor="#1a5f7a",
            )
            subtitle_style = ParagraphStyle(
                "Subtitle",
                parent=styles["Heading2"],
                fontSize=14,
                spaceAfter=25,
                alignment=0,
                textColor="#2c7a8c",
            )
            normal_style = styles["Normal"]
            bold_style = ParagraphStyle(
                "Bold",
                parent=normal_style,
                fontName="Helvetica-Bold",
                fontSize=12,
                textColor="#1a5f7a",
            )

            content = []

            # Logo a la derecha del título usando tabla
            logo_path = r"C:\Users\mnldz\tualergiahoy.com\backend\logo.jpg"

            if os.path.exists(logo_path):
                logo_img = Image(logo_path, width=160, height=210)  # tamaño equilibrado

                title_text = Paragraph(
                    "Pronóstico Personalizado<br/>de Salud Alérgica", title_style
                )

                data = [[title_text, logo_img]]

                table = Table(data, colWidths=[280, 180])
                table.setStyle(
                    TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ]
                    )
                )
                content.append(table)
            else:
                content.append(
                    Paragraph("Pronóstico Personalizado de Salud Alérgica", title_style)
                )

            content.append(Spacer(1, 30))

            # Información del usuario
            content.append(Paragraph(f"<b>Nombre:</b> {nombre_completo}", bold_style))
            content.append(Paragraph(f"<b>Ciudad:</b> {ciudad}", normal_style))
            content.append(
                Paragraph(
                    f"<b>Nivel de riesgo alérgico:</b> {nivel_riesgo}", normal_style
                )
            )
            content.append(
                Paragraph(
                    f"<b>Situación actual del polen:</b> {pollen_report}", normal_style
                )
            )
            content.append(Spacer(1, 25))

            # Pronóstico
            content.append(
                Paragraph("<b>¿Cómo te sentirás esta semana?</b>", bold_style)
            )
            content.append(Paragraph(pronostico, normal_style))
            content.append(Spacer(1, 25))

            # Recomendaciones
            content.append(Paragraph("<b>Consejos prácticos:</b>", bold_style))
            content.append(
                Paragraph(
                    "• Mantén las ventanas cerradas por la mañana y al atardecer.",
                    normal_style,
                )
            )
            content.append(
                Paragraph(
                    "• Usa gafas de sol y mascarilla si sales en días con mucho polen.",
                    normal_style,
                )
            )
            content.append(
                Paragraph("• Bebe mucha agua y descansa bien.", normal_style)
            )
            content.append(Spacer(1, 30))

            # Agradecimiento
            content.append(
                Paragraph(
                    "¡Gracias por registrarte en <b>tualergiahoy.com</b>!<br/><br/>"
                    "Esperamos que este pronóstico te ayude a disfrutar más la primavera.<br/><br/>"
                    "Recuerda: cada día es una oportunidad para respirar mejor 🌿",
                    normal_style,
                )
            )

            content.append(Spacer(1, 25))
            content.append(Paragraph("¡Un abrazo!", normal_style))
            content.append(Paragraph("El equipo de tualergiahoy", normal_style))

            doc.build(content)

            print(
                f"✅ PDF generado correctamente con logo a la derecha: {pdf_filename}"
            )
            return pdf_filename

        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
            return None

    def _save_to_google_sheets(
        self, data: dict, nombre_completo: str, nivel_riesgo: str, alergias: list
    ):
        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-493508-5cb178e0f4a0.json"
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
