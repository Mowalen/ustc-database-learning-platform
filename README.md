# USTC Database Learning Platform

A comprehensive platform for database learning, featuring course management, task submissions, and automated grading.

## 📚 Documentation
- [Cloud Documentation (Feishu)](https://sh6uqljbln.feishu.cn/wiki/F0tRwBQl4itZ6RkSgbtcBRv9nI6?from=from_copylink)

## 🏗 Project Structure

This repository contains:
- **`server/`**: The backend API service built with FastAPI.
- **`web/`**: The frontend web application (Under Development).

---

## 🚀 Backend (Server)

The backend provides a RESTful API for managing the platform's core functionalities, including authentication, course management, and student performance tracking.

### 🛠 Tech Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Testing**: [pytest](https://docs.pytest.org/)

### ✨ Key Features
- **Authentication**: JWT-based auth with role management (Student, Teacher, Admin).
- **Course Management**: Create and manage courses, sections, and enrollments.
- **Task System**: Assign tasks, accept submissions, and grade student work.
- **Announcements**: System-wide or course-specific announcements.
- **Score Tracking**: Track and export student scores.

### ⚡ Quick Start

#### 1. Prerequisites
- Python 3.13+
- `uv` package manager installed

#### 2. Installation
Navigate to the server directory and set up the environment:

```bash
cd server

# Create virtual environment
uv venv --python python3.13

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
uv sync
```

#### 3. Configuration
Configure your environment variables. Copy the example file:

```bash
cp .env.example .env
```

Edit `.env` to set your database connection string (`DATABASE_URL`) and `SECRET_KEY`.
Default database URL (MySQL): `mysql+aiomysql://root:password@localhost:3306/ustc_db`

#### 4. Running the Server
Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 🧪 Testing
Run the test suite to ensure everything is working correctly:

```bash
cd server
uv run pytest
```

---

## 🌐 Frontend (Web)

*Documentation for the frontend will be added once initialization is complete.*

