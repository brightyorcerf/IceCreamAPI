# Ice Cream API

![image.jpg](image.jpg) 

Imagine you run an ice cream shop and you have a list of flavors in the freezer. This project is a menu board on the internet — anyone can ask it say:

- "what flavors do you have?" → it tells them the whole list
- "show me flavor #3" → it shows just that one
- "add choco chip cookie flavor!" → it saves the new flavor
- "remove Vanilla, it's gone" → it deletes it

FastAPI is the tool that listens for those questions and gives back answers, all in JSON.

---

## Project Overview

A REST API built with FastAPI and SQLModel that manages an ice cream flavor inventory stored in a SQLite database.

### Stack
- FastAPI — the web framework (handles routes, validation, docs)
- SQLModel — combines SQLAlchemy (database) + Pydantic (validation) in one
- SQLite — lightweight file-based database (`database.db`)
- Uvicorn — the server that runs everything

### Running the Project

```bash
pip install fastapi sqlmodel uvicorn
fastapi dev main.py
```

Then visit `http://localhost:8000/docs` for the interactive API docs (Swagger UI).

---

## API Endpoints (main crux of project)

| Method | Path | What it does |
|--------|------|--------------|
| GET | `/flavors` | list all flavors |
| GET | `/flavors/{id}` | get one flavor by ID |
| POST | `/flavors` | add a new flavor |
| PUT | `/flavors/{id}` | update a flavor |
| DELETE | `/flavors/{id}` | remove a flavor |

---

## What I learnt 

### 1. Decorators map URLs to functions

```python
@app.get("/flavors")
async def read_flavors():
    ...
```

The `@app.get("/flavors")` decorator tells FastAPI: "when someone sends a GET request to /flavors, run this function." Same idea as `app.get('/flavors', (req, res) => {})` in Node/Express.

### 2. SQLModel combines your DB table and your data validator in one class

```python
class Flavor(SQLModel, table=True):
    scoopID: int | None = Field(default = None, primary_key = True)
    flavor: str = Field(index = True)
```

Without `table = True` it's just a Pydantic validation model. With it, SQLModel also creates the actual database table. Two jobs, one class.

### 3. Dependency Injection with `Depends`

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/flavors")
async def read_flavors(session: SessionDep):
    ...
```

Instead of opening a DB connection inside every route, we write it once in `get_session()` and FastAPI automatically "injects" it into any function that asks for `SessionDep`. Cleaner and reusable.

### 4. Generics and TypeVar — the advanced part 

```python
T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T
```

- `TypeVar("T")` creates a placeholder type, like a variable, but for types instead of values. `T` could be a `Flavor`, a `list[Flavor]`, a `str`, anything.

- `Generic[T]` tells Python: this class works with any type T

- `data: T` means the `data` field will be whatever type `T` turns out to be

---