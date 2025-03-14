from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService
from src.db.models import Tag

from .schemas import TagAddModel, TagCreateModel

book_service = BookService()


server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong"
)


class TagService:
    async def get_all_tags(self, session: AsyncSession):
        """Get all tags"""

        statement = select(Tag).order_by(desc(Tag.created_at))

        tags =  await session.exec(statement)

        return tags
    
    async def add_tags_to_book(self, session: AsyncSession, book_uid:str, tag_data: TagAddModel):
        """Add tags to a book"""
        book = await book_service.get_book_by_id(session, book_uid)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Book not found"
                )
        for tag_item in tag_data.tags:
            tag = await session.exec(
                select(Tag)
                .where(Tag.name==tag_item.name)
            )

            result = tag.one_or_none()

            if not result:
                tag = Tag(name=tag_item.name)
            book.tags.append(tag)
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book
    
    async def get_tags_by_id(self, session: AsyncSession, tag_uid:str):
        "Get a tag by id"
        statement = select(Tag).where(Tag.uid == tag_uid)

        tag = await session.exec(statement)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return tag.first()
    
    async def add_tag(self, session, tag_data: TagCreateModel):
        """Create a tag"""

        result = await session.exec(
            select(Tag).where(Tag.name == tag_data.name)
        )
        tag = result.first()

        if tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tag already exists"
            )
        
        new_tag = Tag(name=tag_data.name)
        session.add(new_tag)
        await session.commit()

        return new_tag
    
    async def update_tag(self, session: AsyncSession, tag_uid: str, tag_Updatedata: TagCreateModel):
        """Update a tag"""

        tag = await self.get_tags_by_id(session, tag_uid)

        update_tag = tag_Updatedata.model_dump()

        for k, v in update_tag.items():
            setattr(tag, k, v)

            await session.commit()
            await session.refresh(tag)

        return tag
    
    async def delete_tag(self, session: AsyncSession, tag_uid: str):
        """delete a tag"""

        tag = await self.get_tags_by_id(session, tag_uid)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        await session.delete(tag)

        await session.commit()
