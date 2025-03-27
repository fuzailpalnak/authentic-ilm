from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class Media(BaseModel):
    type: str
    url: str


# Pydantic Model for Session
class Session(BaseModel):
    session_number: int
    title: str
    description: str
    media: List[Media]


class CourseRequest(BaseModel):
    professor_name: str
    professor_email: str
    pathway_name: str
    topic_name: str
    course_title: str
    course_description: str
    sessions: List[Session]


class ErrorResponse(BaseModel):
    error: str


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    professor: dict
    sessions: list


class SessionRequest(BaseModel):
    professor_name: str
    topic_name: str
    sessions: List[Session]
