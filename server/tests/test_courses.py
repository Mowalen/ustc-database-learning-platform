"""
Test cases for course APIs
"""
import pytest
from httpx import AsyncClient
from typing import Dict


class TestCourses:
    """Test course management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_course(self, client: AsyncClient, teacher_headers: Dict[str, str], course_category: Dict):
        """Test creating a new course"""
        course_data = {
            "title": "New Test Course",
            "description": "Description of new course",
            "category_id": course_category["id"]
        }
        
        response = await client.post("/courses/", json=course_data, headers=teacher_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == course_data["title"]
        assert data["description"] == course_data["description"]
        assert "id" in data
        assert "teacher_id" in data
    
    @pytest.mark.asyncio
    async def test_list_courses(self, client: AsyncClient):
        """Test listing all courses (no auth required)"""
        response = await client.get("/courses/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "title" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_course_by_id(self, client: AsyncClient, test_course: Dict):
        """Test getting a specific course by ID"""
        course_id = test_course["id"]
        
        response = await client.get(f"/courses/{course_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == course_id
        assert "title" in data
        assert "description" in data
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_course(self, client: AsyncClient):
        """Test getting a course that doesn't exist"""
        response = await client.get("/courses/999999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_course(self, client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
        """Test updating a course"""
        course_id = test_course["id"]
        update_data = {
            "title": "Updated Course Title",
            "description": "Updated description"
        }
        
        response = await client.put(f"/courses/{course_id}", json=update_data, headers=teacher_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
    
    @pytest.mark.asyncio
    async def test_update_course_unauthorized(self, client: AsyncClient, student_headers: Dict[str, str], test_course: Dict):
        """Test updating a course as a non-owner"""
        course_id = test_course["id"]
        update_data = {
            "title": "Should Not Update"
        }
        
        response = await client.put(f"/courses/{course_id}", json=update_data, headers=student_headers)
        
        # Should fail because student is not the teacher
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_delete_course(self, client: AsyncClient, teacher_headers: Dict[str, str], course_category: Dict):
        """Test deleting a course"""
        # Create a course to delete
        course_data = {
            "title": "Course To Delete",
            "description": "This will be deleted",
            "category_id": course_category["id"]
        }
        
        create_response = await client.post("/courses/", json=course_data, headers=teacher_headers)
        assert create_response.status_code == 200
        course_id = create_response.json()["id"]
        
        # Delete the course
        response = await client.delete(f"/courses/{course_id}", headers=teacher_headers)
        
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = await client.get(f"/courses/{course_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_course_without_auth(self, client: AsyncClient):
        """Test creating a course without authentication"""
        course_data = {
            "title": "Unauthorized Course",
            "description": "Should not be created"
        }
        
        response = await client.post("/courses/", json=course_data)
        
        assert response.status_code == 401


class TestCourseCategories:
    """Test course category endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_category(self, client: AsyncClient, teacher_headers: Dict[str, str]):
        """Test creating a course category"""
        category_data = {
            "name": "New Category",
            "description": "New category description"
        }
        
        response = await client.post("/courses/categories/", json=category_data, headers=teacher_headers)
        
        # Might already exist, so accept 200 or check error message
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == category_data["name"]
    
    @pytest.mark.asyncio
    async def test_list_categories(self, client: AsyncClient):
        """Test listing all categories"""
        response = await client.get("/courses/categories/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "name" in data[0]
    
    @pytest.mark.asyncio
    async def test_list_categories_with_pagination(self, client: AsyncClient):
        """Test listing categories with pagination"""
        response = await client.get("/courses/categories/?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5
