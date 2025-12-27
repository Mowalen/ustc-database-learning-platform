<template>
  <div class="dashboard">
    <section class="hero">
      <div>
        <h2>你好，{{ auth.user?.full_name || auth.user?.username }}</h2>
        <p>
          这里是你的教学与学习指挥台，集中查看课程、作业、成绩和公告动态。
        </p>
      </div>
      <div class="hero__tag">{{ auth.roleLabel }}模式</div>
    </section>

    <section class="stats">
      <el-card v-for="stat in visibleStats" :key="stat.label" class="stat-card">
        <div class="stat-card__label">{{ stat.label }}</div>
        <div class="stat-card__value">{{ stat.value }}</div>
        <div class="stat-card__desc">{{ stat.desc }}</div>
      </el-card>
    </section>

    <section class="actions">
      <el-card class="action-card">
        <h3>快速入口</h3>
        <div class="action-grid">
          <RouterLink class="action-item" to="/courses">
            <strong>课程管理</strong>
            <span>查看课程列表与详情</span>
          </RouterLink>
          <RouterLink class="action-item" to="/tasks">
            <strong>作业与考试</strong>
            <span>安排与提交任务</span>
          </RouterLink>
          <RouterLink class="action-item" to="/scores">
            <strong>成绩反馈</strong>
            <span>追踪评分与排名</span>
          </RouterLink>
          <RouterLink class="action-item" to="/announcements">
            <strong>公告看板</strong>
            <span>获取系统最新通知</span>
          </RouterLink>
        </div>
      </el-card>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { courseApi, enrollmentApi, scoreApi, adminApi } from "@/services/api";

const auth = useAuthStore();
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
    return stats.value.filter((stat) => stat.label !== "我的选课");
  }
  return stats.value;
});

const loadStats = async () => {
  const courses = await courseApi.listCourses();
  stats.value[0].value = String(courses.length);

  const announcements = await adminApi.listAnnouncements();
  stats.value[3].value = String(announcements.length);

  if (auth.roleId === 1 && auth.user) {
    const enrollments = await enrollmentApi.myEnrollments(auth.user.id);
    stats.value[1].value = String(enrollments.length);

    const scores = await scoreApi.myScores(auth.user.id);
    const pending = scores.filter((score) => !score.score).length;
    stats.value[2].value = String(pending);
  }

  if (auth.roleId === 2) {
    stats.value[1].value = "-";
    stats.value[2].value = "查看课程评分";
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
  gap: 24px;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.15), rgba(209, 143, 59, 0.15));
  border-radius: 20px;
}

.hero h2 {
  font-family: var(--font-display);
  font-size: 26px;
  margin-bottom: 8px;
}

.hero p {
  color: var(--color-ink-muted);
}

.hero__tag {
  background: var(--color-surface);
  padding: 8px 14px;
  border-radius: 999px;
  font-weight: 600;
  color: var(--color-teal);
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  background: var(--color-surface);
}

.stat-card__label {
  color: var(--color-ink-muted);
  font-size: 13px;
}

.stat-card__value {
  font-size: 24px;
  font-weight: 700;
  margin: 8px 0;
}

.stat-card__desc {
  color: var(--color-ink-muted);
  font-size: 12px;
}

.action-card h3 {
  font-family: var(--font-display);
  margin-bottom: 16px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.action-item {
  border-radius: 16px;
  padding: 16px;
  background: rgba(31, 111, 109, 0.1);
  border: 1px solid rgba(31, 111, 109, 0.2);
}

.action-item strong {
  display: block;
  margin-bottom: 6px;
}

.action-item span {
  font-size: 12px;
  color: var(--color-ink-muted);
}
</style>
