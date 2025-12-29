import axios, { AxiosInstance } from "axios";
import type {
  Announcement,
  Course,
  CourseCategory,
  Enrollment,
  EnrollmentWithCourse,
  EnrollmentWithStudent,
  Score,
  Section,
  Submission,
  SubmissionWithStudent,
  Task,
  TokenResponse,
  User,
} from "@/types";

const baseURL =
  import.meta.env.VITE_API_BASE_URL || "http://114.214.188.108:9000/api/v1";

const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  async login(username: string, password: string): Promise<TokenResponse> {
    const form = new URLSearchParams();
    form.set("username", username);
    form.set("password", password);
    const { data } = await api.post<TokenResponse>("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return data;
  },
  async register(payload: {
    username: string;
    password: string;
    email?: string;
    full_name?: string;
    role_id: number;
  }): Promise<User> {
    const { data } = await api.post<User>("/auth/register", payload);
    return data;
  },
  async requestPasswordReset(email: string): Promise<{ message: string; code?: string }> {
    const { data } = await api.post<{ message: string; code?: string }>(
      "/auth/password-reset/request",
      { email }
    );
    return data;
  },
  async confirmPasswordReset(payload: {
    email: string;
    code: string;
    new_password: string;
  }): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>(
      "/auth/password-reset/confirm",
      payload
    );
    return data;
  },
};

export const userApi = {
  async me(): Promise<User> {
    const { data } = await api.get<User>("/users/me");
    return data;
  },
  async verifyPassword(password: string): Promise<boolean> {
    await api.post("/users/verify-password", { password });
    return true;
  },
  async updateMe(payload: {
    full_name?: string;
    password?: string;
    avatar_url?: string;
  }): Promise<User> {
    const { data } = await api.put<User>("/users/me", payload);
    return data;
  },
};

export const courseApi = {
  async listCourses(): Promise<Course[]> {
    const { data } = await api.get<Course[]>("/courses/");
    return data;
  },
  async getCourse(id: number): Promise<Course> {
    const { data } = await api.get<Course>(`/courses/${id}`);
    return data;
  },
  async createCourse(payload: {
    title: string;
    description?: string;
    cover_url?: string;
    category_id?: number;
  }): Promise<Course> {
    const { data } = await api.post<Course>("/courses/", payload);
    return data;
  },
  async updateCourse(id: number, payload: Partial<Course>): Promise<Course> {
    const { data } = await api.put<Course>(`/courses/${id}`, payload);
    return data;
  },
  async deleteCourse(id: number): Promise<Course> {
    const { data } = await api.delete<Course>(`/courses/${id}`);
    return data;
  },
  async listCategories(): Promise<CourseCategory[]> {
    const { data } = await api.get<CourseCategory[]>("/courses/categories/");
    return data;
  },
  async createCategory(payload: {
    name: string;
    description?: string;
  }): Promise<CourseCategory> {
    const { data } = await api.post<CourseCategory>(
      "/courses/categories/",
      payload
    );
    return data;
  },
};

export const sectionApi = {
  async listSections(courseId: number): Promise<Section[]> {
    const { data } = await api.get<Section[]>(
      `/courses/${courseId}/sections`
    );
    return data;
  },
  async createSection(courseId: number, payload: {
    course_id: number;
    title: string;
    content?: string;
    material_url?: string;
    video_url?: string;
    order_index?: number;
  }): Promise<Section> {
    const { data } = await api.post<Section>(
      `/courses/${courseId}/sections`,
      payload
    );
    return data;
  },
  async updateSection(id: number, payload: Partial<Section>): Promise<Section> {
    const { data } = await api.put<Section>(`/sections/${id}`, payload);
    return data;
  },
  async deleteSection(id: number): Promise<Section> {
    const { data } = await api.delete<Section>(`/sections/${id}`);
    return data;
  },
};

export const enrollmentApi = {
  async enroll(courseId: number, studentId: number): Promise<Enrollment> {
    const { data } = await api.post<Enrollment>(
      `/courses/${courseId}/enroll`,
      { student_id: studentId }
    );
    return data;
  },
  async drop(courseId: number, studentId: number): Promise<Enrollment> {
    const { data } = await api.post<Enrollment>(`/courses/${courseId}/drop`, {
      student_id: studentId,
    });
    return data;
  },
  async myEnrollments(studentId: number): Promise<EnrollmentWithCourse[]> {
    const { data } = await api.get<EnrollmentWithCourse[]>("/me/enrollments", {
      params: { student_id: studentId },
    });
    return data;
  },
  async courseStudents(courseId: number): Promise<EnrollmentWithStudent[]> {
    const { data } = await api.get<EnrollmentWithStudent[]>(
      `/courses/${courseId}/students`
    );
    return data;
  },
};

export const taskApi = {
  async createTask(courseId: number, payload: {
    teacher_id: number;
    title: string;
    description?: string;
    file_url?: string;
    type: "assignment" | "exam";
    deadline?: string;
  }): Promise<Task> {
    const { data } = await api.post<Task>(
      `/courses/${courseId}/tasks`,
      payload
    );
    return data;
  },
  async listTasks(courseId: number): Promise<Task[]> {
    const { data } = await api.get<Task[]>(`/courses/${courseId}/tasks`);
    return data;
  },
  async getTask(taskId: number): Promise<Task> {
    const { data } = await api.get<Task>(`/tasks/${taskId}`);
    return data;
  },
  async updateTask(taskId: number, payload: {
    title?: string;
    description?: string;
    file_url?: string;
    type?: "assignment" | "exam";
    deadline?: string;
  }): Promise<Task> {
    const { data } = await api.put<Task>(`/tasks/${taskId}`, payload);
    return data;
  },
  async deleteTask(taskId: number): Promise<void> {
    await api.delete(`/tasks/${taskId}`);
  },
  async submitTask(taskId: number, payload: {
    student_id: number;
    answer_text?: string;
    file_url?: string;
  }): Promise<Submission> {
    const { data } = await api.post<Submission>(
      `/tasks/${taskId}/submit`,
      payload
    );
    return data;
  },
  async gradeSubmission(submissionId: number, payload: {
    score: number;
    feedback?: string;
    status?: "graded" | "submitted" | "late";
  }): Promise<Submission> {
    const { data } = await api.put<Submission>(
      `/submissions/${submissionId}/grade`,
      payload
    );
    return data;
  },
  async listSubmissions(taskId: number): Promise<SubmissionWithStudent[]> {
    const { data } = await api.get<SubmissionWithStudent[]>(
      `/tasks/${taskId}/submissions`
    );
    return data;
  },
  async getMySubmissions(courseId: number): Promise<Submission[]> {
    const { data } = await api.get<Submission[]>(`/courses/${courseId}/my-submissions`);
    return data;
  },
};

export const scoreApi = {
  async myScores(studentId: number): Promise<Score[]> {
    const { data } = await api.get<Score[]>("/me/scores", {
      params: { student_id: studentId },
    });
    return data;
  },
  async courseScores(courseId: number): Promise<Score[]> {
    const { data } = await api.get<Score[]>(`/courses/${courseId}/scores`);
    return data;
  },
  async exportCourseScores(courseId: number): Promise<string> {
    const { data } = await api.get(`/courses/${courseId}/scores/export`, {
      responseType: "text",
    });
    return data;
  },
  async getTeacherPendingGradingCount(): Promise<number> {
    const { data } = await api.get<{ count: number }>("/teacher/pending-grading-count");
    return data.count;
  },
};

export const adminApi = {
  async createUser(payload: {
    username: string;
    password: string;
    role_id: number;
    full_name?: string;
    email?: string;
    phone?: string;
    avatar_url?: string;
    is_active?: boolean;
  }): Promise<User> {
    const { data } = await api.post<User>("/admin/users", payload);
    return data;
  },
  async updateUser(userId: number, payload: {
    full_name?: string;
    email?: string;
    phone?: string;
    avatar_url?: string;
    password?: string;
    is_active?: boolean;
    role_id?: number;
  }): Promise<User> {
    const { data } = await api.put<User>(`/admin/users/${userId}`, payload);
    return data;
  },
  async deleteUser(userId: number): Promise<User> {
    const { data } = await api.delete<User>(`/admin/users/${userId}`);
    return data;
  },
  async deactivateCourse(courseId: number): Promise<{ course_id: number; is_active: boolean }> {
    const { data } = await api.delete<{ course_id: number; is_active: boolean }>(
      `/admin/courses/${courseId}`
    );
    return data;
  },
  async listAnnouncements(includeInactive = false): Promise<Announcement[]> {
    const { data } = await api.get<Announcement[]>("/admin/announcements", {
      params: { include_inactive: includeInactive },
    });
    return data;
  },
  async listUsers(params?: {
    skip?: number;
    limit?: number;
    role_id?: number;
    is_active?: boolean;
  }): Promise<User[]> {
    const { data } = await api.get<User[]>("/admin/users", { params });
    return data;
  },
  async createAnnouncement(payload: {
    title: string;
    content: string;
    created_by: number;
    is_active?: boolean;
  }): Promise<Announcement> {
    const { data } = await api.post<Announcement>(
      "/admin/announcements",
      payload
    );
    return data;
  },
  async updateAnnouncement(
    id: number,
    payload: {
      title?: string;
      content?: string;
      is_active?: boolean;
    }
  ): Promise<Announcement> {
    const { data } = await api.put<Announcement>(
      `/admin/announcements/${id}`,
      payload
    );
    return data;
  },
  async deleteAnnouncement(id: number): Promise<Announcement> {
    const { data } = await api.delete<Announcement>(`/admin/announcements/${id}`);
    return data;
  },
};

export const uploadApi = {
  async uploadFile(file: File): Promise<{ url: string; filename: string }> {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await api.post<{ url: string; filename: string }>(
      "/uploads",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    return data;
  },
};

export default api;
