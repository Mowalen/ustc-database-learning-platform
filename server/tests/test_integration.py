"""
Integration tests - Complete API flow testing
Tests the entire workflow from user registration to course creation
"""
import pytest
from httpx import AsyncClient
from typing import Dict


class TestCompleteFlow:
    """Test complete workflow scenarios"""
    
    @pytest.mark.asyncio
    async def test_teacher_creates_course_workflow(self, client: AsyncClient):
        """
        Complete workflow:
        1. Teacher registers
        2. Teacher logs in
        3. Teacher creates category
        4. Teacher creates course
        5. Teacher creates sections
        6. Teacher updates course
        """
        # 1. Register teacher
        teacher_data = {
            "username": "flow_teacher",
            "password": "password123",
            "email": "flow_teacher@test.com",
            "full_name": "Flow Test Teacher",
            "role_id": 2  # Teacher
        }
        
        response = await client.post("/auth/register", json=teacher_data)
        # May already exist
        
        # 2. Login
        login_data = {
            "username": "flow_teacher",
            "password": "password123"
        }
        
        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create category
        category_data = {
            "name": "Flow Test Category",
            "description": "Category for flow test"
        }
        
        response = await client.post("/courses/categories/", json=category_data, headers=headers)
        
        if response.status_code == 200:
            category_id = response.json()["id"]
        else:
            # Get existing category
            response = await client.get("/courses/categories/")
            categories = response.json()
            category_id = categories[0]["id"]
        
        # 4. Create course
        course_data = {
            "title": "Flow Test Course",
            "description": "A complete test course",
            "category_id": category_id
        }
        
        response = await client.post("/courses/", json=course_data, headers=headers)
        assert response.status_code == 200
        course_id = response.json()["id"]
        
        # 5. Create multiple sections
        for i in range(1, 4):
            section_data = {
                "title": f"Section {i}",
                "content": f"Content for section {i}",
                "course_id": course_id,
                "order_index": i
            }
            
            response = await client.post(
                f"/courses/{course_id}/sections",
                json=section_data,
                headers=headers
            )
            assert response.status_code == 200
        
        # 6. List sections
        response = await client.get(f"/courses/{course_id}/sections")
        assert response.status_code == 200
        sections = response.json()
        assert len(sections) >= 3
        
        # 7. Update course
        update_data = {
            "title": "Updated Flow Test Course",
            "description": "Updated description"
        }
        
        response = await client.put(f"/courses/{course_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_course = response.json()
        assert updated_course["title"] == update_data["title"]
        
        print("✓ Complete teacher workflow successful!")
    
    @pytest.mark.asyncio
    async def test_student_views_courses_workflow(self, client: AsyncClient, test_course: Dict):
        """
        Student workflow:
        1. Student registers
        2. Student logs in
        3. Student views course list
        4. Student views course details
        5. Student views sections
        """
        # 1. Register student
        student_data = {
            "username": "flow_student",
            "password": "password123",
            "email": "flow_student@test.com",
            "full_name": "Flow Test Student",
            "role_id": 1  # Student
        }
        
        response = await client.post("/auth/register", json=student_data)
        # May already exist
        
        # 2. Login
        login_data = {
            "username": "flow_student",
            "password": "password123"
        }
        
        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. View course list
        response = await client.get("/courses/")
        assert response.status_code == 200
        courses = response.json()
        assert len(courses) > 0
        
        # 4. View course details
        course_id = test_course["id"]
        response = await client.get(f"/courses/{course_id}")
        assert response.status_code == 200
        course = response.json()
        assert "title" in course
        
        # 5. View sections
        response = await client.get(f"/courses/{course_id}/sections")
        assert response.status_code == 200
        sections = response.json()
        assert isinstance(sections, list)
        
        # 6. View specific section
        if len(sections) > 0:
            section_id = sections[0]["id"]
            response = await client.get(f"/sections/{section_id}")
            assert response.status_code == 200
        
        print("✓ Complete student workflow successful!")
    
    @pytest.mark.asyncio
    async def test_unauthorized_actions(self, client: AsyncClient, test_course: Dict):
        """
        Test that unauthorized actions are properly rejected
        """
        # Register and login as student
        student_data = {
            "username": "unauth_student",
            "password": "password123",
            "email": "unauth@test.com",
            "full_name": "Unauthorized Test",
            "role_id": 1
        }
        
        await client.post("/auth/register", json=student_data)
        
        login_response = await client.post(
            "/auth/login",
            data={"username": "unauth_student", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to update someone else's course
        update_data = {"title": "Hacked!"}
        response = await client.put(f"/courses/{test_course['id']}", json=update_data, headers=headers)
        assert response.status_code == 400, "Student should not be able to update teacher's course"
        
        # Try to delete someone else's course
        response = await client.delete(f"/courses/{test_course['id']}", headers=headers)
        assert response.status_code == 400, "Student should not be able to delete teacher's course"
        
        print("✓ Authorization checks working correctly!")
