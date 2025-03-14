from pydantic import Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.db.models import User
from .schemas import UserCreateModel
from .utils import get_hashed_password

class UserService:
    async def get_user_by_email(self, email, session: AsyncSession):
        """
        Implement this method to retrieve user from the database based on email
        Args:
            email(str): Email of the user
            session(AsyncSession): sqlmodel async session
        Returns:
            User object if found, otherwise None"""
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user 
    
    async def user_exists(self, email, session: AsyncSession):
        """
        Implement this method to check if a user with the given email already exists in the database
        Args:
            email(str): Email of the user
            session(AsyncSession): sqlmodel async session
        Returns:
            True if user exists, otherwise False"""
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False
    
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        """
        Implement this method to create a new user in the database
        Args:
            session(AsyncSession): sqlmodel async session
            user_data(UserCreate): User data to be created
        Returns:
            User object if created successfully, otherwise None"""
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = get_hashed_password(user_data_dict['password'])
        new_user.role = "user"

        session.add(new_user)
        await session.commit()

        return new_user
    
    async def update_user(self, user, user_update_data, session: AsyncSession):
        """
        Implement this method to update user details in the database
        Args:
            session(AsyncSession): sqlmodel async session
            user_data_dict(dict): User data to be updated
        Returns:
            Updated User object"""
        for k, v in user_update_data.items():
            setattr(user, k, v)

        await session.commit()

        return user
