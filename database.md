# 数据库表结构（完整 Markdown 汇总）

---

## 1. roles（角色表）

| 字段名      | 类型          | 说明                         |
|-------------|---------------|------------------------------|
| id          | INT (PK)      | 角色 ID                      |
| name        | VARCHAR(30)   | 角色名（student / teacher / admin） |
| description | VARCHAR(100)  | 描述                         |

---

## 2. users（用户表）

| 字段名        | 类型                     | 说明             |
|---------------|--------------------------|------------------|
| id            | INT (PK, AUTO_INCREMENT) | 用户 ID          |
| username      | VARCHAR(50)              | 用户名（唯一）    |
| password_hash | VARCHAR(255)             | 密码哈希          |
| full_name     | VARCHAR(100)             | 姓名              |
| email         | VARCHAR(100)             | 邮箱              |
| phone         | VARCHAR(20)              | 电话              |
| role_id       | INT (FK → roles.id)      | 角色 ID           |
| avatar_url    | VARCHAR(255)             | 头像地址          |
| created_at    | DATETIME                 | 创建时间          |
| updated_at    | DATETIME                 | 更新时间          |
| is_active     | BOOLEAN                  | 是否启用          |

---

## 3. courses（课程表）

| 字段名        | 类型                     | 说明                     |
|---------------|--------------------------|--------------------------|
| id            | INT (PK, AUTO_INCREMENT) | 课程 ID                  |
| teacher_id    | INT (FK → users.id)      | 授课教师 ID              |
| title         | VARCHAR(100)             | 课程标题                 |
| description   | TEXT                     | 课程简介                 |
| cover_url     | VARCHAR(255)             | 封面图片路径             |
| material_url  | VARCHAR(255)             | 课件文件路径（新增）     |
| video_url     | VARCHAR(255)             | 视频文件路径（新增）     |
| category_id   | INT (FK → course_categories.id) | 课程分类（新增） |
| created_at    | DATETIME                 | 创建时间                 |
| updated_at    | DATETIME                 | 更新时间                 |
| is_active     | BOOLEAN                  | 是否有效                 |

---

## 4. course_enrollments（选课表）

| 字段名     | 类型                     | 说明        |
|------------|--------------------------|-------------|
| id         | INT (PK, AUTO_INCREMENT) | 记录 ID     |
| course_id  | INT (FK → courses.id)    | 课程 ID     |
| student_id | INT (FK → users.id)      | 学生 ID     |
| enrolled_at| DATETIME                 | 选课时间     |
| status     | ENUM('active','dropped') | 状态         |

---

## 5. tasks（作业 / 考试表）

| 字段名     | 类型                     | 说明                   |
|------------|--------------------------|------------------------|
| id         | INT (PK, AUTO_INCREMENT) | 任务 ID                |
| course_id  | INT (FK → courses.id)    | 所属课程               |
| teacher_id | INT (FK → users.id)      | 发布教师               |
| title      | VARCHAR(100)             | 标题                   |
| description| TEXT                     | 内容描述               |
| type       | ENUM('assignment','exam')| 类型：作业或考试        |
| deadline   | DATETIME                 | 截止时间               |
| created_at | DATETIME                 | 创建时间               |
| updated_at | DATETIME                 | 更新时间               |

---

## 6. submissions（提交记录表）

| 字段名     | 类型                     | 说明                   |
|------------|--------------------------|------------------------|
| id         | INT (PK, AUTO_INCREMENT) | 提交记录 ID            |
| task_id    | INT (FK → tasks.id)      | 任务 ID                |
| student_id | INT (FK → users.id)      | 学生 ID                |
| answer_text| TEXT                     | 答案内容               |
| file_url   | VARCHAR(255)             | 上传文件路径           |
| score      | DECIMAL(5,2)             | 分数                   |
| feedback   | TEXT                     | 评语                   |
| submitted_at| DATETIME                | 提交时间               |
| graded_at  | DATETIME                 | 批改时间               |
| status     | ENUM('submitted','graded','late') | 状态         |

---

## 7. announcements（公告表）

| 字段名     | 类型                     | 说明        |
|------------|--------------------------|-------------|
| id         | INT (PK, AUTO_INCREMENT) | 公告 ID     |
| title      | VARCHAR(100)             | 标题         |
| content    | TEXT                     | 内容         |
| created_by | INT (FK → users.id)      | 创建者 ID    |
| created_at | DATETIME                 | 发布时间     |
| is_active  | BOOLEAN                  | 是否启用     |

---

## 8. operation_logs（操作日志表，可选）

| 字段名     | 类型                     | 说明        |
|------------|--------------------------|-------------|
| id         | INT (PK, AUTO_INCREMENT) | 日志 ID     |
| user_id    | INT (FK → users.id)      | 操作用户      |
| action     | VARCHAR(255)             | 操作描述      |
| created_at | DATETIME                 | 时间          |

---

## 9. course_categories（课程分类表） ※（新增）

| 字段名     | 类型                     | 说明        |
|------------|--------------------------|-------------|
| id         | INT (PK, AUTO_INCREMENT) | 分类 ID     |
| name       | VARCHAR(100)             | 分类名称     |
| description| VARCHAR(255)             | 分类描述     |
| created_at | DATETIME                 | 创建时间     |
| updated_at | DATETIME                 | 更新时间     |

---

## 10. course_sections（课程章节表） ※（新增）

| 字段名      | 类型                     | 说明          |
|-------------|--------------------------|---------------|
| id          | INT (PK, AUTO_INCREMENT) | 小节 ID       |
| course_id   | INT (FK → courses.id)    | 所属课程 ID    |
| title       | VARCHAR(100)             | 小节标题       |
| content     | TEXT                     | 小节文字内容（可选） |
| material_url| VARCHAR(255)             | 课件文件路径    |
| video_url   | VARCHAR(255)             | 视频路径       |
| order_index | INT                      | 小节排序序号    |
| created_at  | DATETIME                 | 创建时间       |
| updated_at  | DATETIME                 | 更新时间       |

---
