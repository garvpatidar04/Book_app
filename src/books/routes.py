from fastapi import APIRouter, status, Depends
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService
from src.db.main import get_session
from src.books.schema import BookUpdateModel, BookCreateModel, BookDetailModel
from src.auth.dependencies import AccessTokenBearer
from src.auth.dependencies import RoleChecker
from src.errors import BookNotFound


books_route = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@books_route.get('/', response_model=List[BookDetailModel], dependencies=[role_checker])
async def get_books(session: AsyncSession = Depends(get_session), token_details = Depends(access_token_bearer)):
    """
    Retrive all the books"""
    books = await book_service.get_all_books(session)
    return books

@books_route.get(
    "/user/{user_uid}", response_model=List[BookDetailModel], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    books = await book_service.get_user_books(session, user_uid)
    return books

@books_route.post('/', status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def create_book(
    book_data: BookCreateModel, 
    session: AsyncSession = Depends(get_session), 
    token_details = Depends(access_token_bearer)
    ) -> dict:
    """
    Create a new book"""
    user_uid = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(session, book_data, user_uid)
    return new_book.model_dump()


@books_route.get('/{book_id}', status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_book_by_id(
    book_id: str, 
    session: AsyncSession = Depends(get_session), 
    token_details = Depends(access_token_bearer)
    ) -> dict:
    """
    Retrieve a book by ID"""
    book = await book_service.get_book_by_id(session, book_id)
    if book:
        return book.model_dump()
    else:
        raise BookNotFound()


@books_route.patch('/{book_id}', dependencies=[role_checker])
async def update_book(
    book_id: str, 
    book_update_data: BookUpdateModel, 
    session: AsyncSession = Depends(get_session),
    token_details = Depends(access_token_bearer)
    ) -> dict:
    """
    Update a book by ID"""
    updated_book = await book_service.update_book(session, book_id, book_update_data)
    if updated_book is not None:
        return updated_book.model_dump()
    else:
        raise BookNotFound()

@books_route.delete("/{book_id}",status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_book(
    book_id: str, 
    session: AsyncSession = Depends(get_session),
    token_details = Depends(access_token_bearer)
    ):
    """
    Delete a book by ID"""
    deleted_book = await book_service.delete_book(session, book_id)
    if deleted_book is None:
        raise BookNotFound()
    else:
        return {}
