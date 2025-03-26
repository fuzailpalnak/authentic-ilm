from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime

from src.db.conn import Base


class Pathway(Base):
    __tablename__ = "pathway"

    id = Column(String(10), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    professors = relationship("Professor", back_populates="pathway")


class Professor(Base):
    __tablename__ = "professors"

    id = Column(String(10), primary_key=True)  # Unique ID for professor
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    pathway_id = Column(
        String(10), ForeignKey("pathway.id", ondelete="CASCADE"), nullable=False
    )

    pathway = relationship("Pathway", back_populates="professors")
    courses = relationship("Course", back_populates="professor")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(10), primary_key=True)  # Unique ID for topic
    name = Column(String(255), unique=True, nullable=False)

    courses = relationship("Course", back_populates="topic")


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(51), primary_key=True)  # Unique ID for course
    title = Column(String(255), nullable=False)
    description = Column(Text)
    professor_id = Column(
        String(10), ForeignKey("professors.id", ondelete="CASCADE"), nullable=False
    )
    topic_id = Column(
        String(10), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )

    professor = relationship("Professor", back_populates="courses")
    topic = relationship("Topic", back_populates="courses")
    sessions = relationship("Session", back_populates="course")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(51), primary_key=True)
    course_id = Column(
        String(51), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    session_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="sessions")
    media = relationship("Media", back_populates="session")


class Media(Base):
    __tablename__ = "media"

    id = Column(String(51), primary_key=True)
    session_id = Column(
        String(51), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(String(50), nullable=False)  # 'youtube', 'pdf', 'live'
    url = Column(Text, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="media")
