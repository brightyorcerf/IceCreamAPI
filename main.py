from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Annotated, TypeVar, Generic, Optional
from datetime import datetime, timezone
from random import randint
from sqlmodel import SQLModel, create_engine, Field, Session, select
from contextlib import asynccontextmanager


# ── Models ────────────────────────────────────────────────────────────────────

class Flavor(SQLModel, table=True):
    scoopID:    int | None = Field(default=None, primary_key=True)
    flavor:     str        = Field(index=True)
    churnedAt:  datetime | None = Field(default=None, index=True)
    bestBefore: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )


class FlavorCreate(SQLModel):
    flavor:    str
    churnedAt: datetime | None = None


class FlavorUpdate(SQLModel):
    flavor:    str | None = None
    churnedAt: datetime | None = None


# ── Generic response wrapper ───────────────────────────────────────────────────

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T


# ── DB setup ──────────────────────────────────────────────────────────────────

sqlite_url  = "sqlite:///database.db"
engine      = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# ── Startup ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Flavor)).first():
            session.add_all([
                Flavor(flavor="Triple Fudge Brownie"),
                Flavor(flavor="Midnight Mint Chip"),
            ])
            session.commit()
    yield


app = FastAPI(root_path="/api/v1", lifespan=lifespan)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def welcome():
    return {"message": "Welcome to the Ice Cream API!"}


@app.get("/flavors", response_model=Response[list[Flavor]])
async def read_flavors(session: SessionDep):
    flavors = session.exec(select(Flavor)).all()
    return Response(data=flavors)


@app.get("/flavors/{id}", response_model=Response[Flavor])
async def read_flavor(id: int, session: SessionDep):
    flavor = session.get(Flavor, id)
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found in the freezer!")
    return Response(data=flavor)


@app.post("/flavors", response_model=Response[Flavor], status_code=201)
async def create_flavor(body: FlavorCreate, session: SessionDep):
    new_flavor = Flavor(
        flavor=body.flavor,
        churnedAt=body.churnedAt,
        bestBefore=datetime.now(timezone.utc),
    )
    session.add(new_flavor)
    session.commit()
    session.refresh(new_flavor)
    return Response(data=new_flavor)


@app.put("/flavors/{id}", response_model=Response[Flavor])
async def update_flavor(id: int, body: FlavorUpdate, session: SessionDep):
    flavor = session.get(Flavor, id)
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found in the freezer!")
    if body.flavor is not None:
        flavor.flavor = body.flavor
    if body.churnedAt is not None:
        flavor.churnedAt = body.churnedAt
    flavor.bestBefore = datetime.now(timezone.utc)
    session.add(flavor)
    session.commit()
    session.refresh(flavor)
    return Response(data=flavor)


@app.delete("/flavors/{id}", status_code=204)
async def delete_flavor(id: int, session: SessionDep):
    flavor = session.get(Flavor, id)
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found in the freezer!")
    session.delete(flavor)
    session.commit()


# Run with: fastapi dev main.py