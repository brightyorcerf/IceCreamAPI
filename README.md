# 🍦 Ice Cream API

## Explain It Like I'm 10

Imagine you run an ice cream shop and you have a list of flavors in the freezer. This project is a **menu board on the internet** — anyone can ask it:

- "What flavors do you have?" → it tells them the whole list
- "Show me flavor #3" → it shows just that one
- "Add Cookie Dough!" → it saves the new flavor
- "Remove Vanilla, it's gone" → it deletes it

FastAPI is the tool that listens for those questions and gives back answers, all in a language computers love called JSON.

---

## Project Overview

A REST API built with **FastAPI** and **SQLModel** that manages an ice cream flavor inventory stored in a SQLite database.

### Stack

- **FastAPI** — the web framework (handles routes, validation, docs)
- **SQLModel** — combines SQLAlchemy (database) + Pydantic (validation) in one
- **SQLite** — lightweight file-based database (`database.db`)
- **Uvicorn** — the server that runs everything

### Running the Project

```bash
pip install fastapi sqlmodel uvicorn
fastapi dev main.py
```

Then visit `http://localhost:8000/docs` for the interactive API docs (Swagger UI — free with FastAPI!).

---

## API Endpoints

| Method | Path | What it does |
|--------|------|--------------|
| GET | `/flavors` | List all flavors |
| GET | `/flavors/{id}` | Get one flavor by ID |
| POST | `/flavors` | Add a new flavor |
| PUT | `/flavors/{id}` | Update a flavor |
| DELETE | `/flavors/{id}` | Remove a flavor |

---

## What We Learned

### 1. Decorators map URLs to functions

```python
@app.get("/flavors")
async def read_flavors():
    ...
```

The `@app.get("/flavors")` decorator tells FastAPI: *"when someone sends a GET request to /flavors, run this function."* Same idea as `app.get('/flavors', (req, res) => {})` in Node/Express.

### 2. SQLModel combines your DB table and your data validator in one class

```python
class Flavor(SQLModel, table=True):
    scoopID: int | None = Field(default=None, primary_key=True)
    flavor:  str        = Field(index=True)
```

Without `table=True` it's just a Pydantic validation model. With it, SQLModel also creates the actual database table. Two jobs, one class.

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

Instead of opening a DB connection inside every route, we write it once in `get_session()` and FastAPI automatically "injects" it into any function that asks for `SessionDep`. Cleaner, testable, reusable.

### 4. Lifespan events (startup logic)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()   # runs BEFORE the server starts taking requests
    yield                    # server is live here
                             # anything after yield runs on shutdown
```

This is where you do setup work — creating tables, seeding data, connecting to external services.

### 5. Generics and TypeVar — the most advanced part 🧠

```python
T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T
```

**Breaking it down:**

- **`TypeVar("T")`** creates a **placeholder type** — like a variable, but for types instead of values. `T` could be a `Flavor`, a `list[Flavor]`, a `str`, anything.

- **`Generic[T]`** tells Python: *"this class works with any type T — fill it in when you use it."*

- **`data: T`** means the `data` field will be whatever type `T` turns out to be.

**Why this matters:**

Without generics you'd need to write a separate response class for every type:

```python
class FlavorResponse(BaseModel):
    data: Flavor

class FlavorListResponse(BaseModel):
    data: list[Flavor]
```

With generics, one class does it all:

```python
Response[Flavor]        # { "data": { single flavor object } }
Response[list[Flavor]]  # { "data": [ array of flavors ] }
```

FastAPI also reads `response_model=Response[list[Flavor]]` to auto-generate correct API docs and validate the shape of what you return.

**Real-world analogy:** Think of `T` like a gift box. `Response` is the box design. `T` is whatever you put inside — a Flavor, a list, a user. Same box, different contents, and the label tells you exactly what's inside.

---

## Files

```
main.py       ← all the API code
database.db   ← auto-created SQLite database (gitignore this)
```

---

## Key Concepts Cheat Sheet

| Concept | What it is |
|---------|-----------|
| `@app.get()` | Decorator — maps a URL path to a Python function |
| `SQLModel` | ORM — lets you talk to the DB with Python objects |
| `Depends()` | Dependency injection — auto-passes shared resources |
| `TypeVar` | A variable that holds a *type* instead of a value |
| `Generic[T]` | Makes a class reusable with any type |
| `lifespan` | Startup/shutdown hooks for the app |
| `response_model` | Tells FastAPI what shape to validate and document |