from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostCreate, PostResponse

app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates = Jinja2Templates(directory="templates")

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


@app.get("/", include_in_schema=False)
def home():
    return {"message":"namaste fastapi"}


@app.get("/posts", include_in_schema=False)
def get_posts_html(request:Request):
    return templates.TemplateResponse(request,"posts.html", 
        {
            "posts":posts,
            "title":"home"
        })

@app.get("/posts/{post_id}", include_in_schema=False)
def get_post_html(request:Request, post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            title = post['title'][:50]
            return templates.TemplateResponse(request,"post.html",
            {
                "post":post,
                "title":title
            })
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")



@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id:int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post(
        "/api/posts",
        response_model=PostResponse,
        status_code=status.HTTP_201_CREATED
)
def create_post(post:PostCreate):
    new_id=(1 + max(p["id"] for p in posts)) if posts else 1

    new_post={
        "id":new_id,
        "author":post.author,
        "title":post.title,
        "content":post.content,
        "date_posted": datetime.now().strftime("%d %b %Y")
    }

    posts.append(new_post)
    return new_post



@app.exception_handler(StarletteHTTPException)
def general_exception_handler(request:Request, exception:StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Pleasecheck your reuest and try again"
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail":message}
        )
    else:
        return templates.TemplateResponse(
            request,
            "error.html",{
            "status_code":exception.status_code,
            "message": message
            },
            status_code = exception.status_code,
        )
    
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request:Request, exception:StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail":exception.errors()}
        )
    else:
        return templates.TemplateResponse(
            request,
            "error.html",{
            "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Check your input again!"
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )