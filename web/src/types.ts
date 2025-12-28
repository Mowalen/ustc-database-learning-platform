export type RoleId = 1 | 2 | 3;
export type TaskType = "assignment" | "exam";
export type SubmissionStatus = "submitted" | "graded" | "late";

export interface Role {
  id: number;
  name: string;
  description?: string | null;
}

export interface User {
  id: number;
  username: string;
  email?: string | null;
  full_name?: string | null;
  phone?: string | null;
  avatar_url?: string | null;
  role_id: RoleId;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
  role?: Role | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CourseCategory {
  id: number;
  name: string;
  description?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface Course {
  id: number;
  teacher_id: number;
  title: string;
  description?: string | null;
  cover_url?: string | null;
  category_id?: number | null;
  created_at: string;
  updated_at?: string | null;
  is_active: boolean;
  category?: CourseCategory | null;
  teacher?: User | null;
  teacher_name?: string | null;
}

export interface Section {
  id: number;
  course_id: number;
  title: string;
  content?: string | null;
  material_url?: string | null;
  video_url?: string | null;
  order_index?: number | null;
  created_at: string;
  updated_at?: string | null;
}

export interface Enrollment {
  id: number;
  course_id: number;
  student_id: number;
  status: "active" | "dropped";
  enrolled_at: string;
}

export interface EnrollmentWithCourse extends Enrollment {
  course: Course;
}

export interface EnrollmentWithStudent extends Enrollment {
  student: User;
}

export interface Task {
  id: number;
  course_id: number;
  teacher_id: number;
  title: string;
  description?: string | null;
  type: TaskType;
  deadline?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface Submission {
  id: number;
  task_id: number;
  student_id: number;
  answer_text?: string | null;
  file_url?: string | null;
  score?: number | null;
  feedback?: string | null;
  submitted_at: string;
  graded_at?: string | null;
  status: SubmissionStatus;
}

export interface SubmissionWithStudent extends Submission {
  student: User;
}

export interface Score {
  submission_id: number;
  course_id: number;
  task_id: number;
  task_title: string;
  student_id: number;
  score?: number | null;
  feedback?: string | null;
  status: SubmissionStatus;
  graded_at?: string | null;
}

export interface Announcement {
  id: number;
  title: string;
  content: string;
  created_by: number;
  created_at: string;
  is_active: boolean;
}
