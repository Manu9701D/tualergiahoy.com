<!-- pages/dashboard.vue -->
<template>
  <div class="auth-root">
    <div class="bg-shapes" aria-hidden="true">
      <span v-for="i in 6" :key="i" class="shape" :class="`shape-${i}`" />
    </div>

    <div class="dashboard-container">
      <!-- Brand header -->
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

      <!-- Welcome message -->
      <div class="welcome-section">
        <h1 class="welcome-title">
          Welcome back, <span class="highlight">{{ user.nombre }}</span>!
        </h1>
        <p class="welcome-subtitle">
          Here's your personal allergy overview for today
        </p>
      </div>

      <!-- User information cards -->
      <div class="info-grid">
        <!-- Personal data card -->
        <div class="info-card">
          <h3 class="card-title">Your Profile</h3>
          <div class="info-item">
            <strong>Full Name:</strong> {{ user.nombre }} {{ user.apellidos }}
          </div>
          <div class="info-item">
            <strong>City:</strong> {{ user.ciudad }}
          </div>
          <div class="info-item">
            <strong>Date of Birth:</strong> {{ user.fecha_nacimiento }}
          </div>
          <div class="info-item">
            <strong>Risk Level:</strong> 
            <span :class="`risk-badge risk-${user.nivel_riesgo}`">
              {{ user.nivel_riesgo | capitalize }}
            </span>
          </div>
        </div>

        <!-- Allergies card -->
        <div class="info-card">
          <h3 class="card-title">Your Allergies</h3>
          <div class="allergies-list">
            <span v-for="(alergia, i) in user.alergias" :key="i" class="allergy-tag">
              {{ alergia }}
            </span>
          </div>
        </div>

        <!-- Current pollen status card -->
        <div class="info-card">
          <h3 class="card-title">Current Pollen Situation</h3>
          <div class="pollen-status">
            <strong>In {{ user.ciudad }}:</strong> {{ user.polen_actual }}
          </div>
          <p class="status-text">
            {{ getRecommendationText() }}
          </p>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="actions">
        <NuxtLink to="/register" class="btn-secondary">
          Register another person
        </NuxtLink>
        <button @click="logout" class="btn-logout">
          Log out
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Reactive user data object - populated from localStorage or backend in the future
const user = ref({
  nombre: 'Juan',
  apellidos: 'Pérez García',
  ciudad: 'Madrid',
  fecha_nacimiento: '1995-06-15',
  alergias: ['polen', 'gramíneas', 'ácaros'],
  nivel_riesgo: 'alto',
  polen_actual: 'Moderado (Total: 34) — Gramíneas: 28'
})

// Load real user data from localStorage (saved during registration)
onMounted(() => {
  const savedData = localStorage.getItem('registroData')
  if (savedData) {
    const data = JSON.parse(savedData)
    user.value = {
      nombre: data.nombre_completo ? data.nombre_completo.split(' ')[0] : 'User',
      apellidos: data.nombre_completo ? data.nombre_completo.split(' ').slice(1).join(' ') : '',
      ciudad: data.ciudad || 'Madrid',
      nivel_riesgo: data.nivel_riesgo || 'medio',
      polen_actual: data.polen_actual || 'Not available',
      alergias: data.alergias || ['polen']
    }
  }
})

// Returns a helpful recommendation message based on risk level
const getRecommendationText = () => {
  if (user.value.nivel_riesgo === 'alto') {
    return 'High caution recommended this week. Keep windows closed during peak pollen hours.'
  } else if (user.value.nivel_riesgo === 'medio') {
    return 'Moderate precautions advised. Monitor symptoms and limit outdoor activities if needed.'
  } else {
    return 'Good conditions to enjoy outdoors, but stay alert to any changes.'
  }
}

// Logout function - clears stored data and redirects to login
const logout = () => {
  localStorage.removeItem('registroData')
  navigateTo('/login')
}
</script>

<style scoped>
/* Consistent styling with register.vue and index.vue */
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
.shape-1 { width: 500px; height: 500px; background: radial-gradient(circle, #bbf7d0 0%, transparent 70%); top: -200px; left: -140px; animation-delay: 0s; }
.shape-2 { width: 300px; height: 300px; background: radial-gradient(circle, #d1fae5 0%, transparent 70%); bottom: -90px; right: -80px; animation-delay: 1.5s; }
.shape-3 { width: 140px; height: 140px; background: radial-gradient(circle, #a7f3d0 0%, transparent 70%); top: 35%; right: 8%; animation-delay: 3s; }
.shape-4 { width: 90px;  height: 90px;  background: radial-gradient(circle, #6ee7b7 0%, transparent 70%); top: 20%; left: 14%; animation-delay: 1s; opacity: 0.5; }
.shape-5 { width: 180px; height: 180px; background: radial-gradient(circle, #ecfdf5 0%, transparent 70%); bottom: 20%; left: 8%; animation-delay: 2s; }
.shape-6 { width: 220px; height: 220px; background: radial-gradient(circle, #bbf7d0 0%, transparent 70%); top: 55%; left: -60px; animation-delay: 4.2s; opacity: 0.4; }

@keyframes shapeFloat {
  0%   { transform: translateY(0) scale(1); }
  50%  { transform: translateY(-25px) scale(1.05); }
  100% { transform: translateY(0) scale(1); }
}

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