<!-- pages/register.vue -->
<template>
  <div class="auth-root">
    <div class="bg-shapes" aria-hidden="true">
      <span v-for="i in 5" :key="i" class="shape" :class="`shape-${i}`" />
    </div>

    <div class="auth-card">
      <div class="brand">
        <span class="brand-icon">
          <svg width="30" height="30" viewBox="0 0 28 28" fill="none">
            <path d="M14 3C8.477 3 4 7.477 4 13s4.477 10 10 10 10-4.477 10-10S19.523 3 14 3Z" fill="#10b981" opacity=".2"/>
            <circle cx="14" cy="13" r="9" stroke="#059669" stroke-width="1.5"/>
            <path d="M9 13h3l2-4 2 8 2-4h1" stroke="#059669" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
        <span class="brand-name">tualergiahoy</span>
      </div>

      <div class="card-header">
        <h1 class="card-title">Crea tu cuenta</h1>
        <p class="card-subtitle">Gestiona tus alergias de forma inteligente</p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="field-row">
          <div class="field" style="--delay: 0.18s">
            <label for="nombre" class="field-label">Nombre</label>
            <div class="field-wrap">
              <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="5.5" r="2.5" stroke="currentColor" stroke-width="1.3"/>
                <path d="M2 13c0-2.761 2.686-5 6-5s6 2.239 6 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
              <input 
                id="nombre" 
                v-model="form.nombre" 
                type="text" 
                required 
                class="field-input" 
                placeholder="Ana" 
                autocomplete="given-name"
              />
            </div>
          </div>

          <div class="field" style="--delay: 0.22s">
            <label for="apellido" class="field-label">Apellido</label>
            <div class="field-wrap">
              <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="5.5" r="2.5" stroke="currentColor" stroke-width="1.3"/>
                <path d="M2 13c0-2.761 2.686-5 6-5s6 2.239 6 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
              <input 
                id="apellido" 
                v-model="form.apellidos" 
                type="text" 
                required 
                class="field-input" 
                placeholder="García" 
                autocomplete="family-name"
              />
            </div>
          </div>
        </div>

        <div class="field" style="--delay: 0.26s">
          <label for="fecha" class="field-label">Fecha de nacimiento</label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="1.5" y="3" width="13" height="11" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 1v3M11 1v3M1.5 7h13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            <input 
              id="fecha" 
              v-model="form.fecha_nacimiento" 
              type="date" 
              required 
              class="field-input field-input--date" 
              autocomplete="bday"
            />
          </div>
        </div>

        <div class="field" style="--delay: 0.3s">
          <label for="ciudad" class="field-label">Ciudad</label>
          <div class="field-wrap">
            <input 
              id="ciudad" 
              v-model="form.ciudad" 
              type="text" 
              required 
              class="field-input" 
              placeholder="Madrid"
            />
          </div>
        </div>

        <div class="field" style="--delay: 0.34s">
          <label for="alergias" class="field-label">Alergias conocidas</label>
          <div class="field-wrap">
            <input 
              id="alergias" 
              v-model="form.alergias" 
              type="text" 
              class="field-input" 
              placeholder="polen, gramíneas, ácaros, olivo..."
            />
          </div>
          <small class="help-text">Sepáralas con comas o escribe "ninguna"</small>
        </div>

        <div class="field" style="--delay: 0.38s">
          <label for="email" class="field-label">Correo electrónico</label>
          <div class="field-wrap">
            <input 
              id="email" 
              v-model="form.email" 
              type="email" 
              required 
              class="field-input" 
            />
          </div>
        </div>

        <div class="field" style="--delay: 0.42s">
          <label for="password" class="field-label">Contraseña</label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="3" y="7" width="10" height="8" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 7V5a3 3 0 0 1 6 0v2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <circle cx="8" cy="11" r="1" fill="currentColor"/>
            </svg>
            <input 
              id="password" 
              v-model="form.password" 
              type="password" 
              required 
              class="field-input" 
              placeholder="Mínimo 8 caracteres" 
              autocomplete="new-password"
            />
          </div>
        </div>

        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? 'Enviando al servidor...' : 'Crear cuenta' }}
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
        </button>

        <p class="terms">
          Al registrarte aceptas los
          <a href="#" class="terms-link">términos de uso</a> y la
          <a href="#" class="terms-link">política de privacidad</a>.
        </p>
      </form>

      <p class="auth-footer">
        ¿Ya tienes cuenta?
        <NuxtLink to="/login" class="auth-link">Iniciar sesión</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup>
const form = reactive({
  nombre: '',
  apellidos: '',
  fecha_nacimiento: '',
  ciudad: '',
  alergias: '',
  email: '',
  password: ''
})

const loading = ref(false)

/**
 * Handles the form submission
 * - Converts allergies from string to array (required by Django backend)
 * - Sends data to Django REST API
 * - Saves response and redirects to welcome page on success
 */
const handleSubmit = async () => {
  if (loading.value) return
  loading.value = true

  // Convert allergies input into array as expected by the backend
  const alergiasArray = form.alergias
    ? form.alergias.split(',').map(a => a.trim()).filter(a => a.length > 0)
    : ['ninguna']

  try {
    const response = await $fetch('http://127.0.0.1:8000/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        nombre: form.nombre,
        apellidos: form.apellidos,
        fecha_nacimiento: form.fecha_nacimiento,
        ciudad: form.ciudad,
        alergias: alergiasArray,
        email: form.email,
        password: form.password
      }
    })

    // Save registration data so it can be used in welcome.vue
    localStorage.setItem('registroData', JSON.stringify(response))

    // Redirect to welcome page after successful registration
    await navigateTo('/welcome')

  } catch (error) {
    console.error('Registration error:', error)
    const errorMsg = error.data?.error || error.message || 'Error connecting to server'
    alert('Error al registrarte:\n' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Your original beautiful styles remain 100% unchanged */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Sora:wght@400;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.auth-root {
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
  background: #f0fdf6;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  position: relative;
  overflow: hidden;
}

.bg-shapes { position: absolute; inset: 0; pointer-events: none; }
.shape {
  position: absolute;
  border-radius: 50%;
  animation: shapeFloat 8s ease-in-out infinite;
}
.shape-1 { width: 500px; height: 500px; background: radial-gradient(circle, #bbf7d0 0%, transparent 70%); top: -200px; left: -140px; animation-delay: 0s; }
.shape-2 { width: 300px; height: 300px; background: radial-gradient(circle, #d1fae5 0%, transparent 70%); bottom: -90px; right: -80px; animation-delay: 1.5s; }
.shape-3 { width: 140px; height: 140px; background: radial-gradient(circle, #a7f3d0 0%, transparent 70%); top: 35%; right: 8%; animation-delay: 3s; }
.shape-4 { width: 90px;  height: 90px;  background: radial-gradient(circle, #6ee7b7 0%, transparent 70%); top: 20%; left: 14%; animation-delay: 1s; opacity: 0.5; }
.shape-5 { width: 180px; height: 180px; background: radial-gradient(circle, #ecfdf5 0%, transparent 70%); bottom: 20%; left: 8%; animation-delay: 2s; }

@keyframes shapeFloat {
  0%   { transform: translateY(0) scale(1); }
  50%  { transform: translateY(-20px) scale(1.04); }
  100% { transform: translateY(0) scale(1); }
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 460px;
  background: #ffffff;
  border: 1.5px solid #d1fae5;
  border-radius: 20px;
  padding: 2.25rem 2rem;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.06), 0 20px 48px rgba(16, 185, 129, 0.1);
  animation: cardIn 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(32px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.75rem;
  animation: fadeUp 0.5s 0.1s both;
}
.brand-name {
  font-family: 'Sora', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #065f46;
  letter-spacing: -0.02em;
}

.card-header { margin-bottom: 1.75rem; animation: fadeUp 0.5s 0.14s both; }
.card-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #064e3b;
  letter-spacing: -0.03em;
  line-height: 1.2;
}
.card-subtitle { font-size: 0.875rem; color: #6b9e88; margin-top: 0.35rem; }

.auth-form { display: flex; flex-direction: column; gap: 1.1rem; }

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.42rem;
  animation: fadeUp 0.5s var(--delay, 0.2s) both;
}

.field-label {
  font-size: 0.78rem;
  font-weight: 500;
  color: #047857;
  letter-spacing: 0.01em;
}

.field-wrap { position: relative; }
.field-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #a7c4b5;
  pointer-events: none;
  transition: color 0.2s;
}
.field-wrap:focus-within .field-icon { color: #10b981; }

.field-input {
  width: 100%;
  background: #f9fffe;
  border: 1.5px solid #d1fae5;
  border-radius: 10px;
  padding: 0.72rem 0.9rem 0.72rem 2.5rem;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.875rem;
  color: #064e3b;
  outline: none;
  transition: border-color 0.22s, box-shadow 0.22s, background 0.22s;
}
.field-input::placeholder { color: #b2d4c6; }
.field-input:hover { border-color: #6ee7b7; background: #f0fdf9; }
.field-input:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.12);
  background: #ffffff;
}
.field-input--date { color-scheme: light; }

.btn-primary {
  margin-top: 0.3rem;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.78rem 1.25rem;
  background: linear-gradient(135deg, #059669 0%, #10b981 60%, #34d399 100%);
  border: none;
  border-radius: 10px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, filter 0.18s;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.28);
  animation: fadeUp 0.5s 0.38s both;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 32px rgba(16, 185, 129, 0.38);
  filter: brightness(1.05);
}
.btn-primary:active { transform: translateY(0) scale(0.985); }
.btn-primary:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.terms {
  text-align: center;
  font-size: 0.76rem;
  color: #a7c4b5;
  line-height: 1.6;
  animation: fadeUp 0.5s 0.42s both;
}
.terms-link { color: #10b981; text-decoration: none; transition: color 0.2s; }
.terms-link:hover { color: #059669; }

.auth-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.85rem;
  color: #6b9e88;
  animation: fadeUp 0.5s 0.46s both;
}
.auth-link { color: #059669; text-decoration: none; font-weight: 500; margin-left: 0.3rem; transition: color 0.2s; }
.auth-link:hover { color: #047857; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 400px) {
  .field-row { grid-template-columns: 1fr; }
  .auth-card { padding: 1.75rem 1.25rem; }
}
</style>