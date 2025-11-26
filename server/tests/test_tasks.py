import pytest
from httpx import AsyncClient
from typing import Dict

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": "2024-12-31T23:59:59",
        "total_score": 100
    }
    
    response = await client.post(
        f"/courses/{test_course['id']}/tasks",
        json=task_data,
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["course_id"] == test_course["id"]
    return data

@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
    # First create a task
    await test_create_task(client, teacher_headers, test_course)
    
    response = await client.get(
        f"/courses/{test_course['id']}/tasks",
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, teacher_headers: Dict[str, str], test_course: Dict):
    # Create a task
    created_task = await test_create_task(client, teacher_headers, test_course)
    task_id = created_task["id"]
    
    response = await client.get(
        f"/tasks/{task_id}",
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == created_task["title"]

@pytest.mark.asyncio
async def test_submit_task(client: AsyncClient, student_headers: Dict[str, str], teacher_headers: Dict[str, str], test_course: Dict):
    # Create a task as teacher
    created_task = await test_create_task(client, teacher_headers, test_course)
    task_id = created_task["id"]
    
    # Submit task as student
    submission_data = {
        "content": "My submission content"
    }
    
    response = await client.post(
        f"/tasks/{task_id}/submit",
        json=submission_data,
        headers=student_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["content"] == submission_data["content"]
    return data

@pytest.mark.asyncio
async def test_grade_submission(client: AsyncClient, teacher_headers: Dict[str, str], student_headers: Dict[str, str], test_course: Dict):
    # Create task and submission
    submission = await test_submit_task(client, student_headers, teacher_headers, test_course)
    submission_id = submission["id"]
    
    # Grade submission as teacher
    grade_data = {
        "score": 95,
        "feedback": "Good job!"
    }
    
    response = await client.put(
        f"/submissions/{submission_id}/grade",
        json=grade_data,
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == submission_id
    assert data["score"] == grade_data["score"]
    assert data["feedback"] == grade_data["feedback"]
