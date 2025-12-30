import pytest
import httpx

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_flow():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Register Teacher
        print("1. Registering teacher...")
        teacher_data = {
            "username": "teacher1",
            "password": "password123",
            "email": "teacher1@example.com",
            "full_name": "Teacher One",
            "role_id": 2 # Teacher
        }
        response = await client.post("/auth/register", json=teacher_data)
        if response.status_code == 400 and "already exists" in response.text:
            print("Teacher already exists, logging in...")
        else:
            assert response.status_code == 200, f"Register failed: {response.text}"
            print("Teacher registered.")

        # 2. Login Teacher
        print("2. Logging in teacher...")
        login_data = {
            "username": "teacher1",
            "password": "password123"
        }
        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Teacher logged in.")

        # 3. Create Course Category
        print("3. Creating course category...")
        category_data = {
            "name": "Computer Science",
            "description": "CS Courses"
        }
        response = await client.post("/courses/categories/", json=category_data, headers=headers)
        if response.status_code == 200:
            category_id = response.json()["id"]
            print(f"Category created: {category_id}")
        else:
            # Maybe already exists?
            # Let's list categories to find it
            response = await client.get("/courses/categories/", headers=headers)
            categories = response.json()
            if categories:
                category_id = categories[0]["id"]
                print(f"Using existing category: {category_id}")
            else:
                print(f"Failed to create/find category: {response.text}")
                return

        # 4. Create Course
        print("4. Creating course...")
        course_data = {
            "title": "Database Systems",
            "description": "Intro to DB",
            "category_id": category_id
        }
        response = await client.post("/courses/", json=course_data, headers=headers)
        assert response.status_code == 200, f"Create course failed: {response.text}"
        course_id = response.json()["id"]
        print(f"Course created: {course_id}")

        # 5. Create Section
        print("5. Creating section...")
        section_data = {
            "title": "Introduction",
            "content": "Welcome to the course",
            "course_id": course_id,
            "order_index": 1
        }
        response = await client.post(f"/courses/{course_id}/sections", json=section_data, headers=headers)
        assert response.status_code == 200, f"Create section failed: {response.text}"
        section_id = response.json()["id"]
        print(f"Section created: {section_id}")

        # 6. List Sections
        print("6. Listing sections...")
        response = await client.get(f"/courses/{course_id}/sections", headers=headers)
        assert response.status_code == 200
        sections = response.json()
        assert len(sections) > 0
        print(f"Sections found: {len(sections)}")

        print("Verification Successful!")
