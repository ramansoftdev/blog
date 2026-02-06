# FastAPI Blog - Architecture Documentation

## Overview

A FastAPI blog application with server-side rendering using Jinja2 templates and REST API endpoints. Features SQLite database persistence with SQLAlchemy ORM, Pydantic validation, and custom error handling.

## Project Structure

```
blog/
├── main.py                    # Application entry point & routes
├── database.py                # SQLAlchemy engine & session config
├── models.py                  # SQLAlchemy ORM models
├── schemas.py                 # Pydantic request/response schemas
├── blog.db                    # SQLite database file
├── pyproject.toml             # Dependencies & project metadata
├── .python-version            # Python 3.12
├── uv.lock                    # Dependency lock file
├── source_css/                # Tailwind CSS source
│   ├── input.css              # Tailwind input
│   ├── tailwind.config.js     # Tailwind config
│   └── package.json           # NPM build scripts
├── static/                    # Static assets (mounted at /static)
│   ├── css/output.css         # Compiled CSS
│   ├── js/utils.js            # JS utilities
│   ├── icons/                 # Icon assets
│   └── profile_pics/          # User avatars
├── media/                     # User uploads (mounted at /media)
└── templates/                 # Jinja2 templates
    ├── layout.html            # Base template
    ├── default.html           # Home page
    ├── posts.html             # All posts listing
    ├── post.html              # Single post view
    ├── user_posts.html        # Posts by user
    └── error.html             # Error page
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.128.0+ |
| Python | 3.12+ |
| Database | SQLite |
| ORM | SQLAlchemy 2.0+ |
| Validation | Pydantic v2 |
| Templates | Jinja2 |
| CSS | Tailwind CSS v4 |
| Package Manager | uv |
| Server | Uvicorn (via fastapi[standard]) |

## Application Architecture

### Module Overview

| File | Purpose |
|------|---------|
| [main.py](main.py) | FastAPI app, routes, exception handlers |
| [database.py](database.py) | Database engine, session factory, Base class |
| [models.py](models.py) | SQLAlchemy ORM models (User, Post) |
| [schemas.py](schemas.py) | Pydantic schemas for validation |

### Database Layer

**[database.py](database.py)** provides:
- SQLite connection via SQLAlchemy `create_engine`
- `SessionLocal` sessionmaker for database sessions
- `Base` declarative base for ORM models
- `get_db()` dependency for request-scoped sessions

### ORM Models

**[models.py](models.py)** defines:

```python
User:
  - id: int (PK)
  - username: str (unique, max 50)
  - email: str (unique, max 120)
  - posts: relationship → Post[]

Post:
  - id: int (PK)
  - title: str (max 100)
  - content: text
  - user_id: int (FK → users.id)
  - date_posted: datetime (auto UTC)
  - author: relationship → User
```

### Pydantic Schemas

**[schemas.py](schemas.py)** defines:

| Schema | Purpose |
|--------|---------|
| `UserBase` | Base user fields (username, email) |
| `UserCreate` | User creation request |
| `UserResponse` | User API response |
| `PostBase` | Base post fields (title, content) |
| `PostCreate` | Post creation request (+ user_id) |
| `PostResponse` | Post API response (+ author) |

### API Endpoints

#### HTML Routes (Server-Side Rendered)

| Endpoint | Method | Template | Description |
|----------|--------|----------|-------------|
| `/` | GET | default.html | Welcome/home page |
| `/posts` | GET | posts.html | All posts listing |
| `/posts/{post_id}` | GET | post.html | Single post view |
| `/users/{user_id}/posts` | GET | user_posts.html | Posts by user |

#### JSON API Routes

| Endpoint | Method | Response | Description |
|----------|--------|----------|-------------|
| `/api/users` | POST | UserResponse | Create user |
| `/api/users/{user_id}` | GET | UserResponse | Get user by ID |
| `/api/users/{user_id}/posts` | GET | PostResponse[] | Get user's posts |
| `/api/posts` | GET | PostResponse[] | List all posts |
| `/api/posts/{post_id}` | GET | PostResponse | Get post by ID |
| `/api/posts` | POST | PostResponse | Create post |

### Error Handling

Custom exception handlers in [main.py](main.py):
- `StarletteHTTPException` → JSON for `/api/*`, HTML error page otherwise
- `RequestValidationError` → JSON 422 for `/api/*`, HTML error page otherwise

## Frontend Architecture

### Template Inheritance

```
layout.html (base)
    ├── default.html (home)
    ├── posts.html (all posts)
    ├── post.html (single post)
    ├── user_posts.html (user's posts)
    └── error.html (error page)
```

**layout.html** provides:
- HTML5 document structure
- Navigation bar
- CSS inclusion via `url_for('static')`
- `{% block content %}` for page content

### CSS Build Pipeline

```
source_css/input.css → Tailwind CLI → static/css/output.css
```

Build commands (from `source_css/`):
- `npm run build` - One-time compilation
- `npm run watch` - Watch mode for development

## Current Limitations

- **No authentication** - All routes public
- **No update/delete** - Only create and read operations
- **No migrations** - Tables auto-created on startup
- **No pagination** - All posts returned at once

## Future Architecture Considerations

### Recommended Additions

1. **Migrations**
   - Alembic for schema versioning

2. **Authentication**
   - JWT tokens or session-based auth
   - OAuth2 with FastAPI security utilities
   - Password hashing (bcrypt)

3. **CRUD Completion**
   - PUT/PATCH endpoints for updates
   - DELETE endpoints with soft delete

4. **Project Structure Evolution**
   ```
   blog/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── config.py
   │   ├── database.py
   │   ├── models/
   │   ├── schemas/
   │   ├── routers/
   │   └── dependencies/
   ├── static/
   └── templates/
   ```

## Running the Application

```bash
# Install dependencies
uv sync

# Run development server
uv run fastapi dev main.py

# Build CSS (from source_css/)
npm install && npm run build
```

## Dependencies

Core dependencies from `pyproject.toml`:
- `fastapi[standard]>=0.128.0` (includes Uvicorn, Pydantic, Jinja2, etc.)
- `sqlalchemy>=2.0.46`

Dev tooling:
- Tailwind CSS CLI (via NPM)
