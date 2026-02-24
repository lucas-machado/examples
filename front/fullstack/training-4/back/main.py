# CRIAR ESSA ESTRUTURA
# training-3/backend/   (ou onde está o FastAPI)
# ├── app/
# │   ├── __init__.py
# │   ├── main.py              # Criação do FastAPI app, inclusão dos routers
# │   │
# │   ├── api/                 # Camada de entrada (HTTP)
# │   │   ├── __init__.py
# │   │   ├── deps.py          # Dependências comuns (get_db, get_current_user, etc.)
# │   │   └── v1/
# │   │       ├── __init__.py
# │   │       ├── router.py    # Agrupa todos os routers da v1
# │   │       ├── moments.py   # Router: momentos
# │   │       └── users.py     # Router: users (exemplo)
# │   │
# │   ├── core/                # Núcleo: config, segurança, coisas compartilhadas
# │   │   ├── __init__.py
# │   │   ├── config.py        # Settings (pydantic-settings)
# │   │   └── security.py      # JWT, hash de senha, etc.
# │   │
# │   ├── models/              # ORM (SQLAlchemy) – tabelas do banco
# │   │   ├── __init__.py
# │   │   └── moment.py
# │   │
# │   ├── schemas/             # Pydantic – request/response, validação
# │   │   ├── __init__.py
# │   │   ├── moment.py
# │   │   └── user.py
# │   │
# │   ├── services/            # Regras de negócio
# │   │   ├── __init__.py
# │   │   ├── moment.py
# │   │   └── user.py
# │   │
# │   └── db/                  # Acesso a dados (repositórios / sessão)
# │       ├── __init__.py
# │       ├── session.py       # Engine, SessionLocal, get_db
# │       └── repositories/    # (opcional) um por entidade
# │           └── moment.py
# ├── tests/
# ├── requirements.txt
# └── .env


from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

from fastapi import FastAPI, status, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import schemas
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models
import s3
import asyncio
from auth import create_access_token, get_current_user

app = FastAPI(title="training 3 - image manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/auth/register", response_model=schemas.Token)
async def register(
    user: schemas.UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.User).where(models.User.username == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(username=user.email, password_hash=pwd_context.hash(user.password))
    db.add(db_user)

    await db.commit()
    await db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.User).where(models.User.username == form_data.username))
    user = result.scalars().first()

    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/moments", response_model=schemas.MomentResponse, status_code=status.HTTP_201_CREATED)
async def create_moment(
    title: str = Form(...), 
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
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


    new_moment = models.Moment(title=title, url=url, user_id=current_user.id)
    db.add(new_moment)
    await db.commit()
    await db.refresh(new_moment)
    return new_moment


@app.get("/moments", response_model=list[schemas.MomentResponse])
async def get_moments(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = select(models.Moment).where(models.Moment.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@app.delete("/moments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_moment(
    id: int, 
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    query = select(models.Moment).where(models.Moment.id == id)
    result = await db.execute(query)
    moment = result.scalar_one_or_none()

    if not moment:
        HTTPException(status_code=404, detail="moment not found")

    await db.delete(moment)
    await db.commit()
    return None


@app.put("/moments/{id}", response_model=schemas.MomentResponse)
async def update_moment(
    id: int, 
    moment: schemas.MomentBase, 
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
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