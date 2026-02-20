from pydantic import BaseModel

class MomentBase(BaseModel):
    title: str
    url: str

class MomentResponse(MomentBase):
    id: int