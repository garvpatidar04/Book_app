from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import Optional, List


class User(SQLModel, table=True):
    __tablename__ = 'user_accounts'

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4))
    username: str
    email: str
    first_name: str = Field(nullable=True)
    last_name: str = Field(nullable=True)
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: bool = Field(default=False)
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    books: List["Book"] = Relationship(
        back_populates="user", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"


class BookTags(SQLModel, table=True):
    book_uid : Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_uid : Optional[uuid.UUID] = Field(default=None, foreign_key="tags.uid", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__="tags"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        link_model=BookTags,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"Tag {self.name}"
    

class Book(SQLModel, table=True):
    __tablename__ = 'books'

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language:str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="user_accounts.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at:datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional["User"] = Relationship(
        back_populates="books"
        )

    reviews: List["Review"] = Relationship(
        back_populates="book", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List[Tag] = Relationship(
        link_model=BookTags,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    
    def __repr__(self) -> str:
        return f"<Book {self.title}>"
    

class Review(SQLModel, table=True):
    __tablename__ ='reviews'

    uid: uuid.UUID = Field(
        sa_column=Column(
        pg.UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
        )
    )
    rating: int = Field(lt=5)
    review_text: str = Field(sa_column=Column(pg.VARCHAR , nullable=False))
    user_uid : Optional[uuid.UUID] = Field(default=None, foreign_key="user_accounts.uid")
    book_uid : Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")

    def __repr__(self) -> str:
        return f"Review for book {self.book_uid} and user {self.user_uid}"
    
