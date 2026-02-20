from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, status, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import schemas
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models
import s3
import asyncio

app = FastAPI(title="training 3 - image manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/moments", response_model=schemas.MomentResponse, status_code=status.HTTP_201_CREATED)
async def create_moment(
    title: str = Form(...), 
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        url = await asyncio.to_thread(
            s3.upload_image,
            contents,
            file.content_type or "",
            file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


    new_moment = models.Moment(title=title, url=url)
    db.add(new_moment)
    await db.commit()
    await db.refresh(new_moment)
    return new_moment


@app.get("/moments", response_model=list[schemas.MomentResponse])
async def get_moments(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(models.Moment).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@app.delete("/moments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_moment(id: int, db: AsyncSession = Depends(get_db)):
    query = select(models.Moment).where(models.Moment.id == id)
    result = await db.execute(query)
    moment = result.scalar_one_or_none()

    if not moment:
        HTTPException(status_code=404, detail="moment not found")

    await db.delete(moment)
    await db.commit()
    return None


@app.put("/moments/{id}", response_model=schemas.MomentResponse)
async def update_moment(id: int, moment: schemas.MomentBase, db: AsyncSession = Depends(get_db)):
    query = select(models.Moment).where(models.Moment.id == id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if not existing:
        HTTPException(status_code=404, detail="moment not found")

    existing.title = moment.title
    existing.url = moment.url

    await db.commit()
    await db.refresh(existing)    
    return existing