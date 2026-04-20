# tualergiahoy.com
🌐 Probar la aplicación: https://tualergiahoy.duckdns.org/
Descripción
tualergiahoy una aplicación web completa diseñada para ayudar a las personas con alergias (polen, ácaros, gramíneas, olivo, pelo de mascotas, etc.) a tomar el control de su salud.
Proporciona:

Pronóstico semanal personalizado según tu ubicación y perfil de alergias.
Información en tiempo real de niveles de polen en tu ciudad.
Consejos prácticos y recomendaciones para minimizar síntomas y disfrutar del aire libre sin miedo.

La aplicación sigue una arquitectura full-stack:

Frontend: Interfaz moderna y responsive construida con Nuxt.js.
Backend: API REST desarrollada con Django + Django REST Framework que gestiona datos de usuarios, alergias y pronósticos.
Base de datos: Google Sheets.

Tecnologías utilizadas

Frontend: Nuxt.js (TypeScript)
Backend: Django + Django REST Framework + uv (Python)
Gestor de dependencias:
Frontend: npm
Backend: uv (pyproject.toml + uv.lock)

Base de datos: Google sheets
Otros: Serializers, vistas y rutas REST en la app api

Cómo ejecutarla localmente
1. Clonar el repositorio
Bashgit clone https://github.com/Manu9701D/tualergiahoy.com.git
cd tualergiahoy.com
2. Backend (Django)
Bashcd backend
3. Se necesitan credenciales de la api de google, un token de geminiflash-lite2.5, y las credenciales del correo personalizado de la aplicación que he dejado en el settings.py

# Instalar dependencias con uv (recomendado) porque es el que se ha usado para desarrollar el backend
uv sync          # o: pip install -r requirements.txt (si generas el archivo)

# Ejecutar el servidor de desarrollo
python manage.py runserver
El backend estará disponible en http://127.0.0.1:8000.
La API se encuentra en /api/ (endpoints definidos en backend/api/urls.py y views.py).
3. Frontend (Nuxt)
En otra terminal:
Bashcd frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
El frontend estará disponible en http://localhost:3000.
Durante el desarrollo, el frontend se conecta al backend (puedes cambiar la URL de la API en nuxt.config.ts o variables de entorno si es necesario).
4. Modo producción (local)

Frontend: npm run build → genera la carpeta .output
Backend: python manage.py collectstatic y servir con Gunicorn + Nginx (o similar).

Cómo se ha desplegado
Aunque inicialmente el objetivo era solo desarrollar la aplicación, se ha desplegado una versión en vivo para demostración:

Dominio y DNS: Se utiliza DuckDNS (tualergiahoy.duckdns.org) para apuntar dinámicamente a la IP del servidor.
Frontend: Se ha hecho build de Nuxt (npm run build) y se sirve estáticamente mediante un servidor web (Nginx) en el puerto 80/443.
Backend: El servidor Django está corriendo en el mismo servidor (en un proceso separado). Se ha usado Gunicorn + Nginx como reverse proxy para producción. La base de datos en google sheets se mantiene.
Sin Docker ni CI/CD: El despliegue actual es manual (no hay Dockerfile ni workflows de GitHub Actions en el repositorio).
