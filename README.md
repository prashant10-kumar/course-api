# 📚 Course API

A RESTful API for an online learning platform built with **FastAPI** and **SQLAlchemy** — similar to Udemy. Supports two roles: **Instructors** who create and manage courses, and **Students** who browse and enroll in them.

---

## 🚀 Tech Stack

- **FastAPI** — Web framework
- **SQLAlchemy** — ORM
- **SQLite** — Database
- **Pydantic** — Data validation
- **JWT (JSON Web Tokens)** — Authentication
- **Passlib + Bcrypt** — Password hashing

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/prashant10-kumar/course-api.git
cd course-api
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic passlib[bcrypt] python-jose python-dotenv python-multipart
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

API will be live at `http://127.0.0.1:8000`

Interactive docs available at `http://127.0.0.1:8000/docs`

---

## 👤 User Roles

| Role | Permissions |
|---|---|
| `instructor` | Create, update, delete courses and lessons |
| `student` | Browse courses, enroll, view enrolled courses |

---

## 📌 API Endpoints

### Auth

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/register` | Register a new user | ❌ |
| `POST` | `/login` | Login and get JWT token | ❌ |

### Courses

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/courses` | List all courses | ❌ |
| `GET` | `/courses/{course_id}` | Get a course with its lessons | ❌ |
| `POST` | `/courses` | Create a new course | ✅ Instructor |
| `PATCH` | `/course/{id}` | Update a course | ✅ Instructor (owner) |
| `DELETE` | `/course/{id}` | Delete a course | ✅ Instructor (owner) |

### Lessons

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/courses/{course_id}/lessons` | Add a lesson to a course | ✅ Instructor (owner) |
| `DELETE` | `/lesson/{id}` | Delete a lesson | ✅ Instructor (owner) |

### Enrollment & Student

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/courses/{course_id}/enroll` | Enroll in a course | ✅ Student |
| `GET` | `/my-course` | View my enrolled courses | ✅ Student |
| `GET` | `/my-created-courses` | View my created courses | ✅ Instructor |

---

## 🔐 Authentication

This API uses **JWT Bearer Token** authentication.

1. Register via `/register`
2. Login via `/login` — you'll receive an `access_token`
3. Pass the token in the `Authorization` header for protected routes:

```
Authorization: Bearer <your_token>
```

---

## 📂 Project Structure

```
course-api/
│
├── main.py          # All routes and Pydantic schemas
├── models.py        # SQLAlchemy database models
├── auth.py          # JWT creation, hashing, verification
├── database.py      # Database connection and session
└── .env             # Environment variables (not committed)
```

---

## 🗃️ Data Models

### User
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `username` | String | Unique username |
| `password` | String | Hashed password |
| `role` | Enum | `student` or `instructor` |

### Course
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `title` | String | Course title |
| `description` | String | Course description |
| `level` | Enum | `beginner`, `intermediate`, `advanced` |
| `user_id` | ForeignKey | Instructor who owns it |

### Lesson
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `title` | String | Lesson title |
| `duration_time` | Integer | Duration in minutes |
| `order` | Integer | Lesson order in course |
| `course_id` | ForeignKey | Parent course |

### Enrollment
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `user_id` | ForeignKey | Enrolled student |
| `course_id` | ForeignKey | Enrolled course |
| `enrolled_at` | DateTime | Enrollment timestamp |

---

## 🧪 Example Usage

### Register as a student
```json
POST /register
{
  "username": "prashant10",
  "password": "mypassword",
  "role": "student"
}
```

### Login
```json
POST /login
{
  "username": "prashant10",
  "password": "mypassword"
}
```

### Enroll in a course
```
POST /courses/1/enroll
Authorization: Bearer <token>
```

---

## 🛠️ Future Improvements

- [ ] Add pagination to course listing
- [ ] Add course search and filter by level
- [ ] Add lesson progress tracking for students
- [ ] Add ratings and reviews
- [ ] Connect a frontend (React / Next.js)

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.


