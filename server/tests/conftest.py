"""
Pytest configuration and fixtures for API testing
"""
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from typing import AsyncGenerator, Dict

# Base URL for API - modify if needed
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for all tests"""
    async with AsyncClient(base_url=API_V1, timeout=30.0) as ac:
        yield ac


@pytest_asyncio.fixture
async def teacher_token(client: AsyncClient) -> str:
    """Register and login a teacher, return auth token"""
    # Register teacher
    teacher_data = {
        "username": "test_teacher",
        "password": "teacher123",
        "email": "teacher@test.com",
        "full_name": "Test Teacher",
        "role_id": 2  # Teacher role
    }
    
    # Try to register (may already exist)
    response = await client.post("/auth/register", json=teacher_data)
    
    # Login to get token
    login_data = {
        "username": "test_teacher",
        "password": "teacher123"
    }
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200, f"Teacher login failed: {response.text}"
    
    token_data = response.json()
    return token_data["access_token"]


@pytest_asyncio.fixture
async def student_token(client: AsyncClient) -> str:
    """Register and login a student, return auth token"""
    # Register student
    student_data = {
        "username": "test_student",
        "password": "student123",
        "email": "student@test.com",
        "full_name": "Test Student",
        "role_id": 1  # Student role
    }
    
    # Try to register (may already exist)
    response = await client.post("/auth/register", json=student_data)
    
    # Login to get token
    login_data = {
        "username": "test_student",
        "password": "student123"
    }
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200, f"Student login failed: {response.text}"
    
    token_data = response.json()
    return token_data["access_token"]


@pytest_asyncio.fixture
async def teacher_headers(teacher_token: str) -> Dict[str, str]:
    """Get authorization headers for teacher"""
    return {"Authorization": f"Bearer {teacher_token}"}


@pytest_asyncio.fixture
async def student_headers(student_token: str) -> Dict[str, str]:
    """Get authorization headers for student"""
    return {"Authorization": f"Bearer {student_token}"}


@pytest_asyncio.fixture
async def course_category(client: AsyncClient, teacher_headers: Dict[str, str]) -> Dict:
    """Create a test course category"""
    category_data = {
        "name": "Test Category",
        "description": "Category for testing"
    }
    
    response = await client.post("/courses/categories/", json=category_data, headers=teacher_headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        # Category might already exist, get the first one
        response = await client.get("/courses/categories/")
        categories = response.json()
        if categories:
            return categories[0]
        else:
            raise Exception("Failed to create or find category")


@pytest_asyncio.fixture
async def test_course(client: AsyncClient, teacher_headers: Dict[str, str], course_category: Dict) -> Dict:
    """Create a test course"""
    course_data = {
        "title": "Test Course",
        "description": "A course for testing",
        "category_id": course_category["id"]
    }
    
    response = await client.post("/courses/", json=course_data, headers=teacher_headers)
    assert response.status_code == 200, f"Failed to create test course: {response.text}"
    
    return response.json()


@pytest_asyncio.fixture
async def test_section(client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict) -> Dict:
    """Create a test section"""
    section_data = {
        "title": "Test Section",
        "content": "Section content for testing",
        "course_id": test_course["id"],
        "order_index": 1
    }
    
    response = await client.post(
        f"/courses/{test_course['id']}/sections",
        json=section_data,
        headers=teacher_headers
    )
    assert response.status_code == 200, f"Failed to create test section: {response.text}"
    
    return response.json()


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    """Register and login an admin, return auth token"""
    # Register admin
    admin_data = {
        "username": "test_admin",
        "password": "admin123",
        "email": "admin@test.com",
        "full_name": "Test Admin",
        "role_id": 3  # Admin role
    }
    
    # Try to register (may already exist)
    response = await client.post("/auth/register", json=admin_data)
    
    # Login to get token
    login_data = {
        "username": "test_admin",
        "password": "admin123"
    }
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    
    token_data = response.json()
    return token_data["access_token"]


@pytest_asyncio.fixture
async def admin_headers(admin_token: str) -> Dict[str, str]:
    """Get authorization headers for admin"""
    return {"Authorization": f"Bearer {admin_token}"}
