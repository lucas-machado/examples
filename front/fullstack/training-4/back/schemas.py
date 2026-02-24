from pydantic import BaseModel, EmailStr

class MomentBase(BaseModel):
    title: str
    url: str

class MomentResponse(MomentBase):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str