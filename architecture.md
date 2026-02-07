# FastAPI Blog - Architecture Documentation

## Overview

A production-ready FastAPI blog application featuring JWT authentication, OAuth2 security, server-side rendering with Jinja2 templates, and comprehensive RESTful API endpoints. Built with async SQLAlchemy, Pydantic validation, and authorization-based access control.

## Project Structure

```
blog/
├── main.py                    # Application entry point, HTML routes & exception handlers
├── auth.py                    # JWT authentication, password hashing & user dependencies
├── config.py                  # Pydantic settings from environment variables
├── database.py                # Async SQLAlchemy engine & session config
├── models.py                  # SQLAlchemy ORM models (User, Post)
├── schemas.py                 # Pydantic request/response schemas
├── blog.db                    # SQLite database file
├── .env                       # Environment variables (SECRET_KEY, etc.)
├── .env.example               # Environment template
├── pyproject.toml             # Dependencies & project metadata
├── .python-version            # Python 3.12
├── uv.lock                    # Dependency lock file
├── routers/                   # API route modules
│   ├── __init__.py
│   ├── users.py               # User CRUD & auth endpoints
│   └── posts.py               # Post CRUD endpoints
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
    ├── register.html          # Registration page
    ├── login.html             # Login page
    └── error.html             # Error page
```

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.128.0+ |
| Python | CPython | 3.12+ |
| Database | SQLite | via aiosqlite |
| ORM | SQLAlchemy | 2.0+ (async) |
| DB Driver | aiosqlite | 0.22.1+ |
| Validation | Pydantic | v2 |
| Templates | Jinja2 | (via FastAPI) |
| Authentication | PyJWT | 2.11.0+ |
| Password Hashing | pwdlib[argon2] | 0.3.0+ |
| Settings | pydantic-settings | 2.12.0+ |
| CSS | Tailwind CSS | v4 |
| Package Manager | uv | Latest |
| Server | Uvicorn | (via fastapi[standard]) |

## Application Architecture

### Module Overview

| File | Purpose | Key Components |
|------|---------|----------------|
| [main.py](main.py) | FastAPI app, HTML routes, exception handlers | `app`, lifespan, HTML endpoints, custom error handlers |
| [auth.py](auth.py) | Authentication & authorization | JWT creation/verification, password hashing, `get_current_user` |
| [config.py](config.py) | Configuration management | Pydantic settings from environment |
| [database.py](database.py) | Database layer | Async engine, session factory, `get_db()` dependency |
| [models.py](models.py) | ORM models | `User`, `Post` with relationships |
| [schemas.py](schemas.py) | API schemas | Request/response validation models |
| [routers/users.py](routers/users.py) | User API routes | User CRUD, registration, login, token |
| [routers/posts.py](routers/posts.py) | Post API routes | Post CRUD with authorization |

### Authentication & Authorization Layer

**[auth.py](auth.py)** provides:

#### Password Security
- **Argon2 hashing** via `pwdlib.PasswordHash.recommended()`
- `hash_password(password: str) -> str` - Hash passwords for storage
- `verify_password(plain: str, hashed: str) -> bool` - Verify credentials

#### JWT Token Management
- `create_access_token(data: dict, expires_delta: timedelta | None)` - Generate JWT
- `verify_access_token(token: str) -> str | None` - Validate & extract user ID
- **OAuth2PasswordBearer** scheme for token extraction

#### User Authentication Dependency
- `get_current_user(token: str, db: AsyncSession) -> models.User`
  - Validates JWT token
  - Retrieves user from database
  - Raises 401 Unauthorized if invalid
- `CurrentUser` type alias for dependency injection

### Configuration Layer

**[config.py](config.py)** uses Pydantic Settings:

```python
Settings:
  - secret_key: SecretStr (from .env)
  - algorithm: str (default: "HS256")
  - access_token_expire_minutes: int (default: 30)
```

### Database Layer

**[database.py](database.py)** provides:

- **Async SQLite** connection via `create_async_engine`
  - Connection string: `sqlite+aiosqlite:///./blog.db`
- `async_sessionmaker` for request-scoped sessions
- `Base` declarative base for ORM models
- `get_db()` async dependency - yields session with auto-cleanup

**Lifecycle Management** ([main.py](main.py)):
- `lifespan` context manager creates tables on startup
- Disposes engine on shutdown

### ORM Models

**[models.py](models.py)** defines:

```python
User:
  - id: int (PK, indexed)
  - username: str (unique, max 50)
  - email: str (unique, max 120)
  - password_hash: str (max 200, Argon2 hash)
  - posts: relationship → Post[] (cascade delete)

Post:
  - id: int (PK, indexed)
  - title: str (max 100)
  - content: text
  - user_id: int (FK → users.id, indexed)
  - date_posted: datetime (auto UTC)
  - author: relationship → User
```

**Key Features**:
- Bidirectional relationships with `back_populates`
- Cascade delete: deleting user deletes all their posts
- Indexed foreign keys for query performance
- Timezone-aware timestamps (UTC)

### Pydantic Schemas

**[schemas.py](schemas.py)** defines:

#### User Schemas
| Schema | Fields | Purpose |
|--------|--------|---------|
| `UserBase` | username, email | Base user fields |
| `UserCreate` | + password | User registration |
| `UserPublic` | id, username | Public user info (no email) |
| `UserPrivate` | + email | Private user profile |
| `UserUpdate` | username?, email? | Partial user updates |
| `Token` | access_token, token_type | JWT response |

#### Post Schemas
| Schema | Fields | Purpose |
|--------|--------|---------|
| `PostBase` | title, content | Base post fields |
| `PostCreate` | (same) | Create post (user_id from token) |
| `PostUpdate` | title?, content? | Partial updates |
| `PostResponse` | + id, user_id, date_posted, author | Full post response |

**Configuration**:
- `ConfigDict(from_attributes=True)` for ORM compatibility
- `EmailStr` validation for email fields
- `Field` constraints for lengths and requirements

### API Endpoints

#### HTML Routes (Server-Side Rendered)

All HTML routes use `include_in_schema=False` to hide from OpenAPI docs.

| Endpoint | Method | Template | Description |
|----------|--------|----------|-------------|
| `/` | GET | default.html | Welcome/home page |
| `/posts` | GET | posts.html | All posts listing (newest first) |
| `/posts/{post_id}` | GET | post.html | Single post view |
| `/users/{user_id}/posts` | GET | user_posts.html | Posts by user |
| `/register` | GET | register.html | Registration form |
| `/login` | GET | login.html | Login form |

**Error Handling**: Returns `error.html` with status code and message for HTML requests.

#### JSON API Routes

All API routes are prefixed with `/api` and return JSON responses.

##### Authentication Endpoints (`/api/users`)

| Endpoint | Method | Auth | Response | Description |
|----------|--------|------|----------|-------------|
| `/api/users` | POST | None | UserPrivate | Register new user |
| `/api/users/token` | POST | None | Token | Login (OAuth2 password flow) |
| `/api/users/me` | GET | **Required** | UserPrivate | Get current authenticated user |

##### User CRUD Endpoints (`/api/users`)

| Endpoint | Method | Auth | Response | Description |
|----------|--------|------|----------|-------------|
| `/api/users/{user_id}` | GET | None | UserPublic | Get user by ID (public info only) |
| `/api/users/{user_id}/posts` | GET | None | PostResponse[] | Get user's posts (with author) |
| `/api/users/{user_id}` | PATCH | **Self only** | UserPrivate | Update own profile |
| `/api/users/{user_id}` | DELETE | **Self only** | 204 | Delete own account |

**Authorization Rules**:
- Update/Delete: User can only modify their own account (enforced via `current_user.id == user_id`)

##### Post CRUD Endpoints (`/api/posts`)

| Endpoint | Method | Auth | Response | Description |
|----------|--------|------|----------|-------------|
| `/api/posts` | GET | None | PostResponse[] | List all posts (newest first) |
| `/api/posts/{post_id}` | GET | None | PostResponse | Get single post |
| `/api/posts` | POST | **Required** | PostResponse | Create post (user_id from token) |
| `/api/posts/{post_id}` | PUT | **Author only** | PostResponse | Full update (replace title & content) |
| `/api/posts/{post_id}` | PATCH | **Author only** | PostResponse | Partial update (title or content) |
| `/api/posts/{post_id}` | DELETE | **Author only** | 204 | Delete post |

**Authorization Rules**:
- Create: Must be authenticated (user_id from JWT token)
- Update/Delete: User must be the post author (enforced via `current_user.id == post.user_id`)
- Violations return `403 Forbidden`

**Data Loading**:
- All post endpoints use `selectinload(models.Post.author)` to eagerly load author relationship
- Prevents N+1 query problems

### Router Organization

**[routers/users.py](routers/users.py)**:
- User registration with duplicate username/email checks
- JWT token generation on login (OAuth2 password flow)
- User profile retrieval (public vs private)
- User update with conflict validation
- User deletion with cascade to posts
- Case-insensitive email/username lookups via `func.lower()`

**[routers/posts.py](routers/posts.py)**:
- Full CRUD operations for posts
- Authorization checks on write operations
- `selectinload` for efficient author loading
- PUT vs PATCH: full vs partial updates
- `model_dump(exclude_unset=True)` for partial updates

### Error Handling

Custom exception handlers in [main.py](main.py):

#### HTTP Exceptions (`StarletteHTTPException`)
- **API requests** (`/api/*`): Return JSON with status code and detail
- **HTML requests**: Return `error.html` template with formatted error message

#### Validation Errors (`RequestValidationError`)
- **API requests** (`/api/*`): Return JSON 422 with validation details
- **HTML requests**: Return `error.html` with user-friendly validation message

**Path-based routing**: Checks `request.url.path.startswith("/api")` to determine response format.

## Frontend Architecture

### Template Inheritance

```
layout.html (base)
    ├── default.html (home)
    ├── posts.html (all posts)
    ├── post.html (single post)
    ├── user_posts.html (user's posts)
    ├── register.html (registration)
    ├── login.html (login)
    └── error.html (error page)
```

**[layout.html](templates/layout.html)** provides:
- HTML5 document structure
- Responsive navigation bar
- CSS inclusion via `url_for('static', path='css/output.css')`
- JavaScript utilities via `url_for('static', path='js/utils.js')`
- `{% block content %}` for page-specific content
- `{% block title %}` for dynamic page titles

### CSS Build Pipeline

```
source_css/input.css → Tailwind CLI → static/css/output.css
```

Build commands (from `source_css/`):
- `npm run build` - One-time production build
- `npm run watch` - Watch mode for development

## Security Features

### Password Security
- **Argon2** hashing (industry standard, OWASP recommended)
- Passwords never stored in plain text
- Configurable hash parameters via pwdlib

### JWT Security
- Token-based authentication (stateless)
- Configurable expiration (default 30 minutes)
- Secret key from environment variables
- HS256 algorithm (HMAC with SHA-256)
- Token validation on every protected request

### Authorization
- **Resource ownership**: Users can only modify their own resources
- **403 Forbidden** responses for unauthorized access
- Dependency injection for clean auth checks

### Input Validation
- Pydantic schemas validate all inputs
- Email format validation via `EmailStr`
- Length constraints on all string fields
- 422 responses for invalid data

## Database Design Patterns

### Async SQLAlchemy Best Practices
- `AsyncSession` for non-blocking I/O
- `selectinload()` for eager loading relationships (prevents N+1 queries)
- `refresh()` after commits to sync state
- Proper session lifecycle via dependency injection

### Query Optimization
- Indexed primary and foreign keys
- Eager loading via `selectinload()` where needed
- `order_by()` for consistent ordering
- Case-insensitive searches via `func.lower()`

## Current Features & Capabilities

✅ **Complete CRUD** - Full create, read, update, delete for users and posts
✅ **JWT Authentication** - Secure token-based auth with OAuth2
✅ **Authorization** - Resource ownership enforcement
✅ **Password Security** - Argon2 hashing
✅ **Async Database** - Non-blocking SQLAlchemy with SQLite
✅ **Dual Interface** - HTML pages + JSON API
✅ **Error Handling** - Custom handlers for HTML/API
✅ **Input Validation** - Comprehensive Pydantic schemas
✅ **Relationship Management** - Cascade deletes, eager loading

## Future Architecture Considerations

### Recommended Additions

1. **Database Migrations**
   - **Alembic** for schema versioning
   - Track database changes over time
   - Safe rollback capabilities

2. **PostgreSQL Migration**
   - Switch from SQLite to PostgreSQL for production
   - Better concurrency and scalability
   - Full-text search capabilities

3. **Pagination**
   - Limit/offset or cursor-based pagination
   - Prevent memory issues with large datasets
   - Improve API performance

4. **Rate Limiting**
   - Prevent abuse of authentication endpoints
   - slowapi or custom middleware

5. **Refresh Tokens**
   - Long-lived refresh tokens
   - Short-lived access tokens
   - Revocation capability

6. **Email Verification**
   - Confirm email addresses on registration
   - Password reset functionality

7. **File Upload Enhancements**
   - Profile picture uploads
   - Post image attachments
   - Cloud storage integration (S3, etc.)

8. **Testing**
   - pytest with async support
   - API endpoint tests
   - Authentication flow tests

9. **CORS Configuration**
   - Enable cross-origin requests for frontend
   - Proper security headers

10. **Advanced Project Structure**
    ```
    blog/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── config.py
    │   ├── database.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   └── post.py
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   └── post.py
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   ├── users.py
    │   │   └── posts.py
    │   ├── dependencies/
    │   │   ├── __init__.py
    │   │   └── auth.py
    │   └── utils/
    │       └── security.py
    ├── tests/
    ├── static/
    └── templates/
    ```

## Running the Application

```bash
# Install dependencies
uv sync

# Set environment variables
cp .env.example .env
# Edit .env with your SECRET_KEY

# Run development server (auto-reload)
uv run fastapi dev main.py

# Run production server
uv run fastapi run main.py

# Build CSS (from source_css/)
npm install && npm run build
```

## Dependencies

Core dependencies from `pyproject.toml`:
- `fastapi[standard]>=0.128.0` - Web framework (includes Uvicorn, Pydantic, Jinja2, etc.)
- `sqlalchemy>=2.0.46` - Async ORM
- `aiosqlite>=0.22.1` - Async SQLite driver
- `pyjwt>=2.11.0` - JWT token handling
- `pwdlib[argon2]>=0.3.0` - Password hashing
- `pydantic-settings>=2.12.0` - Settings management

Dev tooling:
- Tailwind CSS CLI (via NPM)
- Node.js for CSS builds

## API Versioning Strategy

Current: No versioning (v1 implicit)

Future considerations:
- Path-based: `/api/v2/posts`
- Header-based: `Accept: application/vnd.api+json; version=2`
- Query parameter: `/api/posts?version=2`
