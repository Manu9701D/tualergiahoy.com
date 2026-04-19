<!-- pages/dashboard.vue -->
<template>
  <div class="auth-root">
    <div class="bg-shapes" aria-hidden="true">
      <span v-for="i in 6" :key="i" class="shape" :class="`shape-${i}`" />
    </div>

    <div class="dashboard-container">
      <!-- Brand -->
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

      <!-- Welcome -->
      <div class="welcome-section">
        <h1 class="welcome-title">
          ¡Bienvenido de nuevo, <span class="highlight">{{ user.nombre }}</span>!
        </h1>
        <p class="welcome-subtitle">
          Aquí tienes tu resumen personalizado de alergias
        </p>
      </div>

      <!-- Information grid -->
      <div class="info-grid">
        <!-- Profile card -->
        <div class="info-card">
          <h3 class="card-title">Tus datos</h3>
          <div class="info-item">
            <strong>Nombre completo:</strong> {{ user.nombre }} {{ user.apellidos }}
          </div>
          <div class="info-item">
            <strong>Ciudad:</strong> {{ user.ciudad }}
          </div>
          <div class="info-item">
            <strong>Fecha de nacimiento:</strong> {{ user.fecha_nacimiento }}
          </div>
          <div class="info-item">
            <strong>Nivel de riesgo: </strong> 
            <span :class="`risk-badge risk-${user.nivel_riesgo}`">
              {{ capitalize(user.nivel_riesgo) }}
            </span>
          </div>
        </div>

        <!-- Allergies card -->
        <div class="info-card">
          <h3 class="card-title">Tus alergias</h3>
          <div class="allergies-list">
            <span v-for="(alergia, i) in user.alergias" :key="i" class="allergy-tag">
              {{ alergia }}
            </span>
          </div>
        </div>

        <!-- Pollen status card -->
        <div class="info-card">
          <h3 class="card-title">Situación actual del polen</h3>
          <div class="pollen-status">
            <strong>En {{ user.ciudad }}:</strong> {{ user.polen_actual || 'No disponible' }}
          </div>
          <p class="status-text">
            {{ getRecommendationText() }}
          </p>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="actions">
        <NuxtLink to="/register" class="btn-secondary">
          Registrar a otra persona
        </NuxtLink>
        <button @click="logout" class="btn-logout">
          Cerrar sesión
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// User data - will be loaded from localStorage
const user = ref({
  nombre: 'Usuario',
  apellidos: '',
  ciudad: 'Madrid',
  fecha_nacimiento: '',
  alergias: [],
  nivel_riesgo: 'medio',
  polen_actual: 'No disponible'
})

// Load real user data from localStorage (saved during registration)
onMounted(() => {
  const savedData = localStorage.getItem('registroData')
  if (!savedData) {
    navigateTo('/login')
    return
  }

  const parsed = JSON.parse(savedData)

  // Si viene del login, los datos están en parsed.user
  // Si viene del registro, están directamente en parsed
  const data = parsed.user ?? parsed

  user.value = {
    nombre: data.nombre || (data.nombre_completo ? data.nombre_completo.split(' ')[0] : 'Usuario'),
    apellidos: data.apellidos || (data.nombre_completo ? data.nombre_completo.split(' ').slice(1).join(' ') : ''),
    ciudad: data.ciudad || 'Madrid',
    fecha_nacimiento: data.fecha_nacimiento || '',
    nivel_riesgo: data.nivel_riesgo || data.nivel_riesgo || 'bajo',
    polen_actual: data.polen_actual || 'No disponible',
    alergias: data.alergias || []
  }
})

// Capitalize first letter of a string
const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

// Return recommendation based on risk level
const getRecommendationText = () => {
  const level = user.value.nivel_riesgo.toLowerCase()
  if (level === 'alto') {
    return 'Precaución alta recomendada esta semana. Mantén las ventanas cerradas en horas pico de polen.'
  } else if (level === 'medio') {
    return 'Precauciones moderadas recomendadas. Monitorea tus síntomas y limita actividades al aire libre si es necesario.'
  } else {
    return 'Buenas condiciones para disfrutar del exterior, pero mantén la alerta ante cualquier cambio.'
  }
}

// Logout function
const logout = () => {
  localStorage.removeItem('registroData')
  navigateTo('/login')
}
</script>

<style scoped>
/* Same style as register.vue */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Sora:wght@400;600;700&display=swap');

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
/* You can copy the rest of the .shape styles from your register.vue if you want */

.dashboard-container {
  width: 100%;
  max-width: 820px;
  background: white;
  border-radius: 24px;
  padding: 3rem 2.5rem;
  box-shadow: 0 10px 40px rgba(16, 185, 129, 0.12);
  border: 1.5px solid #d1fae5;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 2rem;
}
.brand-name {
  font-family: 'Sora', sans-serif;
  font-size: 1.9rem;
  font-weight: 700;
  color: #065f46;
}

.welcome-title {
  font-family: 'Sora', sans-serif;
  font-size: 2.4rem;
  font-weight: 700;
  color: #064e3b;
  margin-bottom: 0.5rem;
}

.highlight { color: #10b981; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 2.5rem 0;
}

.info-card {
  background: #f8fafc;
  border: 1px solid #d1fae5;
  border-radius: 16px;
  padding: 1.75rem;
}

.card-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: #065f46;
  margin-bottom: 1.25rem;
}

.info-item {
  margin-bottom: 0.85rem;
  color: #374151;
}

.allergy-tag {
  display: inline-block;
  background: #ecfdf5;
  color: #065f46;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.9rem;
  margin: 4px 6px 4px 0;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 2rem;
}

.btn-secondary {
  padding: 14px 24px;
  background: white;
  color: #065f46;
  border: 2px solid #d1fae5;
  border-radius: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f0fdf9;
  border-color: #10b981;
}

.btn-logout {
  padding: 14px 24px;
  background: #fee2e2;
  color: #b91c1c;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #fecaca;
}
</style>