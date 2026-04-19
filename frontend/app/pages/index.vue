<!-- pages/index.vue -->
<template>
  <div class="auth-root">
    <div class="bg-shapes" aria-hidden="true">
      <span v-for="i in 6" :key="i" class="shape" :class="`shape-${i}`" />
    </div>

    <div class="main-content">
      <!-- Panel izquierdo - Presentación -->
      <div class="left-panel">
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

        <div class="hero-content">
          <h1 class="hero-title">
            Las alergias no deberían <span class="highlight">controlar tu vida</span>
          </h1>
          
          <p class="hero-subtitle">
            Miles de personas sufren cada día con picor, estornudos, ojos hinchados y cansancio constante.<br><br>
            <strong>Ya es hora de que alguien te escuche y te ayude de verdad.</strong>
          </p>

          <div class="hero-text">
            <p>
              tualergiahoy nace para todas aquellas personas que viven prisioneras de sus alergias: 
              polen, ácaros, gramíneas, olivo, pelo de mascotas… 
            </p>
            <p class="mt-4">
              Te ofrecemos un pronóstico semanal personalizado, información real de polen en tu ciudad 
              y consejos prácticos para que puedas volver a disfrutar de la primavera y del aire libre.
            </p>
          </div>
        </div>
      </div>

      <!-- Panel derecho - Acciones -->
      <div class="right-panel">
        <div class="action-card">
          <h2 class="action-title">¿Listo para tomar el control?</h2>
          
          <div class="action-buttons">
            <NuxtLink to="/register" class="btn-primary">
              Crear mi cuenta gratis
              <span class="btn-arrow">→</span>
            </NuxtLink>

            <NuxtLink to="/login" class="btn-secondary">
              Ya tengo cuenta
            </NuxtLink>
          </div>

          <p class="trust-text">
            Estás a un click de llevar una mejor primavera.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No necesitamos lógica por ahora
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Sora:wght@400;600;700&display=swap');

.auth-root {
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
  background: #f0fdf6;
  position: relative;
  overflow: hidden;
}

.bg-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, #a7f3d0 0%, transparent 70%);
  animation: shapeFloat 12s ease-in-out infinite;
}

.shape-1 { width: 620px; height: 620px; top: -180px; left: -200px; animation-delay: 0s; opacity: 0.6; }
.shape-2 { width: 420px; height: 420px; bottom: -120px; right: -100px; animation-delay: 2.5s; }
.shape-3 { width: 280px; height: 280px; top: 25%; right: 12%; animation-delay: 4s; opacity: 0.4; }
.shape-4 { width: 180px; height: 180px; top: 15%; left: 18%; animation-delay: 1.2s; }
.shape-5 { width: 150px; height: 150px; bottom: 28%; left: 10%; animation-delay: 3.8s; opacity: 0.35; }
.shape-6 { width: 90px;  height: 90px;  top: 45%; left: 8%; animation-delay: 0.8s; }

@keyframes shapeFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-35px) rotate(8deg); }
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 420px;
  min-height: 100vh;
  position: relative;
  z-index: 2;
}

.left-panel {
  padding: 80px 80px 80px 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 60px;
}

.brand-name {
  font-family: 'Sora', sans-serif;
  font-size: 1.85rem;
  font-weight: 700;
  color: #065f46;
  letter-spacing: -0.04em;
}

.hero-title {
  font-family: 'Sora', sans-serif;
  font-size: 3.1rem;
  line-height: 1.15;
  font-weight: 700;
  color: #064e3b;
  margin-bottom: 28px;
}

.highlight {
  color: #10b981;
  position: relative;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 8px;
  background: #a7f3d0;
  z-index: -1;
}

.hero-subtitle {
  font-size: 1.25rem;
  line-height: 1.5;
  color: #166534;
  margin-bottom: 32px;
  font-weight: 500;
}

.hero-text p {
  color: #4b6f5f;
  line-height: 1.75;
  font-size: 1.05rem;
}

.right-panel {
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  border-left: 1px solid #d1fae5;
}

.action-card {
  width: 100%;
  max-width: 340px;
  text-align: center;
}

.action-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.65rem;
  font-weight: 700;
  color: #065f46;
  margin-bottom: 42px;
  line-height: 1.3;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.btn-primary {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  padding: 18px 24px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 10px 25px rgba(16, 185, 129, 0.25);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(16, 185, 129, 0.35);
}

.btn-secondary {
  background: white;
  color: #065f46;
  border: 2px solid #d1fae5;
  padding: 18px 24px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 1.05rem;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #f0fdf9;
  border-color: #10b981;
}

.trust-text {
  margin-top: 48px;
  font-size: 0.9rem;
  color: #6b9e88;
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  .right-panel {
    padding: 60px 30px;
  }
  .left-panel {
    padding: 80px 40px;
  }
}
</style>