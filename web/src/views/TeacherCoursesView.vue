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
        <el-button type="primary" @click="openCreate">
          新建课程
        </el-button>
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
          <p class="course-card__description">{{ course.description || "暂无课程简介" }}</p>
        </div>
        
        <div class="course-card__footer">
          <div class="course-card__actions">
            <div class="course-card__actions-row">
              <el-button 
                size="default" 
                type="primary" 
                @click="viewDetail(course.id)"
              >
                管理课程
              </el-button>
              <el-button
                size="default"
                @click="openEdit(course)"
              >
                编辑
              </el-button>
            </div>
            <div class="course-card__actions-row" style="margin-top: 10px;">
              <el-button
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
        </div>
      </el-card>

      <div v-if="filteredCourses.length === 0" class="empty-state">
        <p>您还没有创建任何课程。</p>
        <el-button type="primary" @click="openCreate">立即创建课程</el-button>
      </div>
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
        <el-form-item label="课程标题" required>
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { courseApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { Course, CourseCategory } from "@/types";

const auth = useAuthStore();
const router = useRouter();
const courses = ref<Course[]>([]);
const categories = ref<CourseCategory[]>([]);
const selectedCategory = ref<number | null>(null);
const currentPage = ref(1);
const pageSize = ref(8);

const dialogVisible = ref(false);
const dialogTitle = ref("新建课程");
const editCourseId = ref<number | null>(null);

const courseForm = reactive({
  title: "",
  description: "",
  cover_url: "",
  category_id: null as number | null,
});

const myCourses = computed(() => {
  if (!auth.user) return [];
  // Filter courses taught by the current user
  return courses.value.filter(c => c.teacher_id === auth.user?.id);
});

const filteredCourses = computed(() => {
  if (!selectedCategory.value) return myCourses.value;
  return myCourses.value.filter((course) => course.category_id === selectedCategory.value);
});

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredCourses.value.slice(start, end);
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

const refresh = async () => {
  currentPage.value = 1; 
  await Promise.all([loadCourses(), loadCategories()]);
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
  if (!courseForm.title) {
    ElMessage.warning("请填写课程标题");
    return;
  }
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

const viewDetail = (courseId: number) => {
  router.push({ name: "course-detail", params: { id: courseId } });
};

const handleDelete = async (course: Course) => {
  try {
    await courseApi.deleteCourse(course.id);
    ElMessage.success("课程已删除");
    await loadCourses();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "删除失败");
  }
};

onMounted(() => {
  refresh().catch(() => undefined);
});

watch(selectedCategory, () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.courses {
  display: flex;
  flex-direction: column;
  gap: 24px;
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
  min-height: 80px;
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
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-card__footer {
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.course-card__actions-row {
  display: flex;
  gap: 10px;
}

.course-card__actions-row .el-button {
  flex: 1;
}

.delete-button {
  width: 100%;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  background: var(--color-surface);
  border-radius: 12px;
  border: 1px dashed var(--color-border);
}

.empty-state p {
  color: var(--color-ink-muted);
  margin-bottom: 20px;
}
</style>
