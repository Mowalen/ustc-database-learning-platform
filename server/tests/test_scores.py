import pytest
from httpx import AsyncClient
from typing import Dict

@pytest.mark.asyncio
async def test_my_scores(client: AsyncClient, student_headers: Dict[str, str]):
    # Get current user to get ID
    me_res = await client.get("/users/me", headers=student_headers)
    student_id = me_res.json()["id"]
    
    response = await client.get(
        "/me/scores",
        params={"student_id": student_id},
        headers=student_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_course_scores(client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
    response = await client.get(
        f"/courses/{test_course['id']}/scores",
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_export_scores(client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
    response = await client.get(
        f"/courses/{test_course['id']}/scores/export",
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    # Check if content looks like CSV
    assert "," in response.text or len(response.text) == 0 # Empty CSV is possible
