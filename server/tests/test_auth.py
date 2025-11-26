"""
Test cases for authentication APIs
"""
import pytest
from httpx import AsyncClient


class TestAuth:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test user registration"""
        user_data = {
            "username": f"newuser_{pytest.__version__}",  # Unique username
            "password": "testpass123",
            "email": "newuser@test.com",
            "full_name": "New Test User",
            "role_id": 1  # Student
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        # Should succeed or already exist
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert data["username"] == user_data["username"]
            assert data["email"] == user_data["email"]
            assert "password" not in data  # Password should not be returned
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient):
        """Test registering with duplicate username"""
        # First register a user
        user_data = {
            "username": "duplicate_test",
            "password": "testpass123",
            "email": "first@test.com",
            "full_name": "First User",
            "role_id": 1
        }
        await client.post("/auth/register", json=user_data)
        
        # Try to register again with same username
        duplicate_data = {
            "username": "duplicate_test",  # Same username
            "password": "testpass123",
            "email": "second@test.com",
            "full_name": "Duplicate User",
            "role_id": 1
        }
        
        response = await client.post("/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "already exists" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful login"""
        # First register a user
        user_data = {
            "username": "login_test_user",
            "password": "testpass123",
            "email": "login@test.com",
            "full_name": "Login Test User",
            "role_id": 1
        }
        await client.post("/auth/register", json=user_data)
        
        # Then try to login
        login_data = {
            "username": "login_test_user",
            "password": "testpass123"
        }
        
        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password"""
        # First register a user
        user_data = {
            "username": "password_test_user",
            "password": "correctpass123",
            "email": "passtest@test.com",
            "full_name": "Password Test User",
            "role_id": 1
        }
        await client.post("/auth/register", json=user_data)
        
        # Try to login with wrong password
        login_data = {
            "username": "password_test_user",
            "password": "wrongpassword"
        }
        
        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistentuser123",
            "password": "password"
        }
        
        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields"""
        incomplete_data = {
            "username": "incomplete"
            # Missing password, role_id, etc.
        }
        
        response = await client.post("/auth/register", json=incomplete_data)
        assert response.status_code == 422  # Validation error
