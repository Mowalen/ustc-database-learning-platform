<template>
  <div class="auth-layout">
    <!-- 顶部Logo和标语 -->
    <div class="auth-header">
      <div class="auth-logo">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div class="logo-text">
          <h1>USTC 数据库学习平台</h1>
          <p>教学 · 练习 · 考核</p>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="auth-content">
      <!-- 左侧宣传区 -->
      <div class="auth-hero">
        <h2>
          把课堂、练习与考试
          <span>放在同一张学习地图里</span>
        </h2>
        <p>
          课程体系、作业/考试、成绩反馈和公告提醒都集中在这里，
          让教学与学习流程清晰可控。
        </p>
        <div class="auth-features">
          <div class="feature-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <div>
              <strong>Vue 3 + Vite</strong>
              <span>现代前端体验</span>
            </div>
          </div>
          <div class="feature-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <div>
              <strong>FastAPI</strong>
              <span>稳定接口支持</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="auth-form">
        <RouterView />
      </div>
    </div>

    <!-- 底部 -->
    <div class="auth-footer">
      <div class="footer-text">
        <p>© 2025 USTC 数据库学习平台. All rights reserved.</p>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="bg-decoration bg-decoration-1"></div>
    <div class="bg-decoration bg-decoration-2"></div>
    <div class="bg-decoration bg-decoration-3"></div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, 
    rgba(255, 253, 247, 1) 0%, 
    rgba(255, 250, 240, 1) 50%, 
    rgba(255, 253, 247, 1) 100%
  );
}

/* 顶部Logo区域 */
.auth-header {
  padding: 24px 48px;
  border-bottom: 1px solid rgba(31, 111, 109, 0.1);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  z-index: 10;
  position: relative;
  flex-shrink: 0;
}

.auth-logo {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 1400px;
  margin: 0 auto;
}

.logo-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--color-teal), #1e8a87);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(31, 111, 109, 0.3);
}

.logo-text h1 {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--color-ink);
  margin-bottom: 2px;
}

.logo-text p {
  font-size: 13px;
  color: var(--color-ink-muted);
  letter-spacing: 0.5px;
}

/* 主内容区 */
.auth-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  width: 100%;
  margin: 0;
  padding: 0;
  position: relative;
  z-index: 1;
}

/* 左侧宣传区 */
.auth-hero {
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.auth-hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(209, 143, 59, 0.08), transparent);
  border-radius: 50%;
  pointer-events: none;
}

.auth-hero h2 {
  font-family: var(--font-display);
  font-size: clamp(28px, 3.5vw, 42px);
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-ink);
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
  max-width: 500px;
}

.auth-hero h2 span {
  display: block;
  background: linear-gradient(135deg, var(--color-teal), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-top: 8px;
}

.auth-hero p {
  color: var(--color-ink-muted);
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
  max-width: 480px;
}

.auth-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 480px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  border: 1px solid rgba(31, 111, 109, 0.15);
  box-shadow: 0 2px 8px rgba(31, 111, 109, 0.08);
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateX(6px);
  border-color: rgba(31, 111, 109, 0.3);
  box-shadow: 0 4px 16px rgba(31, 111, 109, 0.12);
}

.feature-item svg {
  flex-shrink: 0;
  color: var(--color-teal);
  margin-top: 2px;
}

.feature-item strong {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: 2px;
}

.feature-item span {
  font-size: 13px;
  color: var(--color-ink-muted);
}

/* 右侧表单区 */
.auth-form {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  border-left: 1px solid rgba(31, 111, 109, 0.1);
  height: 100%;
  overflow-y: auto;
}

.auth-form :deep(> *) {
  width: 100%;
  max-width: 480px;
  margin: auto 0;
}

/* 底部 */
.auth-footer {
  padding: 20px 48px;
  border-top: 1px solid rgba(31, 111, 109, 0.1);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  z-index: 10;
  position: relative;
  flex-shrink: 0;
}

.footer-text {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-text p {
  text-align: center;
  font-size: 13px;
  color: var(--color-ink-muted);
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  border-radius: 50%;
  opacity: 0.4;
  z-index: 0;
  animation: pulse 6s ease-in-out infinite;
  pointer-events: none;
}

.bg-decoration-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(31, 111, 109, 0.08), transparent);
  top: -300px;
  right: -300px;
  animation-delay: 0s;
}

.bg-decoration-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(209, 143, 59, 0.08), transparent);
  bottom: -250px;
  left: -250px;
  animation-delay: 2s;
}

.bg-decoration-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(31, 111, 109, 0.06), transparent);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.4;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.6;
  }
}

/* 响应式 */
@media (min-width: 1025px) {
  .auth-layout {
    height: 100vh;
  }
  
  .auth-content {
    height: 100%;
    overflow: hidden;
  }
}

@media (max-width: 1024px) {
  .auth-content {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .auth-form {
    height: auto;
    overflow-y: visible;
    padding: 60px 40px;
    border-left: none;
    border-top: 1px solid rgba(31, 111, 109, 0.1);
  }

  .auth-hero {
    height: auto;
    padding: 60px 40px 40px;
  }

  .auth-header {
    padding: 24px 40px 20px;
  }

  .auth-footer {
    padding: 16px 40px;
  }
}

@media (max-width: 640px) {
  .auth-header {
    padding: 20px 24px 16px;
  }

  .logo-icon {
    width: 40px;
    height: 40px;
  }

  .logo-text h1 {
    font-size: 18px;
  }

  .auth-hero {
    padding: 40px 24px 32px;
  }

  .auth-form {
    padding: 40px 24px;
  }

  .auth-footer {
    padding: 16px 24px;
  }

  .feature-item {
    padding: 14px 16px;
  }
}
</style>
