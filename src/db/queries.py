import json
import re
import uuid
from typing import AsyncGenerator, Optional, Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.models import CourseRequest, ErrorResponse, CourseResponse
from src.db.schema import Professor, Pathway, Topic, Course, Session, Media
from src.exceptions import CourseAlreadyExistsError


async def get_or_create_entity(db: AsyncSession, model: Any, name: str):
    """Generic function to get or create a database entity."""
    result = await db.execute(select(model).filter(model.name == name))
    entity = result.scalars().first()
    if not entity:
        id_value = generate_id(name)
        entity = model(id=id_value, name=name)
        db.add(entity)
        await db.commit()
        await db.refresh(entity)
    return entity


async def get_or_create_professor(
    db: AsyncSession, name: str, email: str, pathway_id: str
):
    """Fetch or create a professor."""
    result = await db.execute(select(Professor).filter(Professor.email == email))
    professor = result.scalars().first()
    if not professor:
        professor = Professor(
            id=generate_id(name), name=name, email=email, pathway_id=pathway_id
        )
        db.add(professor)
        await db.commit()
        await db.refresh(professor)
    return professor


def generate_id(name: str) -> str:
    """Generate a unique ID based on name and a random 4-digit identifier."""
    initials = "".join(
        [part[0].upper() for part in re.split(r"\W+|\s+", name.strip()) if part]
    )
    random_uuid = str(uuid.uuid4().int)[:4]
    return f"{initials}{random_uuid}"


async def stream_courses(
    db: AsyncSession, filter_by: str, value: str
) -> AsyncGenerator[str, None]:
    """Stream courses filtered by professor name or topic name."""
    model = Professor if filter_by == "professor" else Topic
    result = await db.execute(select(model).where(getattr(model, "name") == value))
    entity = result.scalars().first()
    if not entity:
        yield ErrorResponse(
            error=f"{filter_by.capitalize()} not found"
        ).model_dump_json() + "\n"
        return

    result = await db.execute(
        select(Course)
        .options(
            joinedload(Course.professor),
            joinedload(Course.sessions).joinedload(Session.media),
        )
        .where(getattr(Course, f"{filter_by}_id") == entity.id)
    )
    courses = result.unique().scalars().all()

    for course in courses:
        yield CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            professor={"id": course.professor.id, "name": course.professor.name},
            sessions=[
                {
                    "session_number": session.session_number,
                    "title": session.title,
                    "description": session.description,
                    "media": [
                        {"type": media.type, "url": media.url}
                        for media in session.media
                    ],
                }
                for session in course.sessions
            ],
        ).model_dump_json() + "\n"


async def insert_course(db: AsyncSession, request: CourseRequest):
    """Insert a new course with associated professor, topic, and pathway."""
    try:

        pathway = await get_or_create_entity(db, Pathway, request.pathway_name)
        professor = await get_or_create_professor(
            db, request.professor_name, request.professor_email, pathway.id
        )
        topic = await get_or_create_entity(db, Topic, request.topic_name)

        course_id = f"{professor.id}-{topic.id}"

        existing_course = await db.execute(
            select(Course).filter(Course.id == course_id)
        )
        existing_course = existing_course.unique().scalars().first()

        if existing_course:
            raise CourseAlreadyExistsError(existing_course.id)

        course = Course(
            id=course_id,
            title=request.course_title,
            description=request.course_description,
            professor_id=professor.id,
            topic_id=topic.id,
        )
        db.add(course)

        session_objects = []
        media_objects = []
        for session_data in request.sessions:
            session_id = f"{course_id}-{session_data.session_number}"
            session = Session(
                id=session_id,
                course_id=course_id,
                session_number=session_data.session_number,
                title=session_data.title,
                description=session_data.description,
            )
            session_objects.append(session)

            for media_data in session_data.media:
                media_objects.append(
                    Media(
                        id=f"{session_id}-{media_data.type}",
                        session=session,
                        type=media_data.type,
                        url=media_data.url,
                    )
                )

        db.add_all(session_objects + media_objects)
        await db.commit()

        return {"message": "Course added successfully", "course_id": course_id}
    except Exception as e:
        await db.rollback()
        raise e
