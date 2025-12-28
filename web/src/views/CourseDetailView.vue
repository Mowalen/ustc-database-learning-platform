<template>
  <div class="course-detail" v-loading="loading">
    <div class="course-banner">
      <el-tag class="course-banner__category" effect="light">
        {{ course?.category?.name || "未分类" }}
      </el-tag>
      <div class="course-banner__content">
        <h2>{{ course?.title }}</h2>
        <p>{{ course?.description || "暂无课程简介" }}</p>
      </div>
      <div class="course-banner__actions" v-if="isStudent">
        <el-button
          :type="isEnrolled ? 'danger' : 'success'"
          @click="toggleEnroll"
        >
          {{ isEnrolled ? "退课" : "选课" }}
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="章节内容" name="sections">
        <div class="section-header">
          <p>课程章节与学习资源一览。</p>
          <el-button v-if="isCourseOwner" type="primary" @click="openSectionDialog()">
            新建章节
          </el-button>
        </div>
        <div class="sections-list table-wrap">
          <el-table
            :data="sectionTree"
            row-key="unique_key"
            :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
            default-expand-all
            style="width: 100%"
          >
            <el-table-column label="序号" min-width="80">
              <template #default="scope">
                <span v-if="scope.row.type === 'section'">{{ scope.row.order_index }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="章节标题" min-width="200">
               <template #default="scope">
                 <div class="tree-title-cell">
                   <template v-if="scope.row.type === 'section'">
                     <span>{{ scope.row.title }}</span>
                   </template>
                   <template v-else-if="scope.row.type === 'video'">
                     <el-icon class="tree-icon video-icon"><VideoPlay /></el-icon>
                     <span>{{ scope.row.title }}</span>
                   </template>
                   <template v-else-if="scope.row.type === 'material'">
                     <el-icon class="tree-icon material-icon"><Folder /></el-icon>
                     <span>{{ scope.row.title }}</span>
                   </template>
                 </div>
               </template>
            </el-table-column>

            <el-table-column label="内容摘要" min-width="250">
              <template #default="scope">
                <div v-if="scope.row.type === 'section'" class="truncate-text" :title="scope.row.content">
                  {{ scope.row.content || '-' }}
                </div>
                <div v-else class="status-text">
                  <el-tag v-if="scope.row.url" type="success" size="small" effect="plain">已上传</el-tag>
                  <el-tag v-else type="info" size="small" effect="plain">暂无</el-tag>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" min-width="180">
              <template #default="scope">
                <template v-if="scope.row.type === 'section'">
                  <el-button size="small" @click="viewSection(scope.row.raw)">详情</el-button>
                  <el-button v-if="isCourseOwner" size="small" @click="openSectionDialog(scope.row.raw)">编辑</el-button>
                  <el-button v-if="isCourseOwner" size="small" type="danger" plain @click="deleteSection(scope.row.raw)">删除</el-button>
                </template>
                <template v-else>
                  <el-button 
                    v-if="scope.row.type === 'video' && scope.row.url" 
                    size="small" 
                    type="primary" 
                    plain
                    @click="openVideo(scope.row.url)"
                  >
                    播放
                  </el-button>
                  <el-button 
                    v-if="scope.row.type === 'material' && scope.row.url" 
                    size="small" 
                    type="primary" 
                    plain
                    @click="downloadMaterial(scope.row.url)"
                  >
                    下载
                  </el-button>
                </template>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="作业" name="assignments">
        <div class="section-header">
          <p>课程作业列表与提交情况。</p>
          <el-button v-if="isCourseOwner" type="primary" @click="openTaskDialog('assignment')">
            发布作业
          </el-button>
        </div>
        <div class="table-wrap">
          <el-table :data="assignments" style="width: 100%">
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="deadline" label="截止时间" min-width="180">
              <template #default="scope">
                {{ formatDate(scope.row.deadline) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="200">
              <template #default="scope">
                <el-button size="small" @click="viewTask(scope.row)">查看</el-button>
                <el-button
                  v-if="isStudent"
                  size="small"
                  type="success"
                  plain
                  @click="openSubmit(scope.row)"
                >
                  提交
                </el-button>
                <el-button
                  v-if="isCourseOwner"
                  size="small"
                  type="primary"
                  plain
                  @click="openSubmissions(scope.row)"
                >
                  查看提交
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="考试" name="exams">
        <div class="section-header">
          <p>课程考试安排与评分。</p>
          <el-button v-if="isCourseOwner" type="primary" @click="openTaskDialog('exam')">
            发布考试
          </el-button>
        </div>
        <div class="table-wrap">
          <el-table :data="exams" style="width: 100%">
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="deadline" label="截止时间" min-width="180">
              <template #default="scope">
                {{ formatDate(scope.row.deadline) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="200">
              <template #default="scope">
                <el-button size="small" @click="viewTask(scope.row)">查看</el-button>
                <el-button
                  v-if="isStudent"
                  size="small"
                  type="success"
                  plain
                  @click="openSubmit(scope.row)"
                >
                  提交
                </el-button>
                <el-button
                  v-if="isCourseOwner"
                  size="small"
                  type="primary"
                  plain
                  @click="openSubmissions(scope.row)"
                >
                  查看提交
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane v-if="isCourseOwner" label="学生名单" name="students">
        <div class="table-wrap">
          <el-table :data="students" style="width: 100%">
            <el-table-column prop="student.id" label="学生 ID" min-width="100" />
            <el-table-column prop="student.username" label="用户名" min-width="150" />
            <el-table-column prop="student.full_name" label="姓名" min-width="150" />
            <el-table-column label="状态" min-width="100">
              <template #default="scope">
                {{ scope.row.status === "active" ? "在读" : "退课" }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="sectionDialog" :title="sectionDialogTitle" width="520px">
      <el-form :model="sectionForm" label-position="top">
        <el-form-item label="章节标题">
          <el-input v-model="sectionForm.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="sectionForm.content" type="textarea" />
        </el-form-item>
        <el-form-item label="课件 URL">
          <el-input v-model="sectionForm.material_url" />
        </el-form-item>
        <el-form-item label="上传课件">
          <el-upload
            :show-file-list="false"
            :http-request="handleMaterialUpload"
            accept=".ppt,.pptx,.pdf"
          >
            <el-button :loading="uploadingMaterial" type="primary" plain>
              上传课件文件
            </el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="视频 URL">
          <el-input v-model="sectionForm.video_url" />
        </el-form-item>
        <el-form-item label="上传视频">
          <el-upload
            :show-file-list="false"
            :http-request="handleVideoUpload"
            accept="video/*"
          >
            <el-button :loading="uploadingVideo" type="primary" plain>
              上传视频文件
            </el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="sectionForm.order_index" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sectionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSection">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="sectionInfoDialog" title="章节详情" width="600px">
      <div class="section-detail">
        <h3>{{ activeSection?.title }}</h3>
        
        <div class="section-detail__content">
           <p v-if="activeSection?.content" style="white-space: pre-wrap;">{{ activeSection?.content }}</p>
           <p v-else class="text-muted">暂无内容摘要</p>
        </div>

        <div class="section-detail__resources" v-if="activeSection?.material_url || activeSection?.video_url">
          <h4>学习资源</h4>
          <div class="resource-links">
            <a v-if="activeSection?.material_url" :href="activeSection?.material_url" target="_blank" class="resource-item">
              <el-icon><Document /></el-icon>
              <span>课件资料</span>
            </a>
            <a v-if="activeSection?.video_url" :href="activeSection?.video_url" target="_blank" class="resource-item">
               <el-icon><VideoPlay /></el-icon>
               <span>教学视频</span>
            </a>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="sectionInfoDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="taskDialog" title="发布任务" width="520px">
      <el-form :model="taskForm" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="taskForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="taskForm.type" placeholder="选择类型">
            <el-option label="作业" value="assignment" />
            <el-option label="考试" value="exam" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="taskForm.deadline"
            type="datetime"
            placeholder="选择时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">发布</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="submitDialog" title="提交任务" width="520px">
      <el-form :model="submitForm" label-position="top">
        <el-form-item label="答案内容">
          <el-input v-model="submitForm.answer_text" type="textarea" />
        </el-form-item>
        <el-form-item label="附件 URL">
          <el-input v-model="submitForm.file_url" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTask">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="taskInfoDialog" title="任务详情" width="520px">
      <div class="task-detail">
        <h3>{{ activeTask?.title }}</h3>
        <p>{{ activeTask?.description || "暂无描述" }}</p>
        <div class="task-detail__meta">
          <span>类型：{{ formatTaskType(activeTask?.type) }}</span>
          <span>截止：{{ formatDate(activeTask?.deadline) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="taskInfoDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="submissionsDialog" title="提交记录" width="760px">
      <el-table :data="submissions" style="width: 100%">
        <el-table-column prop="student.username" label="学生" min-width="120" />
        <el-table-column prop="answer_text" label="答案" min-width="200" />
        <el-table-column label="附件" min-width="100">
          <template #default="scope">
            <a v-if="scope.row.file_url" :href="scope.row.file_url" target="_blank">查看</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分数" min-width="80">
          <template #default="scope">
            {{ scope.row.score ?? "-" }}
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="100">
          <template #default="scope">
            {{ formatStatus(scope.row.status) }}
          </template>
        </el-table-column>
        <el-table-column label="评分时间" min-width="160">
          <template #default="scope">
            {{ formatDate(scope.row.graded_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="100">
          <template #default="scope">
            <el-button size="small" @click="openGrade(scope.row)">评分</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="submissionsDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="gradeDialog" title="评分" width="420px">
      <el-form :model="gradeForm" label-position="top">
        <el-form-item label="分数">
          <el-input-number v-model="gradeForm.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="gradeForm.feedback" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gradeDialog = false">取消</el-button>
        <el-button type="primary" @click="submitGrade">提交评分</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="videoPlayerDialog" title="视频播放" width="800px" destroy-on-close>
      <div class="video-container">
        <video 
          v-if="playVideoUrl" 
          :src="playVideoUrl" 
          controls 
          autoplay 
          style="width: 100%; max-height: 600px;"
        >
          Your browser does not support the video tag.
        </video>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, type UploadRequestOptions } from "element-plus";
import {
  courseApi,
  sectionApi,
  taskApi,
  enrollmentApi,
  uploadApi,
} from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { Course, Section, Task, EnrollmentWithStudent, SubmissionWithStudent } from "@/types";
import { ArrowRight, Document, VideoPlay, Folder, Download, CaretRight } from "@element-plus/icons-vue";

const auth = useAuthStore();
const route = useRoute();
const courseId = Number(route.params.id);

const loading = ref(false);
const course = ref<Course | null>(null);
const sections = ref<Section[]>([]);
const tasks = ref<Task[]>([]);
const students = ref<EnrollmentWithStudent[]>([]);
const activeTab = ref("sections");

const sectionTree = computed(() => {
  return sections.value.map(section => ({
    id: section.id,
    unique_key: `section_${section.id}`,
    title: section.title,
    order_index: section.order_index,
    content: section.content,
    type: 'section',
    raw: section,
    children: [
      {
        unique_key: `video_${section.id}`,
        title: '教学视频',
        type: 'video',
        url: section.video_url,
        parent: section
      },
      {
        unique_key: `material_${section.id}`,
        title: '课件资料',
        type: 'material',
        url: section.material_url,
        parent: section
      }
    ]
  }));
});

const assignments = computed(() => tasks.value.filter(t => t.type === 'assignment'));
const exams = computed(() => tasks.value.filter(t => t.type === 'exam'));

const sectionDialog = ref(false);
const sectionDialogTitle = ref("新建章节");
const editingSectionId = ref<number | null>(null);

const taskDialog = ref(false);
const submitDialog = ref(false);
const taskInfoDialog = ref(false);
const activeTask = ref<Task | null>(null);
const submissionsDialog = ref(false);
const submissions = ref<SubmissionWithStudent[]>([]);
const gradeDialog = ref(false);
const activeSubmissionId = ref<number | null>(null);

const videoPlayerDialog = ref(false);
const playVideoUrl = ref("");

const sectionInfoDialog = ref(false);
const activeSection = ref<Section | null>(null);
const uploadingMaterial = ref(false);
const uploadingVideo = ref(false);

const sectionForm = reactive({
  title: "",
  content: "",
  material_url: "",
  video_url: "",
  order_index: 0,
});

const taskForm = reactive({
  title: "",
  description: "",
  type: "assignment" as "assignment" | "exam",
  deadline: "",
});

const submitForm = reactive({
  answer_text: "",
  file_url: "",
});
const gradeForm = reactive({
  score: 0,
  feedback: "",
});

const isTeacher = computed(() => auth.roleId === 2);
const isStudent = computed(() => auth.roleId === 1);
const isEnrolled = ref(false);
const isCourseOwner = computed(
  () => isTeacher.value && course.value?.teacher_id === auth.user?.id
);

const loadData = async () => {
  loading.value = true;
  try {
    course.value = await courseApi.getCourse(courseId);
    sections.value = (await sectionApi.listSections(courseId)).sort(
      (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0)
    );
    tasks.value = await taskApi.listTasks(courseId);
    if (isCourseOwner.value) {
      students.value = await enrollmentApi.courseStudents(courseId);
    }
    if (isStudent.value && auth.user) {
      const enrollments = await enrollmentApi.myEnrollments(auth.user.id);
      isEnrolled.value = enrollments.some((enroll) => enroll.course_id === courseId);
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载课程信息失败");
  } finally {
    loading.value = false;
  }
};

const openSectionDialog = (section?: Section) => {
  if (section) {
    sectionDialogTitle.value = "编辑章节";
    editingSectionId.value = section.id;
    Object.assign(sectionForm, {
      title: section.title,
      content: section.content || "",
      material_url: section.material_url || "",
      video_url: section.video_url || "",
      order_index: section.order_index ?? 0,
    });
  } else {
    sectionDialogTitle.value = "新建章节";
    editingSectionId.value = null;
    Object.assign(sectionForm, {
      title: "",
      content: "",
      material_url: "",
      video_url: "",
      order_index: 0,
    });
  }
  sectionDialog.value = true;
};

const saveSection = async () => {
  try {
    if (editingSectionId.value) {
      await sectionApi.updateSection(editingSectionId.value, {
        title: sectionForm.title,
        content: sectionForm.content || null,
        material_url: sectionForm.material_url || null,
        video_url: sectionForm.video_url || null,
        order_index: sectionForm.order_index,
      });
      ElMessage.success("章节已更新");
    } else {
      await sectionApi.createSection(courseId, {
        course_id: courseId,
        title: sectionForm.title,
        content: sectionForm.content || undefined,
        material_url: sectionForm.material_url || undefined,
        video_url: sectionForm.video_url || undefined,
        order_index: sectionForm.order_index,
      });
      ElMessage.success("章节已创建");
    }
    sectionDialog.value = false;
    sections.value = (await sectionApi.listSections(courseId)).sort(
      (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0)
    );
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "保存章节失败");
  }
};

const deleteSection = async (section: Section) => {
  try {
    await sectionApi.deleteSection(section.id);
    ElMessage.success("章节已删除");
    sections.value = sections.value.filter((item) => item.id !== section.id);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "删除失败");
  }
};

const viewSection = (section: Section) => {
  activeSection.value = section;
  sectionInfoDialog.value = true;
};

const openVideo = (url: string) => {
  playVideoUrl.value = url;
  videoPlayerDialog.value = true;
};

const downloadMaterial = (url: string) => {
  window.open(url, '_blank');
};

const handleMaterialUpload = async (options: UploadRequestOptions) => {
  const file = options.file as File;
  uploadingMaterial.value = true;
  try {
    const data = await uploadApi.uploadFile(file);
    sectionForm.material_url = data.url;
    ElMessage.success("课件上传成功");
    options.onSuccess?.(data, file);
  } catch (error: any) {
    options.onError?.(error);
    ElMessage.error(error?.response?.data?.detail || "课件上传失败");
  } finally {
    uploadingMaterial.value = false;
  }
};

const handleVideoUpload = async (options: UploadRequestOptions) => {
  const file = options.file as File;
  uploadingVideo.value = true;
  try {
    const data = await uploadApi.uploadFile(file);
    sectionForm.video_url = data.url;
    ElMessage.success("视频上传成功");
    options.onSuccess?.(data, file);
  } catch (error: any) {
    options.onError?.(error);
    ElMessage.error(error?.response?.data?.detail || "视频上传失败");
  } finally {
    uploadingVideo.value = false;
  }
};

const openTaskDialog = (type: "assignment" | "exam" = "assignment") => {
  Object.assign(taskForm, {
    title: "",
    description: "",
    type: type,
    deadline: "",
  });
  taskDialog.value = true;
};

const saveTask = async () => {
  if (!auth.user) return;
  try {
    await taskApi.createTask(courseId, {
      teacher_id: auth.user.id,
      title: taskForm.title,
      description: taskForm.description || undefined,
      type: taskForm.type,
      deadline: taskForm.deadline || undefined,
    });
    ElMessage.success("任务已发布");
    taskDialog.value = false;
    tasks.value = await taskApi.listTasks(courseId);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "发布任务失败");
  }
};

const viewTask = (task: Task) => {
  activeTask.value = task;
  taskInfoDialog.value = true;
};

const openSubmissions = async (task: Task) => {
  try {
    activeTask.value = task;
    submissions.value = await taskApi.listSubmissions(task.id);
    submissionsDialog.value = true;
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载提交记录失败");
  }
};

const openGrade = (submission: SubmissionWithStudent) => {
  activeSubmissionId.value = submission.id;
  gradeForm.score = Number(submission.score ?? 0);
  gradeForm.feedback = submission.feedback || "";
  gradeDialog.value = true;
};

const submitGrade = async () => {
  if (!activeSubmissionId.value) return;
  try {
    await taskApi.gradeSubmission(activeSubmissionId.value, {
      score: gradeForm.score,
      feedback: gradeForm.feedback || undefined,
    });
    ElMessage.success("评分已提交");
    gradeDialog.value = false;
    if (activeTask.value) {
      submissions.value = await taskApi.listSubmissions(activeTask.value.id);
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "评分失败");
  }
};

const openSubmit = (task: Task) => {
  activeTask.value = task;
  Object.assign(submitForm, { answer_text: "", file_url: "" });
  submitDialog.value = true;
};

const submitTask = async () => {
  if (!auth.user || !activeTask.value) return;
  try {
    await taskApi.submitTask(activeTask.value.id, {
      student_id: auth.user.id,
      answer_text: submitForm.answer_text || undefined,
      file_url: submitForm.file_url || undefined,
    });
    ElMessage.success("提交成功");
    submitDialog.value = false;
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "提交失败");
  }
};

const toggleEnroll = async () => {
  if (!auth.user) return;
  try {
    if (isEnrolled.value) {
      await enrollmentApi.drop(courseId, auth.user.id);
      isEnrolled.value = false;
      ElMessage.success("已退课");
    } else {
      await enrollmentApi.enroll(courseId, auth.user.id);
      isEnrolled.value = true;
      ElMessage.success("选课成功");
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "操作失败");
  }
};

onMounted(() => {
  loadData().catch(() => undefined);
});
</script>

<style scoped>
.course-detail {
  display: grid;
  gap: 20px;
  min-width: 0;
}

.course-banner {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 32px 28px;
  background: rgba(209, 143, 59, 0.12);
  border-radius: 18px;
  min-width: 0;
}

.course-banner__category {
  position: absolute;
  top: 20px;
  right: 28px;
  font-weight: 600;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.15), rgba(209, 143, 59, 0.15));
  color: var(--color-teal);
  border: 1px solid rgba(31, 111, 109, 0.2);
  font-size: 14px;
  padding: 6px 16px;
  z-index: 1;
}

.course-banner__content {
  min-width: 0;
  padding-right: 120px;
}

.course-banner__content h2 {
  font-family: var(--font-display);
  font-size: 28px;
  margin-bottom: 12px;
  overflow-wrap: anywhere;
  color: var(--color-ink);
}

.course-banner__content p {
  color: var(--color-ink-muted);
  overflow-wrap: anywhere;
  font-size: 15px;
  line-height: 1.6;
}

.course-banner__actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-start;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header p {
  color: var(--color-ink-muted);
}

.course-detail :deep(.el-tabs) {
  width: 100%;
  min-width: 0;
}

.course-detail :deep(.el-tabs__content),
.course-detail :deep(.el-tab-pane) {
  min-width: 0;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
}

.table-wrap :deep(.el-table) {
  width: 100%;
}

.link-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 12px;
}

.link-group a {
  color: var(--color-teal);
}

.task-detail h3 {
  font-family: var(--font-display);
  margin-bottom: 8px;
}

.task-detail p {
  color: var(--color-ink-muted);
  margin-bottom: 16px;
}

.task-detail__meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--color-ink-muted);
}


.section-detail h3 {
  font-family: var(--font-display);
  font-size: 20px;
  margin-bottom: 16px;
  color: var(--color-ink);
}

.sections-list {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.section-title-row {
  display: flex;
  align-items: center;
  flex: 1;
  width: 100%;
}

.section-index {
  font-weight: 600;
  margin-right: 12px;
  color: var(--color-teal);
  background: rgba(31, 111, 109, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.section-name {
  font-weight: 600;
  color: var(--color-ink);
  font-size: 15px;
}

.section-actions {
  margin-left: auto;
  margin-right: 12px;
}

.section-content {
  padding: 10px 16px;
  background: #fafafa;
}

.resource-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #eee;
  background: #fff;
  margin-bottom: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.resource-row:last-child {
  margin-bottom: 0;
}

.resource-row.clickable {
  cursor: pointer;
}

.resource-row.clickable:hover {
  background: #f0fdfc;
  transform: translateX(4px);
}

.resource-icon {
  font-size: 20px;
  color: #999;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 50%;
}

.resource-icon.video-icon {
  color: #fff;
  background: #409eff; /* Or teal */
}

.resource-icon.pdf-icon {
  color: #fff;
  background: #e6a23c;
}

.resource-info {
  flex: 1;
}

.resource-label {
  display: block;
  font-weight: 500;
  color: var(--color-ink);
  margin-bottom: 2px;
}

.resource-sub {
  font-size: 12px;
  color: #999;
}

.resource-desc {
  font-size: 13px;
  color: #666;
  margin: 0;
}

.action-icon {
  color: #ccc;
}



.section-detail__content {
  margin-bottom: 24px;
  line-height: 1.6;
  color: var(--color-ink);
}

.section-detail__resources h4 {
  font-size: 16px;
  margin-bottom: 12px;
  color: var(--color-ink);
}

.resource-links {
  display: flex;
  gap: 16px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(31, 111, 109, 0.05);
  border-radius: 8px;
  color: var(--color-teal);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.resource-item:hover {
  background: rgba(31, 111, 109, 0.1);
  transform: translateY(-2px);
}

.text-muted {
  color: var(--color-ink-muted);
  font-style: italic;
}

.tree-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tree-icon {
  font-size: 16px;
  color: #999;
}

.tree-icon.video-icon {
  color: #409eff;
}

.tree-icon.material-icon {
  color: #e6a23c;
}

.truncate-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-ink-muted);
}
</style>
```
