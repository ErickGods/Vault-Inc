---
tags: [skill, languages, rust]
status: active
level: advanced
updated: 2026-04-05
aliases: [Rust, rs]
created: 2026-04-05
---

# Rust

## Overview

Rust é uma linguagem de sistemas com garantias de segurança de memória em compile time, sem garbage collector. O sistema de ownership/borrowing elimina data races e use-after-free em tempo de compilação — categorias de bugs que representam a maioria das vulnerabilidades em sistemas críticos. Em benchmarks consistentes, Rust iguala ou supera C/C++ enquanto provê abstrações de alto nível sem custo de runtime.

Quando usar: serviços com requisitos de latência determinística (sem GC pauses), extensões nativas para [[python]] via PyO3 ou para Node.js via napi-rs, sistemas embarcados, parsers, codecs, proxies de alta performance, e qualquer cenário onde segurança de memória e performance devem coexistir. A integração com [[docker]] é direta — binários Rust são estáticos e produzem imagens mínimas.

Quando NÃO usar: prototipagem onde velocidade de iteração supera performance, projetos onde o time não tem experiência com o borrow checker (a curva de aprendizado é real e impacta produtividade inicial), ou quando um runtime como [[typescript]] ou [[python]] com boas bibliotecas é suficiente. O compilador Rust é também notavelmente lento — projetos grandes precisam de estratégias de cache e builds incrementais.

---

## Core Concepts

### Ownership and Borrowing Deep Dive

Rust's ownership rules: each value has exactly one owner; when the owner goes out of scope, the value is dropped. Moves transfer ownership; borrows create temporary references.

```rust
// Move semantics — String is moved, not copied
fn consume(s: String) -> usize {
    s.len()
} // s is dropped here

let name = String::from("Alice");
let len = consume(name);
// println!("{}", name); // ERROR: value moved

// Borrowing — shared (&T) and exclusive (&mut T)
fn count_bytes(s: &str) -> usize {
    s.len()
} // borrow ends here, caller retains ownership

// The borrow checker enforces: many &T OR one &mut T, never both
fn split_borrow(v: &mut Vec<i32>) {
    let first = &v[0];          // shared borrow
    // v.push(99);              // ERROR: cannot mutate while shared borrow exists
    println!("{}", first);      // shared borrow ends here
    v.push(99);                 // OK now
}
```

### Lifetimes: Named, Elided, and 'static

```rust
// Named lifetimes — the returned reference lives as long as the shorter input
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Struct holding a reference — must annotate lifetime
struct Important<'a> {
    content: &'a str,
}

impl<'a> Important<'a> {
    fn announce(&self, announcement: &str) -> &str {
        // elided lifetime: output lifetime = self's lifetime
        self.content
    }
}

// 'static — reference valid for entire program duration
static CONFIG: &str = "production";

fn get_error_message() -> &'static str {
    "something went wrong"  // string literals are 'static
}

// Trait objects often require 'static for async contexts
use std::error::Error;
type BoxError = Box<dyn Error + Send + Sync + 'static>;
```

### Trait Objects vs Generics: `dyn` vs `impl`

```rust
// impl Trait — monomorphized at compile time, no heap allocation, no dynamic dispatch
fn process_items(iter: impl Iterator<Item = i32>) -> i32 {
    iter.sum()
}

// dyn Trait — dynamic dispatch via vtable, heap allocation (usually), runtime cost
fn make_shape(kind: &str) -> Box<dyn Shape> {
    match kind {
        "circle" => Box::new(Circle { radius: 1.0 }),
        "rect"   => Box::new(Rectangle { w: 2.0, h: 3.0 }),
        _        => panic!("unknown shape"),
    }
}

// Object safety rules — a trait is object-safe if:
// 1. It has no generic methods
// 2. It doesn't return Self
// 3. All methods are dispatchable

trait Drawable: Send + Sync {
    fn draw(&self);
    fn bounding_box(&self) -> (f64, f64, f64, f64);
}

// When to use which:
// - impl Trait: known types at compile time, max performance, no heterogeneous collections
// - dyn Trait: plugin systems, heterogeneous collections, dynamic dispatch needed
```

### Async Runtime with Tokio

```rust
use tokio::{
    sync::{mpsc, oneshot, Semaphore},
    task,
    time::{sleep, Duration},
    select,
};
use std::sync::Arc;

// Spawning tasks — runs on Tokio's thread pool
#[tokio::main]
async fn main() {
    let handle = task::spawn(async {
        heavy_computation().await
    });
    let result = handle.await.unwrap(); // JoinHandle awaiting
}

// select! — race multiple futures, cancel the losers
async fn with_timeout<T>(fut: impl std::future::Future<Output = T>) -> Option<T> {
    select! {
        result = fut => Some(result),
        _ = sleep(Duration::from_secs(5)) => None,
    }
}

// Channels for actor-style communication
async fn actor_example() {
    let (tx, mut rx) = mpsc::channel::<String>(32);

    task::spawn(async move {
        while let Some(msg) = rx.recv().await {
            println!("Received: {msg}");
        }
    });

    tx.send("hello".to_string()).await.unwrap();
}

// Semaphore for concurrency limiting
async fn bounded_requests(urls: Vec<String>) {
    let sem = Arc::new(Semaphore::new(10));
    let mut handles = vec![];

    for url in urls {
        let permit = Arc::clone(&sem).acquire_owned().await.unwrap();
        handles.push(task::spawn(async move {
            let _permit = permit; // dropped when task finishes
            reqwest::get(&url).await
        }));
    }

    for h in handles {
        let _ = h.await;
    }
}
```

### Error Handling: thiserror, anyhow, and the ? Operator

```rust
use thiserror::Error;
use anyhow::{Context, Result, bail};

// thiserror — for library errors (precise, typed)
#[derive(Debug, Error)]
pub enum DatabaseError {
    #[error("connection failed: {0}")]
    Connection(#[from] sqlx::Error),

    #[error("record not found: id={id}")]
    NotFound { id: u64 },

    #[error("constraint violation: {field} must be unique")]
    UniqueViolation { field: String },
}

// anyhow — for application errors (ergonomic, context-rich)
async fn load_user(id: u64) -> Result<User> {
    let row = db_query(id)
        .await
        .context("querying user from database")?; // ? propagates, .context() adds message

    let user = parse_user(row)
        .context("parsing user row")?;

    if user.is_banned() {
        bail!("user {id} is banned"); // anyhow::bail! creates and returns an error
    }

    Ok(user)
}

// Custom error with Display + std::error::Error
#[derive(Debug)]
pub struct ParseError {
    pub input: String,
    pub reason: String,
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "parse error on '{}': {}", self.input, self.reason)
    }
}

impl std::error::Error for ParseError {}
```

### FFI: PyO3 for Python Bindings

```rust
// Cargo.toml: pyo3 = { version = "0.22", features = ["extension-module"] }
use pyo3::prelude::*;
use pyo3::types::PyList;

#[pyfunction]
fn fast_sum(py: Python<'_>, numbers: Vec<f64>) -> PyResult<f64> {
    // Releases the GIL for CPU-intensive work
    py.allow_threads(|| Ok(numbers.iter().sum()))
}

#[pyclass]
struct RustCounter {
    count: u64,
}

#[pymethods]
impl RustCounter {
    #[new]
    fn new(initial: u64) -> Self {
        RustCounter { count: initial }
    }

    fn increment(&mut self) { self.count += 1; }

    fn value(&self) -> u64 { self.count }
}

#[pymodule]
fn my_rust_module(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fast_sum, m)?)?;
    m.add_class::<RustCounter>()?;
    Ok(())
}
```

### Smart Pointers: Box, Rc, Arc, RefCell

```rust
use std::rc::Rc;
use std::sync::Arc;
use std::cell::RefCell;

// Box<T> — heap allocation, single ownership, enables recursive types
enum List {
    Cons(i32, Box<List>),
    Nil,
}

// Rc<T> — reference counted, single-threaded shared ownership
let shared = Rc::new(vec![1, 2, 3]);
let clone1 = Rc::clone(&shared);
let clone2 = Rc::clone(&shared);
// shared, clone1, clone2 all point to same data; dropped when count reaches 0

// Arc<T> — atomic reference counted, safe across threads
let arc_data: Arc<Vec<i32>> = Arc::new(vec![1, 2, 3]);
let arc_clone = Arc::clone(&arc_data);
std::thread::spawn(move || {
    println!("{:?}", arc_clone); // safe to use in another thread
});

// RefCell<T> — interior mutability, runtime borrow checking
let data = Rc::new(RefCell::new(vec![1, 2, 3]));
let d2 = Rc::clone(&data);

data.borrow_mut().push(4);  // runtime borrow check — panics if already borrowed
d2.borrow_mut().push(5);    // OK — previous borrow was released

// Common pattern: Arc<Mutex<T>> for shared mutable state across threads
use std::sync::Mutex;
let counter = Arc::new(Mutex::new(0u64));
```

---

## Patterns

### Zero-Cost Abstractions: Iterators and Closures

```rust
// Iterator chains compile to the same assembly as hand-written loops
fn process(data: &[u32]) -> Vec<u32> {
    data.iter()
        .filter(|&&x| x % 2 == 0)
        .map(|&x| x * x)
        .take(100)
        .collect()
}

// Custom iterator
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Fibonacci {
    fn new() -> Self { Fibonacci { a: 0, b: 1 } }
}

impl Iterator for Fibonacci {
    type Item = u64;
    fn next(&mut self) -> Option<u64> {
        let next = self.a + self.b;
        self.a = self.b;
        self.b = next;
        Some(self.a)
    }
}

// Use all iterator adapters: fib.take_while(...).filter(...).enumerate()
```

### Unsafe Patterns and When to Use Them

```rust
// unsafe is a contract: "I guarantee the invariants the compiler can't verify"
// Valid uses: FFI, raw pointer manipulation, performance-critical aligned access

unsafe fn dangerous_slice(ptr: *const u8, len: usize) -> &'static [u8] {
    // SAFETY: caller guarantees ptr is valid for len bytes and outlives 'static
    std::slice::from_raw_parts(ptr, len)
}

// Wrapping unsafe in safe abstractions
pub struct AlignedBuffer {
    data: *mut u8,
    len: usize,
}

impl AlignedBuffer {
    pub fn new(len: usize) -> Self {
        let layout = std::alloc::Layout::from_size_align(len, 64).unwrap();
        let data = unsafe { std::alloc::alloc(layout) };
        AlignedBuffer { data, len }
    }

    pub fn as_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.data, self.len) }
    }
}

impl Drop for AlignedBuffer {
    fn drop(&mut self) {
        let layout = std::alloc::Layout::from_size_align(self.len, 64).unwrap();
        unsafe { std::alloc::dealloc(self.data, layout) }
    }
}
```

### Containerização com [[docker]]

```dockerfile
# Multi-stage Rust build — final image ~10MB
FROM rust:1.82-slim AS builder
WORKDIR /app
# Cache dependencies layer separately
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main(){}" > src/main.rs && cargo build --release
COPY src/ ./src/
RUN touch src/main.rs && cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/my-service /usr/local/bin/
CMD ["my-service"]
```

---

## Gotchas

> [!danger] Deadlock com Mutex em Código Async
> Segurar um `std::sync::MutexGuard` através de um `.await` causa deadlock pois o guard não é `Send`. Use `tokio::sync::Mutex` em código async, ou garanta que o guard seja dropado antes de qualquer `await`:
> ```rust
> // PERIGO — MutexGuard atravessa await
> let guard = std::sync::Mutex::new(0).lock().unwrap();
> some_async_fn().await; // pode deadlock
>
> // CORRETO — usar tokio::sync::Mutex
> let mutex = tokio::sync::Mutex::new(0);
> let mut guard = mutex.lock().await;
> *guard += 1;
> // guard dropado aqui, antes do próximo await
> ```

> [!warning] Clone em Arc não Clona os Dados
> `Arc::clone(&arc)` incrementa o contador de referência e retorna um novo ponteiro para os **mesmos** dados — não copia os dados. Isso é o comportamento desejado mas pode confundir quem vem de outras linguagens. Para clonar os dados, use `(*arc).clone()`.

> [!warning] `unwrap()` em Produção
> `unwrap()` e `expect()` causam `panic!` em caso de `None` ou `Err`, derrubando a thread (em Tokio, o task). Em handlers de servidor, isso resulta em respostas 500 silenciosas. Use `?` com tipos de erro adequados para propagar erros de forma controlada. Projetos sérios usam `clippy::unwrap_used` para banir `unwrap` do código de produção.

> [!info] Tempo de Compilação
> O compilador Rust é lento por design — realiza análises profundas de lifetime e monomorphization extensiva. Estratégias: ative `incremental = true` no profile, use `cargo-watch` para recompilação rápida, considere `mold` ou `lld` como linker alternativo, e estruture o código para maximizar cache de crates.

> [!danger] Referências Circulares com Rc
> `Rc<RefCell<T>>` não detecta ciclos — pode vazar memória. Se A possui Rc para B e B possui Rc para A, nenhum dos dois será dropado. Use `Weak<T>` para referências de "volta" (backreferences) que não aumentam o contador de strong references.

---

## Snippets

### Servidor HTTP com Axum e Tokio

```rust
use axum::{routing::get, Router, Json, extract::State};
use std::sync::Arc;
use tokio::net::TcpListener;

#[derive(Clone)]
struct AppState {
    db: Arc<sqlx::PgPool>,
}

async fn health(State(state): State<AppState>) -> Json<serde_json::Value> {
    Json(serde_json::json!({ "status": "ok" }))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let pool = sqlx::PgPool::connect(&std::env::var("DATABASE_URL")?).await?;
    let state = AppState { db: Arc::new(pool) };

    let app = Router::new()
        .route("/health", get(health))
        .with_state(state);

    let listener = TcpListener::bind("0.0.0.0:3000").await?;
    axum::serve(listener, app).await?;
    Ok(())
}
```

### Parsing com nom

```rust
use nom::{
    bytes::complete::tag,
    character::complete::{digit1, alpha1},
    sequence::tuple,
    IResult,
};

fn parse_version(input: &str) -> IResult<&str, (u32, u32, u32)> {
    let (input, major) = digit1(input)?;
    let (input, _) = tag(".")(input)?;
    let (input, minor) = digit1(input)?;
    let (input, _) = tag(".")(input)?;
    let (input, patch) = digit1(input)?;
    Ok((input, (
        major.parse().unwrap(),
        minor.parse().unwrap(),
        patch.parse().unwrap(),
    )))
}
```

---

## References

- [The Rust Programming Language (Book)](https://doc.rust-lang.org/book/)
- [Rust Async Book](https://rust-lang.github.io/async-book/)
- [Tokio Documentation](https://tokio.rs/tokio/tutorial)
- [PyO3 User Guide](https://pyo3.rs/latest/)
- [The Rustonomicon (unsafe)](https://doc.rust-lang.org/nomicon/)
- [Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [thiserror crate](https://docs.rs/thiserror)
- [anyhow crate](https://docs.rs/anyhow)

---

## Related

- [[docker]] — containerização de binários Rust com imagens mínimas
- [[python]] — integração via PyO3 para extensões nativas de alta performance
- [[typescript]] — alternativa de alto nível; Rust pode compilar para WASM para uso em JS
- [[database-optimization]] — Rust com sqlx/SeaORM para queries de alta performance
- [[big-o-notation]] — Rust torna análise de complexidade crítica — sem GC para esconder custos
