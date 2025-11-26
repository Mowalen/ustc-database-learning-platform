"""
Test cases for section (course chapter) APIs
"""
import pytest
from httpx import AsyncClient
from typing import Dict


class TestSections:
    """Test course section/chapter endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_section(self, client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
        """Test creating a new section"""
        section_data = {
            "title": "New Section",
            "content": "Section content here",
            "course_id": test_course["id"],
            "order_index": 10
        }
        
        response = await client.post(
            f"/courses/{test_course['id']}/sections",
            json=section_data,
            headers=teacher_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == section_data["title"]
        assert data["content"] == section_data["content"]
        assert data["course_id"] == test_course["id"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_section_wrong_course_id(self, client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
        """Test creating section with mismatched course_id"""
        section_data = {
            "title": "Wrong Course",
            "content": "Content",
            "course_id": 999999,  # Different from URL parameter
            "order_index": 1
        }
        
        response = await client.post(
            f"/courses/{test_course['id']}/sections",
            json=section_data,
            headers=teacher_headers
        )
        
        # Should fail due to course_id mismatch
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_list_course_sections(self, client: AsyncClient, test_course: Dict):
        """Test listing all sections of a course"""
        response = await client.get(f"/courses/{test_course['id']}/sections")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "title" in data[0]
            assert data[0]["course_id"] == test_course["id"]
    
    @pytest.mark.asyncio
    async def test_get_section_by_id(self, client: AsyncClient, test_section: Dict):
        """Test getting a specific section by ID"""
        section_id = test_section["id"]
        
        response = await client.get(f"/sections/{section_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == section_id
        assert "title" in data
        assert "content" in data
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_section(self, client: AsyncClient):
        """Test getting a section that doesn't exist"""
        response = await client.get("/sections/999999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_section(self, client: AsyncClient, teacher_headers: Dict[str, str], test_section: Dict):
        """Test updating a section"""
        section_id = test_section["id"]
        update_data = {
            "title": "Updated Section Title",
            "content": "Updated content",
            "order_index": 5
        }
        
        response = await client.put(f"/sections/{section_id}", json=update_data, headers=teacher_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
    
    @pytest.mark.asyncio
    async def test_update_section_unauthorized(self, client: AsyncClient, student_headers: Dict[str, str], test_section: Dict):
        """Test updating a section as a non-owner"""
        section_id = test_section["id"]
        update_data = {
            "title": "Should Not Update"
        }
        
        response = await client.put(f"/sections/{section_id}", json=update_data, headers=student_headers)
        
        # Should fail because student is not the course teacher
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_delete_section(self, client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
        """Test deleting a section"""
        # Create a section to delete
        section_data = {
            "title": "Section To Delete",
            "content": "Will be deleted",
            "course_id": test_course["id"],
            "order_index": 99
        }
        
        create_response = await client.post(
            f"/courses/{test_course['id']}/sections",
            json=section_data,
            headers=teacher_headers
        )
        assert create_response.status_code == 200
        section_id = create_response.json()["id"]
        
        # Delete the section
        response = await client.delete(f"/sections/{section_id}", headers=teacher_headers)
        
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = await client.get(f"/sections/{section_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_section_without_auth(self, client: AsyncClient, test_course: Dict):
        """Test creating a section without authentication"""
        section_data = {
            "title": "Unauthorized Section",
            "content": "Should not be created",
            "course_id": test_course["id"],
            "order_index": 1
        }
        
        response = await client.post(f"/courses/{test_course['id']}/sections", json=section_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_list_sections_pagination(self, client: AsyncClient, test_course: Dict):
        """Test listing sections with pagination"""
        response = await client.get(f"/courses/{test_course['id']}/sections?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5
