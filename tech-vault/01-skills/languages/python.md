---
tags: [skill, languages, python]
status: active
level: advanced
updated: 2026-04-05
aliases: [Python, Python3, py]
created: 2026-04-05
---

# Python

## Overview

Python é uma linguagem de alto nível com tipagem dinâmica e forte, amplamente adotada em data science, backend web e automação. Com o advento do Python 3.10+, recursos como structural pattern matching e melhorias no sistema de tipos elevaram a linguagem a um nível de expressividade comparável a linguagens funcionais modernas. Usar Python para serviços de alta performance é viável quando se compreende os trade-offs do GIL e as ferramentas certas de concorrência.

Quando usar: APIs web com [[fastapi]] ou [[django]], pipelines de ML/LLM com [[langchain]], scripts de automação, prototipagem rápida, glue code entre sistemas. Python brilha quando a velocidade de desenvolvimento supera a necessidade de performance raw e quando o ecossistema de bibliotecas é um diferencial.

Quando NÃO usar: sistemas com requisitos de latência sub-milissegundo, aplicações que precisam de controle fino de memória ou threads reais (considere Rust ou Go), quando o tamanho do binário distribuído é crítico. O GIL torna Python inadequado para CPU-bound parallelism puro — nesses casos, multiprocessing ou extensões nativas são necessários.

---

## Core Concepts

### Advanced Type Hints: ParamSpec, TypeVar, Protocol

Python's type system has evolved significantly. `ParamSpec` captures callable signatures for higher-order functions, enabling precise typing of decorators.

```python
from typing import ParamSpec, TypeVar, Callable
from functools import wraps
import time

P = ParamSpec("P")
R = TypeVar("R")

def timed(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timed
def heavy_compute(n: int, *, rounds: int = 10) -> list[int]:
    return [i ** 2 for i in range(n) for _ in range(rounds)]
```

`Protocol` enables structural subtyping (duck typing with static guarantees):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, object]: ...
    def to_json(self) -> str: ...

def persist(obj: Serializable) -> None:
    data = obj.to_dict()
    # No inheritance required — any class with these methods satisfies the Protocol
```

### Async/Await Patterns: asyncio, gather, TaskGroup

```python
import asyncio
from typing import Any

# Python 3.11+ TaskGroup — structured concurrency with automatic cancellation
async def fetch_all(urls: list[str]) -> list[Any]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    return [t.result() for t in tasks]

# gather with return_exceptions for partial failure handling
async def resilient_gather(*coros) -> list:
    results = await asyncio.gather(*coros, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

# Semaphore for rate-limiting concurrent tasks
async def bounded_fetch(urls: list[str], concurrency: int = 10) -> list[bytes]:
    sem = asyncio.Semaphore(concurrency)
    async def _fetch(url: str) -> bytes:
        async with sem:
            return await fetch(url)
    return await asyncio.gather(*[_fetch(u) for u in urls])
```

### Dataclasses vs Pydantic v2

```python
from dataclasses import dataclass, field
from pydantic import BaseModel, field_validator, model_validator
from typing import Self

# Dataclass: zero-dependency, fast, no validation
@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float
    tags: list[str] = field(default_factory=list)

# Pydantic v2: validation, serialization, JSON schema generation
class UserCreate(BaseModel):
    model_config = {"str_strip_whitespace": True, "frozen": True}

    name: str
    email: str
    age: int

    @field_validator("age")
    @classmethod
    def age_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError("age must be non-negative")
        return v

    @model_validator(mode="after")
    def check_adult_email(self) -> Self:
        if self.age < 18 and "minor" not in self.email:
            raise ValueError("underage users require special email")
        return self
```

### GIL Implications and Workarounds

The GIL prevents true thread parallelism for CPU-bound work. Strategies:

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np  # NumPy releases the GIL during C-level ops

# CPU-bound: use ProcessPoolExecutor
def cpu_task(chunk: list[int]) -> int:
    return sum(x ** 2 for x in chunk)

def parallel_cpu(data: list[int], workers: int = mp.cpu_count()) -> int:
    chunk_size = len(data) // workers
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return sum(pool.map(cpu_task, chunks))

# IO-bound: threads are fine since GIL is released during IO
def parallel_io(urls: list[str]) -> list[bytes]:
    with ThreadPoolExecutor(max_workers=32) as pool:
        return list(pool.map(requests.get, urls))
```

### Memory Profiling: tracemalloc and objgraph

```python
import tracemalloc
import objgraph

# tracemalloc — snapshot diffing to find leaks
tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# ... run suspect code ...

snapshot2 = tracemalloc.take_snapshot()
top_stats = snapshot2.compare_to(snapshot1, "lineno")
for stat in top_stats[:5]:
    print(stat)

# objgraph — find unexpected object retention
objgraph.show_most_common_types(limit=10)
objgraph.show_growth()  # delta since last call
# Find what's holding a reference:
objgraph.show_backrefs(objgraph.by_type("MyClass")[0], max_depth=3)
```

### Structural Pattern Matching (3.10+)

```python
from typing import TypeAlias

Event: TypeAlias = dict[str, object]

def handle_event(event: Event) -> str:
    match event:
        case {"type": "click", "button": int(btn), "pos": (x, y)}:
            return f"Click button {btn} at ({x}, {y})"
        case {"type": "keydown", "key": str(k)} if k.startswith("F"):
            return f"Function key: {k}"
        case {"type": "error", "code": int(c)} if c >= 500:
            return f"Server error: {c}"
        case _:
            return "Unknown event"
```

---

## Patterns

### Async Context Managers for Resource Management

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncpg  # PostgreSQL async driver used with [[postgresql]]

@asynccontextmanager
async def db_transaction(pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                yield conn
            except Exception:
                raise  # transaction auto-rolls back

# Usage in [[fastapi]] lifespan
from contextlib import asynccontextmanager as acm
from fastapi import FastAPI

@acm
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(dsn="postgresql://...")
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)
```

### Modern Packaging with uv and pyproject.toml

```toml
# pyproject.toml — replaces setup.py, setup.cfg, requirements.txt
[project]
name = "my-service"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "pydantic>=2.0",
    "asyncpg>=0.29",
]

[project.optional-dependencies]
dev = ["pytest-asyncio", "mypy", "ruff"]

[tool.uv]
dev-dependencies = ["pytest>=8", "httpx"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "ANN"]
```

```bash
# uv — ultra-fast package manager (replaces pip + venv + pip-tools)
uv sync                    # install all deps from lockfile
uv add fastapi             # add dependency and update lockfile
uv run pytest              # run in project virtualenv
uv pip compile             # generate requirements.txt from pyproject
```

---

## Gotchas

> [!warning] Mutável como Argumento Default
> Um dos bugs mais clássicos do Python — argumentos mutáveis como default são compartilhados entre chamadas:
> ```python
> # ERRADO
> def append_item(item: int, lst: list[int] = []) -> list[int]:
>     lst.append(item)
>     return lst
>
> append_item(1)  # [1]
> append_item(2)  # [1, 2] — mesmo objeto!
>
> # CORRETO
> def append_item(item: int, lst: list[int] | None = None) -> list[int]:
>     if lst is None:
>         lst = []
>     lst.append(item)
>     return lst
> ```

> [!danger] asyncio.run() dentro de Corrotinas
> `asyncio.run()` cria um novo event loop e **não pode** ser chamado de dentro de um loop já em execução. Em [[fastapi]] e ambientes como Jupyter, use `await` diretamente ou `asyncio.create_task()`.
> ```python
> # Vai explodir em FastAPI handlers:
> # asyncio.run(some_coroutine())
>
> # Correto — apenas await:
> result = await some_coroutine()
> ```

> [!warning] `__slots__` e Herança
> Usar `__slots__` em subclasses quando a classe pai não define `__slots__` anula o benefício — o `__dict__` da classe pai ainda é criado. Defina `__slots__` em toda a cadeia ou use `@dataclass(slots=True)` que cuida disso automaticamente.

> [!info] copy() vs deepcopy() em Dataclasses
> `dataclasses.replace()` faz shallow copy. Para objetos com listas/dicts aninhados, isso pode causar compartilhamento inesperado de estado mutável. Use `copy.deepcopy()` ou construa com `field(default_factory=...)`.

---

## Snippets

### Retry com Backoff Exponencial

```python
import asyncio
import random
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")

async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
    jitter: bool = True,
) -> T:
    for attempt in range(attempts):
        try:
            return await fn()
        except Exception as e:
            if attempt == attempts - 1:
                raise
            delay = base_delay * (2 ** attempt)
            if jitter:
                delay *= (0.5 + random.random())
            await asyncio.sleep(delay)
    raise RuntimeError("unreachable")
```

### Singleton Thread-Safe com Metaclass

```python
import threading
from typing import ClassVar, Any

class SingletonMeta(type):
    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabasePool(metaclass=SingletonMeta):
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
```

### Typed Settings com Pydantic v2 e env vars

```python
from pydantic_settings import BaseSettings
from pydantic import SecretStr, AnyHttpUrl

class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    database_url: SecretStr
    api_key: SecretStr
    base_url: AnyHttpUrl = "http://localhost:8000"
    debug: bool = False
    workers: int = 4

settings = Settings()  # auto-reads from env / .env file
db_url = settings.database_url.get_secret_value()
```

### Containerização com [[docker]]

```dockerfile
# Multi-stage build with uv
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

---

## References

- [Python Docs — typing](https://docs.python.org/3/library/typing.html)
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [asyncio — TaskGroup](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup)
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/)
- [uv — Astral](https://docs.astral.sh/uv/)
- [tracemalloc](https://docs.python.org/3/library/tracemalloc.html)

---

## Related

- [[fastapi]] — web framework assíncrono, usa Pydantic v2 nativamente
- [[django]] — framework full-stack, ORM síncrono com suporte async parcial
- [[langchain]] — orquestração de LLMs em Python
- [[postgresql]] — banco de dados principal usado com asyncpg/SQLAlchemy
- [[docker]] — containerização de aplicações Python
- [[python-snippets]] — snippets adicionais e utilitários reutilizáveis
