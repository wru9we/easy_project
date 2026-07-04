from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from sqlalchemy import select, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()

engine = create_async_engine('sqlite+aiosqlite:///users.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass
    
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))

@app.post("/setup_datebase")
async def setup_datebase():
    async with engine.begin() as coonection:
        await coonection.run_sync(Base.metadata.drop_all)
        await coonection.run_sync(Base.metadata.create_all)
    return {"Success": True}

class UseraddSchema(BaseModel):
    email: EmailStr
    password: str

class BookSchema(UseraddSchema):
    id: int

@app.post("/users")
async def add_user(data: UseraddSchema, session: SessionDep):
    new_user = UserModel(
        email=data.email,
        password=data.password,
    )
    session.add(new_user)
    await session.commit()
    return {"Success": True}


@app.get("/users")
async def get_user(session: SessionDep):
    query = select(UserModel)
    result = await session.execute(query)
    return result.scalars().all()








