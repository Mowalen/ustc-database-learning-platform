"""
Test cases for user APIs
"""
import pytest
from httpx import AsyncClient
from typing import Dict


class TestUsers:
    """Test user management endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_me(self, client: AsyncClient, teacher_headers: Dict[str, str]):
        """Test getting current user info"""
        response = await client.get("/users/me", headers=teacher_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "username" in data
        assert data["username"] == "test_teacher"
        assert "password" not in data  # Password should not be exposed
        assert "password_hash" not in data
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting user info without authentication"""
        response = await client.get("/users/me")
        
        assert response.status_code == 401  # Unauthorized
    
    @pytest.mark.asyncio
    async def test_update_user_me(self, client: AsyncClient, student_headers: Dict[str, str]):
        """Test updating current user info"""
        update_data = {
            "full_name": "Updated Student Name",
            "email": "updated_student@test.com"
        }
        
        response = await client.put("/users/me", json=update_data, headers=student_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == update_data["full_name"]
        assert data["email"] == update_data["email"]
    
    @pytest.mark.asyncio
    async def test_update_user_password(self, client: AsyncClient, student_headers: Dict[str, str]):
        """Test updating user password"""
        # Note: This test updates password but we can't easily verify it changed
        # without logging out and back in
        update_data = {
            "password": "newpassword123"
        }
        
        response = await client.put("/users/me", json=update_data, headers=student_headers)
        
        # Should succeed
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_update_user_invalid_token(self, client: AsyncClient):
        """Test updating user with invalid token"""
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        update_data = {
            "full_name": "Should Not Work"
        }
        
        response = await client.put("/users/me", json=update_data, headers=invalid_headers)
        
        assert response.status_code == 403  # Forbidden
