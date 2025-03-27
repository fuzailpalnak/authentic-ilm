from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.conn import get_db
from src.db.queries import (
    stream_courses_by_filter,
    insert_course,
    insert_session,
    stream_courses_on_prof_and_topic,
)
from src.models import CourseRequest, SessionRequest
from fastapi.responses import StreamingResponse
from loguru import logger

app = FastAPI()


# Endpoint for inserting new data
@app.post("/add_course")
async def add_course(course: CourseRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await insert_course(db, course)
        return response
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")


# Endpoint for add sessions to existing course
@app.post("/add_session")
async def add_session(session: SessionRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await insert_session(db, session)
        return response
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")


# Endpoint to get courses by topic
@app.get("/courses/topic/{topic_name}")
async def get_courses_by_topic(topic_name: str, db: AsyncSession = Depends(get_db)):
    try:
        return StreamingResponse(
            stream_courses_by_filter(filter_by="topic", value=topic_name, db=db),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")


# Endpoint to get courses by professor
@app.get("/courses/prof/{prof_name}")
async def get_courses_by_professor(prof_name: str, db: AsyncSession = Depends(get_db)):
    try:
        return StreamingResponse(
            stream_courses_by_filter(filter_by="professor", value=prof_name, db=db),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")


@app.get("/courses/{professor_name}/{topic_name}")
async def get_courses_by_professor_and_topic(
    professor_name: str, topic_name: str, db: AsyncSession = Depends(get_db)
):
    try:
        return StreamingResponse(
            stream_courses_on_prof_and_topic(
                db=db, professor_name=professor_name, topic_name=topic_name
            ),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")
