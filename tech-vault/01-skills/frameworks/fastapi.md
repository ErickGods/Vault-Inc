---
tags: [skill, frameworks, fastapi]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [FastAPI]
---

# FastAPI

## Overview

FastAPI é um framework web moderno para [[python]], projetado para construir APIs de alta performance com tipagem estática e validação automática via Pydantic. Baseado em Starlette e ASGI, ele oferece suporte nativo a `async/await`, gerando documentação OpenAPI automaticamente. É a escolha dominante para microsserviços Python modernos, especialmente em pipelines de ML, integração com [[supabase]], e deploys em [[docker]].

> [!info] Por que FastAPI?
> FastAPI combina ergonomia de desenvolvimento (autocompletion, validação automática) com performance próxima a Go e Node, graças ao Uvicorn/Gunicorn como servidor ASGI.

A arquitetura recomendada segue [[clean-architecture]], separando routers, serviços, repositórios e schemas. Integra-se naturalmente com [[postgresql]] via SQLAlchemy async e com sistemas de filas para background tasks. Ver [[deployment-strategies]] para padrões de produção.

---

## Core Concepts

### Dependency Injection System

FastAPI's DI system is one of its most powerful features. Dependencies are resolved at request time and can be nested arbitrarily.

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_jwt(token)
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

# Nested dependency — db is shared across the request
async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user
```

### Pydantic v2 Integration

```python
from pydantic import BaseModel, Field, model_validator, computed_field
from typing import Annotated

class UserCreate(BaseModel):
    email: Annotated[str, Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")]
    password: Annotated[str, Field(min_length=8)]
    full_name: str

    @model_validator(mode="after")
    def normalize_email(self) -> "UserCreate":
        self.email = self.email.lower().strip()
        return self

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str

    @computed_field
    @property
    def first_name(self) -> str:
        return self.full_name.split()[0]

    model_config = {"from_attributes": True}  # replaces orm_mode
```

### Lifespan Events

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()
    await redis_client.initialize()
    yield
    # Shutdown
    await database.disconnect()
    await redis_client.close()

app = FastAPI(lifespan=lifespan)
```

---

## Patterns

### Router Organization

```python
# routers/users.py
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

# main.py
from routers import users, auth, items
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
```

### Background Tasks + Celery

```python
from fastapi import BackgroundTasks

# Lightweight: FastAPI BackgroundTasks (same process)
@router.post("/send-email")
async def send_email_endpoint(
    payload: EmailPayload,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(send_email, payload.to, payload.subject)
    return {"status": "queued"}

# Heavy: Celery for distributed workloads
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379/0")

@celery_app.task
def process_video(video_id: int):
    ...  # long-running CPU work

@router.post("/process")
async def trigger_processing(video_id: int):
    process_video.delay(video_id)
    return {"task": "dispatched"}
```

### WebSocket Handler

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, client_id: str):
        await ws.accept()
        self.active[client_id] = ws

    async def broadcast(self, message: str):
        for ws in self.active.values():
            await ws.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: str):
    await manager.connect(ws, client_id)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(f"{client_id}: {data}")
    except WebSocketDisconnect:
        manager.active.pop(client_id, None)
```

### Custom Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class DomainException(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=422,
        content={"error": exc.code, "message": exc.message},
    )
```

### Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(duration)
    return response
```

---

## Gotchas

> [!warning] `async def` vs `def` em rotas
> Usar `def` em vez de `async def` força o FastAPI a rodar a função em uma thread pool (via `run_in_executor`). Isso é correto para código bloqueante (ex: bibliotecas síncronas), mas desnecessário para I/O assíncrono. Misturar incorretamente pode causar deadlocks com SQLAlchemy async.

```python
# ERRADO — bloqueia o event loop
@router.get("/data")
async def get_data():
    result = sync_db_call()  # bloqueia!
    return result

# CORRETO — para código bloqueante
@router.get("/data")
def get_data():  # FastAPI usa threadpool automaticamente
    result = sync_db_call()
    return result
```

> [!danger] Injeção de dependência com escopo incorreto
> Dependências com `yield` que criam conexões de banco não devem ser criadas no escopo do módulo. Cada request precisa de sua própria sessão.

```python
# ERRADO — sessão compartilhada entre requests
db = AsyncSession(bind=engine)  # global! race condition garantida

# CORRETO — sessão por request via Depends
async def get_db():
    async with async_session_factory() as session:
        yield session
```

> [!warning] Pydantic v2: `orm_mode` foi removido
> Em Pydantic v2, `orm_mode = True` foi substituído por `model_config = {"from_attributes": True}`. Código legado v1 falhará silenciosamente em alguns casos.

---

## Snippets

### JWT Auth Full Flow

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"

def create_access_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Async SQLAlchemy Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=10,
    max_overflow=20,
    echo=False,
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

### Pagination with Response Model

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int

@router.get("/", response_model=Page[UserRead])
async def paginate_users(page: int = 1, size: int = 20, db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * size
    total = await db.scalar(select(func.count(User.id)))
    result = await db.execute(select(User).offset(offset).limit(size))
    return Page(items=result.scalars().all(), total=total, page=page, size=size)
```

---

## References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Celery + FastAPI pattern](https://testdriven.io/blog/fastapi-and-celery/)

---

## Related

- [[python]]
- [[postgresql]]
- [[docker]]
- [[supabase]]
- [[deployment-strategies]]
- [[clean-architecture]]
