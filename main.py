from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.conn import get_db
from src.db.queries import (
    stream_courses,
    insert_course,
)
from src.models import CourseRequest
from fastapi.responses import StreamingResponse
from loguru import logger

app = FastAPI()


# Endpoint for inserting new data
@app.post("/add_course/")
async def add_course(course: CourseRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await insert_course(db, course)
        return response
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")


# Endpoint to get courses by topic
@app.get("/courses/topic/{topic_name}")
async def get_courses_by_topic(topic_name: str, db: AsyncSession = Depends(get_db)):
    try:
        return StreamingResponse(
            stream_courses(filter_by="topic", filter_value=topic_name, db=db),
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
            stream_courses(filter_by="professor", filter_value=prof_name, db=db),
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")
