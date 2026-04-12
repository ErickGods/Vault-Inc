---
tags: [skill, frameworks, django]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Django]
---

# Django

## Overview

Django é o framework web [[python]] "batteries included" mais maduro do ecossistema. Oferece ORM poderoso, sistema de autenticação, admin, migrações, e uma filosofia de "convention over configuration" que reduz drasticamente o boilerplate. É a escolha dominante para sistemas de gestão, plataformas SaaS e APIs internas com integração a [[postgresql]].

> [!info] Django em 2025+
> Django Ninja tornou-se o padrão de facto para APIs REST modernas em Django, oferecendo uma experiência similar ao [[fastapi]] com type hints e Pydantic, sem abandonar o ecossistema Django. HTMX ([[htmx]]) revitalizou o padrão "fullstack Django" com interatividade sem SPA.

A arquitetura Django segue [[clean-architecture]] naturalmente: models (domínio), views (use cases), templates/serializers (presentação). Deploy em [[docker]] é straightforward com Gunicorn + Nginx, integrando com [[postgresql]] via psycopg3. Comparado com [[fastapi]], Django oferece mais "out of the box" mas menos performance em I/O intensivo puro.

---

## Core Concepts

### ORM Avançado — Q, F, Subquery

```python
from django.db.models import Q, F, Subquery, OuterRef, Count, Sum, Avg, Prefetch
from django.db.models.functions import Coalesce
from decimal import Decimal

# Q objects — complex boolean filtering
User.objects.filter(
    Q(is_active=True) & (Q(plan="pro") | Q(credits__gt=0))
)

# F expressions — reference other fields (avoids Python-level evaluation)
# Atomic update — safe in concurrent requests
Product.objects.filter(id=product_id).update(
    stock=F("stock") - 1,
    sales_count=F("sales_count") + 1,
)

# Compare fields in same model
User.objects.filter(login_count__gt=F("profile_views") * 2)

# Subquery — correlated subquery
latest_order = Order.objects.filter(
    user=OuterRef("pk")
).order_by("-created_at").values("total")[:1]

users_with_last_order = User.objects.annotate(
    last_order_total=Subquery(latest_order)
)

# Complex aggregation
stats = Order.objects.filter(
    status="completed",
    created_at__year=2025,
).aggregate(
    total_revenue=Sum("total"),
    avg_order_value=Avg("total"),
    order_count=Count("id"),
    avg_items=Avg("items_count"),
)
```

### select_related e prefetch_related

```python
# select_related — SQL JOIN for ForeignKey/OneToOne (reduces queries)
posts = Post.objects.select_related(
    "author",
    "author__profile",  # nested FK
    "category",
).all()

# prefetch_related — separate queries for ManyToMany/reverse FK
posts = Post.objects.prefetch_related(
    "tags",
    Prefetch(
        "comments",
        queryset=Comment.objects.filter(is_approved=True).select_related("author"),
        to_attr="approved_comments",  # accessible as post.approved_comments
    ),
).all()

# Custom manager with default prefetch
class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("author", "category")

    def published(self):
        return self.get_queryset().filter(status="published").prefetch_related("tags")
```

---

## Patterns

### Django Ninja — Modern API

```python
# api.py
from ninja import NinjaAPI, Schema, Query
from ninja.security import HttpBearer
from ninja.pagination import paginate, PageNumberPagination

class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            payload = decode_jwt(token)
            return User.objects.get(id=payload["sub"])
        except (User.DoesNotExist, JWTError):
            return None

api = NinjaAPI(auth=AuthBearer())

class UserSchema(Schema):
    id: int
    email: str
    full_name: str

    @staticmethod
    def resolve_full_name(obj) -> str:
        return f"{obj.first_name} {obj.last_name}"

class UserCreateSchema(Schema):
    email: str
    password: str
    first_name: str
    last_name: str

class FilterParams(Schema):
    search: str | None = None
    is_active: bool = True

@api.get("/users", response=list[UserSchema])
@paginate(PageNumberPagination, page_size=20)
def list_users(request, filters: FilterParams = Query(...)):
    qs = User.objects.filter(is_active=filters.is_active)
    if filters.search:
        qs = qs.filter(
            Q(first_name__icontains=filters.search) |
            Q(email__icontains=filters.search)
        )
    return qs

@api.post("/users", response={201: UserSchema, 422: dict}, auth=None)
def create_user(request, payload: UserCreateSchema):
    if User.objects.filter(email=payload.email).exists():
        return 422, {"detail": "Email already registered"}
    user = User.objects.create_user(**payload.dict())
    return 201, user
```

### DRF — Serializers e ViewSets

```python
from rest_framework import serializers, viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "posts_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_full_name(self, obj) -> str:
        return obj.get_full_name()

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already in use")
        return value.lower()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "plan"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["created_at", "email"]

    def get_queryset(self):
        return User.objects.annotate(
            posts_count=Count("posts")
        ).select_related("profile")

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"status": "deactivated"})
```

### Signals

```python
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # Send welcome email asynchronously
        send_welcome_email.delay(instance.id)

@receiver(pre_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    # Cleanup S3 files before deletion
    storage.delete_directory(f"users/{instance.id}/")
    logger.info("Cleaned up data for user %s", instance.id)

# Custom signal
from django.dispatch import Signal

order_completed = Signal()  # provides: sender, order, user

@receiver(order_completed)
def update_user_stats(sender, order, user, **kwargs):
    user.stats.total_orders = F("total_orders") + 1
    user.stats.save(update_fields=["total_orders"])
```

### Async Views

```python
import asyncio
from django.http import JsonResponse
from django.views import View
import httpx

class AsyncDashboard(View):
    async def get(self, request, user_id: int):
        # Parallel async I/O — Django 4.1+
        async with httpx.AsyncClient() as client:
            stats_task = client.get(f"http://stats-service/users/{user_id}")
            activity_task = client.get(f"http://activity-service/users/{user_id}")
            stats_resp, activity_resp = await asyncio.gather(stats_task, activity_task)

        # Django ORM async methods
        user = await User.objects.aget(pk=user_id)
        recent_orders = [order async for order in Order.objects.filter(user=user).aiterator()]

        return JsonResponse({
            "user": user.email,
            "stats": stats_resp.json(),
            "activity": activity_resp.json(),
            "orders": [o.id for o in recent_orders],
        })
```

### Custom Middleware

```python
import time
import logging
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware(MiddlewareMixin):
    logger = logging.getLogger("requests")

    def process_request(self, request):
        request._start_time = time.perf_counter()

    def process_response(self, request, response):
        duration = time.perf_counter() - getattr(request, "_start_time", time.perf_counter())
        self.logger.info(
            "%s %s %s %.3fms",
            request.method,
            request.path,
            response.status_code,
            duration * 1000,
        )
        return response
```

### Migrations Best Practices

```python
# migrations/0042_add_user_credits.py
from django.db import migrations, models

def backfill_credits(apps, schema_editor):
    """Data migration — backfill existing users"""
    User = apps.get_model("accounts", "User")
    # Use update() for bulk operations — NEVER iterate with save()
    User.objects.filter(plan="pro").update(credits=100)
    User.objects.filter(plan="free").update(credits=10)

def reverse_backfill(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.update(credits=None)

class Migration(migrations.Migration):
    dependencies = [("accounts", "0041_user_plan")]

    operations = [
        # Schema migration
        migrations.AddField(
            model_name="user",
            name="credits",
            field=models.IntegerField(null=True, blank=True),
        ),
        # Data migration
        migrations.RunPython(backfill_credits, reverse_backfill),
        # Make non-nullable after backfill
        migrations.AlterField(
            model_name="user",
            name="credits",
            field=models.IntegerField(default=0),
        ),
    ]
```

---

## Gotchas

> [!danger] N+1 no ORM Django
> Acessar ForeignKey em um loop sem `select_related` dispara uma query por iteração. Django Debug Toolbar e `django-silk` identificam esse problema em desenvolvimento.

```python
# ERRADO — N+1: 1 query para posts + N queries para author
posts = Post.objects.all()
for post in posts:
    print(post.author.name)  # query por iteração!

# CORRETO — 1 JOIN
posts = Post.objects.select_related("author").all()
```

> [!warning] Signals podem mascarar side effects
> Signals criam acoplamento implícito. Um `post_save` que envia email é invisível no código de criação. Use signals com parcimônia e prefira serviços explícitos para lógica de negócio crítica.

> [!warning] Migrations em produção com downtime zero
> Adicionar uma coluna NOT NULL sem default causa lock na tabela em PostgreSQL. A sequência segura é: (1) adicionar com `null=True`, (2) fazer deploy, (3) backfill, (4) adicionar constraint NOT NULL.

```python
# PASSO 1 — safe to deploy
field=models.CharField(max_length=100, null=True, blank=True)
# PASSO 2 — after backfill
field=models.CharField(max_length=100, db_default="")
```

---

## Snippets

### Custom Manager + QuerySet

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, deleted_at__isnull=True)

class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published", published_at__lte=timezone.now())

    def by_tag(self, tag_slug):
        return self.filter(tags__slug=tag_slug)

    def with_stats(self):
        return self.annotate(
            comment_count=Count("comments"),
            like_count=Count("likes"),
        )

class Post(models.Model):
    objects = PostQuerySet.as_manager()
    active = ActiveManager.from_queryset(PostQuerySet)()
```

### Celery Task with Django ORM

```python
from celery import shared_task
from django.db import transaction

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_order(self, order_id: int):
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order_id)
            if order.status != "pending":
                return  # already processed
            # Process...
            order.status = "completed"
            order.save(update_fields=["status"])
            order_completed.send(sender=Order, order=order, user=order.user)
    except Exception as exc:
        raise self.retry(exc=exc)
```

---

## References

- [Django Docs](https://docs.djangoproject.com/)
- [Django Ninja](https://django-ninja.dev/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [Django ORM Cookbook](https://books.agiliq.com/projects/django-orm-cookbook/)

---

## Related

- [[python]]
- [[postgresql]]
- [[docker]]
- [[htmx]]
- [[fastapi]]
- [[clean-architecture]]
