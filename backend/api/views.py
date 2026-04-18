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
    """Main API view responsible for handling user registration flow in tualergiahoy.com"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini_client = self._get_gemini_client()

    def _get_gemini_client(self):
        """Initialize Gemini AI client"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found in .env file")
            return None
        return genai.Client(api_key=api_key)

    def post(self, request):
        """Handle user registration: process data, generate forecast, create PDF and send email"""
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        full_name = f"{data['nombre']} {data['apellidos']}"
        allergies = data.get("alergias", [])
        city = data.get("ciudad", "Madrid")
        user_email = data.get("email")
        password = data.get("password")

        num_allergies = len([a for a in allergies if str(a).lower() != "ninguna"])
        risk_level = "alto" if num_allergies >= 3 else "medio" if num_allergies >= 2 else "bajo"

        pollen_report = self._get_pollen_level(city)

        if pollen_report.startswith("ERROR:"):
            return Response(
                {"error": pollen_report.replace("ERROR: ", ""), "field": "ciudad"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_content = self._generate_gemini_forecast(full_name, city, allergies, risk_level, pollen_report)

        self._save_to_google_sheets(data, full_name, risk_level, allergies, password)

        pdf_path = self._generate_pdf_direct(full_name, city, risk_level, pollen_report, ai_content)

        email_sent = self._send_welcome_email(user_email, full_name, city, pollen_report, pdf_path)

        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                print(f"🗑️ PDF file deleted: {pdf_path}")
            except Exception as e:
                print(f"⚠️ Could not delete PDF: {e}")

        self._log_registration(full_name, data, allergies, risk_level, pollen_report, ai_content)

        return Response({
            "message": "Registration successful! Your personalized forecast has been sent by email.",
            "nombre_completo": full_name,
            "email": user_email,
            "ciudad": city,
            "nivel_riesgo": risk_level,
            "polen_actual": pollen_report,
            "email_enviado": email_sent,
        }, status=status.HTTP_201_CREATED)

    # ... (mantengo tus otros métodos _get_pollen_level, _generate_gemini_forecast, _generate_pdf_direct, _send_welcome_email, _log_registration sin cambios)

    def _save_to_google_sheets(self, data: dict, full_name: str, risk_level: str, allergies: list, password: str = None):
        """Save registration data to Google Sheets, including the password"""
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
                data.get("nivel_sensibilidad", "medio"),
                password or ""                    # ← Guardamos la contraseña aquí
            ])
            print(f"✅ Registration saved to Google Sheets with password for {data.get('email')}")
        except Exception as e:
            print(f"❌ Error saving to Sheets: {e}")

    def _log_registration(self, full_name, data, allergies, risk_level, pollen_report, ai_content):
        """Log registration details to console"""
        print("\n=== NEW REGISTRATION IN tualergiahoy.com ===")
        print(f"Full name       : {full_name}")
        print(f"Email           : {data.get('email')}")
        print(f"City            : {data.get('ciudad')}")
        print(f"Allergies       : {allergies}")
        print(f"Risk level      : {risk_level}")
        print(f"Pollen level    : {pollen_report}")
        print(f"AI Content      : {ai_content[:150]}...")
        print("=" * 70)


# ==================== LOGIN VIEW ====================

class LoginView(APIView):
    """Handles user login by checking email and password against Google Sheets"""

    def post(self, request):
        """Authenticate user using email and password stored in Google Sheets"""
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
                if row.get("CORREO") == email and row.get("CONTRASEÑA") == password:
                    user_data = {
                        "nombre_completo": row.get("NOMBRE COMPLETO", ""),
                        "nombre": row.get("NOMBRE", ""),
                        "apellidos": row.get("APELLIDOS", ""),
                        "ciudad": row.get("CIUDAD", ""),
                        "nivel_riesgo": row.get("NIVEL DE ALERGIA", ""),
                        "alergias": row.get("ALERGIA", "").split(", ") if row.get("ALERGIA", "") else [],
                        "email": row.get("CORREO", ""),
                    }

                    print(f"✅ Login successful for {email}")
                    return Response({
                        "message": "Login successful",
                        "user": user_data
                    }, status=status.HTTP_200_OK)

            print(f"❌ No matching user found for email: {email}")
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(f"❌ Login error: {e}")
            return Response({"error": "Server error during login"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)