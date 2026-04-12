---
tags: [skill, frameworks, htmx]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [HTMX, htmx]
---

# HTMX

## Overview

HTMX é uma biblioteca que devolve ao HTML o poder de fazer requisições HTTP arbitrárias, troca de conteúdo parcial (partial DOM swaps) e interações assíncronas — sem JavaScript customizado. Seu modelo mental é "Hypermedia as the Engine of Application State" (HATEOAS): o servidor retorna HTML, não JSON, e o browser atualiza apenas o fragmento relevante.

> [!info] HTMX vs SPA Frameworks
> HTMX não compete com [[react]] ou [[svelte]] em apps com estado global complexo. É ideal para aplicações Django/Rails/Laravel onde o servidor já renderiza HTML e você quer adicionar interatividade sem migrar para uma SPA. Comparar com [[astro]] (islands) e [[react]] para entender trade-offs.

A combinação [[django]] + HTMX é especialmente poderosa: views retornam fragmentos HTML, formulários submetem via HTMX sem page reload, e a complexidade de frontend é mínima. [[fastapi]] também integra bem via templates Jinja2. Para [[deployment-strategies]], HTMX apps são simples de containerizar com [[docker]] pois não têm build step de frontend.

---

## Core Concepts

### Atributos Fundamentais

```html
<!-- hx-get: fetch and swap HTML fragment -->
<button hx-get="/api/users" hx-target="#user-list" hx-swap="innerHTML">
  Load Users
</button>

<!-- hx-post: submit data -->
<form hx-post="/api/users" hx-target="#result" hx-swap="outerHTML">
  <input name="name" type="text" />
  <button type="submit">Create</button>
</form>

<!-- hx-put / hx-patch / hx-delete -->
<button
  hx-delete="/api/users/42"
  hx-target="closest li"
  hx-swap="outerHTML swap:0.3s"
  hx-confirm="Are you sure?"
>
  Delete
</button>

<!-- hx-trigger: event that fires the request -->
<input
  hx-get="/api/search"
  hx-trigger="keyup changed delay:300ms"
  hx-target="#results"
  name="q"
/>
```

### hx-swap Strategies

```html
<!-- innerHTML (default) — replace content inside target -->
<div id="content" hx-get="/fragment" hx-swap="innerHTML"></div>

<!-- outerHTML — replace the element itself -->
<li hx-delete="/items/1" hx-swap="outerHTML">Item 1</li>

<!-- beforebegin / afterbegin / beforeend / afterend -->
<ul id="todo-list">
  <button hx-get="/todos/new" hx-swap="beforeend" hx-target="#todo-list">
    Add Todo
  </button>
</ul>

<!-- none — don't swap, useful for side effects with OOB -->
<button hx-post="/api/action" hx-swap="none">Trigger Action</button>

<!-- delete — remove the element -->
<div hx-delete="/api/items/1" hx-swap="delete" hx-trigger="click">
  Click to remove
</div>
```

### hx-trigger Advanced

```html
<!-- Multiple triggers -->
<div hx-get="/poll" hx-trigger="load, every 5s"></div>

<!-- Event from a different element (from:) -->
<input id="search-input" type="text" name="q" />
<div
  hx-get="/search"
  hx-trigger="keyup from:#search-input changed delay:300ms"
  hx-target="#results"
  hx-include="#search-input"
></div>

<!-- Intersection observer trigger -->
<div hx-get="/lazy-content" hx-trigger="intersect once" hx-swap="outerHTML">
  Loading...
</div>

<!-- Custom events -->
<div hx-get="/refresh" hx-trigger="refresh-data from:body"></div>
```

---

## Patterns

### Django Integration

```python
# views.py
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

def user_list(request):
    """Full page render"""
    users = User.objects.all()
    return render(request, "users/list.html", {"users": users})

@require_http_methods(["GET"])
def user_list_fragment(request):
    """HTMX partial — returns only the list fragment"""
    users = User.objects.filter(
        name__icontains=request.GET.get("q", "")
    )
    # If HTMX request, return fragment; otherwise full page
    if request.htmx:  # django-htmx middleware
        return render(request, "users/_list.html", {"users": users})
    return render(request, "users/list.html", {"users": users})

@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    User.objects.filter(pk=user_id).delete()
    return HttpResponse(status=200)  # empty response — hx-swap="outerHTML delete"
```

```python
# urls.py
urlpatterns = [
    path("users/", views.user_list, name="user-list"),
    path("users/<int:user_id>/delete/", views.delete_user, name="user-delete"),
]
```

```html
<!-- templates/users/list.html -->
<div id="user-list">
  {% include "users/_list.html" %}
</div>

<input
  type="search"
  name="q"
  placeholder="Search..."
  hx-get="{% url 'user-list' %}"
  hx-target="#user-list"
  hx-trigger="keyup changed delay:300ms"
/>
```

```html
<!-- templates/users/_list.html (fragment) -->
{% for user in users %}
<li id="user-{{ user.id }}">
  {{ user.name }}
  <button
    hx-delete="{% url 'user-delete' user.id %}"
    hx-target="#user-{{ user.id }}"
    hx-swap="outerHTML"
  >
    Delete
  </button>
</li>
{% endfor %}
```

### FastAPI Integration (Jinja2)

```python
# main.py
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/users/search", response_class=HTMLResponse)
async def search_users(request: Request, q: str = ""):
    users = await db.users.search(q)
    # Return only the fragment for HTMX, full page for direct access
    template = "_user_rows.html" if request.headers.get("HX-Request") else "users.html"
    return templates.TemplateResponse(template, {"request": request, "users": users})

@app.post("/users", response_class=HTMLResponse)
async def create_user(request: Request, name: str = Form(...), email: str = Form(...)):
    user = await db.users.create({"name": name, "email": email})
    return templates.TemplateResponse("_user_row.html", {"request": request, "user": user})
```

### Out-of-Band (OOB) Swaps

```html
<!-- Server returns multiple swaps in one response -->
<!-- Primary swap: updates #main-content -->
<!-- OOB swap: simultaneously updates #notification-count -->

<!-- Server response HTML: -->
<div id="cart-items"><!-- updated cart --></div>

<span id="cart-count" hx-swap-oob="true">3</span>
<div id="toast" hx-swap-oob="true" class="toast">Item added!</div>
```

### Response Headers

```python
# Django — trigger client-side events via headers
from django_htmx.http import trigger_client_event, HttpResponseClientRedirect

def create_item(request):
    item = Item.objects.create(name=request.POST["name"])
    response = render(request, "_item.html", {"item": item})
    # Trigger custom event on client
    trigger_client_event(response, "itemCreated", {"id": item.id})
    return response

# Redirect after action
def delete_and_redirect(request, pk):
    Item.objects.filter(pk=pk).delete()
    return HttpResponseClientRedirect("/items/")
```

```python
# FastAPI — manual headers
from fastapi import Response

@app.post("/items")
async def create_item(response: Response, name: str = Form(...)):
    item = await db.items.create(name=name)
    response.headers["HX-Trigger"] = json.dumps({"itemCreated": {"id": item.id}})
    return templates.TemplateResponse("_item.html", {"item": item})

# HX-Redirect: navigate client to new URL
response.headers["HX-Redirect"] = "/items/"

# HX-Refresh: force full page reload
response.headers["HX-Refresh"] = "true"
```

### Alpine.js Companion

```html
<!-- HTMX handles server communication; Alpine.js handles local state -->
<div x-data="{ open: false, count: 0 }">
  <!-- Alpine for local toggle -->
  <button @click="open = !open">Toggle Details</button>

  <!-- HTMX for server data -->
  <button
    hx-get="/api/count"
    hx-on::after-request="count = parseInt($event.detail.xhr.responseText)"
  >
    Refresh Count
  </button>

  <template x-if="open">
    <div hx-get="/details" hx-trigger="load" hx-swap="innerHTML">
      Loading...
    </div>
  </template>

  <span x-text="count"></span>
</div>
```

### WebSocket Extension

```html
<div hx-ext="ws" ws-connect="/ws/chat">
  <div id="messages"></div>
  <form ws-send>
    <input name="message" type="text" />
    <button type="submit">Send</button>
  </form>
</div>
```

```html
<!-- SSE Extension -->
<div hx-ext="sse" sse-connect="/api/events">
  <div sse-swap="notification" hx-swap="beforeend" id="notifications">
    <!-- New notifications stream here -->
  </div>
</div>
```

---

## Gotchas

> [!warning] CSRF com HTMX em Django
> HTMX não inclui o CSRF token automaticamente. Use o middleware `django-htmx` e inclua o token via `hx-headers` no `<body>` ou configure globalmente.

```html
<!-- Solução global — adicione ao <body> -->
<body
  hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
>
```

```python
# settings.py — com django-htmx
MIDDLEWARE = [
    "django_htmx.middleware.HtmxMiddleware",
    # ...
]
```

> [!danger] hx-swap="outerHTML" com hx-target pode ser confuso
> `hx-swap="outerHTML"` troca o elemento *alvo* inteiro, não o elemento com o atributo. Se `hx-target` aponta para outro elemento, esse elemento é removido/substituído. Confirme qual elemento você quer preservar vs substituir.

> [!warning] Histórico de navegação
> HTMX atualiza o DOM mas não o histórico do browser por padrão. Use `hx-push-url="true"` para pushState. Mas atenção: ao voltar, o browser fará um GET completo — o servidor deve retornar a página completa, não apenas o fragmento.

---

## Snippets

### Loading Indicator

```html
<!-- Global indicator -->
<div id="loading-indicator" class="htmx-indicator">
  <span>Loading...</span>
</div>

<!-- Inline indicator -->
<button
  hx-get="/slow-endpoint"
  hx-indicator="#btn-spinner"
>
  <span id="btn-spinner" class="htmx-indicator">⏳</span>
  Load Data
</button>
```

### hx-boost — Progressive Enhancement

```html
<!-- Convert all links/forms in this scope to HTMX requests -->
<div hx-boost="true">
  <a href="/page1">Page 1</a>  <!-- now uses HTMX instead of full navigation -->
  <form action="/submit" method="POST">...</form>  <!-- HTMX POST -->
</div>
```

---

## References

- [HTMX Docs](https://htmx.org/docs/)
- [django-htmx](https://django-htmx.readthedocs.io/)
- [HTMX Response Headers](https://htmx.org/reference/#response_headers)
- [Alpine.js](https://alpinejs.dev/)

---

## Related

- [[django]]
- [[fastapi]]
- [[react]]
- [[astro]]
- [[deployment-strategies]]
