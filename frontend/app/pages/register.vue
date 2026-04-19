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
          <div class="field">
            <label for="nombre" class="field-label">Nombre</label>
            <div class="field-wrap">
              <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.3"/>
                <path d="M2 14c0-3.314 2.686-5 6-5s6 1.686 6 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
              <input id="nombre" v-model="form.nombre" type="text" required class="field-input" placeholder="Ana" autocomplete="given-name"/>
            </div>
          </div>
          <div class="field">
            <label for="apellido" class="field-label">Apellidos</label>
            <div class="field-wrap">
              <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.3"/>
                <path d="M2 14c0-3.314 2.686-5 6-5s6 1.686 6 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
              <input id="apellido" v-model="form.apellidos" type="text" required class="field-input" placeholder="García" autocomplete="family-name"/>
            </div>
          </div>
        </div>

        <div class="field-row">
          <div class="field">
            <label for="fecha" class="field-label">Fecha de nacimiento</label>
            <div class="field-wrap">
              <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="1" y="3" width="14" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
                <path d="M1 7h14M5 1v4M11 1v4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
              <input id="fecha" v-model="form.fecha_nacimiento" type="date" required class="field-input field-input--date" autocomplete="bday"/>
            </div>
          </div>
          <div class="field">
            <label for="ciudad" class="field-label">Ciudad</label>
            <div class="field-wrap">
              <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 1.5C5.515 1.5 3.5 3.515 3.5 6c0 3.75 4.5 8.5 4.5 8.5S12.5 9.75 12.5 6c0-2.485-2.015-4.5-4.5-4.5Z" stroke="currentColor" stroke-width="1.3"/>
                <circle cx="8" cy="6" r="1.5" stroke="currentColor" stroke-width="1.3"/>
              </svg>
              <input id="ciudad" v-model="form.ciudad" type="text" required class="field-input" placeholder="Madrid"/>
            </div>
          </div>
        </div>

        <!-- Dropdown alergias -->
        <div class="field">
          <label class="field-label">Alergias conocidas</label>
          <div class="dropdown-wrapper" ref="dropdownRef">
            <button type="button" class="field-input dropdown-trigger" :class="{ open: dropdownOpen }" @click="toggleDropdown">
              <span :style="{ color: form.alergias.length ? '#064e3b' : '#b2d4c6' }">
                {{ form.alergias.length
                  ? `${form.alergias.length} alergia${form.alergias.length > 1 ? 's' : ''} seleccionada${form.alergias.length > 1 ? 's' : ''}`
                  : 'Selecciona tus alergias...' }}
              </span>
              <svg class="chevron" :class="{ open: dropdownOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <Teleport to="body">
              <div v-show="dropdownOpen" class="dropdown-menu-teleported" :style="dropdownStyle">
                <label v-for="alergia in alergiaOptions" :key="alergia.value" class="dropdown-option">
                  <input type="checkbox" :value="alergia.value" v-model="form.alergias"/>
                  {{ alergia.label }}
                </label>
              </div>
            </Teleport>
          </div>
          <div v-if="form.alergias.length" class="tags-container">
            <span v-for="a in form.alergias" :key="a" class="alergia-tag">
              {{ a }}
              <button type="button" @click="form.alergias = form.alergias.filter(x => x !== a)">×</button>
            </span>
          </div>
        </div>

        <div class="field">
          <label for="email" class="field-label">Correo electrónico</label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M1 5l7 5 7-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            <input id="email" v-model="form.email" type="email" required class="field-input" placeholder="tu@email.com" autocomplete="email"/>
          </div>
        </div>

        <div class="field">
          <label for="password" class="field-label">Contraseña</label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="3" y="7" width="10" height="8" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 7V5a3 3 0 0 1 6 0v2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <circle cx="8" cy="11" r="1" fill="currentColor"/>
            </svg>
            <input id="password" v-model="form.password" type="password" required class="field-input" placeholder="Mínimo 8 caracteres" autocomplete="new-password"/>
          </div>
        </div>

        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? 'Creando tu cuenta...' : 'Crear cuenta' }}
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
import { useToast } from '../composables/useToast'

const form = reactive({
  nombre: '', apellidos: '', fecha_nacimiento: '',
  ciudad: '', alergias: [], email: '', password: ''
})

const loading = ref(false)
const dropdownOpen = ref(false)
const dropdownRef = ref(null)
const dropdownStyle = ref({})

const { addToast } = useToast()

const alergiaOptions = [
  { value: 'polen',         label: 'Polen' },
  { value: 'gramíneas',     label: 'Gramíneas' },
  { value: 'olivo',         label: 'Olivo' },
  { value: 'ácaros',        label: 'Ácaros del polvo' },
  { value: 'pelo de gato',  label: 'Pelo de gato' },
  { value: 'pelo de perro', label: 'Pelo de perro' },
  { value: 'ambrosía',      label: 'Ambrosía' },
  { value: 'artemisa',      label: 'Artemisa' },
  { value: 'aliso',         label: 'Aliso' },
  { value: 'abedul',        label: 'Abedul' },
  { value: 'ninguna',       label: 'Ninguna de las anteriores' },
]

const toggleDropdown = (e) => {
  e.stopPropagation()
  if (!dropdownOpen.value && dropdownRef.value) {
    const rect = dropdownRef.value.getBoundingClientRect()
    dropdownStyle.value = {
      position: 'fixed',
      top: `${rect.bottom}px`,
      left: `${rect.left}px`,
      width: `${rect.width}px`,
      zIndex: 99999,
      background: '#ffffff',
      border: '1.5px solid #10b981',
      borderTop: 'none',
      borderBottomLeftRadius: '10px',
      borderBottomRightRadius: '10px',
      maxHeight: '220px',
      overflowY: 'auto',
      boxShadow: '0 8px 24px rgba(16,185,129,0.12)',
    }
  }
  dropdownOpen.value = !dropdownOpen.value
}

const handleOutsideClick = (e) => {
  const menu = document.querySelector('.dropdown-menu-teleported')
  if (dropdownRef.value && !dropdownRef.value.contains(e.target) && (!menu || !menu.contains(e.target))) {
    dropdownOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))

const handleSubmit = async () => {
  if (loading.value) return

  // Validación de edad antes de llamar a la API
  const hoy = new Date()
  const nacimiento = new Date(form.fecha_nacimiento)
  const edad = hoy.getFullYear() - nacimiento.getFullYear()
  const cumpleEsteAño = hoy >= new Date(hoy.getFullYear(), nacimiento.getMonth(), nacimiento.getDate())
  const edadReal = cumpleEsteAño ? edad : edad - 1

  if (edadReal < 1) {
    addToast('La fecha de nacimiento no es válida.')
    return
  }
  if (edadReal > 120) {
    addToast('La fecha de nacimiento no parece correcta. ¿Eres inmortal? 😄')
    return
  }

  loading.value = true
  try {
    const response = await $fetch('http://127.0.0.1:8000/api/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        nombre: form.nombre,
        apellidos: form.apellidos,
        fecha_nacimiento: form.fecha_nacimiento,
        ciudad: form.ciudad,
        alergias: form.alergias.length ? form.alergias : ['ninguna'],
        email: form.email,
        password: form.password
      }
    })
    localStorage.setItem('registroData', JSON.stringify(response))
    await navigateTo('/welcome')
  } catch (error) {
    const field = error.data?.field
    const mensaje = error.data?.error || error.message || 'Error al registrar'

    if (field === 'ciudad') {
      addToast(`Ciudad no encontrada: comprueba que "${form.ciudad}" está bien escrita.`)
    } else {
      addToast(mensaje)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
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
.shape { position: absolute; border-radius: 50%; animation: shapeFloat 8s ease-in-out infinite; }
.shape-1 { width: 480px; height: 480px; background: radial-gradient(circle, #bbf7d0 0%, transparent 70%); top: -180px; right: -140px; animation-delay: 0s; }
.shape-2 { width: 320px; height: 320px; background: radial-gradient(circle, #d1fae5 0%, transparent 70%); bottom: -100px; left: -100px; animation-delay: 1.5s; }
.shape-3 { width: 160px; height: 160px; background: radial-gradient(circle, #a7f3d0 0%, transparent 70%); top: 40%; left: 6%; animation-delay: 3s; }
.shape-4 { width: 100px; height: 100px; background: radial-gradient(circle, #6ee7b7 0%, transparent 70%); top: 18%; right: 14%; animation-delay: 1s; opacity: 0.5; }
.shape-5 { width: 200px; height: 200px; background: radial-gradient(circle, #ecfdf5 0%, transparent 70%); bottom: 22%; right: 6%; animation-delay: 2s; }

.auth-card {
  position: relative;
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border: 1.5px solid #d1fae5;
  border-radius: 20px;
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 6px rgba(16,185,129,0.06), 0 20px 48px rgba(16,185,129,0.1);
  animation: cardIn 0.6s cubic-bezier(0.22,1,0.36,1) both;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  animation: fadeUp 0.5s 0.1s both;
}
.brand-name {
  font-family: 'Sora', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #065f46;
  letter-spacing: -0.02em;
}

.card-header { margin-bottom: 2rem; animation: fadeUp 0.5s 0.15s both; }
.card-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: #064e3b;
  letter-spacing: -0.03em;
  line-height: 1.2;
}
.card-subtitle { font-size: 0.875rem; color: #6b9e88; margin-top: 0.35rem; }

.auth-form { display: flex; flex-direction: column; gap: 1.1rem; }

.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }

.field { display: flex; flex-direction: column; gap: 0.45rem; animation: fadeUp 0.5s 0.2s both; }

.field-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: #047857;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  padding: 0.75rem 0.9rem 0.75rem 2.6rem;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  color: #064e3b;
  outline: none;
  transition: border-color 0.22s, box-shadow 0.22s, background 0.22s;
}
.field-input::placeholder { color: #b2d4c6; }
.field-input:hover { border-color: #6ee7b7; background: #f0fdf9; }
.field-input:focus { border-color: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.12); background: #ffffff; }
.field-input--date { padding-left: 2.6rem; }

/* Dropdown */
.dropdown-wrapper { position: relative; }
.dropdown-trigger {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding-left: 0.9rem;
  text-align: left;
}
.dropdown-trigger.open { border-color: #10b981; border-bottom-left-radius: 0; border-bottom-right-radius: 0; box-shadow: 0 0 0 3px rgba(16,185,129,0.12); }

.chevron { color: #a7c4b5; transition: transform 0.2s, color 0.2s; flex-shrink: 0; }
.dropdown-trigger.open .chevron,
.chevron.open { transform: rotate(180deg); color: #10b981; }

:global(.dropdown-menu-teleported) { font-family: 'DM Sans', sans-serif; }
:global(.dropdown-menu-teleported .dropdown-option) {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 14px; cursor: pointer;
  font-size: 0.875rem; color: #064e3b; transition: background 0.15s;
}
:global(.dropdown-menu-teleported .dropdown-option:hover) { background: #f0fdf9; }
:global(.dropdown-menu-teleported .dropdown-option input[type="checkbox"]) {
  accent-color: #10b981; width: 15px; height: 15px; cursor: pointer; flex-shrink: 0;
}

.tags-container { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.alergia-tag {
  background: #d1fae5; color: #047857; border-radius: 20px;
  padding: 3px 10px; font-size: 0.75rem; font-weight: 500;
  display: flex; align-items: center; gap: 4px;
}
.alergia-tag button {
  background: none; border: none; color: #059669;
  cursor: pointer; font-size: 14px; line-height: 1; padding: 0;
}

.btn-primary {
  margin-top: 0.4rem;
  width: 100%;
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.8rem 1.25rem;
  background: linear-gradient(135deg, #059669 0%, #10b981 60%, #34d399 100%);
  border: none; border-radius: 10px;
  font-family: 'DM Sans', sans-serif; font-size: 0.9rem; font-weight: 600;
  color: #ffffff; cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, filter 0.18s;
  box-shadow: 0 4px 20px rgba(16,185,129,0.3);
  animation: fadeUp 0.5s 0.3s both;
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 32px rgba(16,185,129,0.4); filter: brightness(1.05); }
.btn-primary:active { transform: translateY(0) scale(0.985); }
.btn-primary:disabled { opacity: 0.75; cursor: not-allowed; }

.terms { font-size: 0.78rem; color: #6b9e88; text-align: center; margin-top: 0.5rem; line-height: 1.6; }
.terms-link { color: #059669; text-decoration: none; font-weight: 500; }
.terms-link:hover { text-decoration: underline; }

.auth-footer { margin-top: 1.75rem; text-align: center; font-size: 0.85rem; color: #6b9e88; animation: fadeUp 0.5s 0.35s both; }
.auth-link { color: #059669; text-decoration: none; font-weight: 500; margin-left: 0.3rem; transition: color 0.2s; }
.auth-link:hover { color: #047857; }

@keyframes shapeFloat {
  0%   { transform: translateY(0) scale(1); }
  50%  { transform: translateY(-20px) scale(1.04); }
  100% { transform: translateY(0) scale(1); }
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(28px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>