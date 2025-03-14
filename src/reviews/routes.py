from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.auth.dependencies import RoleChecker, get_current_user
from src.errors import ReviewNotFound
from .service import ReviewService
from .schemas import ReviewCreateModel, ReviewModel

review_routes = APIRouter()
review_service = ReviewService()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))

@review_routes.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    """
    Get all reviews
    """
    books = await review_service.get_all_review(session)
    
    return books
@review_routes.get("/{review_uid}", dependencies=[user_role_checker])
async def get_reviews(review_uid: str, session: AsyncSession = Depends(get_session)):
    """
    Get single reviews by id
    """
    books = await review_service.get_review(review_uid, session)
    if not books:
        ReviewNotFound()
    
    return books

@review_routes.post("/book/{book_uid}", dependencies=[user_role_checker])
async def create_review(
    book_uid: str,
    review_data: ReviewCreateModel, 
    Current_user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)):
    """
    Create a review
    """
    new_review = await review_service.add_review_to_book(
        Current_user.email,
        book_uid,
        review_data, 
        session
        )
    
    return new_review

@review_routes.delete(
        "/{review_uid}", 
        dependencies=[user_role_checker], 
        status_code=status.HTTP_204_NO_CONTENT
        )
async def delete_review(
    review_uid: str, 
    Current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
    ):
    """
    Delete a review by id
    """
    await review_service.delete_review_from_book(review_uid, Current_user.email, session)

    return None
