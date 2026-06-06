from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import Enum
import enum

class UserRole(enum.Enum):
    student = "student"
    instructor = "instructor"

class CourseLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    username = Column(String , nullable = False)
    password = Column(String, nullable = False)
    role = Column(Enum(UserRole), nullable = False)
    course = relationship("Course" , back_populates = "owner") 
    enrollment = relationship("Enrollment", back_populates = "owner")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    description = Column(String, nullable = False)
    level = Column(Enum(CourseLevel), nullable = False)
    user_id = Column(Integer ,ForeignKey("users.id"), nullable = False)
    owner = relationship("User", back_populates = "course")
    lesson = relationship("Lesson" , back_populates = "course")
    enrolled = relationship("Enrollment", back_populates = "course")


class Lesson(Base):
    __tablename__ ="lessons"
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    duration_minutes = Column(Integer, nullable = False)
    order = Column(Integer, index = True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable = False)
    course = relationship("Course", back_populates = "lesson")

class Enrollment(Base):
     __tablename__ = "enrollment"

     id = Column(Integer, primary_key = True, index = True)
     user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
     course_id = Column(Integer, ForeignKey("courses.id"), nullable = False)
     enrolled_at = Column(DateTime, default = datetime.utcnow) 
     owner = relationship("User", back_populates = "enrollment")
     course = relationship("Course", back_populates = "enrolled")