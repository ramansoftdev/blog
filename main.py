from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

posts:list[dict] = [
    {
        "id": 1,
        "title": "My First Post",
        "author": "Ravi Kumar",
        "content": "This is the content of the first post.",
        "date_posted": "2023-10-27"
    },
    {
        "id": 2,
        "title": "Exploring FastAPI",
        "author": "Priya Sharma",
        "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.",
        "date_posted": "2023-10-28"
    }
]

@app.get("/posts", response_class = HTMLResponse, include_in_schema=False)
def get_posts_html():
    return f"<h1>{posts[0]['title']}</h1>"

@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/")
def home():
    return {"message":"namaste fastapi"}
