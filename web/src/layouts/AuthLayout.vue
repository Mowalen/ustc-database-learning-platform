<template>
  <div class="auth-layout">
    <section class="auth-hero">
      <div class="auth-hero__badge">USTC 数据库学习平台</div>
      <h1>把课堂、练习与考试
        <span>放在同一张学习地图里</span>
      </h1>
      <p>
        课程体系、作业/考试、成绩反馈和公告提醒都集中在这里，
        让教学与学习流程清晰可控。
      </p>
      <div class="auth-hero__meta">
        <div>
          <strong>Vue 3 + Vite</strong>
          <span>现代前端体验</span>
        </div>
        <div>
          <strong>FastAPI</strong>
          <span>稳定接口支持</span>
        </div>
      </div>
    </section>
    <section class="auth-panel">
      <RouterView />
    </section>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  padding: 32px;
  align-items: center;
}

.auth-hero {
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.12), rgba(209, 143, 59, 0.16));
  border-radius: 28px;
  padding: 48px 40px;
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(31, 27, 22, 0.08);
}

.auth-hero__badge {
  display: inline-flex;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(31, 111, 109, 0.16);
  color: var(--color-teal);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.auth-hero h1 {
  margin: 24px 0 16px;
  font-family: var(--font-display);
  font-size: clamp(28px, 4vw, 44px);
  line-height: 1.1;
}

.auth-hero h1 span {
  display: block;
  color: var(--color-accent-strong);
}

.auth-hero p {
  color: var(--color-ink-muted);
  font-size: 16px;
  line-height: 1.8;
}

.auth-hero__meta {
  margin-top: 28px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.auth-hero__meta div {
  background: rgba(255, 253, 247, 0.85);
  padding: 14px 16px;
  border-radius: 14px;
  min-width: 160px;
  border: 1px solid rgba(209, 143, 59, 0.2);
}

.auth-hero__meta strong {
  display: block;
  font-size: 15px;
  color: var(--color-ink);
}

.auth-hero__meta span {
  font-size: 13px;
  color: var(--color-ink-muted);
}

.auth-panel {
  background: var(--color-surface);
  border-radius: 24px;
  padding: 40px;
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--color-border);
}

@media (max-width: 720px) {
  .auth-layout {
    padding: 20px;
  }

  .auth-panel {
    padding: 28px;
  }
}
</style>
