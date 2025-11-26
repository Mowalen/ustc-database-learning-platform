import pytest
from httpx import AsyncClient
from typing import Dict

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, admin_headers: Dict[str, str]):
    user_data = {
        "username": "new_user",
        "password": "password123",
        "email": "new_user@test.com",
        "full_name": "New User",
        "role_id": 1
    }
    
    response = await client.post(
        "/admin/users",
        json=user_data,
        headers=admin_headers
    )
    
    if response.status_code == 400 and "already registered" in response.text:
        # User might already exist from previous tests
        pass
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, admin_headers: Dict[str, str]):
    # First create a user (or ensure one exists)
    user_data = {
        "username": "update_user_test",
        "password": "password123",
        "email": "update_user@test.com",
        "full_name": "Update User",
        "role_id": 1
    }
    create_res = await client.post("/admin/users", json=user_data, headers=admin_headers)
    if create_res.status_code == 200:
        user_id = create_res.json()["id"]
    else:
        # Try to login to get ID if already exists? Or just fail if not 200/400
        # For simplicity, let's assume we can query or it succeeds.
        # If it failed because it exists, we need to find it. 
        # But we don't have a get_user_by_username endpoint exposed to admin easily here without listing all.
        # Let's just use a unique username
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        user_data["username"] = f"update_user_{unique_suffix}"
        user_data["email"] = f"update_{unique_suffix}@test.com"
        create_res = await client.post("/admin/users", json=user_data, headers=admin_headers)
        assert create_res.status_code == 200
        user_id = create_res.json()["id"]

    update_data = {
        "full_name": "Updated Name",
        "is_active": True
    }
    
    response = await client.put(
        f"/admin/users/{user_id}",
        json=update_data,
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]

@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, admin_headers: Dict[str, str]):
    # Create a user to delete
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"delete_user_{unique_suffix}",
        "password": "password123",
        "email": f"delete_{unique_suffix}@test.com",
        "full_name": "Delete User",
        "role_id": 1
    }
    create_res = await client.post("/admin/users", json=user_data, headers=admin_headers)
    assert create_res.status_code == 200
    user_id = create_res.json()["id"]
    
    response = await client.delete(
        f"/admin/users/{user_id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False

@pytest.mark.asyncio
async def test_create_announcement(client: AsyncClient, admin_headers: Dict[str, str]):
    announcement_data = {
        "title": "Test Announcement",
        "content": "This is a test announcement"
    }
    
    response = await client.post(
        "/admin/announcements",
        json=announcement_data,
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == announcement_data["title"]
    assert data["content"] == announcement_data["content"]

@pytest.mark.asyncio
async def test_list_announcements(client: AsyncClient, admin_headers: Dict[str, str]):
    await test_create_announcement(client, admin_headers)
    
    response = await client.get(
        "/admin/announcements",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
