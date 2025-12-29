<template>
  <div class="dashboard">
    <!-- 公告看板 (轮播文字模式 - 大屏居中) -->
    <section class="announcement-board">
      <button
        class="carousel-nav"
        type="button"
        aria-label="上一条公告"
        :disabled="announcementList.length < 2"
        @click.stop="prevAnnouncement"
      >
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <div class="board-carousel">
        <Transition name="slide-fade" mode="out-in">
          <div 
            v-if="currentAnnouncement"
            :key="currentAnnouncement.id"
            class="carousel-item"
            style="cursor: default;"
          >
            <div class="carousel-text">
              <div class="carousel-title">{{ currentAnnouncement.title }}</div>
              <div class="carousel-content">{{ currentAnnouncement.content }}</div>
            </div>

            <div class="carousel-date">{{ formatDate(currentAnnouncement.created_at) }}</div>
          </div>
          <div v-else class="carousel-item empty">
            暂无公告
          </div>
        </Transition>
      </div>
      <button
        class="carousel-nav"
        type="button"
        aria-label="下一条公告"
        :disabled="announcementList.length < 2"
        @click.stop="nextAnnouncement"
      >
        <el-icon><ArrowRight /></el-icon>
      </button>
    </section>

    <!-- 欢迎横幅 -->
    <section class="hero">
      <div class="hero__content">
        <div class="hero__greeting">
          <span class="hero__wave">👋</span>
          <h2>你好，{{ auth.user?.full_name || auth.user?.username }}</h2>
        </div>
        <p>{{ welcomeMessage }}</p>
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

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { courseApi, enrollmentApi, scoreApi, adminApi, taskApi } from "@/services/api";
import type { Announcement } from "@/types";
import { ArrowLeft, ArrowRight } from "@element-plus/icons-vue";
import { formatDate } from "@/utils/format";

const auth = useAuthStore();
const router = useRouter();
const announcementList = ref<Announcement[]>([]);
const currentIndex = ref(0);
let timer: number | null = null;

const stats = ref([
  { label: "课程总量", value: "-", desc: "系统内已发布课程" },
  { label: "我的选课", value: "-", desc: "当前进行中的学习" },
  { label: "待评分任务", value: "-", desc: "尚未完成评分" },
  { label: "公告更新", value: "-", desc: "最新通知条数" },
]);

const currentAnnouncement = computed(() => {
  if (announcementList.value.length === 0) return null;
  return announcementList.value[currentIndex.value];
});

const startCarousel = () => {
  if (timer) clearInterval(timer);
  timer = setInterval(() => {
    if (announcementList.value.length > 1) {
      currentIndex.value = (currentIndex.value + 1) % announcementList.value.length;
    }
  }, 5000) as unknown as number;
};

const nextAnnouncement = () => {
  if (announcementList.value.length === 0) return;
  currentIndex.value = (currentIndex.value + 1) % announcementList.value.length;
  startCarousel();
};

const prevAnnouncement = () => {
  if (announcementList.value.length === 0) return;
  const total = announcementList.value.length;
  currentIndex.value = (currentIndex.value - 1 + total) % total;
  startCarousel();
};

const visibleStats = computed(() => {
  if (auth.roleId === 3) {
      // Admin dashboard Stats
    return [
      { label: "课程总量", value: stats.value[0].value, desc: "系统内已发布课程" },
      { label: "教师总量", value: stats.value[1].value, desc: "系统内注册教师" },
      { label: "学生总量", value: stats.value[2].value, desc: "系统内注册学生" },
    ];
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
      { label: "待完成任务", value: stats.value[2].value, desc: "等待提交的任务" },
    ];
  }
  return stats.value;
});

const welcomeMessage = computed(() => {
  if (auth.roleId === 1) {
    return "这里是你的学习指挥台，集中查看课程、作业、成绩和公告动态。";
  } else if (auth.roleId === 2) {
    return "这里是您的教学工作台，您可以管理课程内容、发布作业任务、批改学生成绩。";
  } else if (auth.roleId === 3) {
    return "这里是系统管理中心，您可以维护用户信息、管理所有课程与公告内容。";
  }
  return "这里是你的教学与学习指挥台，集中查看课程、作业、成绩和公告动态。";
});

const loadStats = async () => {
  const courses = await courseApi.listCourses();
  stats.value[0].value = String(courses.length);

  const announcements = await adminApi.listAnnouncements();
  announcementList.value = announcements;
  // stats.value[3].value = String(announcements.length); 

  if (auth.roleId === 1 && auth.user) {
    const enrollments = await enrollmentApi.myEnrollments(auth.user.id);
    const activeEnrollments = enrollments.filter(e => e.status === 'active');
    stats.value[1].value = String(activeEnrollments.length);

    try {
      const tasksPromises = activeEnrollments.map(e => taskApi.listTasks(e.course_id));
      const tasksLists = await Promise.all(tasksPromises);
      const allTasks = tasksLists.flat();

      const myScores = await scoreApi.myScores(auth.user.id);
      const submittedTaskIds = new Set(myScores.map(s => s.task_id));

      const pendingCount = allTasks.filter((t: any) => !submittedTaskIds.has(t.id)).length;
      stats.value[2].value = String(pendingCount);
    } catch (error) {
      console.error("Failed to load student tasks stats", error);
      stats.value[2].value = "-";
    }
  }

  if (auth.roleId === 2 && auth.user) {
    const myCourses = courses.filter(c => c.teacher_id === auth.user?.id);
    stats.value[1].value = String(myCourses.length);
    
    try {
      const pendingGradingCount = await scoreApi.getTeacherPendingGradingCount();
      stats.value[2].value = String(pendingGradingCount);
    } catch (error) {
       console.error("Failed to load teacher grading stats", error);
       stats.value[2].value = "-";
    }
  }

  if (auth.roleId === 3) {
      // Load user stats
      const users = await adminApi.listUsers({limit: 1000});
      const teachers = users.filter(u => u.role_id === 2);
      const students = users.filter(u => u.role_id === 1);
      
      stats.value[1].value = String(teachers.length);
      stats.value[2].value = String(students.length);
  }
  
  startCarousel();
};


onMounted(() => {
  loadStats().catch(() => {
    // Ignore dashboard errors for now.
  });
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.dashboard {
  display: grid;
  gap: 32px;
}

/* 公告看板 (轮播文字模式) */
.announcement-board {
  display: grid;
  grid-template-columns: 48px 1fr 48px;
  align-items: center;
  gap: 16px;
  padding: 0 20px;
  background: white;
  border-radius: 16px;
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02);
  height: 240px; /* Increased height */
  position: relative;
}

.board-carousel {
  flex: 1;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.carousel-nav {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(31, 111, 109, 0.18);
  background: linear-gradient(180deg, #ffffff 0%, #f8faf9 100%);
  color: var(--color-teal);
  display: grid;
  place-items: center;
  cursor: pointer;
  box-shadow: 0 6px 14px rgba(31, 111, 109, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.carousel-nav:hover {
  transform: translateY(-1px);
  border-color: rgba(31, 111, 109, 0.35);
  box-shadow: 0 10px 20px rgba(31, 111, 109, 0.15);
}

.carousel-nav:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.carousel-item {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center; /* Center main content */
  cursor: pointer;
  padding: 0 24px;
}

.carousel-item.empty {
  color: var(--color-ink-muted);
  font-size: 16px;
}

.carousel-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start; /* Changed to left align as per "middle" content usually reads better, but user said "center". Let's assume left-aligned block in center of card? 
                            The user image shows text starting from the left of the content area. 
                            Wait, "Modify announcement content in the middle" usually means centering. 
                            Let's try ALIGN-ITEMS: FLEX-START but the BLOCK is centered?
                            Actually, looking at the image: title and content are distinct.
                            Let's try sticking to Left Aligned Text, but comfortably padded/centered vertically.
                            If I center the block, the text starts from left. */
  gap: 12px;
  max-width: 60%; /* Limit width */
  margin-left: 140px; /* Offset for left info */
  margin-right: 140px; /* Offset for date */
}

/* User said "Content in the middle". 
   If I just use the code from previous step's intent: "align-items: center; text-align: center;"
   Let's stick to the center text plan as it's the safest interpretation of "middle". */
.carousel-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center; 
  gap: 16px;
  max-width: 700px;
}

.carousel-title {
  color: var(--color-ink);
  font-size: 28px; /* Larger Title */
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.carousel-content {
  color: var(--color-ink-muted);
  font-size: 16px; /* Larger content */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.8;
  max-width: 100%;
}

.carousel-date {
  color: var(--color-ink-muted);
  font-size: 14px;
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
}

/* Transition Effects */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.4s ease;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}
.slide-fade-leave-active {
  position: absolute; /* Needed for smooth cross-fade/slide out */
}

/* 欢迎横幅 styled as before */
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

/* 统计卡片 styled as before */
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

@media (max-width: 768px) {
  .announcement-board {
    grid-template-columns: 36px 1fr 36px;
    padding: 0 12px;
    height: 220px;
  }

  .carousel-nav {
    width: 36px;
    height: 36px;
    border-radius: 10px;
  }

  .carousel-date {
    right: 18px;
  }

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
}
</style>