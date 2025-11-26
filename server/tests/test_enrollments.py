import pytest
from httpx import AsyncClient
from typing import Dict

@pytest.mark.asyncio
async def test_enroll_student(client: AsyncClient, student_headers: Dict[str, str], test_course: Dict):
    enrollment_data = {
        "student_id": 0 # This might be ignored by the backend if it takes from token, but the schema requires it? 
                        # Let's check the schema or router. 
                        # Router: async def enroll(course_id: int, payload: EnrollmentCreate, db: AsyncSession = Depends(get_db)):
                        # return await crud_enrollments.enroll_student(db, course_id, payload.student_id)
                        # Wait, the payload has student_id. But usually students enroll themselves. 
                        # If the API allows passing student_id, it might be for admins/teachers?
                        # Or maybe the student passes their own ID?
                        # Let's assume for now we need to pass a valid student ID.
                        # But we don't have the student ID easily in the fixture unless we parse the token or return it.
                        # The student_token fixture returns the token. 
                        # Let's fetch "me" first to get the ID.
    }
    
    # Get current user to get ID
    me_res = await client.get("/users/me", headers=student_headers)
    assert me_res.status_code == 200
    student_id = me_res.json()["id"]
    
    enrollment_data["student_id"] = student_id
    
    response = await client.post(
        f"/courses/{test_course['id']}/enroll",
        json=enrollment_data,
        headers=student_headers
    )
    
    if response.status_code == 400 and "already enrolled" in response.text:
        pass
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == student_id
        assert data["course_id"] == test_course["id"]

@pytest.mark.asyncio
async def test_my_enrollments(client: AsyncClient, student_headers: Dict[str, str], test_course: Dict):
    # Ensure enrolled
    await test_enroll_student(client, student_headers, test_course)
    
    # Get current user to get ID
    me_res = await client.get("/users/me", headers=student_headers)
    student_id = me_res.json()["id"]
    
    response = await client.get(
        "/me/enrollments",
        params={"student_id": student_id}, # The router expects student_id as query param?
        # Router: async def my_enrollments(student_id: int, db: AsyncSession = Depends(get_db)):
        # It seems it expects it as a query param.
        headers=student_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check if the test course is in the list
    course_ids = [e["course"]["id"] for e in data]
    assert test_course["id"] in course_ids

@pytest.mark.asyncio
async def test_course_students(client: AsyncClient, teacher_headers: Dict[str, str], student_headers: Dict[str, str], test_course: Dict):
    # Ensure a student is enrolled
    await test_enroll_student(client, student_headers, test_course)
    
    response = await client.get(
        f"/courses/{test_course['id']}/students",
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_drop_course(client: AsyncClient, student_headers: Dict[str, str], test_course: Dict):
    # Ensure enrolled
    await test_enroll_student(client, student_headers, test_course)
    
    # Get current user to get ID
    me_res = await client.get("/users/me", headers=student_headers)
    student_id = me_res.json()["id"]
    
    drop_data = {
        "student_id": student_id
    }
    
    response = await client.post(
        f"/courses/{test_course['id']}/drop",
        json=drop_data,
        headers=student_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == student_id
    assert data["course_id"] == test_course["id"]
