Title: C++ to Rust, Part 3: Concurrency, Unsafe, and Migration
Date: 2026-10-16 12:00:00
Category: Engineering
Tags: rust, cpp, programming-languages, tutorial, memory-safety
Slug: cpp-to-rust-part-3-advanced
Series: C++ to Rust
Series_index: 3
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: A phrasebook for C++ developers moving to Rust, part 3 of 3. Threads, locks, atomics, async, lifetimes, compile-time programming, macros, graphs, unsafe, and FFI, with the semantic gaps that matter when you port advanced C++ and a practical plan for migrating a real code base.
Status: draft
scratch: ['cpp_to_rust_research_landscape', 'cpp_to_rust_research_versions']

## TL;DR

Most of the advanced half of C++ (threads, templates, the preprocessor, raw memory) has a Rust counterpart, and in each case Rust moves a rule out of the documentation and into the type system. A mutex owns the data it protects, so you cannot forget to lock it, and `Send` and `Sync` turn data races into compile errors. Macros work on syntax, not text. And `unsafe` does not switch the checks off: it unlocks a short, fixed list of operations and marks exactly where a reviewer has to look. The biggest takeaway: Rust does not remove the dangerous parts of systems programming; it fences them, and a migration succeeds when you put the fences at the boundaries of your C++ code instead of rewriting everything at once.

[TOC]

## What this part covers, and what it does not

Part 1 mapped the everyday vocabulary, and Part 2 covered ownership, borrowing, smart pointers, errors, traits, and closures. This part assumes both. It covers concurrency, lifetimes in depth, compile-time programming, macros, self-referential data, `unsafe`, and FFI, and it ends with how teams move real C++ code to Rust.

It is not a tutorial on async runtimes, and it does not replace [the Rustonomicon](https://doc.rust-lang.org/nomicon/), the official guide to unsafe Rust. Read it as a map: where each advanced C++ tool lives in Rust, and how its rules change on the way.

Same setup as before: every snippet was compiled with **rustc 1.99 (edition 2024)** and **Apple clang 21 with `-std=c++23`**, and each one carries its own `#include` lines or `use` imports. A Rust snippet whose first line is `// does not compile` fails with the error code it names.

## Threads: spawn, scope, and the `'static` rule

| C++ | Rust |
|---|---|
| `std::thread t(f); t.join();` | `let h = thread::spawn(f); h.join()` |
| `std::jthread` (joins in its destructor) | `thread::scope` (joins at the end of the scope) |
| `t.detach()` | drop the `JoinHandle` |
| exception escapes a thread: `std::terminate` | a panic ends that thread; `join()` returns `Err` |

C++20's `std::jthread` made "start some threads, join them before the data goes away" the safe default. Here is a parallel sum with two threads that borrow a local vector:

```cpp
#include <numeric>
#include <print>
#include <thread>
#include <vector>

int main() {
    std::vector<long> data(1000);
    std::iota(data.begin(), data.end(), 1);
    auto mid = data.begin() + data.size() / 2;
    long left = 0, right = 0;
    {
        std::jthread a([&] { left = std::accumulate(data.begin(), mid, 0L); });
        std::jthread b([&] { right = std::accumulate(mid, data.end(), 0L); });
    } // both threads join here
    std::println("{}", left + right); // 500500
}
```

The Rust equivalent is **scoped threads** (`std::thread::scope`, stable since Rust 1.63). Every thread spawned in the scope joins before `scope` returns, so the threads may borrow local data:

```rust
use std::thread;

fn main() {
    let data: Vec<i64> = (1..=1000).collect();
    let (left, right) = data.split_at(data.len() / 2);
    let (a, b) = thread::scope(|s| {
        let a = s.spawn(|| left.iter().sum::<i64>());
        let b = s.spawn(|| right.iter().sum::<i64>());
        (a.join().unwrap(), b.join().unwrap())
    }); // every scoped thread has joined here
    println!("{}", a + b); // 500500
}
```

Plain `thread::spawn` is stricter. The new thread may outlive the function that started it, so its closure must own everything it uses: it must be `'static`. Borrowing a local is a compile error:

```rust
// does not compile: E0373
use std::thread;

fn main() {
    let data = vec![1, 2, 3];
    let h = thread::spawn(|| println!("{data:?}")); // borrows `data`
    h.join().unwrap();
}
```

The compiler suggests the fix: `thread::spawn(move || ...)` moves `data` into the thread.

**The gap:** in C++, a `[&]` lambda on a plain `std::thread` that you `detach()` compiles and dangles. In Rust, a thread borrows only inside a scope that provably outlives it, and every other thread must own its data. C++ leaves the choice between `jthread` and `thread` to discipline; Rust puts it in the lifetime bound on the closure: `'static` for `thread::spawn`, the scope for `thread::scope`.

## `Send` and `Sync`: data races become type errors

Two marker traits carry the whole thread-safety story:

- **`Send`**: a value of this type can be moved to another thread.
- **`Sync`**: a `&T` can be shared between threads. Precisely, `T` is `Sync` if and only if `&T` is `Send`.

The compiler implements both automatically, field by field, and the standard library opts out where it must. In C++, this unprotected counter compiles, runs, and has undefined behavior:

```cpp
#include <thread>

int hits = 0; // shared, unprotected

void count(int n) {
    for (int i = 0; i < n; ++i) ++hits; // data race: undefined behavior
}

int main() {
    std::jthread a(count, 100000), b(count, 100000);
} // `hits` holds any value, and the program has UB
```

Safe Rust cannot express that program, and the check reaches beyond globals. `Rc` (Part 2) updates its reference count without atomics, so it is not `Send`, and moving one into a thread is rejected at compile time:

```rust
// does not compile: E0277
use std::rc::Rc;
use std::thread;

fn main() {
    let shared = Rc::new(vec![1, 2, 3]);
    let s2 = Rc::clone(&shared);
    let h = thread::spawn(move || println!("{s2:?}"));
    // error[E0277]: `Rc<Vec<i32>>` cannot be sent between threads safely
    h.join().unwrap();
}
```

| Type | `Send` | `Sync` | Why |
|---|---|---|---|
| `i32`, `String` | yes | yes | plain owned data |
| `Vec<T>`, `Box<T>`, `Option<T>` | if `T: Send` | if `T: Sync` | inherit from their contents |
| `Rc<T>` | no | no | non-atomic reference count |
| `Arc<T>` (with `T: Send + Sync`) | yes | yes | atomic reference count |
| `Cell<T>`, `RefCell<T>` | if `T: Send` | no | unsynchronized interior mutability |
| `Mutex<T>` (with `T: Send`) | yes | yes | every access goes through the lock |
| `MutexGuard<'_, T>` | no | if `T: Sync` | some platforms must unlock on the locking thread |
| `*const T`, `*mut T` | no | no | the compiler cannot know what they point to |

**The gap:** the [Rustonomicon](https://doc.rust-lang.org/nomicon/races.html) states the guarantee precisely: "Safe Rust guarantees an absence of data races", and a few lines later, "Rust does not prevent general race conditions." Deadlocks, lock-order inversions, and check-then-act bugs all still compile. Rust removes the undefined behavior, not the need to design your synchronization.

## The mutex owns the data

In C++, a mutex and the data it protects are two separate members, linked by a comment and by discipline:

```cpp
#include <cstddef>
#include <mutex>
#include <string>
#include <utility>
#include <vector>

struct Inventory {
    std::mutex m; // protects `items`, by convention
    std::vector<std::string> items;
};

void add(Inventory& inv, std::string item) {
    std::lock_guard lock(inv.m);
    inv.items.push_back(std::move(item));
}

std::size_t count(Inventory& inv) {
    return inv.items.size(); // forgot the lock: compiles, races
}
```

In Rust, `Mutex<T>` **contains** the `T`. The only way to reach the data is `lock()`, which returns a guard, and the guard unlocks when it is dropped, exactly like `std::lock_guard`:

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let items = Arc::new(Mutex::new(Vec::new()));
    let handles: Vec<_> = (0..4)
        .map(|i| {
            let items = Arc::clone(&items);
            thread::spawn(move || {
                items.lock().unwrap().push(format!("item-{i}"));
            }) // the guard drops at the end of the statement: unlocked
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    // items.len()  // error[E0599]: no method named `len` found for struct `Arc<...>`
    println!("{}", items.lock().unwrap().len()); // 4
}
```

**The gap:** `lock()` returns a `Result` because of **poisoning**: if a thread panics while it holds the lock, the data may be half-updated, so later `lock()` calls return an error and you decide whether the data is still usable. `std::mutex` has no equivalent; an exception that leaves a `lock_guard` scope unlocks silently.

The rest of the toolbox maps one to one: `std::shared_mutex` becomes `RwLock<T>`, `std::condition_variable` becomes `Condvar`, and `std::barrier` becomes `Barrier`.

Several C++ tools have no standard library counterpart:

- `std::scoped_lock(m1, m2)`, which locks several mutexes without deadlock (in Rust, you lock in a fixed order)
- semaphores
- `std::latch`
- `std::recursive_mutex`
- timed locks
- `atomic::wait` and `atomic::notify`

Crates such as `parking_lot` and `tokio` fill most of these gaps.

In the other direction, Rust ships something C++ does not: **channels**. `std::sync::mpsc::channel()` gives you a multi-producer queue with cloneable senders, and a receiver loop that ends when the last sender is dropped. Idiomatic Rust uses channels wherever C++ code would build a queue from a deque, a mutex, and a condition variable.

## Atomics, globals, and one-time initialization

Rust's atomics are C++'s atomics. The [std::sync::atomic documentation](https://doc.rust-lang.org/std/sync/atomic/index.html) says it directly: "Rust atomics currently follow the same rules as C++20 atomics, specifically the rules from the intro.races section, without the 'consume' memory ordering." `memory_order_acquire` becomes `Ordering::Acquire`, and your knowledge of the memory model transfers, with small differences: the same page notes that Rust's model is access-based where C++'s is object-based.

Globals are where the languages differ. A function-local `static` in C++ is initialized once, thread-safely, on first use. Rust has `LazyLock` (stable since 1.80) and `OnceLock` (since 1.70) for the same job:

```cpp
#include <atomic>
#include <cstdint>
#include <map>
#include <string>

std::atomic<std::uint64_t> requests{0};

const std::map<std::string, int>& limits() {
    static const std::map<std::string, int> table{{"free", 10}, {"pro", 1000}};
    return table; // initialized once, thread-safely, on first call
}

void handle() { requests.fetch_add(1, std::memory_order_relaxed); }
```

```rust
use std::collections::HashMap;
use std::sync::LazyLock;
use std::sync::atomic::{AtomicU64, Ordering};

static REQUESTS: AtomicU64 = AtomicU64::new(0);
static LIMITS: LazyLock<HashMap<&str, u32>> =
    LazyLock::new(|| HashMap::from([("free", 10), ("pro", 1000)]));

fn handle() {
    REQUESTS.fetch_add(1, Ordering::Relaxed);
}

fn main() {
    handle();
    handle();
    println!("{} {}", REQUESTS.load(Ordering::Relaxed), LIMITS["pro"]); // 2 1000
}
```

**The gap:** a mutable global in Rust must be thread-safe by type, because any thread can reach it. `static mut` still exists, but every access is `unsafe`, and in edition 2024 the `static_mut_refs` lint, which flags any reference to a `static mut`, is deny by default. Read `static mut` as the Rust spelling of "I am about to write a data race".

## Async and coroutines: the same machine, different batteries

C++20 coroutines and Rust's `async`/`await` are close relatives. Both compile a function into a state machine that can suspend and resume, and neither allocates a stack per task. C++ heap-allocates each coroutine frame unless the compiler elides it, while a Rust future is an ordinary value that lives wherever you put it. The difference is in what ships with the language.

| C++ | Rust |
|---|---|
| C++20 coroutines: `co_await`, `co_return` | `async fn`, `.await` |
| promise types you write, or a library | the standard library's `Future` trait; executors come from crates (Tokio, smol) |
| `std::generator` (C++23) | an `Iterator` impl or `std::iter::from_fn`; `gen` blocks are unstable |
| `std::async(std::launch::async, f)` + `get()` | `thread::spawn(f)` + `join()` |

Two Rust facts trip up C++ developers:

- **The standard library has no executor.** `async fn main` is rejected (E0752) unless a runtime's attribute macro, such as `#[tokio::main]`, rewrites it into a normal `main`.
- **A Rust future is lazy.** Calling an `async fn` runs nothing until something polls the result, while `std::async(std::launch::async, ...)` starts work immediately.

On the language side, Rust has stabilized `async fn` in traits (1.75) and async closures (1.85). Generators are still behind a feature flag: on 1.99, a `gen { yield 1; }` block fails with `error[E0658]: gen blocks are experimental`, and edition 2024 only reserves the keyword.

Until they land, a C++23 `std::generator` becomes a struct that implements `Iterator`, or a closure passed to `std::iter::from_fn`. (Apple clang 21's libc++ does not ship `<generator>` yet either, so in practice the two languages are closer here than their standards suggest.)

## Lifetimes in depth

Parts 1 and 2 used lifetimes through one rule: "a reference cannot outlive what it points to". The next step is the case C++ developers meet first: a **struct that holds a reference**.

In C++, a struct with a `std::string_view` member looks like a value type, and nothing in its name says it borrows. In Rust, the borrow is part of the type: `Parser<'a>` reads "a parser that borrows something for `'a`".

When a function returns a reference, the compiler must know which input it borrows from. With two candidates, you have to say:

```rust
// does not compile: E0106
fn longest(a: &str, b: &str) -> &str {
    if a.len() >= b.len() { a } else { b }
} // error[E0106]: missing lifetime specifier
```

The fix is the signature `fn longest<'a>(a: &'a str, b: &'a str) -> &'a str`. The annotation changes nothing at runtime. It states a relationship, "the result lives no longer than both inputs", which the checker then enforces at every call site.

Most of the time you write no annotations at all, thanks to the **lifetime elision rules**, which [the Reference](https://doc.rust-lang.org/reference/lifetime-elision.html) defines in three steps:

1. Each elided lifetime in the parameters becomes a distinct lifetime parameter.
2. If there is exactly one lifetime in the parameters, it is assigned to all elided output lifetimes.
3. In methods, if the receiver is `&self` or `&mut self`, the lifetime of `self` is assigned to all elided output lifetimes.

Rule 3 is where elision can give the wrong answer. In this tokenizer, an elided return type `Option<&str>` would borrow from `&mut self`, the parser, instead of from the text. Every word would keep the parser mutably borrowed, and the loop in `main` would fail with `error[E0499]: cannot borrow parser as mutable more than once at a time`. Naming the lifetime says what is true: the words borrow the input, which lives for `'a`.

```rust
struct Parser<'a> {
    input: &'a str,
    pos: usize,
}

impl<'a> Parser<'a> {
    // `-> Option<&str>` would tie each word to `&mut self` (rule 3): E0499 below
    fn next_word(&mut self) -> Option<&'a str> {
        let rest = self.input[self.pos..].trim_start();
        if rest.is_empty() {
            return None;
        }
        let start = self.input.len() - rest.len();
        let end = rest.find(' ').map_or(self.input.len(), |i| start + i);
        self.pos = end;
        Some(&self.input[start..end])
    }
}

fn main() {
    let source = String::from("let x = 1;");
    let mut parser = Parser { input: &source, pos: 0 };
    let mut words = Vec::new();
    while let Some(w) = parser.next_word() {
        words.push(w); // fine: `w` borrows `source`, not `parser`
    }
    println!("{words:?}"); // ["let", "x", "=", "1;"]
}
```

**The gap:** a lifetime is not a duration you choose. It is a constraint you describe, and the compiler checks every use against it.

One more misreading to avoid: `T: 'static` does not mean "lives forever". It means "contains no borrows shorter than `'static`", so every type that owns all its data, such as `String` or `Vec<u8>`, satisfies it. That is the bound `thread::spawn` asks for.

## Compile-time programming

C++ has three compile-time languages: `constexpr` functions, templates, and the preprocessor. Rust splits the same work between `const fn`, generics with traits, and macros.

### `constexpr` and non-type template parameters

```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

constexpr std::size_t kib(std::size_t n) { return n * 1024; }
constexpr std::size_t buffer_size = kib(4);

template <typename T, std::size_t N>
struct Ring {
    std::array<std::optional<T>, N> items{};
    std::size_t head = 0;
    static constexpr std::size_t capacity = N;
};
static_assert(sizeof(std::uint64_t) == 8);
```

```rust
const fn kib(n: usize) -> usize {
    n * 1024
}
const BUFFER_SIZE: usize = kib(4);

struct Ring<T, const N: usize> {
    items: [Option<T>; N],
    head: usize,
}

impl<T: Copy, const N: usize> Ring<T, N> {
    const CAPACITY: usize = N;

    fn new() -> Self {
        Self { items: [None; N], head: 0 }
    }
}

const _: () = assert!(size_of::<u64>() == 8); // static_assert

fn main() {
    let ring: Ring<u32, 8> = Ring::new();
    println!("{} {} {}", BUFFER_SIZE, Ring::<u32, 8>::CAPACITY, ring.items.len()); // 4096 8 8
}
```

`const fn` is Rust's `constexpr`, **const generics** (stable since 1.51) are its non-type template parameters, and a `const _: () = assert!(...)` item is its `static_assert`.

Two limits apply on stable Rust. Const parameters can only be integers, `bool`, or `char` (C++20 also allows floating-point and class types). And a const parameter cannot appear in an expression inside a type, so `[T; N + 1]` in a generic signature needs the unstable `generic_const_exprs` feature.

### SFINAE, `enable_if`, and constrained templates

Part 2 mapped C++20 concepts to traits. The older tools, SFINAE and `std::enable_if`, land in the same place: a trait bound. What surprises C++ developers is that the standard library has no "is integral" trait. You define the capability you need and implement it for each type, and a small `macro_rules!` macro (explained in the next section) writes the repetitive impls:

```cpp
#include <concepts>

template <std::integral T> // before C++20: std::enable_if_t<std::is_integral_v<T>, int> = 0
T half(T x) { return x / 2; }
// half(3.0) fails: double does not satisfy std::integral
```

```rust
use std::ops::Div;

trait Integer: Copy + Div<Output = Self> {
    const TWO: Self;
}

macro_rules! impl_integer {
    ($($t:ty),*) => { $(impl Integer for $t { const TWO: Self = 2; })* };
}
impl_integer!(i8, i16, i32, i64, i128, isize, u8, u16, u32, u64, u128, usize);

fn half<T: Integer>(x: T) -> T {
    x / T::TWO
}

fn main() {
    println!("{} {}", half(7_u8), half(-9_i64)); // 3 -4
    // half(3.0_f64); // error[E0277]: the trait bound `f64: Integer` is not satisfied
}
```

In real code, the `num-traits` crate already defines these numeric traits.

### Type traits and associated types

`typename Container::value_type` and `std::numeric_limits<T>::max()` are type-level functions. In Rust they are **associated types** and **associated constants**: `I::Item`, `u8::MAX` (in generic code, `T::MAX` needs a trait that declares it, such as `num_traits::Bounded`).

### CRTP and specialization

The **Curiously Recurring Template Pattern** gives C++ static polymorphism with shared code in a base class template. In Rust, it is just a trait with a default method, because generics already dispatch statically:

```cpp
#include <string>

template <typename Derived>
struct Greeter {
    std::string greet() const { return "Hello, " + static_cast<const Derived*>(this)->name(); }
};

struct English : Greeter<English> {
    std::string name() const { return "world"; }
};
```

```rust
trait Greeter {
    fn name(&self) -> String;

    fn greet(&self) -> String {
        format!("Hello, {}", self.name()) // the "base class" code
    }
}

struct English;

impl Greeter for English {
    fn name(&self) -> String {
        "world".to_string()
    }
}

fn main() {
    println!("{}", English.greet());
}
```

**Specialization** is the big missing piece. A blanket `impl<T> Trait for T` plus a more specific `impl Trait for u8` is an overlap error on stable Rust (`error[E0119]: conflicting implementations`), and the `specialization` feature that would allow it is still unstable in 1.99. `if constexpr` and partial specialization usually become one of three things:

- a trait method that each type implements its own way
- an associated constant that generic code branches on (the optimizer removes the dead branch)
- separate impls for concrete types, with no blanket impl

**The gap:** you lose duck typing and specialization. You gain errors that point at the bound you broke, instead of forty lines of instantiation backtrace, and a library author knows that every caller who satisfies the bounds will compile.

## Macros and conditional compilation

The C preprocessor works on flat tokens and knows no syntax. Rust's `macro_rules!` matches **token trees**, and a fragment such as `$x:expr` is parsed as one whole expression. The classic preprocessor bug shows the difference:

```cpp
#include <print>

#define SQUARE(x) x * x

int main() { std::println("{}", SQUARE(1 + 2)); } // 5: expands to 1 + 2 * 1 + 2
```

```rust
macro_rules! square {
    ($x:expr) => { $x * $x };
}

fn main() {
    println!("{}", square!(1 + 2)); // 9: $x is one expression, not text
}
```

`macro_rules!` is also partly **hygienic**: local variables and labels inside a macro cannot collide with the caller's, although item and function names still resolve at the call site.

Expression fragments fix precedence, and hygiene stops a macro from capturing the caller's local variables. Neither fixes double evaluation: `square!(next())` still calls `next()` twice. If a function can do the job, write a function.

**Variadic templates** have no direct equivalent, because Rust has no variadic generics; that is the reason `println!` is a macro. A C++17 fold expression such as `(xs + ... + 0)` becomes a recursive macro for the compile-time cases, and a slice or an iterator for everything else:

```rust
macro_rules! sum {
    () => { 0 };
    ($first:expr $(, $rest:expr)*) => { $first + sum!($($rest),*) };
}

fn main() {
    println!("{}", sum!(1, 2, 3)); // 6
    println!("{}", [1, 2, 3].iter().sum::<i32>()); // usually a slice is all you need
}
```

The rest of the preprocessor maps one tool at a time:

- `#ifdef` becomes the `#[cfg(...)]` attribute on an item (`#[cfg(target_os = "linux")]`, `#[cfg(test)]`) or the `cfg!(...)` macro in an expression.
- Cargo **features** replace `-DENABLE_FOO`.
- Include guards disappear with the headers.
- `__FILE__` and `__LINE__` become `file!()` and `line!()`.
- Code generators and X-macros become **procedural macros**: Rust functions, compiled as their own crate, that receive tokens and return tokens.

`#[derive(Debug, Clone)]` is a built-in derive macro and serde's `#[derive(Serialize)]` is a procedural one. Derives are how Rust generates code that C++ would generate with templates, X-macros, or an external tool.

## Graphs, parent pointers, and self-referential data

Ownership in Rust forms a tree: every value has exactly one owner. C++ data structures that are not trees, such as doubly linked lists, trees with parent pointers, and graphs with cycles, are where the borrow checker pushes back hardest. The usual C++ shape:

```cpp
#include <memory>
#include <string>
#include <vector>

struct Node {
    std::string name;
    Node* parent = nullptr;                      // non-owning back pointer
    std::vector<std::unique_ptr<Node>> children; // owning
};
```

There are three Rust answers, in order of preference:

1. **An arena with indices.** Store all nodes in one `Vec` and link them by index. The vector owns everything, and indices are plain numbers the borrow checker does not need to track.
2. **`Rc` for ownership plus `Weak` for back pointers**, with `RefCell` for mutation (Part 2). It works, but it pays for reference counts and runtime borrow checks.
3. **Raw pointers inside `unsafe`**, behind a safe API. This is how `std::collections::LinkedList` is written.

```rust
struct Node {
    name: String,
    parent: Option<usize>,
    children: Vec<usize>,
}

#[derive(Default)]
struct Tree {
    nodes: Vec<Node>,
}

impl Tree {
    fn add(&mut self, name: &str, parent: Option<usize>) -> usize {
        let id = self.nodes.len();
        self.nodes.push(Node { name: name.to_string(), parent, children: Vec::new() });
        if let Some(p) = parent {
            self.nodes[p].children.push(id);
        }
        id
    }

    fn path(&self, mut id: usize) -> String {
        let mut parts = vec![self.nodes[id].name.as_str()];
        while let Some(p) = self.nodes[id].parent {
            parts.push(self.nodes[p].name.as_str());
            id = p;
        }
        parts.reverse();
        parts.join("/")
    }
}

fn main() {
    let mut tree = Tree::default();
    let usr = tree.add("usr", None);
    let lib = tree.add("lib", Some(usr));
    let rustlib = tree.add("rustlib", Some(lib));
    println!("{} ({} child)", tree.path(rustlib), tree.nodes[usr].children.len()); // usr/lib/rustlib (1 child)
}
```

An index is a pointer the compiler does not check, so a stale index can point at the wrong node. The failure mode is still different from a dangling pointer: a logic bug or a bounds-check panic, never undefined behavior. Generational arenas such as the `slotmap` crate catch stale indices too.

**Self-referential structs**, where one field points into another field of the same object, are the hardest case. C++ handles them with a user-written move constructor that fixes up the pointer. Rust has no move constructors: a move is always a copy of the bytes, so an internal pointer would dangle after every move. Rust gives you three options:

- Store an offset instead of a pointer.
- Use a crate built for the job, such as `self_cell` or `ouroboros`.
- Promise that the value never moves, with **`Pin`**.

`Pin` exists mostly for async: an `async fn` state machine can borrow from itself, and pinning is how the executor promises never to move the state machine again, from the first poll until it is dropped.

## `unsafe`: five superpowers, not an off switch

C++ is unsafe everywhere, so nothing marks the dangerous lines. Rust inverts that: safe code cannot cause undefined behavior, and the dangerous operations need an `unsafe` block. [The Rust Book](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html) lists five "unsafe superpowers" (the Reference's full list adds a few more, such as declaring `extern` blocks, covered below):

1. Dereference a raw pointer.
2. Call an unsafe function or method.
3. Access or modify a mutable static variable.
4. Implement an unsafe trait.
5. Access fields of unions.

And, in the Book's words, "`unsafe` doesn't turn off the borrow checker or disable any of Rust's other safety checks". Types, reference lifetimes, and slice bounds checks all still apply inside the block.

Why does `unsafe` exist at all? Because some correct code cannot be proven correct by the borrow checker. Splitting a slice into two mutable halves is the textbook case. The halves never overlap, but the checker only sees two mutable borrows of the same slice:

```rust
// does not compile: E0499
fn split_at_mut(v: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    (&mut v[..mid], &mut v[mid..])
}
```

The `unsafe` version proves the non-overlap by hand and writes the proof down in a **`// SAFETY:` comment**, the convention for every unsafe block (Clippy can enforce it with the `undocumented_unsafe_blocks` lint):

```rust
use std::slice;

fn split_at_mut(v: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    assert!(mid <= v.len());
    let len = v.len();
    let ptr = v.as_mut_ptr();
    // SAFETY: `mid <= len`, so both halves are in bounds, and they do not
    // overlap, so handing out two `&mut` slices is sound.
    unsafe {
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}

fn main() {
    let mut v = [1, 2, 3, 4, 5];
    let (a, b) = split_at_mut(&mut v, 2);
    a[0] = 10;
    b[0] = 30;
    println!("{v:?}"); // [10, 2, 30, 4, 5]
}
```

This is the pattern for all unsafe Rust: a small unsafe core inside a safe function whose signature makes misuse impossible. The standard library is built this way, and so is every good FFI wrapper.

Type punning shows how much C++ undefined behavior disappears. The classic `reinterpret_cast` read violates strict aliasing, and C++20 added `std::bit_cast` to do it legally. In Rust, the safe methods are the idiomatic answer, and `transmute` is the explicit, unsafe last resort:

```cpp
#include <bit>
#include <cstdint>

std::uint32_t bits_of(float f) {
    // return *reinterpret_cast<std::uint32_t*>(&f); // strict-aliasing violation: UB
    return std::bit_cast<std::uint32_t>(f);          // C++20: defined
}
```

```rust
use std::mem;

fn main() {
    let f = 1.0_f32;
    let a = f.to_bits();                         // safe: the idiomatic answer
    let b = u32::from_ne_bytes(f.to_ne_bytes()); // safe: works for any plain bytes
    // SAFETY: f32 and u32 have the same size, and every bit pattern is a valid u32.
    let c: u32 = unsafe { mem::transmute(f) };
    println!("{a:#x} {b:#x} {c:#x}"); // 0x3f800000 0x3f800000 0x3f800000
}
```

| C++ | Rust |
|---|---|
| `T*` | `*const T`, `*mut T` (dereferencing is unsafe) |
| `reinterpret_cast` between pointer types | `ptr.cast::<U>()` |
| `std::bit_cast` | `to_bits`, `from_ne_bytes`, or `transmute` (unsafe; sizes checked at compile time) |
| casting a byte buffer to a struct | the `bytemuck` or `zerocopy` crates, which check the layout |
| placement `new` into raw storage | `MaybeUninit<T>` |
| `union` | `union` (reading a field is unsafe); usually an `enum` instead |
| `volatile` access | `ptr::read_volatile`, `ptr::write_volatile` |
| inline assembly | `asm!` (stable since 1.59) |
| ASan, UBSan | Miri, plus sanitizers on nightly |

**The gap:** Rust's list of undefined behavior is *different* from C++'s, not just shorter. Some C++ undefined behavior is gone, such as signed overflow and type-based aliasing.

Some Rust undefined behavior is stricter than C++: two `&mut` to the same memory are undefined as soon as you use the older one after creating the newer one, even in single-threaded code (the exact aliasing rules are not final yet, and Miri checks the current model). A `bool` holding the value `2` is undefined as soon as it is produced, while C++ makes it undefined only when it is read.

The [Reference's list](https://doc.rust-lang.org/reference/behavior-considered-undefined.html) is short and worth reading once. To check unsafe code against it, run your tests under [Miri](https://github.com/rust-lang/miri), an interpreter that detects many kinds of undefined behavior, aliasing violations included: `cargo +nightly miri test`.

Edition 2024 also tightened the syntax around unsafe code:

- `extern` blocks must be written `unsafe extern`.
- The `no_mangle`, `export_name`, and `link_section` attributes must be written `#[unsafe(...)]`.
- The `unsafe_op_in_unsafe_fn` lint warns by default, so an `unsafe fn` needs explicit `unsafe {}` blocks around the unsafe operations in its body.

## FFI and incremental migration

Nobody rewrites a million lines of C++ in one go. Rust and C++ meet at a boundary, and the most stable boundary is the C ABI, in both directions. Here is Rust calling C and exporting a function to C, in edition 2024 syntax:

```rust
use std::ffi::{CStr, c_char, c_int};

unsafe extern "C" {
    safe fn sqrt(x: f64) -> f64;          // declared safe: defined for every f64
    fn strlen(s: *const c_char) -> usize; // unsafe to call: needs a valid C string
}

#[unsafe(no_mangle)]
pub extern "C" fn rust_add(a: c_int, b: c_int) -> c_int {
    a.wrapping_add(b)
}

fn main() {
    let msg: &CStr = c"hello";
    // SAFETY: `msg` is a valid, NUL-terminated C string.
    let n = unsafe { strlen(msg.as_ptr()) };
    println!("{} {} {}", sqrt(49.0), n, rust_add(2, 3)); // 7 5 5
}
```

Marking a foreign function `safe` is a promise you make, and the compiler cannot check it. C's `abs` looks just as harmless as `sqrt`, but `abs(INT_MIN)` is undefined behavior in C, so `abs` must stay an ordinary unsafe declaration.

On the C++ side, `rust_add` is an ordinary `extern "C" int rust_add(int a, int b);`, and `cbindgen` can generate that header from the Rust source. A raw C ABI is fine for a handful of functions. For a real C++ API with classes, strings, and smart pointers, use a bindings tool:

| Tool | Direction | What it does | Status (October 2026) |
|---|---|---|---|
| [bindgen](https://github.com/rust-lang/rust-bindgen) | C/C++ headers to Rust | generates `extern` declarations | 0.73.2, maintained by the Rust project |
| [cbindgen](https://github.com/mozilla/cbindgen) | Rust to C/C++ headers | generates headers for `extern "C"` items | 0.29.4 |
| [cxx](https://cxx.rs/) | both | a safe bridge over a shared subset: `String`, `Vec`, `UniquePtr`, `SharedPtr`; `Result` returns map to C++ exceptions | 1.0.205, actively released |
| [Crubit](https://github.com/google/crubit) | both, in progress | Google's bidirectional bindings generator | C++ calling Rust usable in Chromium since July 2026, with restrictions; Bazel only, no releases |
| [Zngur](https://github.com/HKalbasi/zngur) | mainly C++ calling Rust | exposes arbitrary Rust types and methods to C++ | 0.11.0 |
| [autocxx](https://github.com/google/autocxx) | C++ to Rust | generates cxx bridges from C++ headers | archived, no longer maintained by Google |

`cxx` is the default choice today. You declare both sides of the boundary in one `#[cxx::bridge]` module, and its code generator writes the glue for both compilers, checking that the types on each side agree.

### Where to start

Google's Android team has published the most detailed data on mixing Rust into a large C and C++ code base, and it changes the migration strategy. Their [2024 analysis](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html) found that "vulnerabilities decay exponentially": based on average vulnerability lifetimes, 5-year-old code has a 3.4x to 7.4x lower vulnerability density than new code. Their conclusion: "The problem is overwhelmingly with new code."

Memory safety issues fell from 76% of Android vulnerabilities in 2019 to 24% in 2024, while Android wrote its *new* code in memory-safe languages instead of rewriting old code.

Their [November 2025 update](https://blog.google/security/rust-in-android-move-fast-fix-things/) reports:

- memory safety vulnerabilities below 20% of the total for the first time
- a 1000x reduction in memory safety vulnerability density for Rust compared to Android's C and C++ code (an estimate built on a single near-miss in about 5 million lines of Rust)
- a roughly 4x lower rollback rate for medium and large Rust changes
- about 25% less time in code review
- about 4% of the Rust code written inside `unsafe` blocks

These are one company's numbers on one code base. The shape of the strategy still transfers:

1. **Write new components in Rust first**, behind a narrow C ABI or a `cxx` bridge. New code is where most bugs are born.
2. **Port leaf modules next**: parsers, codecs, protocol handlers. They take untrusted input and depend little on the rest of the code base.
3. **Keep the boundary small and test it hard.** Fuzz both sides. Every pointer that crosses the boundary is an unchecked contract.
4. **Put the `unsafe` at the boundary and keep the inside safe**: a thin layer that turns raw pointers into slices and references, and safe Rust behind it.
5. **Translate intent, not lines.** A line-by-line port produces C++ in Rust syntax, with `unsafe` and `Rc<RefCell<...>>` everywhere. Automated translation is an active research area (c2rust for C, DARPA's [TRACTOR](https://www.darpa.mil/research/programs/translating-all-c-to-rust) program for C to Rust), and idiomatic output is the hard part, not the syntax.

## What does not translate

Some C++ tools have no Rust equivalent, on purpose. Most of them came up earlier in the series; this table puts them in one place.

| C++ feature | Rust answer |
|---|---|
| implementation inheritance, `protected` | composition, traits with default methods, delegation |
| virtual and multiple inheritance | trait objects; a trait can require other traits |
| function overloading | distinct names, or a generic function over a trait |
| default arguments | `Default` + struct update syntax, or builders |
| implicit conversions, converting constructors | explicit `From`/`Into` |
| partial and full specialization | per-type trait impls; `specialization` is unstable |
| `friend` | module privacy |
| move constructors, self-fixing pointers | moves are byte copies; indices, offsets, or `Pin` |
| variadic templates | macros, tuples, slices |
| `dynamic_cast`, RTTI | `std::any::Any` downcasting, for `'static` types only |
| exceptions through `extern "C"` | a panic that reaches an `extern "C"` boundary aborts (since 1.81); `extern "C-unwind"` (since 1.71) allows unwinding |

The last row matters most in mixed code bases. A C++ exception must never travel through Rust frames, and a Rust panic must never travel through C++ frames, unless both sides use the `-unwind` ABI on purpose. The safe pattern is to catch at the boundary on both sides, with `catch (...)` in C++ and `std::panic::catch_unwind` in Rust, and to convert the failure into an error code.

## Cheat sheet

| C++ | Rust |
|---|---|
| `std::thread`, `detach()` | `thread::spawn` (needs `'static`), drop the handle |
| `std::jthread` with `[&]` captures | `thread::scope` |
| thread safety by documentation | `Send` and `Sync`, checked by the compiler |
| `std::mutex` beside the data | `Mutex<T>` around the data (poisoning on panic) |
| `std::shared_mutex` / `std::condition_variable` | `RwLock<T>` / `Condvar` |
| `std::scoped_lock(m1, m2)` | lock in a fixed order (no std equivalent) |
| deque + mutex + condition variable queue | `std::sync::mpsc` channel |
| `std::atomic<T>`, `memory_order_*` | `AtomicI32` etc., `Ordering::*` (C++20 model, no consume) |
| function-local `static`, `std::call_once` | `LazyLock`, `OnceLock` |
| mutable global | `static` with an atomic or a `Mutex`; avoid `static mut` |
| `thread_local` | `thread_local!` |
| C++20 coroutines | `async`/`await` plus a runtime crate |
| `std::generator` | `Iterator` impl, `iter::from_fn` (`gen` is unstable) |
| struct with a `string_view` member | `struct Parser<'a> { input: &'a str }` |
| `constexpr` function | `const fn` |
| `template <std::size_t N>` | `const N: usize` |
| `enable_if`, SFINAE, concepts | trait bounds |
| `typename T::value_type`, `numeric_limits` | associated types and constants |
| CRTP | trait default methods |
| `if constexpr`, specialization | per-type trait impls (no stable specialization) |
| `#define` macro | `macro_rules!` (hygienic, token-based) |
| variadic template, fold expression | recursive macro, tuple, or slice |
| `#ifdef`, `-DFOO` | `#[cfg(...)]`, `cfg!`, Cargo features |
| code generators, X-macros | `#[derive]`, procedural macros |
| parent pointers, graphs | arena + indices, or `Rc` + `Weak` |
| raw pointer code | `unsafe` block + `// SAFETY:` comment, safe wrapper |
| `reinterpret_cast`, `std::bit_cast` | `to_bits`, `from_ne_bytes`, `transmute` |
| `extern "C"` | `unsafe extern "C" { ... }`, `#[unsafe(no_mangle)] extern "C" fn` |
| C++ interop | bindgen, cbindgen, cxx, Crubit, Zngur |

## Traps for C++ developers

1. **Rust prevents data races, not race conditions.** Deadlocks and check-then-act bugs still compile.
2. **`lock()` returns a `Result`** because of poisoning. Decide what a panic under the lock means for your data.
3. **`thread::spawn` needs owned data.** Use `move` closures, `Arc`, or `thread::scope`.
4. **Futures are lazy, and the standard library has no executor.** Nothing runs until something polls it.
5. **`T: 'static` does not mean "lives forever".** It means "holds no short borrows".
6. **Elided lifetimes in methods borrow from `self`.** Name the lifetime when the result borrows from a field.
7. **No specialization on stable.** Design trait impls so they do not overlap.
8. **Macros still evaluate an argument as many times as it appears.**
9. **`unsafe` does not disable the borrow checker**, and aliasing `&mut` references are undefined behavior even in single-threaded code.
10. **Panics and exceptions must not cross the FFI boundary.** Catch on both sides, or use the `-unwind` ABIs on purpose.

## Closing the series

C++ and Rust can express the same programs. What changes is where the rules live. In C++, "lock before you touch this", "this view must not outlive that string", and "these two pointers never alias" live in comments, code review, and sanitizer runs. In Rust, they live in types that the compiler checks on every build, and the few rules it cannot check sit inside `unsafe` blocks with a written justification.

Moving rules into checked types is the same principle as making dependencies visible and explicit, which the [software design post](https://alexsavio.github.io/first-principles-software-design) argues for from first principles.

That is also the migration plan in one sentence: move the rules into types where code is new or exposed to untrusted input, keep `unsafe` thin and at the edges, and let the old C++ that has already survived years of bug reports age in place. The advice from Part 1 still holds: translate the intent, not the syntax, and read every compile error as an assumption your C++ code was making without writing it down.

---

## References

1. [The Rust Programming Language: Unsafe Rust](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html), the five unsafe superpowers
2. [The Rust Programming Language: Fearless Concurrency](https://doc.rust-lang.org/book/ch16-00-concurrency.html), threads, channels, and shared state
3. [std::sync::atomic](https://doc.rust-lang.org/std/sync/atomic/index.html), Rust atomics follow the C++20 memory model
4. [The Rustonomicon: Data Races and Race Conditions](https://doc.rust-lang.org/nomicon/races.html), what Rust does and does not prevent
5. [The Rustonomicon](https://doc.rust-lang.org/nomicon/), the guide to unsafe Rust
6. [The Rust Reference: Lifetime elision](https://doc.rust-lang.org/reference/lifetime-elision.html), the three elision rules
7. [The Rust Reference: Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html), Rust's list of UB
8. [Rust Edition Guide: Unsafe extern blocks](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html), edition 2024 FFI syntax
9. [Rust Edition Guide: Disallow references to static mut](https://doc.rust-lang.org/edition-guide/rust-2024/static-mut-references.html), the `static_mut_refs` lint
10. [Rust release notes](https://doc.rust-lang.org/releases.html), stabilization versions cited in this post
11. [Miri](https://github.com/rust-lang/miri), an interpreter that detects undefined behavior
12. [cppreference: std::generator](https://en.cppreference.com/w/cpp/coroutine/generator.html), C++23 coroutine generator
13. [cppreference: std::bit_cast](https://en.cppreference.com/w/cpp/numeric/bit_cast.html), defined type punning in C++20
14. [CXX: safe interop between Rust and C++](https://cxx.rs/)
15. [rust-bindgen](https://github.com/rust-lang/rust-bindgen), C/C++ headers to Rust
16. [cbindgen](https://github.com/mozilla/cbindgen), Rust to C/C++ headers
17. [Crubit](https://github.com/google/crubit), Google's C++/Rust bindings generator
18. [Crubit's cpp_api_from_rust is now available in Chromium](https://groups.google.com/a/chromium.org/g/rust-dev/c/Kixvw8bhfME), Chromium rust-dev, July 2026
19. [Zngur](https://github.com/HKalbasi/zngur), C++/Rust interop that exposes Rust types to C++
20. [autocxx](https://github.com/google/autocxx), archived C++ to Rust bindings generator
21. [Eliminating Memory Safety Vulnerabilities at the Source](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html), Google Security Blog, September 2024
22. [Rust in Android: move fast and fix things](https://blog.google/security/rust-in-android-move-fast-fix-things/), Google, November 2025
23. [DARPA TRACTOR: Translating All C to Rust](https://www.darpa.mil/research/programs/translating-all-c-to-rust), automated C to Rust translation research
24. [First Principles: Software Design](https://alexsavio.github.io/first-principles-software-design), related post on where design rules should live
