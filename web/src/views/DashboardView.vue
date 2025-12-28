<template>
  <div class="dashboard">
    <!-- 公告看板 (教师/学生模式 - 顶部滚动条) -->
    <section class="announcement-board" v-if="auth.roleId === 2 || auth.roleId === 1">
      <div class="board-header">
        <div class="board-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <h3>公告看板</h3>
      </div>
      <div class="board-window">
        <div class="board-list" :style="{ '--item-count': announcementList.length }">
          <div 
            v-for="(item, index) in announcementList" 
            :key="item.id" 
            class="board-item"
            @click="router.push('/announcements')"
          >
            <span class="tag">最新</span>
            <span class="title">{{ item.title }}</span>
            <span class="date">{{ new Date(item.created_at).toLocaleDateString() }}</span>
          </div>
          <div 
             v-if="announcementList.length > 0"
             class="board-item"
             @click="router.push('/announcements')"
          >
             <span class="tag">最新</span>
             <span class="title">{{ announcementList[0].title }}</span>
             <span class="date">{{ new Date(announcementList[0].created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>
      <div class="board-action">
        <el-button link @click="router.push('/announcements')">
          查看全部
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </section>

    <!-- 欢迎横幅 -->
    <section class="hero">
      <div class="hero__content">
        <div class="hero__greeting">
          <span class="hero__wave">👋</span>
          <h2>你好，{{ auth.user?.full_name || auth.user?.username }}</h2>
        </div>
        <p>这里是你的教学与学习指挥台，集中查看课程、作业、成绩和公告动态。</p>
      </div>
      <div class="hero__badge">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
        <span>{{ auth.roleLabel }}模式</span>
      </div>
    </section>

    <!-- 统计卡片 -->
    <section class="stats">
      <el-card 
        v-for="(stat, index) in visibleStats" 
        :key="stat.label" 
        class="stat-card"
        :class="`stat-card--${index % 4}`"
      >
        <div class="stat-card__icon">
          <svg v-if="index === 0" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          <svg v-else-if="index === 1" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <svg v-else-if="index === 2" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <div class="stat-card__content">
          <div class="stat-card__label">{{ stat.label }}</div>
          <div class="stat-card__value">{{ stat.value }}</div>
          <div class="stat-card__desc">{{ stat.desc }}</div>
        </div>
      </el-card>
    </section>

    <!-- 快速入口 (仅管理员) -->
    <section class="actions" v-if="auth.roleId === 3">
      <div class="actions__header">
        <h3>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="8" y1="6" x2="21" y2="6"/>
            <line x1="8" y1="12" x2="21" y2="12"/>
            <line x1="8" y1="18" x2="21" y2="18"/>
            <line x1="3" y1="6" x2="3.01" y2="6"/>
            <line x1="3" y1="12" x2="3.01" y2="12"/>
            <line x1="3" y1="18" x2="3.01" y2="18"/>
          </svg>
          快速入口
        </h3>
        <p>快速访问各个功能模块</p>
      </div>
      
      <div class="action-grid">
        <RouterLink class="action-item" to="/courses">
          <div class="action-item__icon action-item__icon--courses">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
            </svg>
          </div>
          <div class="action-item__content">
            <strong>课程中心</strong>
            <span>查看课程列表与详情</span>
          </div>
          <svg class="action-item__arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </RouterLink>

        <RouterLink class="action-item" to="/tasks">
          <div class="action-item__icon action-item__icon--tasks">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <div class="action-item__content">
            <strong>作业与考试</strong>
            <span>安排与提交任务</span>
          </div>
          <svg class="action-item__arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </RouterLink>

        <RouterLink class="action-item" to="/scores">
          <div class="action-item__icon action-item__icon--scores">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
            </svg>
          </div>
          <div class="action-item__content">
            <strong>成绩反馈</strong>
            <span>追踪评分与排名</span>
          </div>
          <svg class="action-item__arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </RouterLink>

        <RouterLink class="action-item" to="/announcements">
          <div class="action-item__icon action-item__icon--announcements">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="action-item__content">
            <strong>公告看板</strong>
            <span>获取系统最新通知</span>
          </div>
          <svg class="action-item__arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </RouterLink>
      </div>
    </section>


  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { courseApi, enrollmentApi, scoreApi, adminApi } from "@/services/api";
import type { Announcement } from "@/types";
import { ArrowRight } from "@element-plus/icons-vue";

const auth = useAuthStore();
const router = useRouter();
const announcementList = ref<Announcement[]>([]);
const stats = ref([
  { label: "课程总量", value: "-", desc: "系统内已发布课程" },
  { label: "我的选课", value: "-", desc: "当前进行中的学习" },
  { label: "待评分任务", value: "-", desc: "尚未完成评分" },
  { label: "公告更新", value: "-", desc: "最新通知条数" },
]);

const visibleStats = computed(() => {
  if (auth.roleId === 3) {
    return stats.value.filter((stat) => stat.label !== "我的选课");
  }
  if (auth.roleId === 2) {
    return [
      { label: "平台课程数量", value: stats.value[0].value, desc: "全平台已发布课程" },
      { label: "教师教授课程", value: stats.value[1].value, desc: "您教授的课程" },
      { label: "待批改作业", value: stats.value[2].value, desc: "等待批改的提交" },
    ];
  }
  if (auth.roleId === 1) {
    return [
      { label: "课程总量", value: stats.value[0].value, desc: "系统内已发布课程" },
      { label: "我的选课", value: stats.value[1].value, desc: "当前进行中的学习" },
      { label: "待完成作业", value: stats.value[2].value, desc: "等待提交的作业" },
    ];
  }
  return stats.value;
});

const loadStats = async () => {
  const courses = await courseApi.listCourses();
  stats.value[0].value = String(courses.length);

  const announcements = await adminApi.listAnnouncements();
  announcementList.value = announcements;
  stats.value[3].value = String(announcements.length);

  if (auth.roleId === 1 && auth.user) {
    const enrollments = await enrollmentApi.myEnrollments(auth.user.id);
    stats.value[1].value = String(enrollments.length);

    const scores = await scoreApi.myScores(auth.user.id);
    const pending = scores.filter((score) => !score.score).length;
    stats.value[2].value = String(pending);
  }

  if (auth.roleId === 2 && auth.user) {
    const myCourses = courses.filter(c => c.teacher_id === auth.user?.id);
    stats.value[1].value = String(myCourses.length);
    stats.value[2].value = "0"; 
  }

  if (auth.roleId === 3) {
    stats.value[2].value = "查看成绩列表";
  }
};

onMounted(() => {
  loadStats().catch(() => {
    // Ignore dashboard errors for now.
  });
});
</script>

<style scoped>
.dashboard {
  display: grid;
  gap: 32px;
}

/* 欢迎横幅 */
.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  padding: 32px 36px;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.12), rgba(209, 143, 59, 0.12));
  border-radius: 24px;
  border: 1px solid rgba(31, 111, 109, 0.15);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(209, 143, 59, 0.1), transparent);
  border-radius: 50%;
  pointer-events: none;
}

.hero__content {
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.hero__greeting {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.hero__wave {
  font-size: 32px;
  animation: wave 2s ease-in-out infinite;
  display: inline-block;
}

@keyframes wave {
  0%, 100% {
    transform: rotate(0deg);
  }
  10%, 30% {
    transform: rotate(14deg);
  }
  20%, 40% {
    transform: rotate(-8deg);
  }
  50% {
    transform: rotate(14deg);
  }
  60% {
    transform: rotate(0deg);
  }
}

.hero h2 {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--color-ink);
}

.hero p {
  color: var(--color-ink-muted);
  font-size: 15px;
  line-height: 1.6;
}

.hero__badge {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--color-surface);
  padding: 12px 20px;
  border-radius: 999px;
  font-weight: 600;
  color: var(--color-teal);
  box-shadow: 0 4px 12px rgba(31, 111, 109, 0.15);
  border: 1px solid rgba(31, 111, 109, 0.1);
  position: relative;
  z-index: 1;
  white-space: nowrap;
}

.hero__badge svg {
  flex-shrink: 0;
}

/* 统计卡片 */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.stat-card--0::before {
  background: radial-gradient(circle, rgba(31, 111, 109, 0.08), transparent);
}

.stat-card--1::before {
  background: radial-gradient(circle, rgba(209, 143, 59, 0.08), transparent);
}

.stat-card--2::before {
  background: radial-gradient(circle, rgba(31, 111, 109, 0.08), transparent);
}

.stat-card--3::before {
  background: radial-gradient(circle, rgba(209, 143, 59, 0.08), transparent);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(31, 111, 109, 0.12);
  border-color: rgba(31, 111, 109, 0.25);
}

.stat-card:hover::before {
  right: -10%;
  opacity: 0.7;
}

.stat-card__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.1), rgba(209, 143, 59, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-teal);
  margin-bottom: 16px;
}

.stat-card__content {
  position: relative;
  z-index: 1;
}

.stat-card__label {
  color: var(--color-ink-muted);
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.stat-card__value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-ink);
  font-family: var(--font-display);
  margin-bottom: 6px;
}

.stat-card__desc {
  color: var(--color-ink-muted);
  font-size: 13px;
}

/* 快速入口 */
.actions {
  background: var(--color-surface);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--color-border);
}

.actions__header {
  margin-bottom: 24px;
}

.actions__header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--color-ink);
  margin-bottom: 8px;
}

.actions__header h3 svg {
  color: var(--color-teal);
}

.actions__header p {
  color: var(--color-ink-muted);
  font-size: 14px;
  margin-left: 30px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 253, 247, 0.5);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.03), rgba(209, 143, 59, 0.03));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-item:hover::before {
  opacity: 1;
}

.action-item:hover {
  transform: translateX(4px);
  border-color: rgba(31, 111, 109, 0.3);
  box-shadow: 0 4px 16px rgba(31, 111, 109, 0.1);
}

.action-item__icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.action-item__icon--courses {
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.15), rgba(31, 111, 109, 0.08));
  color: var(--color-teal);
}

.action-item__icon--tasks {
  background: linear-gradient(135deg, rgba(209, 143, 59, 0.15), rgba(209, 143, 59, 0.08));
  color: var(--color-accent);
}

.action-item__icon--scores {
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.15), rgba(31, 111, 109, 0.08));
  color: var(--color-teal);
}

.action-item__icon--announcements {
  background: linear-gradient(135deg, rgba(209, 143, 59, 0.15), rgba(209, 143, 59, 0.08));
  color: var(--color-accent);
}

.action-item__content {
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.action-item strong {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: 4px;
}

.action-item span {
  display: block;
  font-size: 13px;
  color: var(--color-ink-muted);
}

.action-item__arrow {
  flex-shrink: 0;
  color: var(--color-ink-muted);
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.action-item:hover .action-item__arrow {
  color: var(--color-teal);
  transform: translateX(4px);
}


/* 公告看板 */
.announcement-board {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 32px;
  background: white;
  border-radius: 20px;
  border: 1px solid var(--color-border);
  box-shadow: 0 4px 20px rgba(31, 111, 109, 0.05);
  height: 80px;
}

.board-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-right: 24px;
  border-right: 1px solid var(--color-border);
  min-width: unset;
}

.board-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.1), rgba(209, 143, 59, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-teal);
}

.board-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-ink);
  white-space: nowrap;
  font-family: var(--font-display);
}

.board-window {
  flex: 1;
  height: 40px;
  overflow: hidden;
  position: relative;
  mask-image: none;
}

.board-list {
  display: flex;
  flex-direction: column;
  animation: scrollUp 10s linear infinite;
  padding: 0;
}

.board-item {
  height: 40px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  flex-shrink: 0;
  padding: 0 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.board-item:hover {
  background: rgba(0,0,0,0.02);
}

.board-item .tag {
  background: rgba(209, 143, 59, 0.1);
  color: var(--color-accent);
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  white-space: nowrap;
}

.board-item .title {
  color: var(--color-ink);
  font-size: 15px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 400px;
}

.board-item .date {
  color: var(--color-ink-muted);
  font-size: 13px;
  margin-left: auto;
}

.board-action {
  padding-left: 20px;
  border-left: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes scrollUp {
  0% { transform: translateY(0); }
  100% { transform: translateY(calc(-100% + 40px)); } 
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 24px;
  }

  .hero__badge {
    align-self: flex-start;
  }

  .stats {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
  }

  .actions {
    padding: 24px;
  }

  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>
