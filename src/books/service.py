from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from datetime import datetime
from fastapi import status
from src.books.schema import BookCreateModel
from src.db.models import Book

class BookService:
    """
    This class provides methods to create, read, update, and delete books."""
    async def get_all_books(self, session: AsyncSession):
        """
        Get all the books in the 
        
        Args:
            session(AsyncSession): sqlmodel async session
        Returns:
            List of all books
        """
        statement = select(Book).order_by(Book.created_at)
        result = await session.exec(statement)

        return result.all()
    
    async def get_user_books(self, session: AsyncSession, user_uid: str):
        statement = (
            select(Book) 
            .where(Book.user_uid == user_uid) 
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)

        return result.all()

    async def create_book(self, session: AsyncSession, book_data: BookCreateModel, user_uid: str):
        """
        Create a new book
        
        Args:
            session(AsyncSession): sqlmodel async session
            book_data: Book data to create
            user_uid(str): Id of the user who created the book
        Returns:
            Create a new book and return it
        """
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user_uid = user_uid
        # new_book.published_date = datetime.strptime(book_data_dict['published_date'],"%Y-%m-%d")
        session.add(new_book)
        await session.commit()
        return new_book
        
    async def get_book_by_id(self, session: AsyncSession, book_uid: str):
        """
        Retrieve a book by ID

        Args:
            session(AsyncSession): sqlmodel async session
            book_uid(str): Id of the book
        Returns:
            Book: a Book object 
        """
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None
    
    async def update_book(self, session: AsyncSession, book_uid: str, book_data: BookCreateModel):
        """
        Update a book by ID
        Args:
            session(AsyncSession): sqlmodel async session
            book_uid(str): Id of the book
            book_data: Book data to update
        Returns:
            Updated Book object
        """
        book_to_update = await self.get_book_by_id(session, book_uid)

        if book_to_update is not None:
            book_data = book_data.model_dump()
            for k,v in book_data.items():
                setattr(book_to_update, k, v)
            
            await session.commit()
            return book_to_update
        else:
            return None
        
    async def delete_book(self, session: AsyncSession, book_uid: str):
        """
        Delete a book by ID
        Args:
            session(AsyncSession): sqlmodel async session
            book_uid(str): Id of the book
        """
        book_to_delete = await self.get_book_by_id(session, book_uid)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return None
        
