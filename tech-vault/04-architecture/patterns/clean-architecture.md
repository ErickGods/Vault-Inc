---
tags: [skill, architecture, clean-architecture]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Clean Architecture, Hexagonal, Ports and Adapters]
---

# Clean Architecture

## Overview

Clean Architecture (Robert C. Martin, 2017) é um conjunto de princípios que organiza o código em camadas concêntricas com uma regra fundamental: **dependências só apontam para dentro**. O código de negócio nunca depende de frameworks, bancos de dados ou interfaces de usuário.

> [!important] A Dependency Rule
> Código fonte de uma camada externa pode depender de camadas internas. Nunca o contrário. O domínio (centro) não importa nada do FastAPI, SQLAlchemy ou qualquer framework.

Hexagonal Architecture (Alistair Cockburn, 2005) — também chamada Ports & Adapters — expressa o mesmo conceito de forma diferente: a aplicação se comunica com o mundo externo apenas através de **ports** (interfaces) e **adapters** (implementações concretas).

Ambas visam o mesmo objetivo: **testabilidade e substituibilidade**. Trocar PostgreSQL por DynamoDB não deve exigir tocar na lógica de negócio.

---

## Core Concepts

### As Quatro Camadas

```
┌─────────────────────────────────────────┐
│  Frameworks & Drivers (camada externa)  │  FastAPI, SQLAlchemy, Redis, HTTP
├─────────────────────────────────────────┤
│  Interface Adapters                     │  Controllers, Presenters, Gateways
├─────────────────────────────────────────┤
│  Application / Use Cases                │  Regras de aplicação, Interactors
├─────────────────────────────────────────┤
│  Entities / Domain (camada interna)     │  Regras de negócio puras, sem imports externos
└─────────────────────────────────────────┘
```

**Entities**: objetos que encapsulam regras de negócio críticas. Sem dependências externas. Sobrevivem à troca de qualquer framework.

**Use Cases**: orquestram o fluxo de dados entre entidades. Implementam casos de uso específicos da aplicação. Dependem apenas de interfaces (ports), nunca de implementações.

**Interface Adapters**: convertem dados do formato dos use cases para o formato conveniente para agentes externos (e vice-versa). DTOs, presenters, repositórios concretos vivem aqui.

**Frameworks & Drivers**: detalhes. FastAPI routes, SQLAlchemy models, Celery tasks. Trocáveis sem impacto no domínio.

### Ports & Adapters (Hexagonal)

```python
# PORT — interface pura no domínio (interna)
from abc import ABC, abstractmethod
from domain.entities import User

class UserRepository(ABC):
    """Port: contrato que o domínio conhece."""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def exists_with_email(self, email: str) -> bool: ...

# ADAPTER — implementação concreta na camada externa
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.models import UserModel

class PostgresUserRepository(UserRepository):
    """Adapter: implementação SQL do port."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self._session.get(UserModel, user_id)
        if not result:
            return None
        return User(id=result.id, email=result.email, name=result.name)

    async def save(self, user: User) -> None:
        model = UserModel(id=user.id, email=user.email, name=user.name)
        self._session.merge(model)
        await self._session.flush()

    async def exists_with_email(self, email: str) -> bool:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None
```

---

## Patterns

### Use Case Interactors

O use case é a unidade central da arquitetura. Coordena entidades e chama ports. Não sabe nada de HTTP, SQL ou qualquer framework.

```python
# domain/entities.py — puro Python, zero imports externos
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class User:
    id: str
    email: str
    name: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self):
        if not self.is_active:
            raise ValueError("User is already inactive")
        self.is_active = False

    def change_email(self, new_email: str):
        if "@" not in new_email:
            raise ValueError(f"Invalid email: {new_email}")
        self.email = new_email

# application/use_cases/register_user.py
@dataclass
class RegisterUserInput:
    name: str
    email: str
    password: str

@dataclass
class RegisterUserOutput:
    user_id: str
    email: str
    created_at: datetime

class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,          # Port, não implementação
        password_hasher: PasswordHasher,    # Port
        event_bus: EventBus,               # Port
    ):
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._event_bus = event_bus

    async def execute(self, input: RegisterUserInput) -> RegisterUserOutput:
        if await self._user_repo.exists_with_email(input.email):
            raise EmailAlreadyRegisteredError(input.email)

        hashed_password = self._password_hasher.hash(input.password)
        user = User(
            id=str(uuid.uuid4()),
            email=input.email,
            name=input.name,
        )

        await self._user_repo.save(user)
        await self._event_bus.publish(UserRegistered(user_id=user.id, email=user.email))

        return RegisterUserOutput(
            user_id=user.id,
            email=user.email,
            created_at=user.created_at,
        )
```

### Presenter e DTO Pattern

O presenter converte a output do use case para o formato específico da interface (HTTP JSON, CLI, gRPC). Isso evita acoplar o use case ao formato de resposta.

```python
# interface_adapters/presenters/user_presenter.py
from application.use_cases.register_user import RegisterUserOutput
from pydantic import BaseModel

class UserRegisteredResponse(BaseModel):
    """DTO de resposta HTTP — separado da entidade de domínio."""
    id: str
    email: str
    created_at: str  # ISO 8601 string para JSON

class UserPresenter:
    @staticmethod
    def present_registration(output: RegisterUserOutput) -> UserRegisteredResponse:
        return UserRegisteredResponse(
            id=output.user_id,
            email=output.email,
            created_at=output.created_at.isoformat(),
        )

# frameworks/fastapi/routers/users.py — camada mais externa
@router.post("/users", status_code=201, response_model=UserRegisteredResponse)
async def register_user(
    body: RegisterUserRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    """Controller: converte HTTP request → use case input → HTTP response."""
    output = await use_case.execute(RegisterUserInput(
        name=body.name,
        email=body.email,
        password=body.password,
    ))
    return UserPresenter.present_registration(output)
```

### Dependency Injection

A inversão de dependências é implementada via DI container. O use case declara o que precisa (ports); o container resolve as implementações concretas (adapters).

```python
# frameworks/fastapi/dependencies.py
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def get_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

async def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    return PostgresUserRepository(session)  # Adapter concreto injetado aqui

async def get_register_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo=user_repo,
        password_hasher=BcryptPasswordHasher(),
        event_bus=RabbitMQEventBus(),
    )
```

### Repository Pattern

O repository abstrai o mecanismo de persistência. O domínio trabalha com entidades puras; o repositório é responsável pela tradução para o modelo de dados.

> [!tip] Repository não é DAO
> DAO (Data Access Object) é uma abstração de tabelas. Repository é uma abstração de coleção de entidades de domínio. O repository pensa em objetos de negócio, não em linhas de banco.

---

## Gotchas

> [!danger] Anemic Domain Model
> O maior antipadrão em Clean Architecture: entidades sem comportamento, apenas getters/setters. Toda a lógica de negócio acaba nos use cases (que viram scripts procedurais). Entidades devem encapsular suas invariantes e comportamentos.

> [!warning] DTO Proliferation
> Clean Architecture pode gerar muitos DTOs: Request → Input → Entity → Output → Response. Para aplicações simples, isso é over-engineering. Avalie o custo/benefício: a camada de domínio tem lógica complexa que justifica o isolamento?

> [!bug] Circular Dependencies
> Se o use case precisa retornar uma entidade de domínio diretamente para o controller, e o controller importa do domínio, e o domínio importa do use case... você tem um ciclo. Use output DTOs no use case — nunca retorne a entidade diretamente.

### Estrutura de Diretórios Recomendada

```
src/
├── domain/
│   ├── entities/          # User, Order, Product — puro Python
│   ├── value_objects/     # Email, Money, Address
│   └── exceptions.py      # DomainError, BusinessRuleViolation
├── application/
│   ├── use_cases/         # RegisterUser, PlaceOrder
│   ├── ports/             # UserRepository (ABC), EventBus (ABC)
│   └── dtos/              # Input/Output dataclasses
├── infrastructure/
│   ├── repositories/      # PostgresUserRepository
│   ├── messaging/         # RabbitMQEventBus
│   └── models/            # SQLAlchemy ORM models
└── frameworks/
    ├── fastapi/
    │   ├── routers/       # HTTP route handlers
    │   ├── dependencies/  # DI wiring
    │   └── schemas/       # Pydantic request/response models
    └── celery/            # Async task workers
```

---

## Testing Boundaries

A principal vantagem de Clean Architecture é a testabilidade em camadas.

```python
# Teste unitário do use case — sem banco, sem HTTP, sem framework
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_register_user_raises_on_duplicate_email():
    # Arrange — fakes/mocks dos ports
    user_repo = AsyncMock(spec=UserRepository)
    user_repo.exists_with_email.return_value = True  # simula email já existente
    password_hasher = MagicMock(spec=PasswordHasher)
    event_bus = AsyncMock(spec=EventBus)

    use_case = RegisterUserUseCase(user_repo, password_hasher, event_bus)

    # Act + Assert
    with pytest.raises(EmailAlreadyRegisteredError):
        await use_case.execute(RegisterUserInput(
            name="Test User",
            email="existing@example.com",
            password="secret123",
        ))

    # Garantir que não foi salvo nem evento publicado
    user_repo.save.assert_not_called()
    event_bus.publish.assert_not_called()
```

---

## References

- **Clean Architecture** — Robert C. Martin (Uncle Bob), 2017
- **Hexagonal Architecture** — Alistair Cockburn, 2005 — [alistair.cockburn.us](https://alistair.cockburn.us/hexagonal-architecture/)
- **Domain-Driven Design** — Eric Evans — conceitos de entidades e value objects
- [[fastapi]] — implementação de referência para a camada de framework em Python
- [[django]] — alternativa com Django REST Framework
- [[python]] — linguagem principal dos exemplos
- [[typescript]] — implementação equivalente em TypeScript/Node.js

---

## Related

- [[microservices]] — Clean Architecture para a estrutura interna de cada serviço
- [[fastapi]] — framework web Python para a camada mais externa
- [[django]] — alternativa full-stack com ORM integrado
- [[typescript]] — implementação com TypeScript e inversão de dependências
- [[python]] — linguagem dos exemplos neste documento
