---
tags: [skill, frameworks, svelte]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Svelte, SvelteKit]
---

# Svelte / SvelteKit

## Overview

Svelte 5 introduziu os **Runes** — uma reformulação completa do sistema de reatividade. Ao invés de reatividade implícita via análise de AST em tempo de compilação, Runes são funções explícitas (`$state`, `$derived`, `$effect`) que tornam a reatividade declarativa e composível fora de componentes `.svelte`. O resultado é uma DX superior para lógica complexa e reatividade mais previsível.

> [!info] Svelte vs React
> Svelte compila para JavaScript vanilla — sem virtual DOM, sem runtime pesado. Comparado com [[react]], o bundle é menor e a performance de atualização de DOM é direta. Comparado com [[nextjs]], SvelteKit é mais simples mas menos maduro para apps enterprise.

SvelteKit é o framework full-stack equivalente ao [[nextjs]] para o ecossistema Svelte: routing baseado em arquivos, SSR/SSG/SPA modes, load functions server-side, form actions, e hooks. Integra bem com [[typescript]] e pode coexistir em projetos [[astro]] como islands. Para comparação com abordagem diferente, ver [[htmx]].

---

## Core Concepts

### Runes — Sistema de Reatividade Svelte 5

```svelte
<script lang="ts">
  // $state — reactive primitive (replaces let with reactivity)
  let count = $state(0)
  let user = $state({ name: "Alice", age: 30 })

  // $derived — computed value (replaces $: reactive statement)
  let doubled = $derived(count * 2)
  let greeting = $derived(`Hello, ${user.name}!`)

  // $derived.by — for complex derivations
  let sortedItems = $derived.by(() => {
    return [...items].sort((a, b) => a.name.localeCompare(b.name))
  })

  // $effect — side effects (replaces afterUpdate + onMount for reactive deps)
  $effect(() => {
    document.title = `Count: ${count}`
    // Cleanup runs before re-execution or unmount
    return () => {
      document.title = "App"
    }
  })

  // $effect.pre — runs before DOM update (like useLayoutEffect)
  $effect.pre(() => {
    console.log("Before DOM update:", count)
  })

  // $props — typed component props (replaces export let)
  let { title, onClose }: { title: string; onClose: () => void } = $props()
</script>
```

### Runes Fora de Componentes (Composable Logic)

```ts
// src/lib/stores/counter.svelte.ts
// Runes work in .svelte.ts files — reusable reactive logic
export function createCounter(initial = 0) {
  let count = $state(initial)
  let history = $state<number[]>([])

  return {
    get count() { return count },
    get history() { return history },
    increment() {
      history.push(count)
      count++
    },
    decrement() {
      history.push(count)
      count--
    },
    reset() {
      history = []
      count = initial
    },
  }
}

// Usage in component
import { createCounter } from "$lib/stores/counter.svelte"
const counter = createCounter(10)
// counter.count is reactive — template updates automatically
```

### $state.raw — Fine-grained Control

```svelte
<script lang="ts">
  // $state.raw — not deeply reactive (avoids proxying large objects)
  let config = $state.raw({
    theme: "dark",
    language: "en",
    features: { beta: false },
  })

  // Must reassign to trigger reactivity
  function toggleBeta() {
    config = { ...config, features: { ...config.features, beta: !config.features.beta } }
  }
</script>
```

---

## Patterns

### SvelteKit — Load Functions

```ts
// src/routes/users/[id]/+page.server.ts
import type { PageServerLoad, Actions } from "./$types"
import { error, fail } from "@sveltejs/kit"

export const load: PageServerLoad = async ({ params, locals, fetch }) => {
  const user = await locals.db.users.findOne(params.id)
  if (!user) error(404, "User not found")

  // Parallel fetching
  const [posts, followers] = await Promise.all([
    locals.db.posts.findByUser(params.id),
    locals.db.follows.countFollowers(params.id),
  ])

  return { user, posts, followers }
  // Returned data is serialized and sent to the client
}

// +page.svelte receives data prop
// let { data } = $props()  →  data.user, data.posts, etc.
```

### SvelteKit — Form Actions

```ts
// src/routes/users/[id]/+page.server.ts
export const actions: Actions = {
  updateProfile: async ({ request, params, locals }) => {
    const formData = await request.formData()
    const name = formData.get("name") as string

    if (!name || name.length < 2) {
      return fail(422, { name, error: "Name too short" })
    }

    await locals.db.users.update(params.id, { name })
    return { success: true }
  },

  deleteAccount: async ({ params, locals, cookies }) => {
    await locals.db.users.delete(params.id)
    cookies.delete("session", { path: "/" })
    return redirect(303, "/goodbye")
  },
}
```

```svelte
<!-- +page.svelte -->
<script lang="ts">
  import { enhance } from "$app/forms"
  let { data, form } = $props()
</script>

<form method="POST" action="?/updateProfile" use:enhance>
  <input name="name" value={data.user.name} />
  {#if form?.error}<p class="error">{form.error}</p>{/if}
  <button>Save</button>
</form>
```

### SvelteKit Hooks

```ts
// src/hooks.server.ts
import type { Handle, HandleFetch } from "@sveltejs/kit"
import { sequence } from "@sveltejs/kit/hooks"

const authHook: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get("auth-token")
  if (token) {
    event.locals.user = await validateToken(token)
  }
  return resolve(event)
}

const corsHook: Handle = async ({ event, resolve }) => {
  if (event.request.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE",
      },
    })
  }
  const response = await resolve(event)
  response.headers.set("Access-Control-Allow-Origin", "*")
  return response
}

export const handle = sequence(authHook, corsHook)

// Intercept external fetch calls from load functions
export const handleFetch: HandleFetch = async ({ request, fetch }) => {
  if (request.url.startsWith("https://internal-api/")) {
    request = new Request(request.url.replace("https://internal-api/", "http://localhost:8000/"), request)
  }
  return fetch(request)
}
```

### Transitions e Animations

```svelte
<script lang="ts">
  import { fade, fly, slide, scale } from "svelte/transition"
  import { flip } from "svelte/animate"
  import { quintOut } from "svelte/easing"

  let items = $state(["a", "b", "c"])
  let visible = $state(true)
</script>

{#if visible}
  <div transition:fly={{ y: -20, duration: 300, easing: quintOut }}>
    Animated in/out
  </div>
{/if}

<!-- Keyed each for flip animation -->
{#each items as item (item)}
  <div animate:flip={{ duration: 300 }} transition:fade>
    {item}
  </div>
{/each}
```

### Stores Migration para Runes

```ts
// ANTES — Svelte 4 writable store
import { writable, derived } from "svelte/store"
const count = writable(0)
const doubled = derived(count, $c => $c * 2)

// DEPOIS — Svelte 5 runes (em .svelte.ts)
export function createAppState() {
  let count = $state(0)
  let doubled = $derived(count * 2)

  return {
    get count() { return count },
    get doubled() { return doubled },
    increment: () => count++,
  }
}
// Stores ainda funcionam no Svelte 5 para interop com libs externas
```

---

## Gotchas

> [!danger] $effect com dependências circulares
> Um `$effect` que lê e escreve o mesmo `$state` cria um loop infinito. O Svelte detecta e lança erro em dev, mas o padrão deve ser evitado.

```svelte
<script>
  let count = $state(0)

  // ERRADO — loop infinito
  $effect(() => {
    count = count + 1  // lê e escreve count
  })

  // CORRETO — use $derived para transformações
  let incremented = $derived(count + 1)
</script>
```

> [!warning] Reatividade de arrays/objetos com $state
> O `$state` cria um Proxy profundo. Mutações diretas (`arr.push()`, `obj.key = val`) são reativas. Mas objetos retornados por funções externas (ex: resultado de fetch) precisam ser wrapped.

```svelte
<script>
  let todos = $state([])

  async function loadTodos() {
    const data = await fetchTodos()
    todos = data  // OK — reassignment
    // ou: todos.push(...data)  — também reativo com proxy
  }
</script>
```

> [!warning] SSR e browser APIs
> Load functions server-side não têm acesso a `window`, `localStorage`, `document`. Use `browser` do `$app/environment` para guards.

```ts
import { browser } from "$app/environment"
if (browser) {
  localStorage.setItem("key", "value")
}
```

---

## Snippets

### Snippet (Svelte 5 — substitui slots)

```svelte
<!-- Component.svelte -->
<script lang="ts">
  let { header, children }: {
    header: Snippet<[string]>,
    children: Snippet,
  } = $props()
</script>

<div>
  {@render header("Title")}
  {@render children()}
</div>

<!-- Usage -->
<Component>
  {#snippet header(title)}
    <h1>{title}</h1>
  {/snippet}
  <p>Body content</p>
</Component>
```

### SvelteKit API Route

```ts
// src/routes/api/users/+server.ts
import { json, error } from "@sveltejs/kit"
import type { RequestHandler } from "./$types"

export const GET: RequestHandler = async ({ locals, url }) => {
  const page = Number(url.searchParams.get("page") ?? 1)
  const users = await locals.db.users.paginate(page)
  return json(users)
}

export const POST: RequestHandler = async ({ request, locals }) => {
  const body = await request.json()
  const user = await locals.db.users.create(body)
  return json(user, { status: 201 })
}
```

---

## References

- [Svelte 5 Runes](https://svelte.dev/docs/svelte/what-are-runes)
- [SvelteKit Docs](https://svelte.dev/docs/kit/introduction)
- [Svelte 4 → 5 Migration](https://svelte.dev/docs/svelte/v5-migration-guide)

---

## Related

- [[typescript]]
- [[react]]
- [[astro]]
- [[nextjs]]
- [[htmx]]
