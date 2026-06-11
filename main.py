from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.orm import Session, joinedload
import models
import auth
from models import UserRole, CourseLevel
from database import SessionLocal, engine

class UserCreate(BaseModel):
    username : str = Field(min_length = 6)
    password : str = Field(min_length = 8)
    role : UserRole

    model_config = {"use_enum_values": True}

class Token(BaseModel):
    access_token : str
    token_type : str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

class CourseCreate(BaseModel):
    title : str = Field(min_length = 3)
    description : str = Field(min_length = 20)
    level : CourseLevel

class CourseUpdate(BaseModel):
    title : str = Field(min_length = 3)
    description : str = Field(min_length = 20)
    level : CourseLevel

class CourseResponse(BaseModel):
    id : int
    title : str
    description : str
    level : CourseLevel

    class Config:
        from_attributes = True


class LessonsCreate(BaseModel):
    title : str = Field(min_length = 2)
    duration_time : int = Field(gt = 0)

class LessonsUpdate(BaseModel):
    title : str = Field(min_length = 2)
    duration_time : int = Field(gt = 0)

class LessonResponse(BaseModel):
    id : int
    title : str
    duration_time : int
    order : int

    class Config:
        from_attributes = True


class CourseWithLesson(BaseModel):
    id: int
    title: str
    description: str
    level: str
    lesson: List[LessonResponse]

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token : str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = auth.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid or expired token"
        )
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()
    if user is None:
        raise HTTPException(
            status_code = 401,
            detail = "User not found"
        )
    return user 

def get_current_instructor(current_user: models.User = Depends(get_current_user)):
    if current_user.role != UserRole.instructor:
        raise HTTPException(
            status_code=403,
            detail="Only instructors can perform this action"
        )
    return current_user

def get_current_student(current_user : models.User = Depends(get_current_user)):
    if current_user.role != UserRole.student:
        raise HTTPException(
            status_code = 403,
            detail = "Only student can perform this action"
        )
    return current_user
          
@app.post("/register")
def register(user: UserCreate, db : Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code = 400, 
            detail = "Username already exists"
        )
    hashed = auth.hash_password(user.password)
    new_user = models.User(username = user.username, password = hashed, role = user.role)
    db.add(new_user)
    db.commit()
    return {"message" : "User registered successfully"}

@app.post("/login", response_model = Token)
def login(from_data : OAuth2PasswordRequestForm = Depends(), 
          db : Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == from_data.username
    ).first()
    
    if not user or not auth.verify_password(from_data.password, user.password):
        raise HTTPException(
            status_code = 401, 
            detail = "Invalid credentials"
        )
    token = auth.create_access_token(data = {"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/courses", response_model = List[CourseResponse])
def view_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@app.post("/courses", response_model = CourseResponse)
def add_course(course: CourseCreate, 
               db : Session = Depends(get_db), 
               current_user : models.User = Depends(get_current_instructor)):
    
    new_course = models.Course(title = course.title, 
                               description = course.description,
                               level = course.level,
                               user_id = current_user.id)
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.get("/courses/{course_id}", response_model=CourseWithLesson)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).options(
        joinedload(models.Course.lesson)
    ).filter(
        models.Course.id == course_id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/courses/{course_id}/lessons", response_model = LessonResponse)
def add_lesson(course_id : int,lesson : LessonsCreate, 
               db : Session = Depends(get_db), 
               current_user : models.User = Depends(get_current_instructor)):
    course = db.query(models.Course).filter(models.Course.id == course_id,
                                             models.Course.user_id == current_user.id).first()
   
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson_count = db.query(models.Lesson).filter(models.Lesson.course_id == course_id).count()
    order = lesson_count + 1
    new_lesson = models.Lesson(title = lesson.title,
                               duration_time = lesson.duration_time,
                               course_id = course_id,
                               order = order)
    
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson

@app.patch("/course/{id}", response_model = CourseResponse)
def updt_course(id : int, update : CourseUpdate,
                db : Session = Depends(get_db),
                current_user : models.User = Depends(get_current_instructor)):
    course = db.query(models.Course).filter(models.Course.id == id, 
                                            models.Course.user_id == current_user.id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.level = update.level
    course.title = update.title
    course.description = update.description
    db.commit()
    db.refresh(course)
    return course

@app.delete("/course/{id}")
def del_course(id : int, 
               db : Session = Depends(get_db),
               current_user : models.User = Depends(get_current_instructor)):
    course = db.query(models.Course).filter(models.Course.id == id, models.Course.user_id == current_user.id).first()
    
    if not course:
        raise HTTPException(status_code = 404, detail = "Course Not Found")
    db.delete(course)
    db.commit()
    return {"message": f"Course with id {id} deleted successfully"}

@app.delete("/lesson/{id}")
def del_lesson(id : int, 
               db : Session = Depends(get_db),
               current_user : models.User = Depends(get_current_instructor)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == id).first()
    if not lesson:
        raise HTTPException(status_code = 404, detail = "Lesson Not Found")
    
    course = db.query(models.Course).filter(
        models.Course.id == lesson.course_id,
        models.Course.user_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(lesson)
    db.commit()
    return {"message": f"Lesson with id {id} deleted successfully"}

@app.get("/my-course", response_model = List[CourseResponse])
def my_enrolled_courses(db : Session = Depends(get_db),
                        current_user : models.User = Depends(get_current_student)):
    my_courses = db.query(models.Course).join(models.Enrollment).filter(
        models.Enrollment.uesr_id == current_user.id
    ).all()
    return my_courses

@app.get("/my-created-courses", response_model = List[CourseResponse])
def my_crested_courses(db : Session = Depends(get_db),
                       current_user : models.User = Depends(get_current_instructor)):
    
    my_courses = db.query(models.Course).filter(
        models.Course.user_id == current_user.id
    ).all()
    return my_courses