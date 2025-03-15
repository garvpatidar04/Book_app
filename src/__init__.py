from fastapi import FastAPI
from .books.routes import books_route
from .auth.routes import user_routes
from .reviews.routes import review_routes
from .tags.routes import tags_router
from contextlib import asynccontextmanager
from .errors import register_error_handler
from .middleware import register_middleware

version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
"""

version_prefix = f"/api/{version}"

app = FastAPI(
    title="BookStore",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Garv Patidar",
        "url": "https://github.com/garvpatidar04",
        "email": "notgarvpatidar@gmail.com",
    },
    terms_of_service="httpS://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

register_error_handler(app)
register_middleware(app)

@app.get("/")
async def root():
    """
    default for render.com"""

    return {'hello, this my app BooKStore'}

app.include_router(books_route, prefix=f"{version_prefix}/books", tags=['books'])
app.include_router(user_routes, prefix=f"{version_prefix}/auth", tags=['User'])
app.include_router(review_routes, prefix=f"{version_prefix}/review", tags=['Review'])
app.include_router(tags_router, prefix=f"{version_prefix}/tags", tags=["tags"]) 
