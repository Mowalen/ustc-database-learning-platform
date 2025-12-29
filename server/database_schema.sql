-- USTC Database Learning Platform - MySQL Schema
-- Character Set: UTF-8
-- Collation: utf8mb4_unicode_ci

-- 删除已存在的数据库（警告：会删除所有数据）
-- DROP DATABASE IF EXISTS ustc_learning_platform;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ustc_learning_platform 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE ustc_learning_platform;

-- ==========================================
-- 1. 角色表 (roles)
-- ==========================================
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
    name VARCHAR(30) NOT NULL UNIQUE COMMENT '角色名称（student/teacher/admin）',
    description VARCHAR(100) COMMENT '角色描述',
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 插入初始角色数据
INSERT INTO roles (id, name, description) VALUES
(1, 'student', 'Student role'),
(2, 'teacher', 'Teacher role'),
(3, 'admin', 'Admin role')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- ==========================================
-- 2. 用户表 (users)
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名（唯一）',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) COMMENT '姓名',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '电话',
    role_id INT NOT NULL COMMENT '角色ID',
    avatar_url VARCHAR(255) COMMENT '头像地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    INDEX idx_username (username),
    INDEX idx_role_id (role_id),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ==========================================
-- 3. 课程分类表 (course_categories)
-- ==========================================
CREATE TABLE IF NOT EXISTS course_categories (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '分类名称',
    description VARCHAR(255) COMMENT '分类描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程分类表';

-- 插入30个常见课程分类数据



-- ==========================================
-- 4. 课程表 (courses)
-- ==========================================
CREATE TABLE IF NOT EXISTS courses (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '课程ID',
    teacher_id INT NOT NULL COMMENT '授课教师ID',
    title VARCHAR(100) NOT NULL COMMENT '课程标题',
    description TEXT COMMENT '课程简介',
    cover_url VARCHAR(255) COMMENT '封面图片路径',
    material_url VARCHAR(255) COMMENT '课件文件路径',
    video_url VARCHAR(255) COMMENT '视频文件路径',
    category_id INT COMMENT '课程分类ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES course_categories(id) ON DELETE SET NULL,
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_category_id (category_id),
    INDEX idx_title (title),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- ==========================================
-- 5. 课程章节表 (course_sections)
-- ==========================================
CREATE TABLE IF NOT EXISTS course_sections (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '小节ID',
    course_id INT NOT NULL COMMENT '所属课程ID',
    title VARCHAR(100) NOT NULL COMMENT '小节标题',
    content TEXT COMMENT '小节文字内容（可选）',
    material_url VARCHAR(255) COMMENT '课件文件路径',
    video_url VARCHAR(255) COMMENT '视频路径',
    order_index INT NOT NULL DEFAULT 0 COMMENT '小节排序序号',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_course_id (course_id),
    INDEX idx_order (course_id, order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程章节表';

-- ==========================================
-- 6. 选课表 (course_enrollments)
-- ==========================================
CREATE TABLE IF NOT EXISTS course_enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    course_id INT NOT NULL COMMENT '课程ID',
    student_id INT NOT NULL COMMENT '学生ID',
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    status ENUM('active', 'dropped') DEFAULT 'active' COMMENT '状态',
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_course_student (course_id, student_id),
    INDEX idx_student_id (student_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课表';

-- ==========================================
-- 7. 作业/考试表 (tasks)
-- ==========================================
CREATE TABLE IF NOT EXISTS tasks (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '任务ID',
    course_id INT NOT NULL COMMENT '所属课程ID',
    teacher_id INT NOT NULL COMMENT '发布教师ID',
    title VARCHAR(100) NOT NULL COMMENT '标题',
    description TEXT COMMENT '内容描述',
    type ENUM('assignment', 'exam') NOT NULL COMMENT '类型：作业或考试',
    deadline DATETIME COMMENT '截止时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_course_id (course_id),
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_type (type),
    INDEX idx_deadline (deadline)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业/考试表';

-- ==========================================
-- 8. 提交记录表 (submissions)
-- ==========================================
CREATE TABLE IF NOT EXISTS submissions (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '提交记录ID',
    task_id INT NOT NULL COMMENT '任务ID',
    student_id INT NOT NULL COMMENT '学生ID',
    answer_text TEXT COMMENT '答案内容',
    file_url VARCHAR(255) COMMENT '上传文件路径',
    score DECIMAL(5,2) COMMENT '分数',
    feedback TEXT COMMENT '评语',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    graded_at DATETIME COMMENT '批改时间',
    status ENUM('submitted', 'graded', 'late') DEFAULT 'submitted' COMMENT '状态',
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_task_student (task_id, student_id),
    INDEX idx_student_id (student_id),
    INDEX idx_status (status),
    INDEX idx_submitted_at (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提交记录表';

-- ==========================================
-- 9. 公告表 (announcements)
-- ==========================================
CREATE TABLE IF NOT EXISTS announcements (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '公告ID',
    title VARCHAR(100) NOT NULL COMMENT '标题',
    content TEXT COMMENT '内容',
    created_by INT NOT NULL COMMENT '创建者ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公告表';

-- ==========================================
-- 10. 操作日志表 (operation_logs) - 可选
-- ==========================================
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT COMMENT '操作用户ID',
    action VARCHAR(255) NOT NULL COMMENT '操作描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- ==========================================
-- 查看所有表
-- ==========================================
SHOW TABLES;
