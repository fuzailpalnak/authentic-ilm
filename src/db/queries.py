import json
import re
import uuid
from typing import AsyncGenerator, Union, Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.models import CourseRequest, ErrorResponse, CourseResponse, SessionRequest
from src.db.schema import Professor, Pathway, Topic, Course, Session, Media
from src.exceptions import (
    CourseAlreadyExistsError,
    CourseNotFoundError,
    EntityAlreadyExistsError,
    DatabaseError,
    EntityNotFoundError,
)

from sqlalchemy.exc import SQLAlchemyError


async def get_or_create_entity(db: AsyncSession, model: Any, name: str, *kwargs):
    """Fetch an entity by name or insert it if it doesn't exist."""
    try:
        entity = await _fetch_entity(db, model, name)
        return entity
    except EntityNotFoundError:
        entity = await _insert_entity(db, model, name, *kwargs)
        return entity


async def _insert_entity(
    db: AsyncSession, model: Any, name: str, **kwargs
) -> Union[Pathway, Topic]:
    """Insert a new entity into the database."""
    try:
        id_value = generate_id(name)
        entity = model(id=id_value, name=name, **kwargs)
        db.add(entity)
        await db.commit()
        await db.refresh(entity)

        return entity
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(f"Error inserting {model.__name__}: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise e


async def _fetch_entity(
    db: AsyncSession, model: Any, name: str
) -> Union[Pathway, Topic]:
    """Fetch an entity by name."""
    try:
        result = await db.execute(select(model).filter(model.name == name))
        entity = result.scalars().first()
        if not entity:
            raise EntityNotFoundError(model.__name__, name)
        return entity
    except SQLAlchemyError as e:
        raise DatabaseError(
            f"Error fetching {model.__name__} by name '{name}': {str(e)}"
        )
    except Exception as e:
        raise e


def generate_id(name: str) -> str:
    """Generate a unique ID based on name and a random 4-digit identifier."""
    initials = "".join(
        [part[0].upper() for part in re.split(r"\W+|\s+", name.strip()) if part]
    )
    random_uuid = str(uuid.uuid4().int)[:4]
    return f"{initials}{random_uuid}"


async def stream_courses_by_filter(
    db: AsyncSession, filter_by: str, value: str
) -> AsyncGenerator[str, None]:
    """Fetch courses filtered by professor or topic name."""
    try:
        # Determine model and fetch entity by filter type
        model = Professor if filter_by == "professor" else Topic
        entity = await _fetch_entity(db, model, value)

        # Fetch courses related to the entity
        result = await db.execute(
            select(Course)
            .options(
                joinedload(Course.professor),
                joinedload(Course.sessions).joinedload(Session.media),
            )
            .where(getattr(Course, f"{filter_by}_id") == entity.id)
        )
        courses = result.unique().scalars().all()

        # Stream courses
        for course in courses:
            yield await course_to_response(course)

    except ValueError as e:
        yield ErrorResponse(error=str(e)).model_dump_json() + "\n"


async def course_to_response(course) -> str:
    """Transform course object to response format."""
    return (
        CourseResponse(
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
        ).model_dump_json()
        + "\n"
    )


async def stream_courses_on_prof_and_topic(
    db: AsyncSession, professor_name: str, topic_name: str
) -> AsyncGenerator[str, None]:
    """Stream courses based on professor name and topic name."""
    try:
        # Fetch professor and topic
        professor = await _fetch_entity(db, Professor, professor_name)
        topic = await _fetch_entity(db, Topic, topic_name)

        # Fetch courses that match the professor and topic IDs
        result = await db.execute(
            select(Course)
            .options(
                joinedload(Course.professor),
                joinedload(Course.sessions).joinedload(Session.media),
            )
            .filter(Course.professor_id == professor.id, Course.topic_id == topic.id)
        )
        courses = result.unique().scalars().all()

        # Stream course responses
        for course in courses:
            yield await course_to_response(course)

    except ValueError as e:
        yield ErrorResponse(error=str(e)).model_dump_json() + "\n"


async def insert_course(db: AsyncSession, request: CourseRequest):
    """Insert a new course with associated professor, topic, and pathway."""
    try:

        pathway = await get_or_create_entity(db, Pathway, request.pathway_name)
        professor = await get_or_create_entity(
            db,
            request.professor_name,
            email=request.professor_email,
            pathway_id=pathway.id,
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


async def insert_session(db: AsyncSession, request: SessionRequest):
    """Add new sessions and media to an existing course."""
    try:
        professor = await _fetch_entity(db, Professor, request.professor_name)
        topic = await _fetch_entity(db, Topic, request.topic_name)

        course_id = f"{professor.id}-{topic.id}"

        existing_course = await db.execute(
            select(Course).filter(Course.id == course_id)
        )
        existing_course = existing_course.unique().scalars().first()

        if not existing_course:
            raise CourseNotFoundError(f"Course {course_id} not found.")

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
                media_id = f"{session_id}-{media_data.type}"
                media = Media(
                    id=media_id,
                    session=session,
                    type=media_data.type,
                    url=media_data.url,
                )
                media_objects.append(media)

        db.add_all(session_objects + media_objects)
        await db.commit()

        return {
            "message": "New sessions and media added successfully",
            "course_id": course_id,
        }

    except Exception as e:
        await db.rollback()
        raise e
