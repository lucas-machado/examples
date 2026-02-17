from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="training 1 - todo list")

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Todo(BaseModel):
    id: int | None = None
    name: str

todo_list = [Todo(id=1, name="have fun")]
    
@app.get("/todo", response_model=list[Todo])
async def get_todo_list():
    return todo_list


@app.post("/todo", response_model=Todo)
async def add_todo(todo: Todo):
    todo.id = len(todo_list) + 1
    todo_list.append(todo)
    return todo

@app.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int):
    for index, item in enumerate(todo_list):
        if item.id == todo_id:
            todo_list.pop(index)
            return {"message": f"Todo {todo_id} succesfully removed"}

    raise HTTPException(status_code=404, detail="Todo not found")
