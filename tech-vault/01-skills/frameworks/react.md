---
tags: [skill, frameworks, react]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [React, ReactJS]
---

# React

## Overview

React 19 consolidou um conjunto de mudanças que transformam o modelo mental de desenvolvimento de interfaces. Server Components, o React Compiler, o hook `use()`, e Actions representam a evolução de uma biblioteca client-only para um sistema full-stack. A integração com [[nextjs]] é a forma mais madura de usar Server Components, mas o React standalone também evoluiu.

> [!info] React Compiler (React 19+)
> O React Compiler substitui a necessidade de `useMemo`, `useCallback` e `React.memo` na maioria dos casos. Ele analisa o código em tempo de compilação e insere memoização automaticamente onde é seguro fazê-lo.

Comparado com [[svelte]] e [[htmx]], React tem mais overhead de runtime mas um ecossistema incomparável. [[astro]] pode hospedar islands React para adicionar interatividade cirúrgica. [[typescript]] é considerado obrigatório em projetos React profissionais.

---

## Core Concepts

### Server Components

```tsx
// Roda APENAS no servidor — sem bundle client-side
// Pode fazer fetch direto, acessar DB, ler env secrets
async function UserProfile({ userId }: { userId: string }) {
  // Direct DB query — zero API overhead
  const user = await db.users.findOne(userId)
  const posts = await db.posts.findByUser(userId)

  return (
    <div>
      <h1>{user.name}</h1>
      {/* Pass serializable props to client components */}
      <FollowButton userId={userId} initialFollowed={user.isFollowed} />
      <PostList posts={posts} />
    </div>
  )
}
```

### use() Hook — Data Fetching & Context

```tsx
"use client"
import { use, Suspense } from "react"

// use() unwraps a Promise (replaces useEffect + useState for async)
function UserCard({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise)  // suspends until resolved
  return <div>{user.name}</div>
}

// use() also reads context conditionally (unlike useContext)
function ConditionalTheme({ show }: { show: boolean }) {
  if (!show) return null
  const theme = use(ThemeContext)  // valid — use() can be conditional
  return <div style={{ color: theme.primary }}>Themed content</div>
}

// Parent passes the promise
function App() {
  const userPromise = fetchUser("123")  // initiated outside, passed down
  return (
    <Suspense fallback={<Skeleton />}>
      <UserCard userPromise={userPromise} />
    </Suspense>
  )
}
```

### Concurrent Features

```tsx
"use client"
import { useTransition, useDeferredValue, startTransition } from "react"

// useTransition — mark state update as non-urgent
function SearchPage() {
  const [query, setQuery] = useState("")
  const [isPending, startTransition] = useTransition()
  const [results, setResults] = useState([])

  function handleSearch(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value
    setQuery(value)  // urgent — update input immediately

    startTransition(async () => {
      const data = await searchAPI(value)
      setResults(data)  // non-urgent — can be interrupted
    })
  }

  return (
    <>
      <input value={query} onChange={handleSearch} />
      {isPending && <Spinner />}
      <ResultList results={results} />
    </>
  )
}

// useDeferredValue — defer rendering of expensive component
function ExpensiveList({ filter }: { filter: string }) {
  const deferredFilter = useDeferredValue(filter)
  const isStale = filter !== deferredFilter

  return (
    <div style={{ opacity: isStale ? 0.5 : 1 }}>
      <HeavyVirtualizedList filter={deferredFilter} />
    </div>
  )
}
```

---

## Patterns

### State Management — Zustand

```tsx
import { create } from "zustand"
import { subscribeWithSelector } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"

interface CartStore {
  items: CartItem[]
  total: number
  addItem: (item: Product) => void
  removeItem: (id: string) => void
  clear: () => void
}

const useCartStore = create<CartStore>()(
  subscribeWithSelector(
    immer((set, get) => ({
      items: [],
      total: 0,
      addItem: (product) =>
        set((state) => {
          const existing = state.items.find(i => i.id === product.id)
          if (existing) {
            existing.quantity++
          } else {
            state.items.push({ ...product, quantity: 1 })
          }
          state.total = state.items.reduce((s, i) => s + i.price * i.quantity, 0)
        }),
      removeItem: (id) =>
        set((state) => {
          state.items = state.items.filter(i => i.id !== id)
          state.total = state.items.reduce((s, i) => s + i.price * i.quantity, 0)
        }),
      clear: () => set({ items: [], total: 0 }),
    }))
  )
)

// Selector-based subscription — only re-renders when total changes
const total = useCartStore(state => state.total)
```

### State Management — Jotai (atomic)

```tsx
import { atom, useAtom, useAtomValue, useSetAtom } from "jotai"
import { atomWithStorage, loadable } from "jotai/utils"

// Primitive atoms
const countAtom = atom(0)
const userIdAtom = atomWithStorage("userId", null)  // persists to localStorage

// Derived atom (computed)
const doubleCountAtom = atom(get => get(countAtom) * 2)

// Async atom
const userAtom = atom(async (get) => {
  const id = get(userIdAtom)
  if (!id) return null
  return fetchUser(id)
})

// loadable prevents suspense
const loadableUser = loadable(userAtom)

function UserBadge() {
  const user = useAtomValue(loadableUser)
  if (user.state === "loading") return <Spinner />
  if (user.state === "hasError") return <Error />
  return <span>{user.data?.name}</span>
}
```

### Custom Hooks — Advanced Patterns

```tsx
// Stable callback (avoids useCallback dependency arrays)
function useStableCallback<T extends (...args: any[]) => any>(callback: T): T {
  const ref = useRef(callback)
  useLayoutEffect(() => { ref.current = callback })
  return useCallback((...args) => ref.current(...args), []) as T
}

// Data fetching with abort
function useFetch<T>(url: string) {
  const [state, setState] = useState<{ data: T | null; loading: boolean; error: Error | null }>({
    data: null, loading: true, error: null,
  })

  useEffect(() => {
    const controller = new AbortController()
    fetch(url, { signal: controller.signal })
      .then(r => r.json())
      .then(data => setState({ data, loading: false, error: null }))
      .catch(err => {
        if (err.name !== "AbortError")
          setState({ data: null, loading: false, error: err })
      })
    return () => controller.abort()
  }, [url])

  return state
}

// Previous value
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>()
  useEffect(() => { ref.current = value })
  return ref.current
}
```

### Error Boundaries

```tsx
"use client"
import { Component, type ReactNode } from "react"

interface Props {
  children: ReactNode
  fallback: ReactNode | ((error: Error, reset: () => void) => ReactNode)
}

class ErrorBoundary extends Component<Props, { error: Error | null }> {
  state = { error: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("Boundary caught:", error, info)
    // reportToSentry(error, info)
  }

  reset = () => this.setState({ error: null })

  render() {
    const { error } = this.state
    if (error) {
      return typeof this.props.fallback === "function"
        ? this.props.fallback(error, this.reset)
        : this.props.fallback
    }
    return this.props.children
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary
      fallback={(error, reset) => (
        <div>
          <p>{error.message}</p>
          <button onClick={reset}>Retry</button>
        </div>
      )}
    >
      <RiskyComponent />
    </ErrorBoundary>
  )
}
```

---

## Gotchas

> [!danger] Closures em effects capturam valores antigos
> `useEffect` captura o valor da variável no momento da criação do closure. Sem a dependência correta no array, você opera com dados stale.

```tsx
// ERRADO — count sempre será 0 dentro do interval
useEffect(() => {
  const id = setInterval(() => {
    console.log(count)  // stale closure!
  }, 1000)
  return () => clearInterval(id)
}, [])  // count ausente do array

// CORRETO — use functional update ou inclua a dependência
useEffect(() => {
  const id = setInterval(() => {
    setCount(c => c + 1)  // functional update não precisa da dep
  }, 1000)
  return () => clearInterval(id)
}, [])
```

> [!warning] React Compiler não é magia total
> O Compiler não memoiza componentes que violam as regras do React (mutação de estado direta, side effects fora de hooks). ESLint `eslint-plugin-react-compiler` identifica violações.

> [!warning] Server Components não suportam interatividade
> Não use `useState`, `useEffect`, event handlers, ou browser APIs em Server Components. O erro de runtime pode ser confuso. Use `"use client"` no menor subtree necessário.

---

## Snippets

### React 19 Actions (form)

```tsx
"use client"
import { useActionState } from "react"

async function submitAction(prevState: any, formData: FormData) {
  const name = formData.get("name") as string
  if (!name) return { error: "Name required" }
  await saveToServer(name)
  return { success: true }
}

function MyForm() {
  const [state, action, isPending] = useActionState(submitAction, null)
  return (
    <form action={action}>
      <input name="name" />
      <button disabled={isPending}>{isPending ? "Saving..." : "Save"}</button>
      {state?.error && <p>{state.error}</p>}
    </form>
  )
}
```

### Virtualized list with intersection observer

```tsx
function useInfiniteScroll(callback: () => void) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) callback() },
      { threshold: 0.1 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [callback])
  return ref
}
```

---

## References

- [React 19 Blog Post](https://react.dev/blog/2024/12/05/react-19)
- [React Compiler](https://react.dev/learn/react-compiler)
- [useTransition](https://react.dev/reference/react/useTransition)
- [Zustand](https://zustand-demo.pmnd.rs/)
- [Jotai](https://jotai.org/)

---

## Related

- [[typescript]]
- [[nextjs]]
- [[svelte]]
- [[htmx]]
- [[astro]]
