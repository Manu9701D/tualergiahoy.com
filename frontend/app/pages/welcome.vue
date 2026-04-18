<!-- pages/welcome.vue -->
<template>
  <div class="auth-root">
    <div class="bg-shapes" aria-hidden="true">
      <span v-for="i in 6" :key="i" class="shape" :class="`shape-${i}`" />
    </div>

    <div class="welcome-card">
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

      <div class="success-header">
        <h1 class="success-title">¡Bienvenido/a a bordo!</h1>
        <p class="success-subtitle">
          Tu cuenta ha sido creada correctamente.<br>
          Te hemos enviado tu pronóstico personalizado por email.
        </p>
      </div>

      <div class="welcome-content">
        <div v-if="registroData" class="user-info">
          <p class="greeting">
            Hola, <strong>{{ registroData.nombre_completo || 'Usuario' }}</strong>
          </p>
          <p class="info-line">
            <strong>Ciudad:</strong> {{ registroData.ciudad }}<br>
            <strong>Nivel de riesgo:</strong> {{ registroData.nivel_riesgo }}<br>
            <strong>Polen actual:</strong> {{ registroData.polen_actual }}
          </p>
        </div>

        <div class="action-area">
          <a
            :href="registroData?.pdf_generado ? 
              `http://127.0.0.1:8000${registroData.pdf_generado}` : '#'"
            target="_blank"
            class="btn-primary"
          >
            Descargar mi Pronóstico en PDF
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </a>

          <p class="email-notice">
            También te hemos enviado el PDF al correo electrónico registrado.
          </p>
        </div>
      </div>

      <div class="footer-actions">
        <NuxtLink to="/register" class="btn-secondary">
          Registrar otra persona
        </NuxtLink>
        <NuxtLink to="/" class="btn-secondary">
          Volver al inicio
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
const registroData = ref(null)

onMounted(() => {
  const savedData = localStorage.getItem('registroData')
  if (savedData) {
    registroData.value = JSON.parse(savedData)
  } else {
    // Si no hay datos, redirigir al registro
    navigateTo('/register')
  }
})
</script>

<style scoped>
/* Estilo consistente con register.vue e index.vue */
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
.shape-6 { width: 220px; height: 220px; background: radial-gradient(circle, #bbf7d0 0%, transparent 70%); top: 55%; left: -60px; animation-delay: 4.2s; opacity: 0.4; }

@keyframes shapeFloat {
  0%   { transform: translateY(0) scale(1); }
  50%  { transform: translateY(-25px) scale(1.05); }
  100% { transform: translateY(0) scale(1); }
}

.welcome-card {
  position: relative;
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border: 1.5px solid #d1fae5;
  border-radius: 20px;
  padding: 3rem 2.5rem;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.06), 0 20px 48px rgba(16, 185, 129, 0.1);
  text-align: center;
  animation: cardIn 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(32px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}
.brand-name {
  font-family: 'Sora', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #065f46;
  letter-spacing: -0.03em;
}

.success-header {
  margin-bottom: 2.5rem;
}
.success-title {
  font-family: 'Sora', sans-serif;
  font-size: 2.1rem;
  font-weight: 700;
  color: #064e3b;
  margin-bottom: 0.8rem;
}
.success-subtitle {
  font-size: 1.05rem;
  color: #6b9e88;
  line-height: 1.5;
}

.user-info {
  background: #f0fdf9;
  border: 1px solid #a7f3d0;
  border-radius: 14px;
  padding: 1.25rem;
  margin-bottom: 2rem;
  text-align: left;
}
.greeting {
  font-size: 1.35rem;
  color: #065f46;
  margin-bottom: 0.8rem;
}
.info-line {
  color: #166534;
  line-height: 1.7;
  font-size: 1.02rem;
}

.action-area {
  margin: 2rem 0;
}

.btn-primary {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 18px 24px;
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 10px 25px rgba(16, 185, 129, 0.25);
  margin-bottom: 1rem;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(16, 185, 129, 0.35);
}

.email-notice {
  font-size: 0.95rem;
  color: #6b9e88;
  line-height: 1.6;
}

.footer-actions {
  display: flex;
  gap: 12px;
  margin-top: 2rem;
}

.btn-secondary {
  flex: 1;
  padding: 14px;
  background: white;
  color: #065f46;
  border: 2px solid #d1fae5;
  border-radius: 12px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f0fdf9;
  border-color: #10b981;
}

@media (max-width: 480px) {
  .welcome-card {
    padding: 2rem 1.5rem;
  }
}
</style>