<!-- pages/register.vue -->
<template>
  <div class="auth-root">
    <div class="bg-shapes" aria-hidden="true">
      <span v-for="i in 5" :key="i" class="shape" :class="`shape-${i}`" />
    </div>

    <div class="auth-card">
      <div class="header-with-logo">
        <div class="card-header">
          <h1 class="card-title">Crea tu cuenta</h1>
          <p class="card-subtitle">Gestiona tus alergias de forma inteligente</p>
        </div>
        <div class="logo-container">
          <img src="~/assets/logo.jpg" alt="tualergiahoy" class="brand-logo" />
        </div>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="field-row">
          <div class="field" style="--delay: 0.18s">
            <label for="nombre" class="field-label">Nombre</label>
            <div class="field-wrap">
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

        <!-- Dropdown con checkboxes de alergias -->
        <div class="field" style="--delay: 0.34s">
          <label class="field-label">Alergias conocidas</label>
          <div class="dropdown-wrapper" ref="dropdownRef">
            <button
              type="button"
              class="dropdown-trigger"
              :class="{ open: dropdownOpen }"
              @click="toggleDropdown"
            >
              <span :style="{ color: form.alergias.length ? '#064e3b' : '#6b9e88' }">
                {{ form.alergias.length
                  ? `${form.alergias.length} alergia${form.alergias.length > 1 ? 's' : ''} seleccionada${form.alergias.length > 1 ? 's' : ''}`
                  : 'Selecciona tus alergias...' }}
              </span>
              <svg
                class="chevron"
                :class="{ open: dropdownOpen }"
                width="12" height="12" viewBox="0 0 12 12" fill="none"
              >
                <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>

            <!-- Teleport saca el menú fuera de cualquier overflow:hidden -->
            <Teleport to="body">
              <div
                v-show="dropdownOpen"
                class="dropdown-menu-teleported"
                :style="dropdownStyle"
              >
                <label
                  v-for="alergia in alergiaOptions"
                  :key="alergia.value"
                  class="dropdown-option"
                >
                  <input
                    type="checkbox"
                    :value="alergia.value"
                    v-model="form.alergias"
                  />
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
          <small class="help-text">Haz clic para seleccionar varias alergias</small>
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
  alergias: [],
  email: '',
  password: ''
})

const loading = ref(false)
const dropdownOpen = ref(false)
const dropdownRef = ref(null)
const dropdownStyle = ref({})

const alergiaOptions = [
  { value: 'polen', label: 'Polen' },
  { value: 'gramíneas', label: 'Gramíneas' },
  { value: 'olivo', label: 'Olivo' },
  { value: 'ácaros', label: 'Ácaros del polvo' },
  { value: 'pelo de gato', label: 'Pelo de gato' },
  { value: 'pelo de perro', label: 'Pelo de perro' },
  { value: 'ambrosía', label: 'Ambrosía' },
  { value: 'artemisa', label: 'Artemisa' },
  { value: 'aliso', label: 'Aliso' },
  { value: 'abedul', label: 'Abedul' },
  { value: 'ninguna', label: 'Ninguna de las anteriores' },
]

const toggleDropdown = (e) => {
  e.stopPropagation() // Evita que el click llegue al listener del documento
  if (!dropdownOpen.value && dropdownRef.value) {
    const rect = dropdownRef.value.getBoundingClientRect()
    dropdownStyle.value = {
      position: 'fixed',
      top: `${rect.bottom}px`,
      left: `${rect.left}px`,
      width: `${rect.width}px`,
      zIndex: 99999,
      background: '#f9fffe',
      border: '1.5px solid #10b981',
      borderTop: 'none',
      borderBottomLeftRadius: '10px',
      borderBottomRightRadius: '10px',
      maxHeight: '220px',
      overflowY: 'auto',
    }
  }
  dropdownOpen.value = !dropdownOpen.value
}

const handleOutsideClick = (e) => {
  const menu = document.querySelector('.dropdown-menu-teleported')
  if (
    dropdownRef.value && !dropdownRef.value.contains(e.target) &&
    (!menu || !menu.contains(e.target))
  ) {
    dropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})

const handleSubmit = async () => {
  if (loading.value) return
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
    console.error(error)
    const mensaje = error.data?.error || error.message || 'Error al registrar'
    alert('Error al registrarte:\n' + mensaje)
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
.shape {
  position: absolute;
  border-radius: 50%;
  animation: shapeFloat 8s ease-in-out infinite;
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border: 1.5px solid #d1fae5;
  border-radius: 20px;
  padding: 2.25rem 2rem;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.06), 0 20px 48px rgba(16, 185, 129, 0.1);
  animation: cardIn 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.header-with-logo {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.card-header { flex: 1; }

.card-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: #064e3b;
  letter-spacing: -0.03em;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #6b9e88;
  margin-top: 0.35rem;
}

.logo-container { margin-left: 20px; }

.brand-logo {
  width: 110px;
  height: 110px;
  border-radius: 18px;
  object-fit: cover;
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25);
}

.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }

.field { display: flex; flex-direction: column; gap: 0.42rem; animation: fadeUp 0.5s var(--delay, 0.2s) both; }

.field-label { font-size: 0.78rem; font-weight: 500; color: #047857; letter-spacing: 0.01em; }

.field-wrap { position: relative; }

.field-input {
  width: 100%;
  background: #f9fffe;
  border: 1.5px solid #d1fae5;
  border-radius: 10px;
  padding: 0.72rem 0.9rem 0.72rem 2.5rem;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.875rem;
  color: #064e3b;
}

.field-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b9e88;
  pointer-events: none;
}

/* Dropdown */
.dropdown-wrapper { position: relative; }

.dropdown-trigger {
  width: 100%;
  background: #f9fffe;
  border: 1.5px solid #d1fae5;
  border-radius: 10px;
  padding: 0.72rem 0.9rem;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.875rem;
  color: #064e3b;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: border-color 0.2s;
  text-align: left;
}
.dropdown-trigger:hover { border-color: #6ee7b7; }
.dropdown-trigger.open {
  border-color: #10b981;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.chevron {
  color: #10b981;
  transition: transform 0.2s;
  flex-shrink: 0;
}
.chevron.open { transform: rotate(180deg); }

/* Los estilos del menú teleportado van en :global porque está fuera del scoped */
:global(.dropdown-menu-teleported) {
  font-family: 'DM Sans', sans-serif;
}
:global(.dropdown-menu-teleported .dropdown-option) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  cursor: pointer;
  font-size: 0.875rem;
  color: #064e3b;
  transition: background 0.15s;
}
:global(.dropdown-menu-teleported .dropdown-option:hover) {
  background: #ecfdf5;
}
:global(.dropdown-menu-teleported .dropdown-option input[type="checkbox"]) {
  accent-color: #10b981;
  width: 15px;
  height: 15px;
  cursor: pointer;
  flex-shrink: 0;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.alergia-tag {
  background: #d1fae5;
  color: #047857;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 0.75rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}
.alergia-tag button {
  background: none;
  border: none;
  color: #059669;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;
}

.help-text {
  font-size: 0.78rem;
  color: #6b9e88;
  margin-top: 6px;
}

.btn-primary {
  margin-top: 0.8rem;
  width: 100%;
  padding: 0.85rem;
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.terms {
  font-size: 0.8rem;
  color: #6b9e88;
  text-align: center;
  margin-top: 0.75rem;
  line-height: 1.6;
}
.terms-link {
  color: #059669;
  text-decoration: none;
  font-weight: 500;
}
.terms-link:hover { text-decoration: underline; }

.auth-footer {
  font-size: 0.875rem;
  color: #6b9e88;
  text-align: center;
  margin-top: 1rem;
}
.auth-link {
  color: #059669;
  font-weight: 600;
  text-decoration: none;
}
.auth-link:hover { text-decoration: underline; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>