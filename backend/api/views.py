# api/views.py
import os
from datetime import datetime

import gspread
import requests
from django.core.mail import EmailMessage
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
    """Main view for user registration in tualergiahoy.com"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini_client = self._get_gemini_client()

    def _get_gemini_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found")
            return None
        return genai.Client(api_key=api_key)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        full_name = f"{data['nombre']} {data['apellidos']}"
        allergies = data.get("alergias", [])
        city = data.get("ciudad", "Madrid")
        user_email = data.get("email")

        num_allergies = len([a for a in allergies if str(a).lower() != "ninguna"])
        risk_level = (
            "alto" if num_allergies >= 3 else "medio" if num_allergies >= 2 else "bajo"
        )

        pollen_report = self._get_pollen_level(city)

        if pollen_report.startswith("ERROR:"):
            return Response(
                {"error": pollen_report.replace("ERROR: ", ""), "field": "ciudad"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_content = self._generate_gemini_forecast(
            full_name, city, allergies, risk_level, pollen_report
        )

        self._save_to_google_sheets(data, full_name, risk_level, allergies)

        pdf_path = self._generate_pdf_direct(
            full_name, city, risk_level, pollen_report, ai_content
        )

        email_sent = self._send_welcome_email(
            user_email, full_name, city, pollen_report, pdf_path
        )

        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                print(f"🗑️ PDF deleted: {pdf_path}")
            except Exception as e:
                print(f"⚠️ Could not delete PDF: {e}")

        self._log_registration(
            full_name, data, allergies, risk_level, pollen_report, ai_content
        )

        return Response(
            {
                "message": "¡Registro exitoso! Te hemos enviado un correo con tu pronóstico.",
                "nombre_completo": full_name,
                "email": user_email,
                "ciudad": city,
                "nivel_riesgo": risk_level,
                "polen_actual": pollen_report,
                "email_enviado": email_sent,
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_pollen_level(self, city: str) -> str:
        if not city or not city.strip():
            return "ERROR: The 'city' field is required."

        city = city.strip()

        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=es&format=json"
            geo_response = requests.get(geo_url, timeout=8)

            if geo_response.status_code != 200 or not geo_response.json().get(
                "results"
            ):
                return f"ERROR: No data found for the city '{city}'."

            result = geo_response.json()["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]

            print(f"✅ City found: {result.get('name', city)}")

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
                level = "Alto" if total > 80 else "Moderado" if total > 30 else "Bajo"
                details = [
                    f"{name}: {value}"
                    for name, value in pollen_info.items()
                    if value > 5
                ]
                return f"{level} (Total: {total}) — {' | '.join(details)}"

        except Exception as e:
            print(f"Error pollen: {e}")

        return f"ERROR: Could not retrieve pollen data for '{city}'."

    def _generate_gemini_forecast(
        self,
        full_name: str,
        city: str,
        allergies: list,
        risk_level: str,
        pollen_report: str,
    ) -> str:
        """Generate VERY clean text for PDF - strict formatting"""
        if not self.gemini_client:
            return "Forecast not available at this moment."

        prompt = f"""
        Eres un experto en alergología. Genera un texto EXTREMADAMENTE LIMPIO y bien organizado para un PDF.

        Usuario: {full_name}
        Ciudad: {city}
        Alergias: {", ".join(allergies)}
        Nivel de riesgo: {risk_level}
        Situación actual del polen: {pollen_report}

        Reglas estrictas:
        - NO uses asteriscos (**), guiones al principio, ni ningún markdown.
        - Usa títulos claros seguidos de párrafos cortos.
        - Las recomendaciones deben ser una lista con guiones simples (-).
        - El texto debe ser fácil de leer en PDF: párrafos cortos, sin bloques densos.

        Estructura exacta que debes seguir:

        Pronóstico Semanal
        [Párrafo corto y positivo de 3-4 líneas]

        Recomendaciones según el nivel de polen
        - Recomendación clara y práctica 1
        - Recomendación clara y práctica 2
        - Recomendación clara y práctica 3
        - Recomendación clara y práctica 4

        Mantén un tono empático y positivo. Máximo 240 palabras en total.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini error: {e}")
            return "No se pudo generar el pronóstico personalizado."

    def _generate_pdf_direct(
        self, full_name, city, risk_level, pollen_report, ai_content
    ):
        """Generate PDF"""
        try:
            pdf_filename = f"pronostico_{full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

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
            normal_style = styles["Normal"]
            bold_style = ParagraphStyle(
                "Bold",
                parent=normal_style,
                fontName="Helvetica-Bold",
                fontSize=12,
                textColor="#1a5f7a",
            )

            content = []

            # Logo a la derecha
            logo_path = r"C:\Users\mnldz\tualergiahoy.com\backend\logo.jpg"
            if os.path.exists(logo_path):
                logo_img = Image(logo_path, width=165, height=195)
                title_text = Paragraph(
                    "Pronóstico Personalizado<br/>de Salud Alérgica", title_style
                )
                data = [[title_text, logo_img]]
                table = Table(data, colWidths=[290, 165])
                table.setStyle(
                    TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                        ]
                    )
                )
                content.append(table)
            else:
                content.append(
                    Paragraph("Pronóstico Personalizado de Salud Alérgica", title_style)
                )

            content.append(Spacer(1, 25))

            content.append(Paragraph(f"<b>Nombre:</b> {full_name}", bold_style))
            content.append(Paragraph(f"<b>Ciudad:</b> {city}", normal_style))
            content.append(
                Paragraph(
                    f"<b>Nivel de riesgo alérgico:</b> {risk_level}", normal_style
                )
            )
            content.append(
                Paragraph(
                    f"<b>Situación actual del polen:</b> {pollen_report}", normal_style
                )
            )
            content.append(Spacer(1, 25))

            # AI Content - now much cleaner
            content.append(Paragraph(ai_content, normal_style))
            content.append(Spacer(1, 30))

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
            print(f"✅ PDF generated: {pdf_filename}")
            return pdf_filename

        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return None

    def _send_welcome_email(self, to_email, full_name, city, pollen_report, pdf_path):
        """Send real email"""
        try:
            subject = f"¡Bienvenido a tualergiahoy.com, {full_name.split()[0]}!"

            html_body = f"""
            <h2>¡Hola, {full_name}!</h2>
            <p>Gracias por registrarte en <strong>tualergiahoy.com</strong>.</p>
            <p><strong>Ciudad:</strong> {city}<br>
               <strong>Polen actual:</strong> {pollen_report}</p>
            <p>Adjunto encontrarás tu pronóstico personalizado.</p>
            <p>¡Esperamos que te sea muy útil!</p>
            <br>
            <p>Un abrazo,<br><strong>El equipo de tualergiahoy.com</strong></p>
            """

            email = EmailMessage(
                subject=subject,
                body=html_body,
                from_email="tualergiahoy <no-reply@tualergiahoy.com>",
                to=[to_email],
            )
            email.content_subtype = "html"

            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    email.attach(
                        os.path.basename(pdf_path), f.read(), "application/pdf"
                    )

            email.send(fail_silently=False)
            print(f"✅ Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def _save_to_google_sheets(self, data, full_name, risk_level, allergies):
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
                    full_name,
                    data.get("nombre", ""),
                    data.get("apellidos", ""),
                    str(data.get("fecha_nacimiento", "")),
                    data.get("ciudad", ""),
                    risk_level,
                    ", ".join(allergies),
                    data.get("email", ""),
                    data.get("nivel_sensibilidad", "medio"),
                ]
            )
            print("✅ Saved to Google Sheets")
        except Exception as e:
            print(f"❌ Sheets error: {e}")

    def _log_registration(
        self, full_name, data, allergies, risk_level, pollen_report, ai_content
    ):
        print("\n=== NEW REGISTRATION IN tualergiahoy.com ===")
        print(f"Full name : {full_name}")
        print(f"Email     : {data.get('email')}")
        print(f"City      : {data.get('ciudad')}")
        print(f"Allergies : {allergies}")
        print(f"Risk      : {risk_level}")
        print(f"Pollen    : {pollen_report}")
        print("=" * 70)
