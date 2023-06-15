import json
from typing import List
from fastapi import FastAPI
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


class Course(BaseModel):
    name: str
    date: int
    description: str
    domain: List[str]
    chapters: List[Chapter]


@app.get("/courses")
async def get_courses():
    command = {"type": "find", "query": {}, "sort": [("name", 1)]}
    result = db.execute_command(command)
    courses = [doc["name"] for doc in result]
    return {"courses": courses}


@app.get("/course_overview/{course_name}")
async def get_course_overview(course_name: str):
    command = {"type": "find", "query": {"name": course_name}}
    result = db.execute_command(command)
    course_overview = [doc["description"] for doc in result]
    return course_overview


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


@app.on_event("shutdown")
def shutdown_event():
    db.close_connection()


def debug_endpoint():
    client = TestClient(app)
    response = client.get("/chapter_info/Highlights%20of%20Calculus/Big%20Picture%20of%20Calculus")

    print(response.status_code)
    print(response.json())


debug_endpoint()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000)
