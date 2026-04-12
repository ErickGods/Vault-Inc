---
tags: [snippet, python]
status: active
level: advanced
updated: 2026-04-05
aliases: [Python Snippets]
created: 2026-04-05
---

# Python Snippets

Coleção de snippets prontos para copiar e colar. Organizados por categoria para uso rápido no dia a dia com [[python]], [[fastapi]], [[django]] e integrações com [[bash-snippets]] e [[docker-snippets]].

---

## File I/O & Pathlib

```python
from pathlib import Path

# Leitura segura de arquivo
def read_file(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    return p.read_text(encoding="utf-8")

# Escrita atômica (evita corrupção parcial)
def write_atomic(path: str | Path, content: str) -> None:
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(p)

# Glob recursivo com filtro
def find_py_files(root: str | Path) -> list[Path]:
    return sorted(Path(root).rglob("*.py"))

# Leitura de JSON com fallback
import json

def load_json(path: str | Path, default: dict | None = None) -> dict:
    p = Path(path)
    if not p.exists():
        return default or {}
    return json.loads(p.read_text(encoding="utf-8"))
```

---

## Async Patterns

```python
import asyncio
from asyncio import TaskGroup

# asyncio.gather com tratamento de erro
async def fetch_all(urls: list[str]) -> list[dict]:
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [client.get(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r.json() if not isinstance(r, Exception) else {"error": str(r)} for r in results]

# TaskGroup (Python 3.11+) — cancela tudo se um falhar
async def run_pipeline(items: list[str]) -> list[str]:
    results: list[str] = []
    async with TaskGroup() as tg:
        tasks = [tg.create_task(process(item)) for item in items]
    return [t.result() for t in tasks]

# Semáforo para limitar concorrência
async def bounded_fetch(urls: list[str], limit: int = 5) -> list[bytes]:
    sem = asyncio.Semaphore(limit)
    import httpx
    async def fetch(url: str) -> bytes:
        async with sem:
            async with httpx.AsyncClient() as client:
                r = await client.get(url)
                return r.content
    return await asyncio.gather(*[fetch(u) for u in urls])
```

---

## Decorators com Typing

```python
from functools import wraps
from typing import Callable, TypeVar, ParamSpec
import time
import logging

P = ParamSpec("P")
T = TypeVar("T")

# Retry decorator
def retry(times: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    if attempt == times - 1:
                        raise
                    logging.warning(f"Retry {attempt + 1}/{times} after error: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

# Timer decorator
def timer(fn: Callable[P, T]) -> Callable[P, T]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logging.info(f"{fn.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

# Cache simples com TTL
from datetime import datetime, timedelta

def ttl_cache(seconds: int = 60):
    cache: dict = {}
    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                value, expires = cache[key]
                if datetime.now() < expires:
                    return value
            result = fn(*args, **kwargs)
            cache[key] = (result, datetime.now() + timedelta(seconds=seconds))
            return result
        return wrapper
    return decorator
```

---

## Context Managers

```python
from contextlib import contextmanager, asynccontextmanager
import tempfile, os

# Diretório temporário limpo automaticamente
@contextmanager
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)

# Timer como context manager
@contextmanager
def measure(label: str = "block"):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"[{label}] {time.perf_counter() - start:.4f}s")

# DB transaction context (exemplo SQLAlchemy)
@contextmanager
def db_transaction(session):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise

# Async context manager
@asynccontextmanager
async def managed_client():
    import httpx
    async with httpx.AsyncClient() as client:
        yield client
```

---

## Dataclass & Pydantic

```python
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# Dataclass com defaults e post_init
@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")

# Pydantic v2 model
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[\w.+\-]+@[\w\-]+\.[a-z]{2,}$")
    age: Optional[int] = Field(None, ge=0, le=150)

    model_config = {"str_strip_whitespace": True}

# Pydantic settings (env vars)
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    max_workers: int = 4

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = AppSettings()
```

---

## httpx Patterns

```python
import httpx
from typing import Any

# Cliente reutilizável com headers padrão
def get_client(base_url: str, token: str) -> httpx.Client:
    return httpx.Client(
        base_url=base_url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0),
    )

# POST com retry manual
def post_with_retry(url: str, payload: dict, max_retries: int = 3) -> dict:
    with httpx.Client() as client:
        for i in range(max_retries):
            try:
                r = client.post(url, json=payload)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500 or i == max_retries - 1:
                    raise
                time.sleep(2 ** i)

# Async streaming
async def stream_download(url: str, dest: Path) -> None:
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                async for chunk in r.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
```

---

## itertools & functools

```python
import itertools
import functools
from collections import defaultdict

# Batching (chunking) de lista
def batched(iterable, n: int):
    it = iter(iterable)
    while chunk := list(itertools.islice(it, n)):
        yield chunk

# Flatten de lista aninhada
def flatten(nested: list) -> list:
    return list(itertools.chain.from_iterable(nested))

# groupby com sort prévio
def group_by_key(items: list[dict], key: str) -> dict[str, list]:
    sorted_items = sorted(items, key=lambda x: x[key])
    return {k: list(v) for k, v in itertools.groupby(sorted_items, key=lambda x: x[key])}

# reduce para composição de funções
def compose(*fns):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), fns)

# partial application
from functools import partial

def multiply(x: int, y: int) -> int:
    return x * y

double = partial(multiply, y=2)
triple = partial(multiply, y=3)

# lru_cache com maxsize
@functools.lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

---

## Environment & Logging Setup

```python
import os
import logging
import logging.config
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# Helper para env var com fallback e validação
def get_env(key: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(f"Missing required env var: {key}")
    return value

# Logging estruturado (JSON-like)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "simple": {"format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
```

---

> [!tip] Uso com FastAPI
> Para usar esses snippets em projetos [[fastapi]], combine `AppSettings` com `@retry` nos endpoints de integração externa. Veja também [[django]] para alternativas no ORM.

> [!info] Referências Relacionadas
> - Containerize seus scripts com [[docker-snippets]]
> - Automatize tarefas shell com [[bash-snippets]]
