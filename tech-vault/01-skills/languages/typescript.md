---
tags: [skill, languages, typescript]
status: active
level: advanced
updated: 2026-04-05
aliases: [TypeScript, TS]
created: 2026-04-05
---

# TypeScript

## Overview

TypeScript é um superset estaticamente tipado de JavaScript desenvolvido pela Microsoft, compilando para JS puro. Em produção, o valor real não está em "adicionar tipos" — está em modelar domínios de negócio com precisão, eliminar classes inteiras de bugs em compile time e tornar refatorações seguras em bases de código grandes. Com o TypeScript 5.x, recursos como `satisfies`, variância explícita e const type parameters elevaram drasticamente a expressividade do sistema de tipos.

Quando usar: qualquer projeto JavaScript com mais de um desenvolvedor ou que precise durar mais de três meses. TypeScript é essencial em aplicações [[nextjs]] e [[react]] de produção, SDKs públicos, e sistemas com [[vercel-ai-sdk]] onde os tipos das respostas da IA precisam ser modelados com precisão. A integração com [[svelte]] e [[astro]] é igualmente first-class.

Quando NÃO usar: scripts de uso único onde a overhead de configuração não se justifica, ou quando o time não tem familiaridade suficiente para explorar o tipo avançado — TypeScript mal configurado (com `any` em todo lugar e `strict: false`) dá falsa sensação de segurança. Nesse caso, JSDoc tipado pode ser uma alternativa mais honesta.

---

## Core Concepts

### Generics with Constraints

Generics constrained with `extends` enforce structural contracts at the call site without sacrificing flexibility:

```typescript
type DeepPartial<T> = T extends object
  ? { [K in keyof T]?: DeepPartial<T[K]> }
  : T;

// Constrained generic — T must have an id field
function findById<T extends { id: string }>(
  collection: T[],
  id: string
): T | undefined {
  return collection.find(item => item.id === id);
}

// Multiple constraints via intersection
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}
```

### Conditional Types and `infer`

`infer` extracts types from within complex structural positions:

```typescript
// Extract the resolved type of a Promise
type Awaited<T> = T extends PromiseLike<infer U> ? Awaited<U> : T;

// Extract function return type, handling async
type AsyncReturn<T extends (...args: any[]) => any> =
  Awaited<ReturnType<T>>;

// Unpack array element type
type ElementOf<T> = T extends ReadonlyArray<infer E> ? E : never;

// Distribute over union types
type ToArray<T> = T extends any ? T[] : never;
// ToArray<string | number> => string[] | number[]

// Extract constructor parameters
type ConstructorParams<T extends new (...args: any[]) => any> =
  T extends new (...args: infer P) => any ? P : never;
```

### Template Literal Types

```typescript
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
type ApiPath = `/api/${string}`;
type Route = `${Lowercase<HttpMethod>}:${ApiPath}`;
// "get:/api/users" | "post:/api/users" | ...

// Event system with autocomplete
type EventMap = {
  userCreated: { userId: string };
  orderPlaced: { orderId: string; total: number };
};

type EventKey = keyof EventMap;
type EventPayload<K extends EventKey> = EventMap[K];

// Generate handler types
type Handlers = {
  [K in EventKey as `on${Capitalize<K>}`]: (payload: EventPayload<K>) => void;
};
// { onUserCreated: (p: {userId: string}) => void; onOrderPlaced: ... }
```

### Mapped Types

```typescript
// Make all methods async
type AsyncMethods<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? (...args: A) => Promise<R>
    : T[K];
};

// Readonly recursive
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// Pick by value type
type PickByValue<T, V> = {
  [K in keyof T as T[K] extends V ? K : never]: T[K];
};

type StringFields<T> = PickByValue<T, string>;
// StringFields<{name: string; age: number}> => {name: string}
```

### Type Narrowing and Discriminated Unions

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function parseJson<T>(raw: string): Result<T> {
  try {
    return { ok: true, value: JSON.parse(raw) as T };
  } catch (e) {
    return { ok: false, error: e as Error };
  }
}

// Exhaustive checking with never
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "rect": return s.width * s.height;
    case "triangle": return 0.5 * s.base * s.height;
    default: {
      const _exhaustive: never = s;
      throw new Error(`Unhandled shape: ${JSON.stringify(_exhaustive)}`);
    }
  }
}
```

### The `satisfies` Operator (TS 4.9+)

```typescript
// satisfies validates structure without widening the type
const palette = {
  red: [255, 0, 0],
  green: "#00ff00",
  blue: [0, 0, 255],
} satisfies Record<string, string | number[]>;

// red is still typed as number[], not string | number[]
palette.red.map(v => v * 2); // OK — no type widening

// vs `as const` which freezes everything to literals
// vs explicit annotation which would widen to Record<string, string | number[]>
```

### Const Assertions and Variance Annotations

```typescript
// const assertion — infer literal types
const routes = ["users", "posts", "comments"] as const;
type Route = typeof routes[number]; // "users" | "posts" | "comments"

// Variance annotations (TS 4.7+) for performance and correctness
interface Producer<out T> {   // covariant — can only produce T
  produce(): T;
}

interface Consumer<in T> {    // contravariant — can only consume T
  consume(value: T): void;
}

interface Transformer<in T, out U> {  // explicit variance
  transform(value: T): U;
}
```

### Declaration Merging and Module Augmentation

```typescript
// Augment Express Request type globally
declare global {
  namespace Express {
    interface Request {
      user?: { id: string; role: "admin" | "user" };
    }
  }
}

// Extend third-party module types
declare module "some-library" {
  interface SomeLibraryOptions {
    customField: string;
  }
}

// Interface merging for plugin systems
interface PluginRegistry {}

// Plugins self-register:
declare module "./registry" {
  interface PluginRegistry {
    myPlugin: MyPlugin;
  }
}
```

---

## Patterns

### Strict Mode tsconfig for Production

```json
{
  "compilerOptions": {
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "allowUnusedLabels": false,
    "allowUnreachableCode": false,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"]
  }
}
```

### Builder Pattern with Fluent API and Full Type Safety

```typescript
class QueryBuilder<
  T extends Record<string, unknown>,
  TSelected extends keyof T = keyof T
> {
  private conditions: string[] = [];
  private selectedFields: TSelected[] = [];

  select<K extends keyof T>(...fields: K[]): QueryBuilder<T, K> {
    const builder = new QueryBuilder<T, K>();
    builder.selectedFields = fields as K[];
    return builder;
  }

  where(condition: string): this {
    this.conditions.push(condition);
    return this;
  }

  build(): Pick<T, TSelected>[] {
    // type-safe result — only selected fields
    return [] as Pick<T, TSelected>[];
  }
}
```

### Type-Safe Event Emitter

```typescript
type EventMap = Record<string, unknown>;

class TypedEmitter<T extends EventMap> {
  private listeners = new Map<keyof T, Set<Function>>();

  on<K extends keyof T>(event: K, listener: (data: T[K]) => void): this {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event)!.add(listener);
    return this;
  }

  emit<K extends keyof T>(event: K, data: T[K]): void {
    this.listeners.get(event)?.forEach(fn => fn(data));
  }
}

type AppEvents = {
  login: { userId: string; timestamp: Date };
  logout: { userId: string };
};

const emitter = new TypedEmitter<AppEvents>();
emitter.on("login", ({ userId, timestamp }) => { /* fully typed */ });
emitter.emit("login", { userId: "123", timestamp: new Date() });
```

---

## Gotchas

> [!warning] `noUncheckedIndexedAccess` quebra código existente
> Ao ativar essa flag (recomendada), `arr[0]` passa a ser `T | undefined` em vez de `T`. Isso força o tratamento explícito de acessos por índice, evitando runtime errors — mas requer adaptar código existente que assume que o acesso sempre retorna um valor.

> [!danger] Type Assertion com `as` bypassa o sistema de tipos
> `value as SomeType` não faz conversão — apenas suprime o erro do compilador. Em runtime, o valor é o mesmo. Prefira type guards com verificação real:
> ```typescript
> // RUIM — sem garantia em runtime
> const user = data as User;
>
> // BOM — verifica estrutura real
> function isUser(v: unknown): v is User {
>   return typeof v === "object" && v !== null && "id" in v && "email" in v;
> }
> ```

> [!warning] Enums geram código JavaScript inesperado
> Enums numéricos criam mapeamento bidirecional (value→name e name→value), gerando código maior que o esperado. Prefira `as const` objects ou string literal unions:
> ```typescript
> // Evitar — gera código de runtime
> enum Status { Active, Inactive }
>
> // Preferir — zero runtime overhead
> const Status = { Active: "active", Inactive: "inactive" } as const;
> type Status = typeof Status[keyof typeof Status];
> ```

> [!info] Distribuição de Tipos Condicionais
> Tipos condicionais distribuem automaticamente sobre unions — o que pode ser surpreendente. Use `[T] extends [U]` para prevenir distribuição:
> ```typescript
> type IsString<T> = T extends string ? true : false;
> type A = IsString<string | number>; // boolean (true | false — distributed!)
>
> type IsStringExact<T> = [T] extends [string] ? true : false;
> type B = IsStringExact<string | number>; // false (não distribui)
> ```

---

## Snippets

### Result Type com unwrap helper

```typescript
type Ok<T> = { readonly _tag: "Ok"; readonly value: T };
type Err<E> = { readonly _tag: "Err"; readonly error: E };
type Result<T, E = Error> = Ok<T> | Err<E>;

const ok = <T>(value: T): Ok<T> => ({ _tag: "Ok", value });
const err = <E>(error: E): Err<E> => ({ _tag: "Err", error });

function unwrap<T>(result: Result<T>): T {
  if (result._tag === "Ok") return result.value;
  throw result.error;
}

function map<T, U, E>(result: Result<T, E>, fn: (v: T) => U): Result<U, E> {
  return result._tag === "Ok" ? ok(fn(result.value)) : result;
}
```

### Zod Schema com Inferência de Tipo

```typescript
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  role: z.enum(["admin", "user", "guest"]),
  metadata: z.record(z.unknown()).optional(),
  createdAt: z.coerce.date(),
});

type User = z.infer<typeof UserSchema>;
// Full type inference — no duplication between schema and type

function parseUser(raw: unknown): User {
  return UserSchema.parse(raw); // throws ZodError with detailed messages
}
```

### Fetch Wrapper com Tipos Genéricos

```typescript
async function apiFetch<T>(
  url: string,
  options?: RequestInit & { schema?: z.ZodType<T> }
): Promise<Result<T>> {
  try {
    const res = await fetch(url, options);
    if (!res.ok) return err(new Error(`HTTP ${res.status}: ${res.statusText}`));
    const data: unknown = await res.json();
    const parsed = options?.schema ? options.schema.parse(data) : data as T;
    return ok(parsed);
  } catch (e) {
    return err(e instanceof Error ? e : new Error(String(e)));
  }
}
```

---

## References

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [TypeScript 5.x Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/overview.html)
- [Type Challenges](https://github.com/type-challenges/type-challenges)
- [Matt Pocock — Total TypeScript](https://www.totaltypescript.com/)
- [TS Config Reference](https://www.typescriptlang.org/tsconfig)

---

## Related

- [[nextjs]] — framework React com suporte TypeScript nativo e Server Components tipados
- [[react]] — biblioteca UI, uso intenso de generics em hooks e componentes
- [[svelte]] — suporte TypeScript via lang="ts" em componentes .svelte
- [[astro]] — SSG/SSR com TypeScript first-class e Content Collections tipadas
- [[vercel-ai-sdk]] — SDK para integração de LLMs com tipos de streaming e tool calls
