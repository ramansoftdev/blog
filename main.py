from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostCreate, PostResponse , UserCreate, UserResponse

from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
app.mount("/media",StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")

# posts:list[dict] = [
#     {
#         "id": 1,
#         "title": "My First Post",
#         "author": "Ravi Kumar",
#         "content": "This is the content of the first post.",
#         "date_posted": "2023-10-27"
#     },
#     {
#         "id": 2,
#         "title": "Exploring FastAPI",
#         "author": "Priya Sharma",
#         "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.",
#         "date_posted": "2023-10-28"
#     }
# ]


@app.get("/", include_in_schema=False)
def home(request:Request):
    return templates.TemplateResponse(
    request,
    "default.html",{
    "greeting":"Welcome to the samvaad blogs",
    "message": " checkout our platform for more blogs"
    },
    status_code = status.HTTP_200_OK,
    )

@app.get("/posts", include_in_schema=False)
def get_posts_html(request:Request, db:Annotated[Session, Depends(get_db)] ):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(request,"posts.html", 
        {
            "posts":posts,
            "title":"all posts"
        })

@app.get("/posts/{post_id}", include_in_schema=False)
def get_post_html(request:Request, post_id:int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        title = post.title[:50]
        return templates.TemplateResponse(request,"post.html",
        {
            "post":post,
            "title":title
        })
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/users/{user_id}/posts", include_in_schema=False)
def get_user_posts_html(request:Request, user_id:int,db:Annotated[Session, Depends(get_db)]):
    result = db.execute(
    select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
    
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(request,"user_posts.html",
    {
        "posts":posts,
        "title":"user posts"
    })


@app.post(
        "/api/users",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED
)
def create_user(user:UserCreate, db:Annotated[Session, Depends(get_db)]):
    
    result = db.execute(
        select(models.User).where(models.User.username == user.username),
        )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    result = db.execute(
        select(models.User).where(models.User.email == user.email),
        )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id:int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(
    select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()

    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")



@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id:int,db:Annotated[Session, Depends(get_db)]):
    result = db.execute(
    select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
    
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db:Annotated[Session, Depends(get_db)]):
    result = db.execute(
    select(models.Post)
    )
    posts = result.scalars().all()
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id:int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(
    select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post(
        "/api/posts",
        response_model=PostResponse,
        status_code=status.HTTP_201_CREATED
)
def create_post(post:PostCreate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == post.user_id),
        )
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id = post.user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

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