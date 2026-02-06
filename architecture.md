# FastAPI Blog - Architecture Documentation

## Overview

A minimal FastAPI blog application demonstrating server-side rendering with Jinja2 templates and REST API endpoints. Currently in early prototype stage with in-memory data storage.

## Project Structure

```
blog/
├── main.py                    # Application entry point
├── pyproject.toml             # Dependencies & project metadata
├── .python-version            # Python 3.12
├── uv.lock                    # Dependency lock file
├── source_css/                # Tailwind CSS source
│   ├── input.css              # Tailwind input
│   ├── tailwind.cofig.js      # Tailwind config
│   └── package.json           # NPM build scripts
├── static/                    # Static assets
│   ├── css/output.css         # Compiled CSS
│   ├── js/utils.js            # JS utilities
│   ├── icons/                 # Icon assets
│   └── profile_pics/          # User avatars
└── templates/                 # Jinja2 templates
    ├── layout.html            # Base template
    └── home.html              # Home page
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.128.0+ |
| Python | 3.12+ |
| Templates | Jinja2 |
| CSS | Tailwind CSS v4 |
| Package Manager | uv |
| Server | Uvicorn (via fastapi[standard]) |

## Application Architecture

### Entry Point

**[main.py](main.py)** - Single-file application containing:
- FastAPI app initialization
- Static file mounting at `/static`
- Jinja2 template configuration
- Route definitions
- In-memory data store

### API Endpoints

| Endpoint | Method | Response | Description |
|----------|--------|----------|-------------|
| `/` | GET | JSON | Welcome message |
| `/posts` | GET | HTML | Rendered blog posts page |
| `/api/posts` | GET | JSON | Posts data as JSON array |

### Data Model

Currently using in-memory list storage with this structure:

```python
Post = {
    "id": int,
    "title": str,
    "author": str,
    "content": str,
    "date_posted": str  # YYYY-MM-DD
}
```

## Frontend Architecture

### Template Inheritance

```
layout.html (base)
    └── home.html (extends layout)
```

**layout.html** provides:
- HTML5 document structure
- Navigation bar with login/register placeholders
- CSS inclusion via `url_for('static')`
- `{% block content %}` for page content

**home.html** provides:
- Post listing with Jinja2 `{% for %}` loop
- Displays title and content per post

### CSS Build Pipeline

```
source_css/input.css → Tailwind CLI → static/css/output.css
```

Build commands (from `source_css/`):
- `npm run build` - One-time compilation
- `npm run watch` - Watch mode for development

## Current Limitations

- **No database** - Data lost on restart
- **No authentication** - All routes public
- **Read-only** - No create/update/delete operations
- **No Pydantic models** - No request validation
- **No error handling** - Missing HTTP exception handling

## Future Architecture Considerations

### Recommended Additions

1. **Database Layer**
   - SQLAlchemy ORM or async alternative (SQLModel, Tortoise)
   - Alembic for migrations

2. **Project Structure Evolution**
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

3. **Authentication**
   - JWT tokens or session-based auth
   - OAuth2 with FastAPI security utilities

4. **Validation**
   - Pydantic models for request/response schemas
   - Input sanitization

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

Dev tooling:
- Tailwind CSS CLI (via NPM)
