# api/views.py
import os
from datetime import datetime

import bcrypt
import gspread
import requests
from django.core.mail import EmailMessage
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
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


def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash"""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


class RegisterView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini_client = self._get_gemini_client()

    def _get_gemini_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  GEMINI_API_KEY not found")
            return None
        return genai.Client(api_key=api_key)

    def _get_coordinates(self, city: str):
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=5&language=es&format=json"
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            results = r.json().get("results")
            if not results:
                return None, None
            return results[0]["latitude"], results[0]["longitude"]
        except Exception as e:
            print(f"Geocoding error for '{city}': {e}")
            return None, None

    def _get_pollen_level(self, city: str):
        lat, lon = self._get_coordinates(city)
        if lat is None:
            return f"ERROR: City '{city}' not found. Please check the spelling."

        pollen_params = "grass_pollen,birch_pollen,alder_pollen,olive_pollen,ragweed_pollen,mugwort_pollen"
        urls = [
            f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current={pollen_params}&domains=cams_europe",
            f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly={pollen_params}&forecast_hours=1&domains=cams_europe",
        ]

        for i, url in enumerate(urls, 1):
            try:
                r = requests.get(url, timeout=10)
                print(f"[Pollen {i}] status={r.status_code}")
                if r.status_code != 200:
                    print(f"[Pollen {i}] {r.text[:300]}")
                    continue
                data = r.json()
                if i == 1:
                    src = data.get("current", {})
                    vals = [src.get(k) or 0 for k in pollen_params.split(",")]
                else:
                    h = data.get("hourly", {})
                    vals = [(h.get(k, [0])[0] or 0) for k in pollen_params.split(",")]

                total = sum(vals)
                names = ["gramíneas", "abedul", "aliso", "olivo", "ambrosía", "artemisa"]
                dominant = names[vals.index(max(vals))] if max(vals) > 0 else "ninguno"
                level = "Alto" if total > 50 else "Moderado" if total > 20 else "Bajo" if total > 0 else "Muy bajo"
                print(f"✅ Pollen total={total:.1f}, dominant={dominant}")
                return f"{level} (Total: {total:.1f} — dominante: {dominant})"
            except Exception as e:
                print(f"[Pollen {i}] exception: {e}")

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
            return self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=[prompt]
            ).text.strip()
        except Exception as e:
            print(f"Gemini error: {e}")
            return "Mantén una buena hidratación y consulta con tu alergólogo si los síntomas persisten."

    def _generate_pdf_direct(self, full_name, city, risk_level, pollen_report, ai_content, allergies):
        try:
            filename = f"pronostico_{full_name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            filepath = os.path.join(os.path.dirname(__file__), "..", filename)

            doc = SimpleDocTemplate(filepath, pagesize=A4,
                leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)

            titulo      = ParagraphStyle("titulo",    fontName="Helvetica-Bold", fontSize=22, textColor=GREEN_DARK,  leading=28, spaceAfter=2)
            subtitulo   = ParagraphStyle("subtitulo", fontName="Helvetica",      fontSize=11, textColor=TEXT_MUTED,  leading=16)
            seccion     = ParagraphStyle("seccion",   fontName="Helvetica-Bold", fontSize=10, textColor=GREEN_MID,   leading=14, spaceBefore=6, spaceAfter=2)
            cuerpo      = ParagraphStyle("cuerpo",    fontName="Helvetica",      fontSize=11, textColor=GREEN_DARK,  leading=17, spaceAfter=6)
            cuerpo_m    = ParagraphStyle("cuerpo_m",  fontName="Helvetica",      fontSize=10, textColor=TEXT_MUTED,  leading=15, spaceAfter=4)
            footer_s    = ParagraphStyle("footer",    fontName="Helvetica",      fontSize=9,  textColor=TEXT_MUTED,  alignment=1, leading=13)

            def card(content, bg=GREEN_SUBTLE, radius=8):
                t = Table([[content]], colWidths=[doc.width])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0,0),(-1,-1), bg), ("ROUNDEDCORNERS",[radius]),
                    ("TOPPADDING",(0,0),(-1,-1),10), ("BOTTOMPADDING",(0,0),(-1,-1),10),
                    ("LEFTPADDING",(0,0),(-1,-1),14), ("RIGHTPADDING",(0,0),(-1,-1),14),
                ]))
                return t

            risk_map = {
                "alto":  (colors.HexColor("#fef2f2"), colors.HexColor("#dc2626")),
                "medio": (colors.HexColor("#fffbeb"), colors.HexColor("#d97706")),
                "bajo":  (GREEN_SUBTLE, GREEN_MID),
            }
            pill_bg, pill_fg = risk_map.get(risk_level.lower(), (GREEN_SUBTLE, GREEN_MID))
            pill_s = ParagraphStyle("pill", fontName="Helvetica-Bold", fontSize=10, textColor=pill_fg, alignment=1)

            story = []

            # — Cabecera solo con texto, sin logo —
            header_inner = Table(
                [[Paragraph("tualergiahoy", titulo)],
                 [Paragraph("Tu pronóstico personalizado de alergias", subtitulo)]],
                colWidths=[doc.width],
            )
            header_inner.setStyle(TableStyle([
                ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
                ("TOPPADDING",(0,0),(-1,-1),0), ("BOTTOMPADDING",(0,0),(-1,-1),2),
            ]))
            story.append(header_inner)
            story.append(Spacer(1, 3*mm))
            story.append(HRFlowable(width="100%", thickness=1.5, color=GREEN_LIGHT, spaceAfter=6*mm))

            # — Datos usuario —
            user_inner = Table(
                [[Paragraph(f"<b>{full_name}</b>", cuerpo)],
                 [Paragraph(f"Ciudad: {city}", cuerpo_m)],
                 [Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", cuerpo_m)]],
                colWidths=[doc.width - 28],
            )
            user_inner.setStyle(TableStyle([
                ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
                ("TOPPADDING",(0,0),(-1,-1),1), ("BOTTOMPADDING",(0,0),(-1,-1),1),
            ]))
            story.append(card(user_inner))
            story.append(Spacer(1, 4*mm))

            # — Pills: riesgo + polen —
            def pill(text, bg, fg, align=1):
                s = ParagraphStyle("p", fontName="Helvetica-Bold", fontSize=10, textColor=fg, alignment=align)
                t = Table([[Paragraph(text, s)]], colWidths=[(doc.width/2)-6])
                t.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,-1),bg), ("ROUNDEDCORNERS",[6]),
                    ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
                    ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
                ]))
                return t

            row = Table([[
                pill(f"Riesgo: {risk_level.upper()}", pill_bg, pill_fg),
                pill(f"Polen: {pollen_report}", GREEN_LIGHT, GREEN_DARK),
            ]], colWidths=[doc.width/2, doc.width/2])
            row.setStyle(TableStyle([
                ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
                ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
            ]))
            story.append(row)
            story.append(Spacer(1, 4*mm))

            # — Alergias —
            story.append(Paragraph("ALERGIAS REGISTRADAS", seccion))
            text = "  ·  ".join([a.capitalize() for a in allergies if a.lower() != "ninguna"]) or "Ninguna registrada"
            story.append(card(Paragraph(text, cuerpo)))
            story.append(Spacer(1, 4*mm))

            # — Pronóstico IA —
            story.append(Paragraph("TU PRONÓSTICO SEMANAL", seccion))
            story.append(card(Paragraph(ai_content.replace("\n","<br/>"), cuerpo), bg=GREEN_PALE))
            story.append(Spacer(1, 6*mm))

            story.append(HRFlowable(width="100%", thickness=1, color=GREEN_LIGHT, spaceAfter=4*mm))
            story.append(Paragraph("tualergiahoy.com · Este informe es orientativo. Consulta siempre con tu alergólogo.", footer_s))

            doc.build(story)
            return filepath
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None

    def _send_welcome_email(self, email, full_name, city, pollen_report, pdf_path, risk_level, allergies):
        try:
            first_name = full_name.split()[0]
            subject = f"¡Bienvenido a tualergiahoy, {first_name}! 🌿"

            risk_map = {
                "alto":  ("#fef2f2", "#dc2626", "🔴"),
                "medio": ("#fffbeb", "#d97706", "🟡"),
                "bajo":  ("#ecfdf5", "#059669", "🟢"),
            }
            risk_bg, risk_color, risk_icon = risk_map.get(risk_level.lower(), ("#ecfdf5", "#059669", "🟢"))

            allergy_pills = "".join([
                f'<span style="display:inline-block;background:#d1fae5;color:#047857;border-radius:20px;'
                f'padding:3px 12px;font-size:13px;font-weight:500;margin:3px 4px 3px 0;">{a.capitalize()}</span>'
                for a in allergies if a.lower() != "ninguna"
            ]) or '<span style="color:#6b9e88;font-size:13px;">Ninguna registrada</span>'

            html_body = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0fdf6;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf6;padding:32px 16px;">
  <tr><td align="center">
  <table width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;">

    <!-- Header -->
    <tr><td style="background:#fff;border-radius:20px 20px 0 0;border:1.5px solid #d1fae5;border-bottom:none;padding:28px 32px 16px;">
      <p style="margin:0;font-family:'Sora',Georgia,serif;font-size:22px;font-weight:700;color:#064e3b;letter-spacing:-0.5px;">tualergiahoy</p>
      <p style="margin:4px 0 0;font-size:13px;color:#6b9e88;">Tu compañero inteligente contra las alergias</p>
    </td></tr>

    <!-- Línea degradado -->
    <tr><td style="background:#fff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:0 32px;">
      <div style="height:2px;background:linear-gradient(90deg,#059669,#d1fae5);border-radius:2px;"></div>
    </td></tr>

    <!-- Saludo -->
    <tr><td style="background:#fff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:28px 32px 0;">
      <p style="margin:0 0 8px;font-size:20px;font-weight:700;color:#064e3b;">¡Hola, {first_name}! 👋</p>
      <p style="margin:0;font-size:14px;color:#6b9e88;line-height:1.6;">
        Ya formas parte de <strong style="color:#059669;">tualergiahoy</strong>.
        Aquí tienes un resumen de tu perfil alérgico y tu pronóstico adjunto.
      </p>
    </td></tr>

    <!-- Ciudad + Polen -->
    <tr><td style="background:#fff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:16px 32px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fffe;border:1.5px solid #d1fae5;border-radius:12px;">
        <tr>
          <td style="padding:14px 16px;">
            <p style="margin:0 0 3px;font-size:10px;font-weight:600;color:#047857;text-transform:uppercase;letter-spacing:0.05em;">Tu ciudad</p>
            <p style="margin:0;font-size:15px;font-weight:600;color:#064e3b;">📍 {city}</p>
          </td>
          <td style="padding:14px 16px;border-left:1px solid #d1fae5;">
            <p style="margin:0 0 3px;font-size:10px;font-weight:600;color:#047857;text-transform:uppercase;letter-spacing:0.05em;">Polen actual</p>
            <p style="margin:0;font-size:14px;font-weight:600;color:#064e3b;">🌱 {pollen_report}</p>
          </td>
        </tr>
      </table>
    </td></tr>

    <!-- Nivel de riesgo -->
    <tr><td style="background:#fff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:12px 32px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:{risk_bg};border-radius:12px;">
        <tr><td style="padding:14px 16px;">
          <p style="margin:0 0 2px;font-size:10px;font-weight:600;color:{risk_color};text-transform:uppercase;letter-spacing:0.05em;">Nivel de riesgo alérgico</p>
          <p style="margin:0;font-size:18px;font-weight:700;color:{risk_color};">{risk_icon} {risk_level.upper()}</p>
        </td></tr>
      </table>
    </td></tr>

    <!-- Alergias -->
    <tr><td style="background:#fff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:12px 32px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fffe;border:1.5px solid #d1fae5;border-radius:12px;">
        <tr><td style="padding:14px 16px;">
          <p style="margin:0 0 8px;font-size:10px;font-weight:600;color:#047857;text-transform:uppercase;letter-spacing:0.05em;">Alergias registradas</p>
          <div>{allergy_pills}</div>
        </td></tr>
      </table>
    </td></tr>

    <!-- PDF adjunto -->
    <tr><td style="background:#fff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:12px 32px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#ecfdf5;border-radius:12px;">
        <tr><td style="padding:16px 18px;">
          <p style="margin:0 0 4px;font-size:14px;font-weight:600;color:#064e3b;">📄 Tu pronóstico está adjunto</p>
          <p style="margin:0;font-size:13px;color:#6b9e88;line-height:1.6;">Hemos generado un informe personalizado con tu previsión semanal. Encuéntralo adjunto a este correo.</p>
        </td></tr>
      </table>
    </td></tr>

    <!-- Mensaje final -->
    <tr><td style="background:#fff;border-left:1.5px solid #d1fae5;border-right:1.5px solid #d1fae5;padding:20px 32px 24px;">
      <p style="margin:0;font-size:13px;color:#6b9e88;line-height:1.7;">
        Recuerda consultar siempre con tu alergólogo ante cualquier síntoma. Estamos aquí para ayudarte a vivir mejor cada día. 💚
      </p>
    </td></tr>

    <!-- Footer -->
    <tr><td style="background:#f0fdf6;border:1.5px solid #d1fae5;border-top:none;border-radius:0 0 20px 20px;padding:16px 32px;">
      <p style="margin:0;font-size:11px;color:#6b9e88;text-align:center;line-height:1.6;">
        © {datetime.now().year} tualergiahoy.com · Este correo es informativo y no sustituye el consejo médico profesional.
      </p>
    </td></tr>

  </table>
  </td></tr>
</table>
</body></html>"""

            msg = EmailMessage(subject=subject, body=html_body, from_email="tualergiahoy@gmail.com", to=[email])
            msg.content_subtype = "html"
            if pdf_path and os.path.exists(pdf_path):
                msg.attach_file(pdf_path)
            msg.send()
            print(f"✅ Email sent to {email}")
            return True
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False

    def _save_to_google_sheets(self, data, full_name, risk_level, allergies, pollen_report, hashed_password=""):
        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-493508-5cb178e0f4a0.json"
            if not os.path.exists(creds_path):
                print("❌ Credentials file not found")
                return
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open("tualergiahoy_registros").sheet1
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                full_name, data.get("nombre",""), data.get("apellidos",""),
                str(data.get("fecha_nacimiento","")), data.get("ciudad",""),
                risk_level, ", ".join(allergies), data.get("email",""),
                pollen_report, hashed_password,
            ])
            print(f"✅ Saved to Sheets: {data.get('email')}")
        except Exception as e:
            print(f"❌ Sheets error: {type(e).__name__} - {e}")

    def _log_registration(self, full_name, data, allergies, risk_level, pollen_report, ai_content):
        print("\n=== NEW REGISTRATION ===")
        print(f"Name     : {full_name}")
        print(f"Email    : {data.get('email')}")
        print(f"City     : {data.get('ciudad')}")
        print(f"Allergies: {allergies}")
        print(f"Risk     : {risk_level}")
        print(f"Pollen   : {pollen_report}")
        print(f"AI       : {ai_content[:120]}...")
        print("=" * 50)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        full_name = f"{data['nombre']} {data['apellidos']}"
        allergies = data.get("alergias", [])
        city = data.get("ciudad", "").strip()
        user_email = data.get("email")
        plain_password = data.get("password", "")

        if not city:
            return Response({"error": "City is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Hash de contraseña antes de guardar
        hashed_pw = hash_password(plain_password)

        num_allergies = len([a for a in allergies if str(a).lower() != "ninguna"])
        risk_level = "alto" if num_allergies >= 3 else "medio" if num_allergies >= 2 else "bajo"

        pollen_report = self._get_pollen_level(city)
        if pollen_report.startswith("ERROR:"):
            return Response({"error": pollen_report.replace("ERROR: ",""), "field": "ciudad"}, status=status.HTTP_400_BAD_REQUEST)

        ai_content = self._generate_gemini_forecast(full_name, city, allergies, risk_level, pollen_report)

        # Se guarda el hash, nunca la contraseña en texto plano
        self._save_to_google_sheets(data, full_name, risk_level, allergies, pollen_report, hashed_pw)

        pdf_path = self._generate_pdf_direct(full_name, city, risk_level, pollen_report, ai_content, allergies)
        email_sent = self._send_welcome_email(user_email, full_name, city, pollen_report, pdf_path, risk_level, allergies)

        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception as e:
                print(f"⚠️  Could not delete PDF: {e}")

        self._log_registration(full_name, data, allergies, risk_level, pollen_report, ai_content)

        return Response({
            "message": "¡Registro exitoso! Te hemos enviado tu pronóstico por email.",
            "nombre_completo": full_name, "email": user_email,
            "ciudad": city, "nivel_riesgo": risk_level,
            "polen_actual": pollen_report, "email_enviado": email_sent,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):

    def post(self, request):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response({"error": "Email y contraseña son obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            creds_path = r"C:\Users\mnldz\tualergiahoy.com\backend\credentials\tualergiahoy-493508-5cb178e0f4a0.json"
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open("tualergiahoy_registros").sheet1
            records = sheet.get_all_records()

            for row in records:
                row_email = str(row.get("CORREO", "")).strip()
                row_hash  = str(row.get("CONTRASEÑA", "")).strip()

                if row_email == email and verify_password(password, row_hash):
                    user_data = {
                        "nombre_completo": row.get("NOMBRE COMPLETO", ""),
                        "nombre":          row.get("NOMBRE", ""),
                        "apellidos":       row.get("APELLIDOS", ""),
                        "ciudad":          row.get("CIUDAD", ""),
                        "nivel_riesgo":    row.get("NIVEL DE ALERGIA", ""),
                        "alergias":        row.get("ALERGIA", "").split(", ") if row.get("ALERGIA") else [],
                        "email":           row.get("CORREO", ""),
                        "polen_actual":    row.get("CANTIDAD DE POLEN", ""),
                        "fecha_nacimiento":row.get("F. NACIMIENTO", ""),
                    }
                    print(f"✅ Login OK: {email}")
                    return Response({"message": "Login successful", "user": user_data}, status=status.HTTP_200_OK)

            print(f"❌ Login failed: {email}")
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(f"❌ Login error: {e}")
            return Response({"error": "Error del servidor durante el login"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)