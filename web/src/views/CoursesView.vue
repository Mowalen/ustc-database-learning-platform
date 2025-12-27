<template>
  <div class="courses">
    <div class="courses__header">
      <div class="filter">
        <el-select v-model="selectedCategory" placeholder="全部分类" clearable>
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
        <el-button @click="refresh">刷新</el-button>
      </div>
      <div class="actions">
        <el-button v-if="isTeacher" type="primary" @click="openCreate">
          新建课程
        </el-button>
        <el-button v-if="isTeacher || isAdmin" plain @click="openCategory">管理分类</el-button>
      </div>
    </div>

    <div class="course-grid">
      <el-card v-for="course in filteredCourses" :key="course.id" class="course-card">
        <div class="course-card__head">
          <div>
            <h3>{{ course.title }}</h3>
            <p>{{ course.description || "暂无简介" }}</p>
          </div>
          <el-tag size="small" effect="light">
            {{ categoryName(course) }}
          </el-tag>
        </div>
        <div class="course-card__meta">
          <span>教师 ID：{{ course.teacher_id }}</span>
          <span>状态：{{ course.is_active ? "有效" : "已下架" }}</span>
        </div>
        <div class="course-card__actions">
          <el-button size="small" type="primary" plain @click="viewDetail(course.id)">
            查看详情
          </el-button>
          <el-button
            v-if="isStudent"
            size="small"
            :type="enrolledCourseIds.includes(course.id) ? 'danger' : 'success'"
            plain
            @click="toggleEnroll(course.id)"
          >
            {{ enrolledCourseIds.includes(course.id) ? "退课" : "选课" }}
          </el-button>
          <el-button
            v-if="isTeacher && course.teacher_id === auth.user?.id"
            size="small"
            @click="openEdit(course)"
          >
            编辑
          </el-button>
          <el-button
            v-if="canDelete(course)"
            size="small"
            type="danger"
            plain
            @click="handleDelete(course)"
          >
            删除
          </el-button>
        </div>
      </el-card>
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
import { computed, onMounted, reactive, ref } from "vue";
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

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.course-card h3 {
  font-size: 18px;
  margin-bottom: 6px;
}

.course-card p {
  color: var(--color-ink-muted);
  font-size: 13px;
  min-height: 34px;
}

.course-card__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.course-card__meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-ink-muted);
  margin-bottom: 12px;
}

.course-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
