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
        <h1 class="card-title">Bienvenido de nuevo</h1>
        <p class="card-subtitle">Accede a tu historial de alergias</p>
      </div>

      <form class="auth-form" @submit.prevent>
        <div class="field">
          <label for="email" class="field-label">Correo electrónico</label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M1 5l7 5 7-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            <input id="email" type="email" class="field-input" placeholder="tu@email.com" autocomplete="email"/>
          </div>
        </div>

        <div class="field">
          <label for="password" class="field-label">
            Contraseña
            <a href="#" class="forgot-link">¿Olvidaste tu contraseña?</a>
          </label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="3" y="7" width="10" height="8" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 7V5a3 3 0 0 1 6 0v2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <circle cx="8" cy="11" r="1" fill="currentColor"/>
            </svg>
            <input id="password" type="password" class="field-input" placeholder="••••••••" autocomplete="current-password"/>
          </div>
        </div>

        <button type="submit" class="btn-primary">
          Iniciar sesión
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </form>

      <p class="auth-footer">
        ¿No tienes cuenta?
        <NuxtLink to="/register" class="auth-link">Crear cuenta</NuxtLink>
      </p>
    </div>
  </div>
</template>

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
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.bg-shapes { position: absolute; inset: 0; pointer-events: none; }
.shape {
  position: absolute;
  border-radius: 50%;
  animation: shapeFloat 8s ease-in-out infinite;
}
.shape-1 { width: 480px; height: 480px; background: radial-gradient(circle, #bbf7d0 0%, transparent 70%); top: -180px; right: -140px; animation-delay: 0s; }
.shape-2 { width: 320px; height: 320px; background: radial-gradient(circle, #d1fae5 0%, transparent 70%); bottom: -100px; left: -100px; animation-delay: 1.5s; }
.shape-3 { width: 160px; height: 160px; background: radial-gradient(circle, #a7f3d0 0%, transparent 70%); top: 40%; left: 6%; animation-delay: 3s; }
.shape-4 { width: 100px; height: 100px; background: radial-gradient(circle, #6ee7b7 0%, transparent 70%); top: 18%; right: 14%; animation-delay: 1s; opacity: 0.5; }
.shape-5 { width: 200px; height: 200px; background: radial-gradient(circle, #ecfdf5 0%, transparent 70%); bottom: 22%; right: 6%; animation-delay: 2s; }

@keyframes shapeFloat {
  0%   { transform: translateY(0) scale(1); }
  50%  { transform: translateY(-20px) scale(1.04); }
  100% { transform: translateY(0) scale(1); }
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border: 1.5px solid #d1fae5;
  border-radius: 20px;
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.06), 0 20px 48px rgba(16, 185, 129, 0.1);
  animation: cardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(28px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
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

.auth-form { display: flex; flex-direction: column; gap: 1.25rem; }

.field { display: flex; flex-direction: column; gap: 0.45rem; animation: fadeUp 0.5s 0.2s both; }
.field:nth-child(2) { animation-delay: 0.25s; }

.field-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: #047857;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.forgot-link { color: #10b981; text-decoration: none; font-weight: 400; transition: color 0.2s; }
.forgot-link:hover { color: #059669; }

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
.field-input:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.12);
  background: #ffffff;
}

.btn-primary {
  margin-top: 0.4rem;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.8rem 1.25rem;
  background: linear-gradient(135deg, #059669 0%, #10b981 60%, #34d399 100%);
  border: none;
  border-radius: 10px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, filter 0.18s;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
  animation: fadeUp 0.5s 0.3s both;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 32px rgba(16, 185, 129, 0.4);
  filter: brightness(1.05);
}
.btn-primary:active { transform: translateY(0) scale(0.985); }

.auth-footer {
  margin-top: 1.75rem;
  text-align: center;
  font-size: 0.85rem;
  color: #6b9e88;
  animation: fadeUp 0.5s 0.35s both;
}
.auth-link { color: #059669; text-decoration: none; font-weight: 500; margin-left: 0.3rem; transition: color 0.2s; }
.auth-link:hover { color: #047857; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
