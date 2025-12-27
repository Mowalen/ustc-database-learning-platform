"""
综合测试 - 验证所有后端接口
这个测试文件用于快速验证所有API接口是否正常工作
"""
import pytest
import io
from httpx import AsyncClient
from typing import Dict


class TestAllEndpoints:
    """测试所有API端点的可访问性和基本功能"""
    
    # ============ 1. 认证接口 ============
    
    @pytest.mark.asyncio
    async def test_auth_register(self, client: AsyncClient):
        """测试注册接口"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"test_{unique_id}",
            "password": "test123",
            "email": f"test_{unique_id}@test.com",
            "role_id": 1
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code in [200, 400]  # 200 成功或 400 已存在
    
    @pytest.mark.asyncio
    async def test_auth_login(self, client: AsyncClient, teacher_token: str):
        """测试登录接口"""
        assert teacher_token is not None
        assert len(teacher_token) > 0
    
    # ============ 2. 用户接口 ============
    
    @pytest.mark.asyncio
    async def test_users_me_get(self, client: AsyncClient, teacher_headers: Dict[str, str]):
        """测试获取当前用户信息"""
        response = await client.get("/users/me", headers=teacher_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
    
    @pytest.mark.asyncio
    async def test_users_me_put(self, client: AsyncClient, student_headers: Dict[str, str]):
        """测试更新当前用户信息"""
        update_data = {"full_name": "Test Update"}
        response = await client.put("/users/me", json=update_data, headers=student_headers)
        assert response.status_code == 200
    
    # ============ 3. 课程接口 ============
    
    @pytest.mark.asyncio
    async def test_courses_list(self, client: AsyncClient):
        """测试获取课程列表"""
        response = await client.get("/courses/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_courses_create(self, client: AsyncClient, teacher_headers: Dict[str, str], course_category: Dict):
        """测试创建课程"""
        course_data = {
            "title": "Test Course",
            "description": "Test Description",
            "category_id": course_category["id"]
        }
        response = await client.post("/courses/", json=course_data, headers=teacher_headers)
        assert response.status_code == 200
        assert response.json()["title"] == course_data["title"]
    
    @pytest.mark.asyncio
    async def test_courses_get(self, client: AsyncClient, test_course: Dict):
        """测试获取课程详情"""
        response = await client.get(f"/courses/{test_course['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == test_course["id"]
    
    @pytest.mark.asyncio
    async def test_courses_update(self, client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
        """测试更新课程"""
        update_data = {"description": "Updated Description"}
        response = await client.put(
            f"/courses/{test_course['id']}", 
            json=update_data, 
            headers=teacher_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_courses_delete(self, client: AsyncClient, teacher_headers: Dict[str, str]):
        """测试删除课程"""
        # Create a course to delete
        category_response = await client.get("/courses/categories/")
        categories = category_response.json()
        if not categories:
            pytest.skip("No categories available")
        
        course_data = {
            "title": "Course to Delete",
            "category_id": categories[0]["id"]
        }
        create_response = await client.post("/courses/", json=course_data, headers=teacher_headers)
        course_id = create_response.json()["id"]
        
        response = await client.delete(f"/courses/{course_id}", headers=teacher_headers)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_courses_categories_list(self, client: AsyncClient):
        """测试获取课程分类列表"""
        response = await client.get("/courses/categories/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_courses_categories_create(self, client: AsyncClient, teacher_headers: Dict[str, str]):
        """测试创建课程分类"""
        import uuid
        category_data = {
            "name": f"Test Category {uuid.uuid4()}",
            "description": "Test Description"
        }
        response = await client.post("/courses/categories/", json=category_data, headers=teacher_headers)
        assert response.status_code == 200
    
    # ============ 4. 章节接口 ============
    
    @pytest.mark.asyncio
    async def test_sections_list(self, client: AsyncClient, test_course: Dict):
        """测试获取章节列表"""
        response = await client.get(f"/courses/{test_course['id']}/sections")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_sections_create(self, client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
        """测试创建章节"""
        section_data = {
            "course_id": test_course["id"],
            "title": "Test Section",
            "content": "Test Content"
        }
        response = await client.post(
            f"/courses/{test_course['id']}/sections",
            json=section_data,
            headers=teacher_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_sections_get(self, client: AsyncClient, test_section: Dict):
        """测试获取章节详情"""
        response = await client.get(f"/sections/{test_section['id']}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_sections_update(self, client: AsyncClient, teacher_headers: Dict[str, str], test_section: Dict):
        """测试更新章节"""
        update_data = {"content": "Updated Content"}
        response = await client.put(
            f"/sections/{test_section['id']}",
            json=update_data,
            headers=teacher_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_sections_delete(self, client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
        """测试删除章节"""
        # Create a section to delete
        section_data = {
            "course_id": test_course["id"],
            "title": "Section to Delete"
        }
        create_response = await client.post(
            f"/courses/{test_course['id']}/sections",
            json=section_data,
            headers=teacher_headers
        )
        section_id = create_response.json()["id"]
        
        response = await client.delete(f"/sections/{section_id}", headers=teacher_headers)
        assert response.status_code == 200
    
    # ============ 5. 选课接口 ============
    
    @pytest.mark.asyncio
    async def test_enrollments_enroll(self, client: AsyncClient, test_course: Dict):
        """测试学生选课"""
        enroll_data = {"student_id": 1}  # Assuming student with ID 1 exists
        response = await client.post(
            f"/courses/{test_course['id']}/enroll",
            json=enroll_data
        )
        assert response.status_code in [200, 400]  # 200 成功或 400 已选课
    
    @pytest.mark.asyncio
    async def test_enrollments_drop(self, client: AsyncClient, test_course: Dict):
        """测试学生退课"""
        drop_data = {"student_id": 1}
        response = await client.post(
            f"/courses/{test_course['id']}/drop",
            json=drop_data
        )
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_enrollments_my_list(self, client: AsyncClient):
        """测试获取我的选课列表"""
        response = await client.get("/me/enrollments?student_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_enrollments_course_students(self, client: AsyncClient, test_course: Dict):
        """测试获取课程学生列表"""
        response = await client.get(f"/courses/{test_course['id']}/students")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # ============ 6. 任务接口 ============
    
    @pytest.mark.asyncio
    async def test_tasks_create(self, client: AsyncClient, test_course: Dict):
        """测试创建任务"""
        task_data = {
            "teacher_id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "type": "assignment"
        }
        response = await client.post(
            f"/courses/{test_course['id']}/tasks",
            json=task_data
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_tasks_list(self, client: AsyncClient, test_course: Dict):
        """测试获取任务列表"""
        response = await client.get(f"/courses/{test_course['id']}/tasks")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_tasks_get(self, client: AsyncClient, test_course: Dict):
        """测试获取任务详情"""
        # First create a task
        task_data = {
            "teacher_id": 1,
            "title": "Task for Get Test",
            "type": "assignment"
        }
        create_response = await client.post(
            f"/courses/{test_course['id']}/tasks",
            json=task_data
        )
        task_id = create_response.json()["id"]
        
        response = await client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_tasks_submit(self, client: AsyncClient, test_course: Dict):
        """测试提交任务"""
        # Create a task first
        task_data = {
            "teacher_id": 1,
            "title": "Task for Submit Test",
            "type": "assignment"
        }
        create_response = await client.post(
            f"/courses/{test_course['id']}/tasks",
            json=task_data
        )
        task_id = create_response.json()["id"]
        
        # Submit the task
        submit_data = {
            "student_id": 1,
            "answer_text": "My answer"
        }
        response = await client.post(
            f"/tasks/{task_id}/submit",
            json=submit_data
        )
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_submissions_grade(self, client: AsyncClient, test_course: Dict):
        """测试评分"""
        # Create task and submit
        task_data = {"teacher_id": 1, "title": "Grade Test Task", "type": "assignment"}
        task_response = await client.post(f"/courses/{test_course['id']}/tasks", json=task_data)
        task_id = task_response.json()["id"]
        
        submit_data = {"student_id": 1, "answer_text": "Answer"}
        submit_response = await client.post(f"/tasks/{task_id}/submit", json=submit_data)
        
        if submit_response.status_code == 200:
            submission_id = submit_response.json()["id"]
            
            grade_data = {
                "score": 95,
                "feedback": "Great work!",
                "status": "graded"
            }
            response = await client.put(
                f"/submissions/{submission_id}/grade",
                json=grade_data
            )
            assert response.status_code == 200
    
    # ============ 7. 成绩接口 ============
    
    @pytest.mark.asyncio
    async def test_scores_my_scores(self, client: AsyncClient):
        """测试获取学生成绩"""
        response = await client.get("/me/scores?student_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_scores_course_scores(self, client: AsyncClient, test_course: Dict):
        """测试获取课程成绩"""
        response = await client.get(f"/courses/{test_course['id']}/scores")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_scores_export(self, client: AsyncClient, test_course: Dict):
        """测试导出成绩CSV"""
        response = await client.get(f"/courses/{test_course['id']}/scores/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # ============ 8. 管理员接口 ============
    
    @pytest.mark.asyncio
    async def test_admin_create_user(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """测试管理员创建用户"""
        import uuid
        user_data = {
            "username": f"admin_user_{uuid.uuid4()}",
            "password": "pass123",
            "role_id": 1
        }
        response = await client.post("/admin/users", json=user_data, headers=admin_headers)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_admin_update_user(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """测试管理员更新用户"""
        # Create a user first
        import uuid
        user_data = {
            "username": f"update_test_{uuid.uuid4()}",
            "password": "pass123",
            "role_id": 1
        }
        create_response = await client.post("/admin/users", json=user_data, headers=admin_headers)
        user_id = create_response.json()["id"]
        
        update_data = {"full_name": "Updated Name"}
        response = await client.put(
            f"/admin/users/{user_id}",
            json=update_data,
            headers=admin_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_admin_delete_user(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """测试管理员停用用户"""
        import uuid
        user_data = {
            "username": f"delete_test_{uuid.uuid4()}",
            "password": "pass123",
            "role_id": 1
        }
        create_response = await client.post("/admin/users", json=user_data, headers=admin_headers)
        user_id = create_response.json()["id"]
        
        response = await client.delete(f"/admin/users/{user_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] == False
    
    @pytest.mark.asyncio
    async def test_admin_delete_course(self, client: AsyncClient, admin_headers: Dict[str, str], test_course: Dict):
        """测试管理员下架课程"""
        response = await client.delete(
            f"/admin/courses/{test_course['id']}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["is_active"] == False
    
    @pytest.mark.asyncio
    async def test_admin_create_announcement(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """测试创建公告"""
        announcement_data = {
            "title": "Test Announcement",
            "content": "Test Content",
            "created_by": 1
        }
        response = await client.post(
            "/admin/announcements",
            json=announcement_data,
            headers=admin_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_admin_list_announcements(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """测试获取公告列表"""
        response = await client.get("/admin/announcements", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_admin_list_users(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """测试管理员获取用户列表（新增）"""
        response = await client.get("/admin/users", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_admin_list_courses(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """测试管理员获取课程列表（新增）"""
        response = await client.get("/admin/courses", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # ============ 9. 文件上传接口（新增）============
    
    @pytest.mark.asyncio
    async def test_upload_file(self, client: AsyncClient, teacher_headers: Dict[str, str]):
        """测试上传文件"""
        file_content = b"Test file content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
        response = await client.post("/upload/file", files=files, headers=teacher_headers)
        assert response.status_code == 200
        assert "file_url" in response.json()
    
    @pytest.mark.asyncio
    async def test_upload_image(self, client: AsyncClient, teacher_headers: Dict[str, str]):
        """测试上传图片"""
        png_header = b'\x89PNG\r\n\x1a\n'
        files = {"file": ("test.png", io.BytesIO(png_header), "image/png")}
        response = await client.post("/upload/image", files=files, headers=teacher_headers)
        assert response.status_code == 200
        assert "file_url" in response.json()
    
    @pytest.mark.asyncio
    async def test_upload_avatar(self, client: AsyncClient, student_headers: Dict[str, str]):
        """测试上传头像"""
        jpeg_header = b'\xff\xd8\xff\xe0'
        files = {"file": ("avatar.jpg", io.BytesIO(jpeg_header), "image/jpeg")}
        response = await client.post("/upload/avatar", files=files, headers=student_headers)
        assert response.status_code == 200
        assert "file_url" in response.json()
