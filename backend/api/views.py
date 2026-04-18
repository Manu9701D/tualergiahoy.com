# api/views.py
import os
from datetime import datetime

import gspread
import requests
from django.core.mail import EmailMessage
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
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

GREEN_DARK   = colors.HexColor("#064e3b")
GREEN_MID    = colors.HexColor("#059669")
GREEN_LIGHT  = colors.HexColor("#d1fae5")
GREEN_PALE   = colors.HexColor("#f0fdf6")
GREEN_SUBTLE = colors.HexColor("#ecfdf5")
TEXT_MUTED   = colors.HexColor("#6b9e88")
WHITE        = colors.white


class RegisterView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini_client = self._get_gemini_client()

    def _get_gemini_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found in .env file")
            return None
        return genai.Client(api_key=api_key)

    def _get_coordinates(self, city: str):
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=5&language=es&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("results")
            if not results:
                return None, None
            first = results[0]
            return first["latitude"], first["longitude"]
        except Exception as e:
            print(f"Geocoding error for '{city}': {e}")
            return None, None

    def _get_pollen_level(self, city: str):
        """
        Get pollen level using Open-Meteo Air Quality API.
        Parámetros correctos según documentación oficial:
          - grass_pollen, birch_pollen, alder_pollen, olive_pollen, ragweed_pollen, mugwort_pollen
          - Solo disponibles en Europa durante temporada de pollen
          - 'weed_pollen' y 'tree_pollen' NO existen en la API
        """
        lat, lon = self._get_coordinates(city)

        if lat is None or lon is None:
            return f"ERROR: City '{city}' not found. Please check the spelling."

        # Parámetros correctos de la API de Open-Meteo
        pollen_params = "grass_pollen,birch_pollen,alder_pollen,olive_pollen,ragweed_pollen,mugwort_pollen"

        # Intento 1: con current= (tiempo real)
        url_current = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&current={pollen_params}"
            f"&domains=cams_europe"
        )

        # Intento 2: con hourly= + forecast_hours=1 (fallback)
        url_hourly = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly={pollen_params}"
            f"&forecast_hours=1"
            f"&domains=cams_europe"
        )

        for attempt, url in enumerate([url_current, url_hourly], start=1):
            try:
                response = requests.get(url, timeout=10)
                print(f"[Pollen attempt {attempt}] status={response.status_code} url={url}")

                if response.status_code != 200:
                    print(f"[Pollen attempt {attempt}] body={response.text[:400]}")
                    continue

                data = response.json()

                if attempt == 1:
                    src = data.get("current", {})
                    grass    = src.get("grass_pollen")    or 0
                    birch    = src.get("birch_pollen")    or 0
                    alder    = src.get("alder_pollen")    or 0
                    olive    = src.get("olive_pollen")    or 0
                    ragweed  = src.get("ragweed_pollen")  or 0
                    mugwort  = src.get("mugwort_pollen")  or 0
                else:
                    hourly = data.get("hourly", {})
                    def first(lst): return (lst[0] if lst else 0) or 0
                    grass    = first(hourly.get("grass_pollen", []))
                    birch    = first(hourly.get("birch_pollen", []))
                    alder    = first(hourly.get("alder_pollen", []))
                    olive    = first(hourly.get("olive_pollen", []))
                    ragweed  = first(hourly.get("ragweed_pollen", []))
                    mugwort  = first(hourly.get("mugwort_pollen", []))

                pollen_sum = grass + birch + alder + olive + ragweed + mugwort

                # Determinar tipo dominante para info adicional
                types = {
                    "gramíneas": grass, "abedul": birch, "aliso": alder,
                    "olivo": olive, "ambrosía": ragweed, "artemisa": mugwort
                }
                dominant = max(types, key=types.get)

                if pollen_sum > 50:
                    level = "Alto"
                elif pollen_sum > 20:
                    level = "Moderado"
                elif pollen_sum > 0:
                    level = "Bajo"
                else:
                    level = "Muy bajo"

                print(f"✅ Pollen OK: grass={grass}, birch={birch}, alder={alder}, olive={olive}, ragweed={ragweed}, mugwort={mugwort} → total={pollen_sum:.1f}")
                return f"{level} (Total: {pollen_sum:.1f} — dominante: {dominant})"

            except Exception as e:
                print(f"[Pollen attempt {attempt}] exception: {e}")
                continue

        return "No disponible"

    def _generate_gemini_forecast(self, full_name, city, allergies, risk_level, pollen_report):
        if not self.gemini_client:
            return "No se pudo generar el pronóstico en este momento."

        prompt = f"""
        Eres un experto en alergias. Crea un texto motivador y desenfadado para {full_name} 
        que vive en {city}, tiene alergias a: {', '.join(allergies)} y su nivel de riesgo es {risk_level}.
        El polen actual está en nivel {pollen_report}.
        Texto en español, positivo, útil, máximo 160 palabras.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini error: {e}")
            return "Mantén una buena hidratación y consulta con tu alergólogo si los síntomas persisten."

    def _generate_pdf_direct(self, full_name, city, risk_level, pollen_report, ai_content, allergies):
        try:
            filename = f"pronostico_{full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            filepath = os.path.join(os.path.dirname(__file__), "..", filename)

            doc = SimpleDocTemplate(
                filepath, pagesize=A4,
                leftMargin=18*mm, rightMargin=18*mm,
                topMargin=16*mm, bottomMargin=16*mm,
            )

            titulo = ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=22, textColor=GREEN_DARK, leading=28, spaceAfter=2)
            subtitulo = ParagraphStyle("subtitulo", fontName="Helvetica", fontSize=11, textColor=TEXT_MUTED, leading=16, spaceAfter=0)
            seccion = ParagraphStyle("seccion", fontName="Helvetica-Bold", fontSize=10, textColor=GREEN_MID, leading=14, spaceBefore=6, spaceAfter=2, letterSpacing=0.5)
            cuerpo = ParagraphStyle("cuerpo", fontName="Helvetica", fontSize=11, textColor=GREEN_DARK, leading=17, spaceAfter=6)
            cuerpo_muted = ParagraphStyle("cuerpo_muted", fontName="Helvetica", fontSize=10, textColor=TEXT_MUTED, leading=15, spaceAfter=4)
            footer_style = ParagraphStyle("footer", fontName="Helvetica", fontSize=9, textColor=TEXT_MUTED, alignment=1, leading=13)

            def card(inner_content, bg=GREEN_SUBTLE, radius=8):
                t = Table([[inner_content]], colWidths=[doc.width])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), bg),
                    ("ROUNDEDCORNERS", [radius]),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ]))
                return t

            risk_colors = {
                "alto":  (colors.HexColor("#fef2f2"), colors.HexColor("#dc2626")),
                "medio": (colors.HexColor("#fffbeb"), colors.HexColor("#d97706")),
                "bajo":  (GREEN_SUBTLE, GREEN_MID),
            }
            pill_bg, pill_fg = risk_colors.get(risk_level.lower(), (GREEN_SUBTLE, GREEN_MID))
            pill_style = ParagraphStyle("pill", fontName="Helvetica-Bold", fontSize=10, textColor=pill_fg, alignment=1)

            story = []

            logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend", "logo.jpg")
            if not os.path.exists(logo_path):
                logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.jpg")

            if os.path.exists(logo_path):
                logo = Image(logo_path, width=60, height=60)
                logo.hAlign = "CENTER"
                header_left = [[logo]]
            else:
                header_left = [[Paragraph("🌿", titulo)]]

            header_right = [
                [Paragraph("tualergiahoy", titulo)],
                [Paragraph("Tu pronóstico personalizado de alergias", subtitulo)],
            ]

            header_table = Table(
                [[Table(header_left, colWidths=[70]), Table(header_right, colWidths=[doc.width - 80])]],
                colWidths=[80, doc.width - 80],
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 4*mm))
            story.append(HRFlowable(width="100%", thickness=1.5, color=GREEN_LIGHT, spaceAfter=6*mm))

            user_inner = Table(
                [[Paragraph(f"<b>{full_name}</b>", cuerpo)],
                 [Paragraph(f"📍 {city}", cuerpo_muted)],
                 [Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", cuerpo_muted)]],
                colWidths=[doc.width - 28],
            )
            user_inner.setStyle(TableStyle([("LEFTPADDING", (0,0),(-1,-1), 0), ("RIGHTPADDING", (0,0),(-1,-1), 0), ("TOPPADDING", (0,0),(-1,-1), 1), ("BOTTOMPADDING", (0,0),(-1,-1), 1)]))
            story.append(card(user_inner))
            story.append(Spacer(1, 4*mm))

            risk_pill = Table([[Paragraph(f"Riesgo: {risk_level.upper()}", pill_style)]], colWidths=[(doc.width/2)-6])
            risk_pill.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,-1), pill_bg), ("ROUNDEDCORNERS", [6]), ("TOPPADDING", (0,0),(-1,-1), 8), ("BOTTOMPADDING", (0,0),(-1,-1), 8), ("LEFTPADDING", (0,0),(-1,-1), 8), ("RIGHTPADDING", (0,0),(-1,-1), 8)]))

            pollen_pill = Table([[Paragraph(f"Polen actual: {pollen_report}", ParagraphStyle("pp", fontName="Helvetica-Bold", fontSize=10, textColor=GREEN_DARK, alignment=1))]], colWidths=[(doc.width/2)-6])
            pollen_pill.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,-1), GREEN_LIGHT), ("ROUNDEDCORNERS", [6]), ("TOPPADDING", (0,0),(-1,-1), 8), ("BOTTOMPADDING", (0,0),(-1,-1), 8), ("LEFTPADDING", (0,0),(-1,-1), 8), ("RIGHTPADDING", (0,0),(-1,-1), 8)]))

            pills_row = Table([[risk_pill, pollen_pill]], colWidths=[doc.width/2, doc.width/2])
            pills_row.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),("ALIGN",(0,0),(-1,-1),"CENTER")]))
            story.append(pills_row)
            story.append(Spacer(1, 4*mm))

            story.append(Paragraph("ALERGIAS REGISTRADAS", seccion))
            allergy_text = "  ·  ".join([a.capitalize() for a in allergies if a.lower() != "ninguna"]) or "Ninguna registrada"
            story.append(card(Paragraph(allergy_text, cuerpo)))
            story.append(Spacer(1, 4*mm))

            story.append(Paragraph("TU PRONÓSTICO SEMANAL", seccion))
            story.append(card(Paragraph(ai_content.replace("\n", "<br/>"), cuerpo), bg=GREEN_PALE))
            story.append(Spacer(1, 6*mm))

            story.append(HRFlowable(width="100%", thickness=1, color=GREEN_LIGHT, spaceAfter=4*mm))
            story.append(Paragraph("tualergiahoy.com · Este informe es orientativo. Consulta siempre con tu alergólogo.", footer_style))

            doc.build(story)
            return filepath

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None

    def _send_welcome_email(self, email, full_name, city, pollen_report, pdf_path, risk_level, allergies):
        """Send welcome email with branded HTML body and PDF attachment"""
        try:
            first_name = full_name.split()[0]
            subject = f"¡Bienvenido a tualergiahoy, {first_name}! 🌿"

            risk_colors_map = {
                "alto":  ("#fef2f2", "#dc2626", "🔴"),
                "medio": ("#fffbeb", "#d97706", "🟡"),
                "bajo":  ("#ecfdf5", "#059669", "🟢"),
            }
            risk_bg, risk_color, risk_icon = risk_colors_map.get(risk_level.lower(), ("#ecfdf5", "#059669", "🟢"))

            allergy_pills = "".join([
                f'<span style="display:inline-block;background:#d1fae5;color:#047857;border-radius:20px;padding:3px 12px;font-size:13px;font-weight:500;margin:3px 4px 3px 0;">{a.capitalize()}</span>'
                for a in allergies if a.lower() != "ninguna"
            ]) or '<span style="color:#6b9e88;font-size:13px;">Ninguna registrada</span>'

            html_body = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bienvenido a tualergiahoy</title>
</head>
<body style="margin:0;padding:0;background-color:#f0fdf6;font-family:'Segoe UI',Arial,sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf6;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="540" cellpadding="0" cellspacing="0" style="max-width:540px;width:100%;">

          <!-- Header con logo y nombre -->
          <tr>
            <td style="background:#ffffff;border-radius:20px 20px 0 0;border:1.5px solid #d1fae5;border-bottom:none;padding:28px 32px 20px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="vertical-align:middle;">
                    <p style="margin:0;font-size:24px;font-weight:700;color:#064e3b;letter-spacing:-0.5px;">tualergiahoy</p>
                    <p style="margin:4px 0 0 0;font-size:13px;color:#6b9e88;">Tu compañero inteligente contra las alergias</p>
                  </td>
                  <td align="right" style="vertical-align:middle;">
                    <div style="width:48px;height:48px;background:#d1fae5;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;text-align:center;line-height:48px;">🌿</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Línea verde -->
          <tr>
            <td style="background:#ffffff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:0 32px;">
              <div style="height:2px;background:linear-gradient(90deg,#059669,#d1fae5);border-radius:2px;"></div>
            </td>
          </tr>

          <!-- Saludo -->
          <tr>
            <td style="background:#ffffff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:28px 32px 0 32px;">
              <p style="margin:0 0 8px 0;font-size:22px;font-weight:700;color:#064e3b;">¡Hola, {first_name}! 👋</p>
              <p style="margin:0;font-size:15px;color:#6b9e88;line-height:1.6;">
                Ya formas parte de <strong style="color:#059669;">tualergiahoy</strong>. 
                Te adjuntamos tu pronóstico personalizado y aquí tienes un resumen de tu perfil alérgico.
              </p>
            </td>
          </tr>

          <!-- Tarjeta: datos de ubicación -->
          <tr>
            <td style="background:#ffffff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:20px 32px 0 32px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fffe;border:1.5px solid #d1fae5;border-radius:12px;">
                <tr>
                  <td style="padding:16px 18px;">
                    <p style="margin:0 0 4px 0;font-size:11px;font-weight:600;color:#047857;letter-spacing:0.05em;text-transform:uppercase;">Tu ciudad</p>
                    <p style="margin:0;font-size:16px;font-weight:600;color:#064e3b;">📍 {city}</p>
                  </td>
                  <td style="padding:16px 18px;border-left:1px solid #d1fae5;">
                    <p style="margin:0 0 4px 0;font-size:11px;font-weight:600;color:#047857;letter-spacing:0.05em;text-transform:uppercase;">Polen actual</p>
                    <p style="margin:0;font-size:15px;font-weight:600;color:#064e3b;">🌱 {pollen_report}</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Tarjeta: nivel de riesgo -->
          <tr>
            <td style="background:#ffffff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:14px 32px 0 32px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:{risk_bg};border-radius:12px;">
                <tr>
                  <td style="padding:14px 18px;">
                    <p style="margin:0 0 2px 0;font-size:11px;font-weight:600;color:{risk_color};letter-spacing:0.05em;text-transform:uppercase;">Nivel de riesgo alérgico</p>
                    <p style="margin:0;font-size:20px;font-weight:700;color:{risk_color};">{risk_icon} {risk_level.upper()}</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Tarjeta: alergias -->
          <tr>
            <td style="background:#ffffff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:14px 32px 0 32px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fffe;border:1.5px solid #d1fae5;border-radius:12px;">
                <tr>
                  <td style="padding:14px 18px;">
                    <p style="margin:0 0 10px 0;font-size:11px;font-weight:600;color:#047857;letter-spacing:0.05em;text-transform:uppercase;">Alergias registradas</p>
                    <div>{allergy_pills}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA: PDF adjunto -->
          <tr>
            <td style="background:#ffffff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:20px 32px 0 32px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#ecfdf5;border-radius:12px;">
                <tr>
                  <td style="padding:18px 20px;">
                    <p style="margin:0 0 4px 0;font-size:15px;font-weight:600;color:#064e3b;">📄 Tu pronóstico está adjunto</p>
                    <p style="margin:0;font-size:13px;color:#6b9e88;line-height:1.6;">
                      Hemos generado un informe personalizado con tu previsión semanal de alergias. 
                      Encuéntralo adjunto a este correo.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Mensaje final -->
          <tr>
            <td style="background:#ffffff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:24px 32px 28px 32px;">
              <p style="margin:0;font-size:14px;color:#6b9e88;line-height:1.7;">
                Recuerda consultar siempre con tu alergólogo ante cualquier síntoma. 
                Estamos aquí para ayudarte a vivir mejor cada día. 💚
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f0fdf6;border:1.5px solid #d1fae5;border-top:none;border-radius:0 0 20px 20px;padding:18px 32px;">
              <p style="margin:0;font-size:12px;color:#6b9e88;text-align:center;line-height:1.6;">
                © {datetime.now().year} tualergiahoy.com · Este correo es informativo y no sustituye el consejo médico profesional.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""

            email_message = EmailMessage(
                subject=subject,
                body=html_body,
                from_email="tualergiahoy@gmail.com",
                to=[email],
            )
            email_message.content_subtype = "html"

            if pdf_path and os.path.exists(pdf_path):
                email_message.attach_file(pdf_path)

            email_message.send()
            print(f"✅ Email sent to {email}")
            return True

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def _save_to_google_sheets(self, data: dict, full_name: str, risk_level: str, allergies: list, pollen_report: str, password: str = None):
        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-493508-5cb178e0f4a0.json"
            if not os.path.exists(creds_path):
                print("❌ Credentials file not found")
                return
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
            ]
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open("tualergiahoy_registros").sheet1
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                full_name,
                data.get("nombre", ""),
                data.get("apellidos", ""),
                str(data.get("fecha_nacimiento", "")),
                data.get("ciudad", ""),
                risk_level,
                ", ".join(allergies),
                data.get("email", ""),
                pollen_report,
                password or ""
            ])
            print(f"✅ Registration saved to Google Sheets for {data.get('email')}")
        except Exception as e:
            print(f"❌ Error saving to Google Sheets: {type(e).__name__} - {e}")

    def _log_registration(self, full_name, data, allergies, risk_level, pollen_report, ai_content):
        print("\n=== NEW REGISTRATION IN tualergiahoy.com ===")
        print(f"Full name       : {full_name}")
        print(f"Email           : {data.get('email')}")
        print(f"City            : {data.get('ciudad')}")
        print(f"Allergies       : {allergies}")
        print(f"Risk level      : {risk_level}")
        print(f"Pollen level    : {pollen_report}")
        print(f"AI Content      : {ai_content[:150]}...")
        print("=" * 70)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        full_name = f"{data['nombre']} {data['apellidos']}"
        allergies = data.get("alergias", [])
        city = data.get("ciudad", "").strip()
        user_email = data.get("email")
        password = data.get("password")

        if not city:
            return Response({"error": "City is required"}, status=status.HTTP_400_BAD_REQUEST)

        num_allergies = len([a for a in allergies if str(a).lower() != "ninguna"])
        risk_level = "alto" if num_allergies >= 3 else "medio" if num_allergies >= 2 else "bajo"

        pollen_report = self._get_pollen_level(city)

        if pollen_report.startswith("ERROR:"):
            return Response(
                {"error": pollen_report.replace("ERROR: ", ""), "field": "ciudad"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_content = self._generate_gemini_forecast(full_name, city, allergies, risk_level, pollen_report)

        self._save_to_google_sheets(data, full_name, risk_level, allergies, pollen_report, password)

        pdf_path = self._generate_pdf_direct(full_name, city, risk_level, pollen_report, ai_content, allergies)

        # Pasamos risk_level y allergies al email
        email_sent = self._send_welcome_email(user_email, full_name, city, pollen_report, pdf_path, risk_level, allergies)

        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception as e:
                print(f"⚠️ Could not delete PDF: {e}")

        self._log_registration(full_name, data, allergies, risk_level, pollen_report, ai_content)

        return Response({
            "message": "¡Registro exitoso! Te hemos enviado tu pronóstico por email.",
            "nombre_completo": full_name,
            "email": user_email,
            "ciudad": city,
            "nivel_riesgo": risk_level,
            "polen_actual": pollen_report,
            "email_enviado": email_sent,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-493508-5cb178e0f4a0.json"
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
            ]
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open("tualergiahoy_registros").sheet1
            records = sheet.get_all_records()

            for row in records:
                if str(row.get("CORREO", "")).strip() == email and str(row.get("CONTRASEÑA", "")).strip() == password:
                    user_data = {
                        "nombre_completo": row.get("NOMBRE COMPLETO", ""),
                        "nombre": row.get("NOMBRE", ""),
                        "apellidos": row.get("APELLIDOS", ""),
                        "ciudad": row.get("CIUDAD", ""),
                        "nivel_riesgo": row.get("NIVEL DE ALERGIA", ""),
                        "alergias": row.get("ALERGIA", "").split(", ") if row.get("ALERGIA") else [],
                        "email": row.get("CORREO", ""),
                        "polen_actual": row.get("CANTIDAD DE POLEN", ""),
                        "fecha_nacimiento": row.get("F. NACIMIENTO", ""),
                    }
                    print(f"✅ Login successful for {email}")
                    return Response({"message": "Login successful", "user": user_data}, status=status.HTTP_200_OK)

            print(f"❌ No matching user found for email: {email}")
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(f"❌ Login error: {e}")
            return Response({"error": "Server error during login"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)