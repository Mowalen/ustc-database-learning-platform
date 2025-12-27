# 前端接口对接文档（与当前后端实现一致）

> 本文档基于 `server/app/routers` 与 `schemas` 编写，供前后端对接使用。
> 默认 API Base URL：`http://localhost:8000/api/v1`

## 通用约定

- 认证方式：JWT Bearer
- Header：

```
Authorization: Bearer <access_token>
```

- 时间字段为 ISO-8601 字符串（示例：`2024-12-31T23:59:59+00:00`）。
- 下面标注的“权限校验”以当前后端实现为准，个别接口尚未强制鉴权（见备注）。

---

## 1. 认证 Auth

### 1.1 注册
**POST** `/auth/register`

- Auth：不需要
- Body（JSON）：
  - `username` (string, required)
  - `password` (string, required)
  - `role_id` (number, required) // 1=student, 2=teacher, 3=admin
  - `email` (string, optional)
  - `full_name` (string, optional)
  - `phone` (string, optional)
  - `avatar_url` (string, optional)

- Response：`UserResponse`

### 1.2 登录
**POST** `/auth/login`

- Auth：不需要
- Body（x-www-form-urlencoded）：
  - `username`
  - `password`

- Response：

```json
{ "access_token": "...", "token_type": "bearer" }
```

---

## 2. 用户 Users

### 2.1 当前用户信息
**GET** `/users/me`

- Auth：需要
- Response：`UserResponse`

### 2.2 更新当前用户
**PUT** `/users/me`

- Auth：需要
- Body（JSON）：
  - `full_name` (string, optional)
  - `email` (string, optional)
  - `password` (string, optional)

- Response：`UserResponse`

---

## 3. 课程 Courses

### 3.1 课程列表
**GET** `/courses/`

- Auth：不需要
- Query：`skip`、`limit`
- Response：`Course[]`

### 3.2 创建课程
**POST** `/courses/`

- Auth：需要（后端目前只校验登录，不限制角色）
- Body（JSON）：
  - `title` (string, required)
  - `description` (string, optional)
  - `cover_url` (string, optional)
  - `category_id` (number, optional)

- Response：`Course`

### 3.3 课程详情
**GET** `/courses/{id}`

- Auth：不需要
- Response：`Course`

### 3.4 更新课程
**PUT** `/courses/{id}`

- Auth：需要（后端校验课程教师为当前用户）
- Body（JSON）：`CourseUpdate` 任意字段
- Response：`Course`

### 3.5 删除课程
**DELETE** `/courses/{id}`

- Auth：需要（后端校验课程教师为当前用户）
- Response：`Course`

### 3.6 课程分类列表
**GET** `/courses/categories/`

- Auth：不需要
- Query：`skip`、`limit`
- Response：`CourseCategory[]`

### 3.7 创建课程分类
**POST** `/courses/categories/`

- Auth：需要（后端暂未限制管理员）
- Body（JSON）：
  - `name` (string, required)
  - `description` (string, optional)

- Response：`CourseCategory`

---

## 4. 章节 Sections

### 4.1 课程章节列表
**GET** `/courses/{course_id}/sections`

- Auth：不需要
- Query：`skip`、`limit`
- Response：`Section[]`

### 4.2 创建章节
**POST** `/courses/{course_id}/sections`

- Auth：需要（后端校验课程教师为当前用户）
- Body（JSON）：
  - `course_id` (number, required, 必须与 URL 一致)
  - `title` (string, required)
  - `content` (string, optional)
  - `material_url` (string, optional)
  - `video_url` (string, optional)
  - `order_index` (number, optional)

- Response：`Section`

### 4.3 章节详情
**GET** `/sections/{id}`

- Auth：不需要
- Response：`Section`

### 4.4 更新章节
**PUT** `/sections/{id}`

- Auth：需要（后端校验课程教师为当前用户）
- Body（JSON）：`SectionUpdate` 任意字段
- Response：`Section`

### 4.5 删除章节
**DELETE** `/sections/{id}`

- Auth：需要（后端校验课程教师为当前用户）
- Response：`Section`

---

## 5. 选课 Enrollments

> 注意：当前后端路由未强制鉴权，前端仍按登录用户调用。

### 5.1 学生选课
**POST** `/courses/{course_id}/enroll`

- Auth：后端未强制
- Body（JSON）：`{ "student_id": number }`
- Response：`Enrollment`

### 5.2 学生退课
**POST** `/courses/{course_id}/drop`

- Auth：后端未强制
- Body（JSON）：`{ "student_id": number }`
- Response：`Enrollment`

### 5.3 我的选课列表
**GET** `/me/enrollments`

- Auth：后端未强制
- Query：`student_id` (required)
- Response：`EnrollmentWithCourse[]`

### 5.4 课程学生列表
**GET** `/courses/{course_id}/students`

- Auth：后端未强制
- Response：`EnrollmentWithStudent[]`

---

## 6. 作业 / 考试 Tasks & Submissions

> 注意：当前后端路由未强制鉴权，前端仍按登录用户调用。

### 6.1 创建作业/考试
**POST** `/courses/{course_id}/tasks`

- Auth：后端未强制
- Body（JSON）：
  - `teacher_id` (number, required)
  - `title` (string, required)
  - `description` (string, optional)
  - `type` ("assignment" | "exam", required)
  - `deadline` (ISO datetime, optional)

- Response：`Task`

### 6.2 课程任务列表
**GET** `/courses/{course_id}/tasks`

- Auth：后端未强制
- Response：`Task[]`

### 6.3 任务详情
**GET** `/tasks/{task_id}`

- Auth：后端未强制
- Response：`Task`

### 6.4 学生提交任务
**POST** `/tasks/{task_id}/submit`

- Auth：后端未强制
- Body（JSON）：
  - `student_id` (number, required)
  - `answer_text` (string, optional)
  - `file_url` (string, optional)

- Response：`Submission`

### 6.5 教师评分
**PUT** `/submissions/{submission_id}/grade`

- Auth：后端未强制
- Body（JSON）：
  - `score` (number, required)
  - `feedback` (string, optional)
  - `status` ("graded" | "submitted" | "late", optional)

- Response：`Submission`

---

## 7. 成绩 Scores

> 注意：当前后端路由未强制鉴权。

### 7.1 学生成绩
**GET** `/me/scores`

- Auth：后端未强制
- Query：`student_id` (required)
- Response：`Score[]`

### 7.2 课程成绩列表
**GET** `/courses/{course_id}/scores`

- Auth：后端未强制
- Response：`Score[]`

### 7.3 导出成绩 CSV
**GET** `/courses/{course_id}/scores/export`

- Auth：后端未强制
- Response：CSV 字符串（`text/csv`）

---

## 8. 管理员 Admin

> 注意：当前后端路由未强制鉴权。

### 8.1 新建用户
**POST** `/admin/users`

- Auth：后端未强制
- Body（JSON）：`UserCreate`
- Response：`UserResponse`

### 8.2 更新用户
**PUT** `/admin/users/{user_id}`

- Auth：后端未强制
- Body（JSON）：`UserUpdate`
- Response：`UserResponse`

### 8.3 停用用户
**DELETE** `/admin/users/{user_id}`

- Auth：后端未强制
- Response：`UserResponse`（is_active=false）

### 8.4 下架课程
**DELETE** `/admin/courses/{course_id}`

- Auth：后端未强制
- Response：

```json
{ "course_id": 123, "is_active": false }
```

### 8.5 创建公告
**POST** `/admin/announcements`

- Auth：后端未强制
- Body（JSON）：
  - `title` (string, required)
  - `content` (string, required)
  - `created_by` (number, required)
  - `is_active` (boolean, optional)

- Response：`Announcement`

### 8.6 公告列表
**GET** `/admin/announcements`

- Auth：后端未强制
- Query：`include_inactive` (boolean, optional)
- Response：`Announcement[]`

---

## 9. 返回对象结构（摘要）

### UserResponse
```
{
  id: number,
  username: string,
  email?: string,
  full_name?: string,
  phone?: string,
  avatar_url?: string,
  role_id: number,
  is_active: boolean,
  created_at: string,
  updated_at?: string,
  role?: { id: number, name: string, description?: string }
}
```

### Course
```
{
  id: number,
  teacher_id: number,
  title: string,
  description?: string,
  cover_url?: string,
  category_id?: number,
  created_at: string,
  updated_at?: string,
  is_active: boolean,
  category?: { id: number, name: string, description?: string, created_at: string, updated_at?: string }
}
```

### Section
```
{
  id: number,
  course_id: number,
  title: string,
  content?: string,
  material_url?: string,
  video_url?: string,
  order_index?: number,
  created_at: string,
  updated_at?: string
}
```

### Enrollment / EnrollmentWithCourse / EnrollmentWithStudent
```
{
  id: number,
  course_id: number,
  student_id: number,
  status: "active" | "dropped",
  enrolled_at: string,
  course?: Course,
  student?: UserOut
}
```

### Task
```
{
  id: number,
  course_id: number,
  teacher_id: number,
  title: string,
  description?: string,
  type: "assignment" | "exam",
  deadline?: string,
  created_at: string,
  updated_at: string
}
```

### Submission
```
{
  id: number,
  task_id: number,
  student_id: number,
  answer_text?: string,
  file_url?: string,
  score?: number,
  feedback?: string,
  submitted_at: string,
  graded_at?: string,
  status: "submitted" | "graded" | "late"
}
```

### Score
```
{
  submission_id: number,
  course_id: number,
  task_id: number,
  task_title: string,
  student_id: number,
  score?: number,
  status: "submitted" | "graded" | "late",
  graded_at?: string
}
```

### Announcement
```
{
  id: number,
  title: string,
  content: string,
  created_by: number,
  created_at: string,
  is_active: boolean
}
```

---

## 10. 需要后端补充/确认的点（建议）

- 选课、任务、成绩、管理员接口建议增加鉴权与角色校验。
- 文件上传目前仅提供 `file_url` 文本字段，若需真实上传，请提供上传接口。
- 管理员缺少用户列表与课程列表接口，若需要可新增。
