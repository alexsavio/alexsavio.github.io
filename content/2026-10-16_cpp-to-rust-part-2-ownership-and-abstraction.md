Title: C++ to Rust, Part 2: Ownership and Abstraction
Date: 2026-10-16 11:00:00
Category: Engineering
Tags: rust, cpp, programming-languages, tutorial, memory-safety
Slug: cpp-to-rust-part-2-ownership-and-abstraction
Series: C++ to Rust
Series_index: 2
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: A phrasebook for C++ developers moving to Rust, part 2 of 3. Moves, copies, RAII, borrowing, smart pointers, interior mutability, sum types, generics, traits, operators, errors, closures, and iterators, mapped from the C++ idiom to the Rust idiom, with the semantic gaps that bite.
Status: draft
scratch: ['cpp_to_rust_research_landscape', 'cpp_to_rust_research_versions']

## TL;DR

C++ already has ownership, but it lives in conventions: `std::unique_ptr` owns, a raw pointer observes, a moved-from object must not be used, an iterator dies when the vector grows, a destructor releases the resource. Rust makes those conventions part of the type system: moves are destructive, every value has exactly one owner, and the compiler checks every borrow. Abstraction follows the same pattern: exceptions become `Result`, `std::variant` becomes `enum`, templates become generics that are type-checked at their definition, and virtual functions become traits whose dispatch you pick at each call site. Most of this is the discipline that good modern C++ already follows. The difference is who checks it.

[TOC]

## Where this fits

This is Part 2 of a three-part series for working C++ developers. Part 1 covered the everyday vocabulary: types, variables, control flow, strings, containers, structs, enums, and `Option`. Part 3 covers concurrency, lifetimes in depth, compile-time programming, `unsafe`, FFI, and migration strategy.

This part is not a theory of the borrow checker, and it does not cover explicit lifetime annotations (Part 3 does). It covers the ownership rules you meet on day two, and the tools Rust gives you to build abstractions without classes, exceptions, or templates.

As before, every snippet was compiled with **rustc 1.99 (edition 2024)** and **Apple clang 21 with `-std=c++23`**, and each one carries its own `#include` lines or `use` imports. A snippet whose first line is `// does not compile` fails with the error code it names.

## Moves are destructive

In C++, `std::move` does not move anything. It is a cast to an rvalue reference. The move constructor then decides what happens, and the source object stays alive until its destructor runs at the end of the scope. Standard library types promise a "valid but unspecified state"; your own types leave whatever their move constructor leaves.

```cpp
#include <print>
#include <string>
#include <utility>

std::string a = "hello";
std::string b = std::move(a); // a cast; the move constructor steals the buffer
std::println("[{}]", a);      // compiles; `a` is valid but unspecified (empty in practice)
```

In Rust, assigning a non-`Copy` value **is** the move. The compiler copies the bytes of the value (for a `String`: pointer, length, capacity), and the source is dead from that line on:

```rust
// does not compile: E0382
fn main() {
    let a = String::from("hello");
    let b = a;         // move: `a` is no longer a valid name
    println!("[{a}]"); // error[E0382]: borrow of moved value: `a`
}
```

**The gap:** a C++ move leaves a husk. Every movable class must define what its husk looks like, keep it destructible, and survive users who touch it. A Rust move leaves nothing. There is no moved-from state, no destructor runs for the source, and no user code runs during the move. This has knock-on effects:

- There are **no move constructors** to write, and no `noexcept` move to remember for `std::vector` growth.
- A type does not need an "empty" state. A `Box<T>` can never be null, unlike a moved-from `std::unique_ptr<T>`.
- Passing by value moves by default, so the C++ "sink parameter" idiom (`void set_name(std::string name)`) is how Rust functions take ownership.

```rust
fn consume(s: String) -> usize {
    s.len() // `s` is dropped at the end of this function
}

fn main() {
    let a = String::from("hello");
    let borrowed = a.len();    // borrow: `a` is still ours
    let cloned = consume(a.clone()); // explicit deep copy, then move the copy
    let moved = consume(a);    // move: `a` is gone after this line
    println!("{borrowed} {cloned} {moved}");
}
```

## Copy, Clone, and the end of the rule of five

| C++ | Rust |
|---|---|
| implicit copy constructor | `Clone`: an explicit `.clone()` call |
| trivially copyable type (`int`, a POD struct) | `Copy`: implicit bitwise copy, the source stays usable |
| move constructor and move assignment | nothing to write: moves are always bitwise |
| destructor | `impl Drop` |
| rule of three / rule of five | does not apply |
| rule of zero | `#[derive(Clone)]` and let the fields do the work |
| `T(const T&) = delete;` (move-only type) | the default: just do not implement `Clone` |

```rust
#[derive(Debug, Clone, Copy, PartialEq)]
struct Point {
    x: f64,
    y: f64,
}

#[derive(Debug, Clone)]
struct Polygon {
    points: Vec<Point>,
}

fn main() {
    let p = Point { x: 1.0, y: 2.0 };
    let q = p; // Copy: `p` is still usable, like an int
    let poly = Polygon { points: vec![p, q] };
    let copy = poly.clone(); // deep copy, spelled out
    let moved = poly;        // move: `poly` is gone
    println!("{p:?} {} {}", copy.points.len(), moved.points.len());
}
```

**The gap:** C++ gives the most expensive operation, a deep copy, the cheapest syntax: `a = b`. Rust turns that around. `a = b` is always cheap, a fixed-size copy of bytes, and every deep copy says `.clone()`, so you can find allocations with `grep`. A type with a `Drop` impl can never be `Copy`, which closes the door on accidentally duplicated resources.

Watch for the opposite reflex. Calling `.clone()` until the borrow checker goes quiet is the most common beginner anti-pattern. It is fine for small or rarely copied data, and a smell in a hot loop.

## RAII with `Drop`

RAII is the resource model of both languages. A C++ destructor becomes an `impl Drop`, and it runs when the owner goes out of scope:

```rust
struct Guard(&'static str);

impl Drop for Guard {
    fn drop(&mut self) {
        println!("drop {}", self.0);
    }
}

struct Pair {
    first: Guard,
    second: Guard,
}

fn main() {
    let _a = Guard("a");
    let _b = Guard("b");
    let _pair = Pair { first: Guard("pair.first"), second: Guard("pair.second") };
    let _ = Guard("unnamed"); // `_` does not bind: dropped right here
    let early = Guard("early");
    drop(early); // std::mem::drop ends the value's life now
    println!("end of main");
}
```

The output is `drop unnamed`, `drop early`, `end of main`, `drop pair.first`, `drop pair.second`, `drop b`, `drop a`.

**The gap:** local variables are dropped in reverse order of declaration, exactly as in C++. Struct **fields** are not. The [Rust Reference](https://doc.rust-lang.org/reference/destructors.html) says "the fields of a struct are dropped in declaration order", while C++ destroys members in *reverse* declaration order.

If a C++ class depends on member destruction order (a worker thread member that must stop before the queue it reads is destroyed, say), reorder the fields when you port it, or write an explicit `Drop`.

Three more differences:

- `let _ = Guard(...)` drops the value at once, because `_` is a pattern that binds nothing. It is the same bug as an unnamed `std::lock_guard<std::mutex>{m};` in C++. Name your guards `_guard`, not `_`.
- You cannot call `x.drop()` yourself (error E0040). Call `drop(x)`, which moves `x` into a function that does nothing, so the value dies there.
- `Drop` is not guaranteed to run. `std::mem::forget` and reference-counting cycles leak, and leaking is considered safe. Use `Drop` for resource cleanup, never as the only thing that keeps memory safe.

## Borrowing: the rule that removes iterator invalidation

Part 1 stated the rule: at any moment, a value has **either any number of shared `&T` borrows or exactly one `&mut T` borrow**. This C++ loop is undefined behavior: `push_back` always invalidates the `end()` iterator that the range-for cached, and it can also reallocate the buffer under the loop's iterator:

```cpp
#include <vector>

std::vector<int> v{1, 2, 3};
for (int x : v) {
    if (x == 2) v.push_back(4); // may reallocate: the loop iterator now dangles
}
```

In Rust, the loop holds a shared borrow of `v`, and `push` needs a mutable one, so the compiler rejects it:

```rust
// does not compile: E0502
fn main() {
    let mut v = vec![1, 2, 3];
    for x in &v {
        if *x == 2 {
            v.push(4); // error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
        }
    }
}
```

The fix is to separate reading from writing, which is what the C++ code should have done too:

```rust
fn main() {
    let mut v = vec![1, 2, 3];
    if v.contains(&2) {
        v.push(4);
    }
    println!("{v:?}"); // [1, 2, 3, 4]
}
```

The same rule, plus "a reference cannot outlive its owner", removes dangling references:

```rust
// does not compile: E0515
fn longest(names: &[String]) -> &str {
    let fallback = String::from("nobody");
    match names.iter().max_by_key(|n| n.len()) {
        Some(name) => name,
        None => &fallback, // error[E0515]: cannot return value referencing local variable `fallback`
    }
}
```

(The compiler infers that the returned `&str` borrows from `names`. Part 3 shows when you must write that link yourself.)

Borrows end at their **last use**, not at the end of the scope, so a lot of code that looks like a conflict compiles fine. When the borrow checker does push back, these are the usual moves:

| Symptom | Idiomatic fix |
|---|---|
| mutate a collection while iterating it | collect the changes, then apply them; or use `retain`, `drain`, `iter_mut` |
| two `&mut` into different parts of one struct | borrow the fields directly (the checker tracks fields inside a function body); `split_at_mut` for slices |
| a struct that stores a reference | store an owned value, an index, or an `Rc` instead (or add a lifetime parameter, Part 3) |
| a graph with back pointers | indices into a `Vec` (an **arena**), or `Rc` + `Weak` (Part 3) |

## Smart pointers

| C++ | Rust | Note |
|---|---|---|
| `std::unique_ptr<T>` | `Box<T>` | never null; `Option<Box<T>>` is still pointer-sized |
| `std::unique_ptr<T[]>` | `Box<[T]>` or `Vec<T>` | |
| `std::shared_ptr<T>` | `Rc<T>` (one thread) or `Arc<T>` (atomic count) | shared means read-only, see the next section |
| `std::weak_ptr<T>` | `rc::Weak<T>` / `sync::Weak<T>` | `upgrade()` returns an `Option` |
| `std::make_shared<T>(...)` | `Rc::new(value)` | count and value in one allocation |
| custom deleter | a newtype with `Drop` | `Box` has no deleter parameter |
| raw observer `T*` | `&T`, `&mut T`, or an index | |

```rust
use std::rc::{Rc, Weak};

fn main() {
    let config = Rc::new(String::from("prod"));
    let for_worker = Rc::clone(&config); // count + 1, no deep copy
    let observer: Weak<String> = Rc::downgrade(&config);
    println!("strong={} weak={}", Rc::strong_count(&config), Rc::weak_count(&config));
    drop(config);
    drop(for_worker);
    println!("{:?}", observer.upgrade()); // None: the String is gone
}
```

**The gap:** `std::shared_ptr` must keep its reference count thread-safe, because nothing stops you from copying it into another thread, so in general every copy pays for an atomic operation.

Rust has two types. `Rc` uses a plain counter, and if you try to send an `Rc` to another thread, the program does not compile (error E0277; Part 3 shows the error and the `Send` trait behind it). Single-threaded code gets the cheap counter, and the compiler makes sure it stays single-threaded.

The second gap is that shared ownership means shared **read-only** access. Two `Rc` handles to one value cannot both mutate it, because "shared XOR mutable" applies to owners too.

## Interior mutability: `mutable`, but checked

C++ uses `mutable` to let a `const` member function update a cache or a counter:

```cpp
#include <optional>
#include <string>

class Report {
public:
    const std::string& summary() const {
        if (!cache_) cache_ = expensive(); // allowed in a const method because of `mutable`
        return *cache_;
    }
private:
    static std::string expensive() { return "42 rows"; }
    mutable std::optional<std::string> cache_;
};
```

Rust's equivalent is a family of **cell** types that allow mutation through a shared `&self`, each with its own safety story:

```rust
use std::cell::{Cell, OnceCell, RefCell};

struct Report {
    cache: OnceCell<String>,  // set once, then read-only: lazy caches
    hits: Cell<u32>,          // copy values in and out, no references handed out
    log: RefCell<Vec<String>>, // borrow rules checked at run time
}

impl Report {
    fn summary(&self) -> &str {
        self.hits.set(self.hits.get() + 1);
        self.log.borrow_mut().push("summary".into());
        self.cache.get_or_init(|| "42 rows".to_string())
    }
}

fn main() {
    let r = Report { cache: OnceCell::new(), hits: Cell::new(0), log: RefCell::new(vec![]) };
    r.summary();
    println!("{} hits={} log={:?}", r.summary(), r.hits.get(), r.log.borrow());
}
```

**The gap:** C++ `mutable` switches the check off. `RefCell` moves the borrow check from compile time to run time: a second `borrow_mut()` while a borrow is alive panics with `RefCell already borrowed` instead of corrupting memory.

`Rc<RefCell<T>>` is the Rust spelling of a `shared_ptr<T>` that everyone mutates. It works, and you will see it in tutorials, but a code base full of it is usually a C++ object graph translated line by line. Before you reach for it, ask whether one owner plus borrows, or an arena with indices, would do. The thread-safe cousins (`Mutex`, `RwLock`, atomics, `OnceLock`) are in Part 3.

## Sum types: `std::variant` becomes `enum`

C++17 `std::variant` plus the "overloaded lambdas" trick is the standard way to write a tagged union in C++:

```cpp
#include <variant>

struct Circle { double r; };
struct Rect { double w, h; };
using Shape = std::variant<Circle, Rect>;

template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

double area(const Shape& s) {
    return std::visit(overloaded{
        [](const Circle& c) { return 3.14159 * c.r * c.r; },
        [](const Rect& r) { return r.w * r.h; },
    }, s);
}
```

In Rust, this is just an `enum`, and `std::visit` is just `match`:

```rust
use std::f64::consts::PI;

enum Shape {
    Circle { r: f64 },
    Rect { w: f64, h: f64 },
}

fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle { r } => PI * r * r,
        Shape::Rect { w, h } => w * h,
    }
}

fn main() {
    let shapes = [Shape::Circle { r: 1.0 }, Shape::Rect { w: 2.0, h: 3.0 }];
    let total: f64 = shapes.iter().map(area).sum();
    println!("{total:.2}"); // 9.14
}
```

**The gap:** an `enum` does more than `std::variant`:

- Variants have names, so `std::variant<int, int>` and its index-based access have no equivalent problem.
- There is no `valueless_by_exception` state.
- Patterns nest and take guards (`Some(Shape::Rect { w, .. }) if *w > 1.0`).
- `match` is exhaustive, so adding a variant turns every unhandled `match` into a compile error. That is the refactoring tool C++ never had.

`Option` and `Result` are not special language features. They are ordinary enums in the standard library.

A rule of thumb for choosing between an `enum` and a trait (next sections): if the set of **types** is closed and the set of **operations** keeps growing, use an `enum`. If the set of types keeps growing and the operations are fixed, use a trait.

## Templates become generics

Both languages compile generics by **monomorphization**: one copy of the code per concrete type, with the same speed and the same binary-size trade-off. The difference is *when* the code is type-checked.

```cpp
#include <concepts>
#include <vector>

template <std::totally_ordered T>
const T& largest(const std::vector<T>& items) {
    const T* best = &items.front();
    for (const auto& x : items)
        if (x > *best) best = &x;
    return *best;
}

template <std::equality_comparable T>
bool less_than(const T& a, const T& b) {
    return a < b; // `<` is not part of the concept, and the definition still compiles
}
```

The second template is the surprise. A C++20 concept constrains the *callers*, but the compiler does not check the template *body* against the concept. The error only appears when someone instantiates `less_than` with a type that has `==` but no `<`, deep inside an instantiation backtrace.

A Rust generic body is checked once, at its definition, against its **trait bounds**. You can only use what the bounds promise:

```rust
fn largest<T: PartialOrd>(items: &[T]) -> &T {
    let mut best = &items[0];
    for x in items {
        if x > best {
            best = x;
        }
    }
    best
}

fn main() {
    println!("{} {}", largest(&[3, 9, 2]), largest(&["kiwi", "apple"]));
}
```

```rust
// does not compile: E0369
fn less_than<T: PartialEq>(a: &T, b: &T) -> bool {
    a < b // error[E0369]: binary operation `<` cannot be applied to type `&T`
}
```

| C++ | Rust |
|---|---|
| `template <typename T>` | `fn f<T>(...)`, `struct S<T>` |
| concept, `requires` clause | trait bound `T: Trait`, `where` clause |
| abbreviated template `void f(auto x)` | `fn f(x: impl Trait)` |
| deduced return type `auto` | `-> impl Trait` |
| `typename T::value_type` | associated type, `T::Item` |
| `template <std::size_t N>` | const generics, `<const N: usize>` (Part 3) |
| full or partial specialization | not available on stable Rust (Part 3) |

**The gap:** Rust generics give you better errors and safer libraries, because a generic function cannot quietly depend on an operation its signature does not mention. The price is the duck typing you lose. Generic numeric code must name every operation it uses (`T: Add<Output = T> + Copy`), which is why crates like [`num-traits`](https://docs.rs/num-traits) exist.

## Virtual functions become traits

```cpp
#include <memory>
#include <string>
#include <vector>

class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual std::string name() const { return "shape"; }
};

class Square : public Shape {
public:
    explicit Square(double side) : side_(side) {}
    double area() const override { return side_ * side_; }
    std::string name() const override { return "square"; }
private:
    double side_;
};

double total_area(const std::vector<std::unique_ptr<Shape>>& shapes) {
    double sum = 0;
    for (const auto& s : shapes) sum += s->area();
    return sum;
}
```

```rust
trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> String {
        "shape".to_string() // a default method, like a non-pure virtual
    }
}

struct Square {
    side: f64,
}

impl Shape for Square {
    fn area(&self) -> f64 {
        self.side * self.side
    }
    fn name(&self) -> String {
        "square".to_string()
    }
}

impl Shape for f64 {
    fn area(&self) -> f64 {
        *self // a trait implemented for a type we did not write
    }
}

fn total_area(shapes: &[Box<dyn Shape>]) -> f64 {
    shapes.iter().map(|s| s.area()).sum() // dynamic dispatch, like virtual
}

fn describe(shape: &impl Shape) -> String {
    format!("{}: {}", shape.name(), shape.area()) // static dispatch, like a template
}

fn main() {
    let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Square { side: 2.0 }), Box::new(1.5)];
    println!("{} | {}", total_area(&shapes), describe(&Square { side: 3.0 }));
}
```

**The gap:** in C++, the vtable pointer lives inside every object of a polymorphic class, and you choose virtual or non-virtual when you *define* the class. A Rust struct has no vtable pointer at all. The vtable travels with the reference instead: `&dyn Shape` and `Box<dyn Shape>` are **fat pointers**, a data pointer plus a vtable pointer (16 bytes on a 64-bit target). Three things follow:

- The same type works with static dispatch (`impl Shape`, generics) and dynamic dispatch (`dyn Shape`), and each *use site* picks one.
- You can implement your trait for types you did not write, like `f64` above, as long as either the trait or the type belongs to your crate (the **orphan rule**).
- You never write a virtual destructor: the vtable knows how to drop the concrete type.

What you lose is **implementation inheritance**. Traits cannot hold data members. The replacements:

| C++ pattern | Rust replacement |
|---|---|
| base class with shared data | composition: the struct contains the "base" struct as a field |
| shared behavior in a base class | default methods in the trait |
| interface inheritance (`class B : public A`) | supertraits: `trait Widget: Draw` |
| closed hierarchy with a `type()` switch | an `enum` |
| `dynamic_cast` | rarely needed: an enum, a trait method, or `std::any::Any` |
| upcast `Derived*` to `Base*` | `&dyn Sub` coerces to `&dyn Super` (trait upcasting, stable since Rust 1.86) |

Losing inheritance feels like losing a tool for about a month. After that it feels like losing a source of coupling, which is the argument [First Principles: Software Design](https://alexsavio.github.io/first-principles-software-design) makes from the other direction: coupling determines the blast radius of every change.

## Operators come from traits

Operator overloading is trait implementation, and most of the common cases are one `#[derive]` away.

| C++ | Rust |
|---|---|
| `operator==` | `PartialEq` (plus `Eq` when equality is reflexive) |
| `operator<=>`, `operator<` | `PartialOrd` / `Ord` |
| `std::hash<T>` specialization | `Hash` |
| `operator+`, `operator-`, ... | `Add`, `Sub`, ... in `std::ops` |
| `operator+=` | `AddAssign` |
| `operator[]` | `Index`, `IndexMut` |
| `operator*`, `operator->` on a smart pointer | `Deref`, `DerefMut` |
| `operator<<` to a stream, `std::formatter` | `Display` (and `Debug`) |
| conversion operators, `operator bool` | `From` / `Into`, or a named method |
| C++20 defaulted comparisons | `#[derive(PartialEq, Eq, PartialOrd, Ord, Hash)]` |
| `operator=`, `operator&&`, `operator||`, `operator,` | cannot be overloaded |

```rust
use std::collections::HashSet;
use std::fmt;
use std::ops::Add;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
struct Money {
    cents: i64,
}

impl Add for Money {
    type Output = Money;
    fn add(self, rhs: Money) -> Money {
        Money { cents: self.cents + rhs.cents }
    }
}

impl fmt::Display for Money {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "${}.{:02}", self.cents / 100, self.cents % 100)
    }
}

fn main() {
    let total = Money { cents: 1050 } + Money { cents: 199 };
    let mut prices = vec![total, Money { cents: 5 }];
    prices.sort(); // derived Ord compares field by field, like a defaulted <=>
    let unique: HashSet<Money> = prices.iter().copied().collect();
    println!("{total} {prices:?} {}", unique.len());
}
```

**The gap:** the split between `PartialEq`/`Eq` and `PartialOrd`/`Ord` is not pedantry. Floating-point numbers have `NaN`, which is not equal to itself, so `f64` is only `PartialOrd`. That makes this a compile error:

```rust
// does not compile: E0277
fn main() {
    let mut v = vec![2.5, f64::NAN, 1.0];
    v.sort(); // error[E0277]: the trait bound `f64: Ord` is not satisfied
}
```

In C++, `std::sort` on a vector that contains `NaN` breaks the strict weak ordering that it requires, which is undefined behavior. In Rust you write `v.sort_by(f64::total_cmp)` and get a total order: a positive `NaN` sorts after infinity, a negative one before minus infinity.

## Errors: from exceptions to `Result`

| C++ | Rust |
|---|---|
| `throw` / `try` / `catch` for expected failures | return `Result<T, E>`, propagate with `?` |
| `std::expected<T, E>` (C++23) | `Result<T, E>` |
| error codes and out-parameters | `Result<T, E>` |
| exception class hierarchy | an error `enum` per module, `From` impls between them |
| `what()` | `impl Display` + `impl std::error::Error` |
| `assert`, `std::abort`, "this cannot happen" | `panic!`, `assert!`, `unreachable!`, `.expect("why")` |
| catch-all at the top of `main` | `fn main() -> Result<(), Box<dyn Error>>` |

C++23's `std::expected` is the closest relative. What C++ lacks is the propagation operator, so every call site repeats the same three lines:

```cpp
#include <charconv>
#include <expected>
#include <string_view>
#include <system_error>

enum class PortError { Empty, NotANumber, OutOfRange };

std::expected<int, PortError> parse_port(std::string_view s) {
    if (s.empty()) return std::unexpected(PortError::Empty);
    int value = 0;
    auto [end, ec] = std::from_chars(s.data(), s.data() + s.size(), value);
    if (ec != std::errc{} || end != s.data() + s.size()) return std::unexpected(PortError::NotANumber);
    if (value < 1 || value > 65535) return std::unexpected(PortError::OutOfRange);
    return value;
}

std::expected<int, PortError> port_sum(std::string_view a, std::string_view b) {
    auto x = parse_port(a);
    if (!x) return std::unexpected(x.error()); // manual propagation
    auto y = parse_port(b);
    if (!y) return std::unexpected(y.error());
    return *x + *y;
}
```

In Rust, `?` returns early on `Err`, and converts the error type through `From` on the way out:

```rust
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
enum PortError {
    Empty,
    NotANumber(ParseIntError),
    OutOfRange(u32),
}

impl fmt::Display for PortError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            PortError::Empty => write!(f, "empty port"),
            PortError::NotANumber(e) => write!(f, "not a number: {e}"),
            PortError::OutOfRange(n) => write!(f, "port {n} out of range"),
        }
    }
}

impl Error for PortError {}

impl From<ParseIntError> for PortError {
    fn from(e: ParseIntError) -> Self {
        PortError::NotANumber(e)
    }
}

fn parse_port(s: &str) -> Result<u16, PortError> {
    if s.is_empty() {
        return Err(PortError::Empty);
    }
    let n: u32 = s.parse()?; // ParseIntError becomes PortError through From
    match u16::try_from(n) {
        Ok(port) if port != 0 => Ok(port),
        _ => Err(PortError::OutOfRange(n)),
    }
}

fn port_sum(a: &str, b: &str) -> Result<u32, PortError> {
    Ok(u32::from(parse_port(a)?) + u32::from(parse_port(b)?))
}

fn main() -> Result<(), Box<dyn Error>> {
    println!("{}", port_sum("8080", "443")?);
    for bad in ["", "http", "70000"] {
        println!("{}", parse_port(bad).unwrap_err());
    }
    Ok(())
}
```

**The gap:** errors are part of the function signature, like checked exceptions, but they are ordinary values: cheap, composable, and visible at every call site as a `?`. Control flow never jumps invisibly out of a function.

**Panics are not exceptions.** They are for bugs, the moral equivalent of a failed `assert`. By default a panic unwinds the stack and runs `Drop` impls, and with `panic = "abort"` in the Cargo profile it aborts, like `-fno-exceptions` plus `std::terminate`. `std::panic::catch_unwind` exists for boundaries such as thread pools and FFI, not for control flow.

The `Display` and `From` boilerplate above is what the [`thiserror`](https://docs.rs/thiserror) crate derives for you in libraries. Applications that only need to report errors often use [`anyhow`](https://docs.rs/anyhow) instead. And every `.unwrap()` is a hidden crash path: fine in tests and prototypes, a code-review question everywhere else.

## Lambdas become closures

| C++ | Rust |
|---|---|
| `[](int x) { return x + 1; }` | `|x: i32| x + 1` |
| `[&]` capture by reference | the default: each variable is captured in the weakest mode the body needs (`&`, `&mut`, or by value) |
| `[=]` or `[x = std::move(x)]` | a `move` closure |
| `mutable` lambda | inferred: the closure becomes `FnMut` |
| `std::function<int(int)>` | `Box<dyn Fn(i32) -> i32>` |
| template parameter `F f` | `f: impl Fn(i32) -> i32` |

Returning a lambda that captures a local by reference is a classic C++ dangling bug:

```cpp
#include <functional>

std::function<int()> make_counter() {
    int count = 0;
    return [&count] { return ++count; }; // `count` dies when the function returns
}
```

The Rust compiler sees the same mistake:

```rust
// does not compile: E0373
fn make_counter() -> impl FnMut() -> u32 {
    let mut count = 0;
    || {
        count += 1;
        count
    } // error[E0373]: closure may outlive the current function, but it borrows `count`
}
```

The fix is `move`, which transfers ownership of `count` into the closure:

```rust
fn make_counter() -> impl FnMut() -> u32 {
    let mut count = 0;
    move || {
        count += 1;
        count
    }
}

fn apply_twice(f: impl Fn(i32) -> i32, x: i32) -> i32 {
    f(f(x))
}

fn main() {
    let mut next = make_counter();
    println!("{} {}", next(), next()); // 1 2
    let offset = 10;
    println!("{}", apply_twice(|x| x + offset, 1)); // 21
    let ops: Vec<Box<dyn Fn(i32) -> i32>> = vec![Box::new(|x| x * 2), Box::new(move |x| x - offset)];
    println!("{:?}", ops.iter().map(|f| f(5)).collect::<Vec<_>>()); // [10, -5]
}
```

**The gap:** three traits encode what C++ leaves to documentation:

- `Fn` can be called many times and only reads its captures.
- `FnMut` can be called many times and mutates its captures, so it needs exclusive access.
- `FnOnce` consumes its captures and can be called once.

The compiler infers the most capable trait for each closure, and each API asks for the least it needs: `Iterator::map` takes an `FnMut`, and `std::thread::spawn` takes an `FnOnce`.

## Iterators instead of index loops and `<algorithm>`

C++20 ranges and Rust iterators are close cousins: lazy adapters, composed into a pipeline, compiled down to a plain loop.

```cpp
#include <numeric>
#include <ranges>
#include <vector>

std::vector<int> v{1, 2, 3, 4, 5, 6};
auto out = v
    | std::views::filter([](int x) { return x % 2 == 0; })
    | std::views::transform([](int x) { return x * x; })
    | std::ranges::to<std::vector>();
int total = std::accumulate(out.begin(), out.end(), 0);
```

```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5, 6];
    let out: Vec<i32> = v.iter().copied().filter(|x| x % 2 == 0).map(|x| x * x).collect();
    let total: i32 = out.iter().sum();
    println!("{out:?} {total}"); // [4, 16, 36] 56

    let parsed: Result<Vec<i32>, _> = ["1", "2", "x"].iter().map(|s| s.parse::<i32>()).collect();
    println!("{parsed:?}"); // Err(ParseIntError { kind: InvalidDigit })
}
```

| C++ | Rust |
|---|---|
| `for (const auto& x : v)` | `v.iter()`, yields `&T` |
| `for (auto& x : v)` | `v.iter_mut()`, yields `&mut T` |
| iterate by value, consuming `v` | `v.into_iter()`, yields `T` |
| `std::transform`, `views::transform` | `.map()` |
| `std::copy_if`, `views::filter` | `.filter()` |
| `std::accumulate`, `ranges::fold_left` | `.fold()`, `.sum()`, `.product()` |
| `std::find_if` | `.find()`, returns `Option` |
| `std::any_of`, `std::all_of` | `.any()`, `.all()` |
| `std::count_if` | `.filter(...).count()` |
| `views::zip`, `views::enumerate` | `.zip()`, `.enumerate()` |
| `views::take`, `views::drop` | `.take()`, `.skip()` |
| `std::ranges::to<std::vector>()` | `.collect::<Vec<_>>()` |
| erase-remove idiom | `.retain()` |
| `std::unique` + `erase` | `.dedup()` |
| `std::sort` | `.sort_unstable()` |
| `std::stable_sort` | `.sort()` |

**The gap:** `collect` builds whatever the type annotation asks for: a `Vec`, a `HashMap` from pairs, a `String` from characters, or, as the last line shows, a `Result<Vec<_>, _>` that stops at the first error.

Iterators are also the idiomatic answer to bounds checks: an iterator never indexes, so there is nothing to check, while `for i in 0..v.len() { v[i] }` checks on every access unless the optimizer can prove it safe. Read an index loop in Rust code review as a small smell.

And watch the names: Rust's `sort` is the **stable** one.

## Cheat sheet

| C++ | Rust |
|---|---|
| `std::move(x)`, moved-from state | plain assignment moves; the source is dead |
| copy constructor | `#[derive(Clone)]`, explicit `.clone()` |
| trivially copyable type | `#[derive(Clone, Copy)]` |
| rule of three/five | not needed; rule of zero via `derive` |
| destructor | `impl Drop` (fields drop in declaration order) |
| `std::lock_guard` and friends | guard types that implement `Drop` (`MutexGuard`) |
| `const T&` / `T&` parameters | `&T` / `&mut T`: many readers XOR one writer |
| iterator invalidation | compile error (E0502) |
| returning a reference to a local | compile error (E0515) |
| `std::unique_ptr<T>` | `Box<T>` |
| `std::shared_ptr<T>` | `Rc<T>` (one thread), `Arc<T>` (many) |
| `std::weak_ptr<T>` | `Weak<T>` |
| `mutable` member | `Cell`, `RefCell`, `OnceCell` |
| exceptions | `Result<T, E>` + `?` |
| `std::expected<T, E>` | `Result<T, E>` |
| `assert` / `std::abort` | `panic!`, `assert!`, `.expect()` |
| `std::variant` + `std::visit` | `enum` + `match` |
| template + concept | generic + trait bound, checked at definition |
| abstract base class | `trait` |
| `virtual` call through `Base*` | `&dyn Trait`, `Box<dyn Trait>` |
| `std::vector<std::unique_ptr<Base>>` | `Vec<Box<dyn Trait>>` |
| non-virtual template polymorphism | `impl Trait`, generics |
| implementation inheritance | composition + default methods + supertraits |
| `operator==`, `<=>`, `std::hash` | `#[derive(PartialEq, Eq, PartialOrd, Ord, Hash)]` |
| `operator+` | `impl Add` |
| `operator<<` | `impl Display` |
| lambda | closure; `move` to take ownership |
| `std::function` | `Box<dyn Fn(...)>` |
| `<algorithm>`, ranges | iterator adapters + `collect` |
| `std::sort` / `std::stable_sort` | `sort_unstable` / `sort` |

## Traps for C++ developers

1. **`let _ = Guard(...)` drops at once.** `_` binds nothing, so a temporary guard dies at the semicolon. With a mutex (Part 3), `let _ = m.lock().unwrap();` unlocks immediately. Bind guards to a name like `_guard`.
2. **Struct fields drop in declaration order**, the reverse of C++ member destruction.
3. **`sort()` is stable.** `sort_unstable()` is the `std::sort` you know.
4. **`f64` is not `Ord`.** Sort floats with `sort_by(f64::total_cmp)`.
5. **`.clone()` to silence the borrow checker** works, and hides the design question the error was asking.
6. **`Rc<RefCell<T>>` everywhere** means the C++ object graph came along unchanged. Consider one owner plus borrows, or an arena.
7. **`Drop` is not guaranteed to run.** Leaks are safe in Rust; never make memory safety depend on a destructor.
8. **`.unwrap()` in library code** is a crash path that callers can only survive with `catch_unwind`, which almost nobody writes. Under `panic = "abort"`, it is a real `std::terminate`.

## What comes next

The first weeks in Rust feel slow for a reason: the compiler asks, up front, every ownership question that C++ lets you postpone until a crash.

None of the answers are new. Single ownership is `std::unique_ptr`, borrowing is `const T&` and `T&` with a rule attached, and RAII, the rule of zero, `std::expected`, concepts, and ranges are already in your toolbox. What changes is that the rules you used to carry in your head, your review checklist, and your sanitizer runs now come back as errors with numbers.

Part 3 is where that investment pays the biggest dividend. With ownership in place, **data races become compile errors**, and the same rules extend to threads, locks, and atomics. It also covers lifetime annotations, compile-time programming, macros, self-referential structures, `unsafe`, FFI, and how teams actually migrate C++ code bases.

---

## References

1. [The Rust Programming Language, ch. 4: Understanding Ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html), moves, borrowing, and slices
2. [The Rust Programming Language, ch. 9: Error Handling](https://doc.rust-lang.org/book/ch09-00-error-handling.html), `Result`, `?`, and panics
3. [The Rust Programming Language, ch. 10: Generic Types, Traits, and Lifetimes](https://doc.rust-lang.org/book/ch10-00-generics.html)
4. [The Rust Programming Language: Using Trait Objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html), `dyn Trait` and dynamic dispatch
5. [The Rust Reference: Destructors](https://doc.rust-lang.org/reference/destructors.html), drop order for variables and fields
6. [std::cell](https://doc.rust-lang.org/std/cell/index.html), `Cell`, `RefCell`, `OnceCell`
7. [std::rc](https://doc.rust-lang.org/std/rc/index.html), `Rc` and `Weak`
8. [std::iter](https://doc.rust-lang.org/std/iter/index.html), iterator adapters and `collect`
9. [Rust 1.86.0 release announcement](https://blog.rust-lang.org/2025/04/03/Rust-1.86.0/), trait upcasting
10. [cppreference: std::move](https://en.cppreference.com/w/cpp/utility/move.html), moved-from standard library objects are "valid but unspecified"
11. [cppreference: std::expected](https://en.cppreference.com/w/cpp/utility/expected.html)
12. [cppreference: std::vector::push_back](https://en.cppreference.com/w/cpp/container/vector/push_back.html), iterator invalidation on reallocation
13. [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), the ownership conventions Rust enforces
14. [C++ to Rust Phrasebook: Rule of three/five/zero](https://cel.cs.brown.edu/crp/idioms/constructors/rule_of_three_five_zero.html), Brown University
15. [C++ to Rust Phrasebook: Inheritance and reuse](https://cel.cs.brown.edu/crp/idioms/data_modeling/inheritance_and_reuse.html), Brown University
16. [Rust Design Patterns: Clone to satisfy the borrow checker](https://rust-unofficial.github.io/patterns/anti_patterns/borrow_clone.html), the anti-pattern
17. [thiserror](https://docs.rs/thiserror) and [anyhow](https://docs.rs/anyhow), error-handling crates
18. [First Principles: Software Design](https://alexsavio.github.io/first-principles-software-design), related post on coupling
