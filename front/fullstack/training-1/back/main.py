import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

import models
import schemas
from database import engine, get_db, Base

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="training 1 - todo list", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/todos", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: schemas.TodoCreate, db: AsyncSession = Depends(get_db)):
    new_todo = models.Todo(**todo.model_dump())
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return new_todo


@app.get("/todos", response_model=list[schemas.TodoResponse])
async def get_todo_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(models.Todo).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await db.get(models.Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    await db.delete(todo)
    await db.commit()
    return None
