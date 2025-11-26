后端开发任务划分方案
（基于文档内容 USTC_IAT_Database_2025Fall）

总体分工原则
- 两位开发者任务量均衡
- 模块边界清晰，无强耦合
- 每个人均可独立并行开发
- 仅需对基础数据库（users / courses）字段提前约定
  

---

👤 开发者 A：用户系统 & 课程体系（基础模块）
负责整个系统的基础能力，包括用户、权限、课程结构与课程内容。

A1. 用户与权限系统
来源：文档第 1 页功能点  
涉及表：roles, users, operation_logs

开发内容：
- 用户注册 / 登录 / 退出登录
- 用户角色（student/teacher/admin）设计
- 权限控制（RBAC）
- 用户个人信息管理（修改密码/头像）
- 操作日志中间件（记录用户行为）
  
API（示例）：
- POST /auth/register  
- POST /auth/login  
- POST /auth/logout  
- GET /users/me  
- PUT /users/me  
- RBAC 中间件  
- 操作日志自动记录
  

---

A2. 课程管理模块（课程基础信息）
来源：文档第 2 页  
涉及表：courses, course_categories

开发内容：
- 创建课程（教师）
- 查看课程列表（全部 / 指定分类）
- 查看课程详情
- 编辑课程信息
- 课程分类管理（增删改查）
  
API：
- POST /courses  
- GET /courses  
- GET /courses/{id}  
- PUT /courses/{id}  
- DELETE /courses/{id}  
- 分类管理接口（增删改查）
  

---

A3. 课程章节（课程内容层）
来源：文档第 7–8 页  
涉及表：course_sections

开发内容：
- 小节创建、修改、删除
- 上传课件（material_url）
- 上传视频（video_url）
- 排序（order_index）
  
API：
- POST /courses/{id}/sections  
- GET /courses/{id}/sections  
- GET /sections/{id}  
- PUT /sections/{id}  
- DELETE /sections/{id}
  

---

📌 开发者 A 工作总结

模块
复杂度
用户系统（登录、角色、权限）
⭐⭐⭐⭐
课程管理
⭐⭐⭐
课程分类
⭐⭐
课程章节
⭐⭐
操作日志
⭐


---

👤 开发者 B：选课 + 作业考试 + 成绩 + 管理后台（业务流程模块）

B1. 选课系统
来源：文档第 1 & 4 页  
涉及表：course_enrollments

开发内容：
- 学生选课/退课
- 查看选课列表
- 老师查看选课学生
  
API：
- POST /courses/{id}/enroll  
- POST /courses/{id}/drop  
- GET /me/enrollments  
- GET /courses/{id}/students
  

---

B2. 作业与考试模块
来源：文档第 3–5 页  
涉及表：tasks, submissions

开发内容：
- 老师发布作业、考试
- 学生提交作业（文本/文件）
- 自动判定是否迟交（late）
- 老师批改 + 评分 + 反馈
  
API：
- POST /courses/{id}/tasks  
- GET /courses/{id}/tasks  
- GET /tasks/{id}  
- POST /tasks/{id}/submit  
- PUT /submissions/{id}/grade  
  

---

B3. 成绩模块
来源：文档第 2 页

开发内容：
- 学生查看成绩
- 老师查看课程成绩
- 成绩导出 CSV/Excel
  
API：
- GET /me/scores  
- GET /courses/{id}/scores  
- GET /courses/{id}/scores/export  
  

---

B4. 管理员后台
来源：文档第 2 页  
涉及表：announcements

开发内容：
- 用户管理（增删改查）
- 课程强制下架
- 公告管理
  
API：
- POST /admin/users  
- PUT /admin/users/{id}  
- DELETE /admin/users/{id}  
- DELETE /admin/courses/{id}  
- POST /admin/announcements  
- GET /admin/announcements  
  

---

📌 开发者 B 工作总结

模块
复杂度
选课系统
⭐⭐
作业与考试
⭐⭐⭐⭐
成绩管理
⭐⭐⭐
管理后台/公告
⭐⭐


---

🎯 最终分工总结（可直接发给两位开发者）

开发者 A 负责：  
用户与权限模块、课程管理、课程分类、课程章节、操作日志。

开发者 B 负责：  
选课系统、作业/考试系统、成绩管理、管理员后台、公告管理。


---
