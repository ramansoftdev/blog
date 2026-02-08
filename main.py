
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler,request_validation_exception_handler
import time

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_db
import models
from routers import posts, users

@asynccontextmanager
async def lifespan(_app:FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.mount("/static",StaticFiles(directory="static"),name="static")
app.mount("/media",StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")

#***************************************************middleware*********************************************************

class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to measure request processing time.
    Adds X-Process-Time header to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add custom header with processing time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        # Optional: Log the request for monitoring
        print(f"{request.method} {request.url.path} - {process_time:.4f}s - {response.status_code}")

        return response

# Register middleware
app.add_middleware(RequestTimingMiddleware)

# Function-based logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Simple function-based middleware to log all incoming requests.
    """
    # Get client IP
    client_host = request.client.host if request.client else "unknown"

    # Log incoming request
    print(f"📥 Incoming: {request.method} {request.url.path} from {client_host}")

    # Process request
    response = await call_next(request)

    # Log response status
    status_emoji = "✅" if response.status_code < 400 else "❌"
    print(f"{status_emoji} Response: {response.status_code} for {request.method} {request.url.path}")

    return response

#***************************************************html posts pages*********************************************************
@app.get("/", include_in_schema=False)
async def home(request:Request):
    return templates.TemplateResponse(
    request,
    "default.html",{
    "greeting":"Welcome to the vaada blogs",
    "message": " checkout our platform for more blogs"
    },
    status_code = status.HTTP_200_OK,
    )

@app.get("/posts", include_in_schema=False)
async def get_posts_html(request:Request, db:Annotated[AsyncSession, Depends(get_db)] ):
    result = await db.execute(select(models.Post).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return templates.TemplateResponse(request,"posts.html", 
        {
            "posts":posts,
            "title":"all posts"
        })

@app.get("/posts/{post_id}", include_in_schema=False)
async def get_post_html(request:Request, post_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
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
async def get_user_posts_html(request:Request, user_id:int,db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
    select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
    
    result = await db.execute(select(models.Post).order_by(models.Post.date_posted.desc()).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(request,"user_posts.html",
    {
        "posts":posts,
        "title":"user posts"
    })



app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])

#***************************************************login/register*********************************************************

@app.get("/register",include_in_schema=False)
async def register_page(request:Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title":"Register"}
    )

@app.get("/login",include_in_schema=False)
async def login_page(request:Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title":"login"}
    )




#***************************************************exception handler*********************************************************


@app.exception_handler(StarletteHTTPException)
async def general_exception_handler(request:Request, exception:StarletteHTTPException):


    if request.url.path.startswith("/api"):
        return await http_exception_handler(request,exception)
    else:
        message = (
        exception.detail
        if exception.detail
        else "An error occurred. Pleasecheck your reuest and try again"
        )
            
        return templates.TemplateResponse(
            request,
            "error.html",{
            "status_code":exception.status_code,
            "message": message
            },
            status_code = exception.status_code,
        )
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exception:StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request,exception)
    else:
        return templates.TemplateResponse(
            request,
            "error.html",{
            "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Check your input again!"
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )