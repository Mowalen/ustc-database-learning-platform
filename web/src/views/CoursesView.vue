<template>
  <div class="courses">
    <div class="courses__header">
      <div class="filter">
      </div>
      <div class="actions">
        <!-- Admin only actions if needed, or removing entirely as requested for "only view" -->
        <el-button v-if="isAdmin" plain @click="openCategory">管理分类</el-button>
      </div>
    </div>

    <div class="course-grid">
      <el-card v-for="course in paginatedCourses" :key="course.id" class="course-card">
        <div class="course-card__header">
          <el-tag class="course-card__category" effect="light">
            {{ categoryName(course) }}
          </el-tag>
          <el-tag 
            :type="course.is_active ? 'success' : 'info'" 
            size="small" 
            effect="plain"
          >
            {{ course.is_active ? "有效" : "已下架" }}
          </el-tag>
        </div>
        
        <div class="course-card__body">
          <h3 class="course-card__title">{{ course.title }}</h3>
          <p class="course-card__description">{{ course.description || "暂无课程简介，请联系教师了解详情。" }}</p>
        </div>
        
        <div class="course-card__footer">
          <div class="course-card__meta">
            <span class="meta-item">
              <span class="meta-label">授课教师</span>
              <span class="meta-value">{{ getTeacherName(course) }}</span>
            </span>
          </div>
          
          <div class="course-card__actions">
            <div class="course-card__actions-row">
              <el-button 
                size="default" 
                type="primary" 
                class="full-width-btn"
                :disabled="isStudent && !enrolledCourseIds.includes(course.id)"
                @click="viewDetail(course.id)"
              >
                查看详情
              </el-button>
              <el-button
                v-if="isStudent"
                size="default"
                :type="enrolledCourseIds.includes(course.id) ? 'danger' : 'success'"
                @click="toggleEnroll(course.id)"
              >
                {{ enrolledCourseIds.includes(course.id) ? "退课" : "选课" }}
              </el-button>
            </div>
            <el-button
              v-if="isAdmin"
              size="default"
              type="danger"
              plain
              class="delete-button"
              @click="handleDelete(course)"
            >
              删除
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <div class="pagination" v-if="filteredCourses.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredCourses.length"
        layout="total, prev, pager, next, jumper"
        background
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="520px"
      append-to-body
    >
      <el-form :model="courseForm" label-position="top">
        <el-form-item label="课程标题">
          <el-input v-model="courseForm.title" />
        </el-form-item>
        <el-form-item label="课程简介">
          <el-input v-model="courseForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="封面 URL">
          <el-input v-model="courseForm.cover_url" placeholder="可选" />
        </el-form-item>
        <el-form-item label="课程分类">
          <el-select v-model="courseForm.category_id" placeholder="选择分类" clearable>
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCourse">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="categoryDialog"
      title="课程分类"
      width="420px"
      append-to-body
    >
      <el-form :model="categoryForm" label-position="top">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="categoryForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCategory">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { courseApi, enrollmentApi, adminApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { Course, CourseCategory } from "@/types";

const auth = useAuthStore();
const router = useRouter();
const courses = ref<Course[]>([]);
const categories = ref<CourseCategory[]>([]);
const selectedCategory = ref<number | null>(null);
const enrolledCourseIds = ref<number[]>([]);
const currentPage = ref(1);
const pageSize = ref(8);

const dialogVisible = ref(false);
const dialogTitle = ref("新建课程");
const editCourseId = ref<number | null>(null);
const categoryDialog = ref(false);

const courseForm = reactive({
  title: "",
  description: "",
  cover_url: "",
  category_id: null as number | null,
});

const categoryForm = reactive({
  name: "",
  description: "",
});

const isTeacher = computed(() => auth.roleId === 2);
const isAdmin = computed(() => auth.roleId === 3);
const isStudent = computed(() => auth.roleId === 1);

const filteredCourses = computed(() => {
  if (!selectedCategory.value) return courses.value;
  return courses.value.filter((course) => course.category_id === selectedCategory.value);
});

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredCourses.value.slice(start, end);
});

const getTeacherName = (course: Course) => {
  if (course.teacher_name) return course.teacher_name;
  const teacher = course.teacher;
  if (teacher) {
    return teacher.full_name || teacher.username || "未设置";
  }
  if (auth.user?.id === course.teacher_id) {
    return auth.user?.full_name || auth.user?.username || "未设置";
  }
  return "未设置";
};

const categoryName = (course: Course) => {
  if (course.category?.name) return course.category.name;
  const found = categories.value.find((cat) => cat.id === course.category_id);
  return found?.name || "未分类";
};

const loadCourses = async () => {
  courses.value = await courseApi.listCourses();
};

const loadCategories = async () => {
  categories.value = await courseApi.listCategories();
};

const loadEnrollments = async () => {
  if (auth.user && auth.roleId === 1) {
    const enrollments = await enrollmentApi.myEnrollments(auth.user.id);
    enrolledCourseIds.value = enrollments.map((enroll) => enroll.course_id);
  }
};

const refresh = async () => {
  currentPage.value = 1; // 刷新时重置到第一页
  await Promise.all([loadCourses(), loadCategories(), loadEnrollments()]);
};

const openCreate = () => {
  dialogTitle.value = "新建课程";
  editCourseId.value = null;
  Object.assign(courseForm, {
    title: "",
    description: "",
    cover_url: "",
    category_id: null,
  });
  dialogVisible.value = true;
};

const openEdit = (course: Course) => {
  dialogTitle.value = "编辑课程";
  editCourseId.value = course.id;
  Object.assign(courseForm, {
    title: course.title,
    description: course.description || "",
    cover_url: course.cover_url || "",
    category_id: course.category_id ?? null,
  });
  dialogVisible.value = true;
};

const submitCourse = async () => {
  try {
    if (editCourseId.value) {
      await courseApi.updateCourse(editCourseId.value, {
        title: courseForm.title,
        description: courseForm.description || null,
        cover_url: courseForm.cover_url || null,
        category_id: courseForm.category_id ?? null,
      });
      ElMessage.success("课程已更新");
    } else {
      await courseApi.createCourse({
        title: courseForm.title,
        description: courseForm.description || undefined,
        cover_url: courseForm.cover_url || undefined,
        category_id: courseForm.category_id ?? undefined,
      });
      ElMessage.success("课程已创建");
    }
    dialogVisible.value = false;
    await loadCourses();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "课程保存失败");
  }
};

const openCategory = () => {
  Object.assign(categoryForm, { name: "", description: "" });
  categoryDialog.value = true;
};

const submitCategory = async () => {
  try {
    await courseApi.createCategory({
      name: categoryForm.name,
      description: categoryForm.description || undefined,
    });
    ElMessage.success("分类已创建");
    categoryDialog.value = false;
    await loadCategories();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "创建分类失败");
  }
};

const toggleEnroll = async (courseId: number) => {
  if (!auth.user) return;
  try {
    if (enrolledCourseIds.value.includes(courseId)) {
      await enrollmentApi.drop(courseId, auth.user.id);
      enrolledCourseIds.value = enrolledCourseIds.value.filter((id) => id !== courseId);
      ElMessage.success("已退课");
    } else {
      await enrollmentApi.enroll(courseId, auth.user.id);
      enrolledCourseIds.value.push(courseId);
      ElMessage.success("选课成功");
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "选课操作失败");
  }
};

const viewDetail = (courseId: number) => {
  router.push({ name: "course-detail", params: { id: courseId } });
};

const canDelete = (course: Course) => {
  if (isAdmin.value) return true;
  return isTeacher.value && auth.user?.id === course.teacher_id;
};

const handleDelete = async (course: Course) => {
  try {
    if (isAdmin.value) {
      await adminApi.deactivateCourse(course.id);
    } else {
      await courseApi.deleteCourse(course.id);
    }
    ElMessage.success("课程已删除");
    await loadCourses();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "删除失败");
  }
};

onMounted(() => {
  refresh().catch(() => undefined);
});

// 监听分类变化，重置到第一页
watch(selectedCategory, () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.courses {
  display: grid;
  gap: 20px;
}

.courses__header {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.filter {
  display: flex;
  gap: 12px;
  align-items: center;
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.course-card {
  transition: all 0.3s ease;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(31, 111, 109, 0.15);
}

.course-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(31, 111, 109, 0.1);
}

.course-card__category {
  font-weight: 600;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.1), rgba(209, 143, 59, 0.1));
  color: var(--color-teal);
  border: none;
}

.course-card__body {
  margin-bottom: 20px;
  min-height: 100px;
}

.course-card__title {
  font-size: 20px;
  font-weight: 700;
  font-family: var(--font-display);
  color: var(--color-ink);
  margin-bottom: 12px;
  line-height: 1.4;
}

.course-card__description {
  color: var(--color-ink-muted);
  font-size: 14px;
  line-height: 1.6;
  min-height: 42px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-card__footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.course-card__meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.meta-label {
  color: var(--color-ink-muted);
  font-weight: 500;
}

.meta-value {
  color: var(--color-ink);
  font-weight: 600;
  background: rgba(31, 111, 109, 0.08);
  padding: 2px 8px;
  border-radius: 6px;
}

.course-card__actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.course-card__actions-row {
  display: flex;
  gap: 10px;
}

.course-card__actions-row .el-button {
  flex: 1;
}

.course-card__actions-row .full-width-btn {
  width: 100%;
}

.course-card__actions .delete-button {
  width: 100%;
}
</style>
