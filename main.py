import json
from typing import List
from fastapi import FastAPI, Query
from pydantic import BaseModel
from database import Database
import uvicorn

from fastapi.testclient import TestClient


app = FastAPI()

db = Database("mongodb://localhost:27017", "kimo", "courses")
db.create_index("name_index", [("name", 1)])
db.create_index("date_index", [("date", -1)])

if not db.collection.count_documents({}):
    with open("courses.json", "r") as f:
        data = json.load(f)
    db.insert_many(data)
    print("Data inserted successfully.")


class Chapter(BaseModel):
    name: str
    contents: str
    rating: int


class Course(BaseModel):
    name: str
    date: int
    description: str
    domain: List[str]
    chapters: List[Chapter]
    rating: int


@app.get("/courses")
async def get_courses(mode: str = Query(..., description="Mode of retrieval")):
    if mode == "alphabetical":
        command = {"type": "find", "query": {}, "sort": [("name", 1)]}
    elif mode == "date":
        command = {"type": "find", "query": {}, "sort": [("date", -1)]}
    elif mode == "rating":
        command = {"type": "find", "query": {}, "sort": [("rating", -1)]}
    else:
        return {"error": "Invalid mode"}
    
    result = db.execute_command(command)
    courses = [doc["name"] for doc in result]
    return {"courses": courses}


@app.get("/course_overview/{course_name}")
async def get_course_overview(course_name: str):
    command = {"type": "find", "query": {"name": course_name}}
    result = db.execute_command(command)
    course = next(result, None)
    if not course:
        return {"error": "Course not found"}
    description = course.get("description")

    return description


@app.get("/chapter_info/{course_name}/{chapter_name}")
async def get_chapter_info(course_name: str, chapter_name: str):
    command = {"type": "find", "query": {"name": course_name}}
    result = db.execute_command(command)
    course = next(result, None)
    if not course:
        return {"error": "Course not found"}

    chapters = course.get("chapters", [])
    chapter_text = next(
        (c["text"] for c in chapters if c.get("name") == chapter_name), None
    )
    if not chapter_text:
        return {"error": "Chapter not found"}

    return chapter_text


@app.post("/rate_chapter/{course_name}/{chapter_name}/{rating}")
async def rate_chapter(course_name: str, chapter_name: str, rating: int):
    if rating not in [-1, 1]:
        return {
            "error": "Invalid rating. Only positive (1) and negative (-1) ratings are allowed."
        }

    command = {"type": "find", "query": {"name": course_name}}
    result = db.execute_command(command)
    course = next(result, None)
    if not course:
        return {"error": "Course not found"}

    chapters = course.get("chapters", [])
    chapter = next((c for c in chapters if c.get("name") == chapter_name), None)
    if not chapter:
        return {"error": "Chapter not found"}

    chapter["rating"] = rating

    chapter_ratings = [ch.get("rating", 0) for ch in chapters]
    course_rating = (
        sum(chapter_ratings) / len(chapter_ratings) if chapter_ratings else 0
    )
    course["rating"] = course_rating

    db.collection.replace_one({"name": course_name}, course)

    return {
        "message": "Chapter rating added successfully",
        "course_rating": course_rating,
    }


@app.on_event("shutdown")
def shutdown_event():
    db.close_connection()


def debug_endpoint():
    client = TestClient(app)
    response = client.get(
        "/chapter_info/Highlights%20of%20Calculus/Big%20Picture%20of%20Calculus"
    )

    print(response.status_code)
    print(response.json())


# debug_endpoint()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000)
