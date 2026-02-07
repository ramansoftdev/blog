# FastAPI Blog Application

A modern blog platform built with FastAPI, featuring JWT authentication, server-side rendering, and RESTful API endpoints.

## Features

- **Full CRUD Operations** - Create, read, update, and delete users and posts
- **JWT Authentication** - Secure token-based authentication with OAuth2
- **Authorization** - User-specific permissions for creating, updating, and deleting content
- **Dual Interface** - Server-side rendered HTML pages and JSON API endpoints
- **Password Security** - Argon2 password hashing via pwdlib
- **Async Database** - AsyncIO-powered SQLAlchemy with SQLite
- **Modern Styling** - Tailwind CSS v4 for responsive design
- **Input Validation** - Pydantic v2 schemas with comprehensive validation

## Tech Stack

- **FastAPI** 0.128.0+ (async web framework)
- **SQLAlchemy** 2.0+ with aiosqlite (async ORM)
- **Pydantic** v2 (data validation)
- **JWT** (PyJWT for tokens)
- **pwdlib[argon2]** (password hashing)
- **Jinja2** (template engine)
- **Tailwind CSS** v4 (styling)
- **Python** 3.12+
- **uv** (package manager)

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js (for Tailwind CSS)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd blog

# Install Python dependencies
uv sync

# Install Node dependencies for CSS
cd source_css
npm install
cd ..

# Create environment variables
cp .env.example .env
# Edit .env and set your SECRET_KEY

# Run the development server
uv run fastapi dev main.py
```

The application will be available at `http://localhost:8000`

### Build CSS (Optional)

```bash
cd source_css

# One-time build
npm run build

# Watch mode for development
npm run watch
```

## API Documentation

Once running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## Project Structure

```
blog/
├── main.py              # FastAPI app & HTML routes
├── auth.py              # JWT authentication & password hashing
├── config.py            # Settings & environment config
├── database.py          # Async SQLAlchemy setup
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic validation schemas
├── routers/             # API route modules
│   ├── users.py         # User CRUD & authentication endpoints
│   └── posts.py         # Post CRUD endpoints
├── templates/           # Jinja2 HTML templates
├── static/              # CSS, JS, icons, profile pics
├── media/               # User uploads
└── source_css/          # Tailwind CSS source
```

## Key Endpoints

### HTML Pages
- `GET /` - Home page
- `GET /posts` - All posts
- `GET /posts/{post_id}` - Single post
- `GET /users/{user_id}/posts` - User's posts
- `GET /register` - Registration page
- `GET /login` - Login page

### API Endpoints

#### Authentication
- `POST /api/users` - Register new user
- `POST /api/users/token` - Login (get JWT token)
- `GET /api/users/me` - Get current user profile

#### Users
- `GET /api/users/{user_id}` - Get user (public info)
- `GET /api/users/{user_id}/posts` - Get user's posts
- `PATCH /api/users/{user_id}` - Update user (authenticated)
- `DELETE /api/users/{user_id}` - Delete user (authenticated)

#### Posts
- `GET /api/posts` - List all posts
- `GET /api/posts/{post_id}` - Get post
- `POST /api/posts` - Create post (authenticated)
- `PUT /api/posts/{post_id}` - Full update (authenticated, author only)
- `PATCH /api/posts/{post_id}` - Partial update (authenticated, author only)
- `DELETE /api/posts/{post_id}` - Delete post (authenticated, author only)

## Authentication

The API uses JWT Bearer tokens. To authenticate:

1. Register a user: `POST /api/users`
2. Login to get token: `POST /api/users/token`
3. Use token in subsequent requests:
   ```
   Authorization: Bearer <your_token>
   ```

## Environment Variables

Create a `.env` file with:

```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

```bash
# Run development server with auto-reload
uv run fastapi dev main.py

# Run in production mode
uv run fastapi run main.py
```

## Architecture

For detailed architecture documentation, see [architecture.md](architecture.md)

## License

This project is a sample application for learning purposes.
