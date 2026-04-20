# tualergiahoy.com

🌐 Probar la aplicación: https://tualergiahoy.duckdns.org/

## Descripción

tualergiahoy es una aplicación web diseñada para ayudar a las personas con alergias (polen, ácaros, gramíneas, olivo, pelo de mascotas, etc.) a tomar el control de su salud.

Proporciona:
- Pronóstico semanal personalizado según tu ubicación y perfil de alergias.
- Información en tiempo real de niveles de polen en tu ciudad.
- Consejos prácticos y recomendaciones para minimizar síntomas y disfrutar del aire libre sin miedo.

La aplicación sigue una arquitectura full-stack:
- **Frontend**: Interfaz moderna y responsive construida con Nuxt.js.
- **Backend**: API REST desarrollada con Django + Django REST Framework que gestiona datos de usuarios, alergias y pronósticos.
- **Base de datos**: Google Sheets.

## Tecnologías utilizadas

- **Frontend**: Nuxt.js (TypeScript)
- **Backend**: Django + Django REST Framework + uv (Python)
- **Gestor de dependencias**: npm (frontend) y uv con pyproject.toml + uv.lock (backend)
- **Base de datos**: Google Sheets
- **Otros**: Serializers, vistas y rutas REST en la app api

## Cómo ejecutarla localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/Manu9701D/tualergiahoy.com.git
cd tualergiahoy.com
```

### 2. Backend (Django)

```bash
cd backend
```

Se necesitan credenciales de la API de Google, un token de Gemini Flash Lite 2.5 y las credenciales del correo personalizado de la aplicación, referenciados en `settings.py`.

```bash
uv sync
python manage.py runserver
```

El backend estará disponible en `http://127.0.0.1:8000`. La API se encuentra en `/api/` (endpoints definidos en `backend/api/urls.py` y `views.py`).

### 3. Frontend (Nuxt)

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:3000`.

### 4. Modo producción (local)

- **Frontend**: `npm run build` → genera la carpeta `.output`
- **Backend**: `python manage.py collectstatic` y servir con Gunicorn + Nginx.

## Cómo se ha desplegado

El despliegue es manual, sin Docker ni CI/CD.

- **Dominio y DNS**: DuckDNS apunta `tualergiahoy.duckdns.org` dinámicamente a la IP del servidor.
- **Frontend**: Build de Nuxt servido por PM2, con Nginx como proxy en los puertos 80/443.
- **Backend**: Gunicorn gestionado por systemd, con Nginx como reverse proxy.
- **Base de datos**: Google Sheets se mantiene tanto en local como en producción.