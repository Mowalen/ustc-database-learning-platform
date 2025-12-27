<template>
  <div class="not-found">
    <h2>页面未找到</h2>
    <p>你访问的页面不存在或已被移动。</p>
    <RouterLink to="/">返回首页</RouterLink>
  </div>
</template>

<style scoped>
.not-found {
  height: 100vh;
  display: grid;
  place-items: center;
  text-align: center;
  padding: 40px;
}

.not-found h2 {
  font-family: var(--font-display);
  font-size: 32px;
  margin-bottom: 12px;
}

.not-found p {
  color: var(--color-ink-muted);
  margin-bottom: 18px;
}

.not-found a {
  color: var(--color-teal);
  font-weight: 600;
}
</style>
