Title: C++ to Rust, Part 1: The Everyday Vocabulary
Date: 2026-10-19 00:00:00
Category: Engineering
Tags: rust, cpp, programming-languages, tutorial, memory-safety
Slug: cpp-to-rust-part-1-basics
Series: C++ to Rust
Series_index: 1
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: A phrasebook for C++ developers moving to Rust, part 1 of 3. Types, variables, overflow, control flow, functions, strings, containers, structs, enums, and null, each mapped from the C++ idiom you know to the Rust idiom you want, with the traps that a pure syntax swap hides.
Status: published
scratch: ['cpp_to_rust_research_landscape', 'cpp_to_rust_research_versions']

## TL;DR

Most everyday C++ has a direct Rust counterpart, but the translation is rarely one keyword for another. What changes is the **defaults**. C++ allows almost everything and makes safety opt-in: `const`, `explicit`, `-Wall`, sanitizers. Rust forbids almost everything and makes permission opt-in: `mut`, `as`, `pub`, `unsafe`. So code that looks the same often behaves differently, and the biggest takeaway is to translate the intent, not the syntax.

[TOC]

## What this series is, and what it is not

This is not a "rewrite it in Rust" sermon, and it is not a language reference. It is a phrasebook, ordered as a learning path, for people who already write C++ for a living:

- **Part 1 (this post)**: the everyday vocabulary. Types, variables, control flow, functions, strings, containers, structs, enums, and null.
- **Part 2**: ownership and abstraction. Moves, RAII, borrowing, smart pointers, sum types, templates, traits, operators, errors, closures, and iterators.
- **Part 3**: the advanced material. Threads and locks, lifetimes, compile-time programming, macros, self-referential data, `unsafe`, FFI, and how teams migrate real C++ code bases.

Each section shows a C++ snippet, the idiomatic Rust, and the **semantic gap** between them. Syntax is the easy part. The gap is where the bugs and the surprises live.

Every snippet in the series was compiled with **rustc 1.99 (edition 2024)** and **Apple clang 21 with `-std=c++23`**. Each snippet carries the `#include` lines or `use` imports it needs. A Rust snippet whose first line is `// does not compile` is there to fail, and it fails with the error code it names.

Two free resources cover similar ground and make good companions: Brown University's [C++ to Rust Phrasebook](https://cel.cs.brown.edu/crp/), a lookup table organized by C++ concept, and Google's [Comprehensive Rust](https://google.github.io/comprehensive-rust/), a multi-day course.

This series differs from both in three ways:

- It is ordered as a learning path.
- Every snippet is compile-checked on a named toolchain.
- It ends with how to migrate a real code base.

## The one big shift: the defaults flip

Rust and C++ share more than either community likes to admit:

- zero-cost abstractions
- no garbage collector
- RAII
- generics compiled by monomorphization (one copy of the code per concrete type, as with templates)
- the same memory model for atomics

The real difference is not what you *can* do. It is what happens when you say nothing.

| When you write nothing... | C++ | Rust |
|---|---|---|
| Mutability | mutable | immutable (`mut` opts in) |
| Visibility | `struct` public, `class` private | private to the module (`pub` opts in) |
| Numeric conversions | implicit, narrowing included | none (`as`, `From`, `TryFrom`) |
| Assigning a non-trivial type | copies | moves |
| Reading an uninitialized local | undefined behavior | compile error |
| Pointers | can be null, and the type does not say so | references are never null; `Option<&T>` opts in |
| Signed integer overflow | undefined behavior | panics in debug builds |
| Out-of-bounds index | undefined behavior | panics |
| `switch` / `match` | falls through, may be incomplete | no fallthrough, must be exhaustive |
| Dangerous operations | allowed anywhere | only inside `unsafe` |

C++ hands you a workshop with every power tool plugged in, plus a thick safety manual. Rust hands you the same workshop with the tools locked in a cabinet, and each key you take out goes on a sign-out sheet. You can still do dangerous things in Rust. You just have to say so in writing, in a place a reviewer can `grep` for.

C++26, technically complete since March 2026, softens two rows of the C++ column:

- Reading an uninitialized local becomes **erroneous behavior** (a defined but wrong result that tools may diagnose) instead of undefined behavior.
- A **hardened standard library** can trap on an out-of-bounds `operator[]`.

Compiler support is still arriving. Both changes turn silent corruption into defined behavior that implementations are encouraged to diagnose or trap, and neither one is a compile error. The rest of the table stands.

Almost every section below is one row of this table.

## Toolchain and project layout

Cargo is the build system, package manager, test runner, documentation generator, and lint driver in one tool. The "which build system, which package manager" decision that starts every C++ project does not exist.

```bash
cargo new inventory       # Cargo.toml + src/main.rs
cargo build --release     # optimized build in target/release
cargo test                # runs every #[test] function, no framework needed
cargo clippy              # lints, the clang-tidy of Rust
cargo fmt                 # formatting, the clang-format of Rust
```

| C++ | Rust |
|---|---|
| Translation unit (`.cpp` + headers) | **Crate**: the whole library or binary is one compilation unit |
| `#include "parser.h"` | `mod parser;` declares a module, `use parser::Token;` imports a name |
| `namespace net { ... }` | `mod net { ... }`, or a file `net.rs` |
| CMake, Meson, Bazel | `Cargo.toml` |
| vcpkg, Conan | crates.io, through `Cargo.toml` `[dependencies]` |
| `-O3` / `-O0 -g` | `--release` / the default `dev` profile |
| GoogleTest, Catch2 | built-in `#[test]` + `cargo test` |
| clang-tidy, clang-format | `cargo clippy`, `cargo fmt` |

**The gap:** there are no headers, so there are no include-order bugs, no forward declarations, and no One Definition Rule violations. Items in a module can refer to each other in any order.

The trade-off is that the crate, not the file, is the unit of compilation, so a big crate behaves like a unity build. Code generation inside one crate already runs in parallel, but parsing and type-checking a crate do not. When builds get slow, split the code into several crates in a **workspace**: they type-check in parallel and rebuild independently.

## Primitive types and conversions

| C++ | Rust | Note |
|---|---|---|
| `int8_t` ... `int64_t` | `i8` ... `i64` | exact match |
| `uint8_t` ... `uint64_t` | `u8` ... `u64` | exact match |
| `int` | `i32` | on every mainstream platform; the standard only promises at least 16 bits |
| `long` | `i64` *or* `i32` | 64-bit on 64-bit Linux and macOS, 32-bit on Windows and 32-bit targets: choose the width you mean |
| `size_t`, `ptrdiff_t` | `usize`, `isize` | lengths and indices are always `usize` |
| `__int128` (extension) | `i128`, `u128` | standard in Rust |
| `float`, `double` | `f32`, `f64` | |
| `bool` | `bool` | no implicit conversion to or from integers |
| `char` (a byte) | `u8` | |
| `char32_t` | `char` | a 4-byte Unicode scalar value, not a byte |

C++ converts between arithmetic types silently, narrowing included. The compiler may warn, but it will not stop you, unless you use brace initialization, where narrowing is an error.

```cpp
#include <cstdint>

int big = 300;
std::uint8_t small = big; // 44, silently
unsigned u = -1;          // 4294967295, silently
double d = 3.9;
int i = d;                // 3, silently
long total = i + small;   // integer promotions do the rest
```

Rust has no implicit numeric conversions at all, not even widening ones. You pick the conversion, and the name of the conversion tells the reader what can go wrong.

```rust
fn main() {
    let big: i32 = 300;
    // let small: u8 = big;          // error[E0308]: mismatched types
    let small = big as u8;           // 44: `as` truncates, and now it says so
    let checked = u8::try_from(big); // Err(TryFromIntError(PosOverflow))
    let wide = i64::from(big);       // From exists only when no value can be lost
    let i = 3.9_f64 as i32;          // 3
    let huge = 1e20_f64 as i32;      // 2147483647: float-to-int `as` saturates
    // let total = i + small;        // error[E0308]: mismatched types, then E0277
    let total = i + i32::from(small);
    println!("{small} {checked:?} {wide} {i} {huge} {total}");
}
```

**The gap:** pick the conversion by what can go wrong:

- Use `From` when the conversion is lossless.
- Use `TryFrom` when it can fail.
- Use `as` only when you mean "truncate".

`as` is the one remaining sharp edge, so Clippy has opt-in `pedantic` lints (`cast_possible_truncation` and friends) to flag it.

One more difference hides in the last cast: a float-to-int conversion that is out of range is undefined behavior in C++, while Rust's `as` saturates to the nearest bound and turns `NaN` into `0`.

## Variables: immutable, inferred, always initialized

| C++ | Rust |
|---|---|
| `const int x = 5;` | `let x = 5;` |
| `int x = 5;` | `let mut x = 5;` |
| `auto x = f();` | `let x = f();` |
| `constexpr std::size_t N = 64;` | `const N: usize = 64;` |
| `int x;` (no initializer) | `let x: i32;` is allowed only if every path assigns it before use |
| global `static int counter;` | `static COUNTER: AtomicUsize` (globals must be thread-safe; Part 3) |

Reading an uninitialized local is a classic C++ bug. This compiles, and it reads garbage when `verbose` is false:

```cpp
int log_level(bool verbose) {
    int level;           // indeterminate value
    if (verbose) level = 2;
    return level;        // undefined behavior when verbose == false
}
```

Rust tracks **definite initialization** on every path:

```rust
// does not compile: E0381
fn log_level(verbose: bool) -> i32 {
    let level: i32;
    if verbose {
        level = 2;
    }
    level // error[E0381]: used binding `level` is possibly-uninitialized
}
```

The idiomatic fix is to stop declaring first and assigning later. In Rust, `if` is an expression, so the value is computed where the variable is born:

```rust
fn log_level(verbose: bool) -> i32 {
    let level = if verbose { 2 } else { 0 };
    level
}
```

Two more differences are worth knowing on day one.

**Shadowing.** Rust lets you declare a new variable with the same name in the same scope. That sounds like a bug factory to C++ ears, but it is the idiomatic way to give a transformed value its natural name, instead of inventing `port_str`, `port_trimmed`, and `port_num`:

```rust
fn main() {
    let port = " 8080\n";
    let port = port.trim();                // &str
    let port: u16 = port.parse().unwrap(); // u16
    println!("{port}");
}
```

**Mutability is deep.** In C++, `const` is part of the type, and it is shallow: a `const` object can hold a pointer to mutable data. That gives you the four-way puzzle of `const T*`, `T* const`, and friends.

In Rust, mutability belongs to the binding and is **inherited** by everything the binding owns. A `let v = vec![1, 2]` cannot be pushed to, its elements cannot be changed, and there is no `const_cast` to get around it. (Part 2 covers the controlled escape hatch, interior mutability.)

## Integer overflow: from undefined to defined

In C++, signed overflow is undefined behavior, so the optimizer is allowed to assume it never happens. Here is a real overflow check that clang 21 at `-O2` compiles to `return false`:

```cpp
bool will_overflow(int x) {
    return x + 1 < x; // "cannot happen", so the compiler deletes the check
}
```

Unsigned arithmetic is the opposite: it is defined to wrap, and a lot of C++ code (hashes, checksums, ring-buffer indices) depends on it.

Rust treats **every** overflow, signed or unsigned, as a bug, but never as undefined behavior. The [Rust Reference](https://doc.rust-lang.org/reference/behavior-not-considered-unsafe.html#integer-overflow) splits the rule by build:

- When debug assertions are on, "implementations must insert dynamic checks that panic on overflow".
- Other builds "may result in panics or silently wrapped values on overflow, at the implementation's discretion", always with two's complement results.

Cargo's defaults are `overflow-checks = true` in the `dev` profile and `false` in `release`.

When you *want* a specific overflow behavior, you name it:

```rust
use std::hint::black_box;

fn main() {
    let a = i32::MAX;
    let b = black_box(1); // hide the value from the compiler's constant checks
    println!("{:?}", a.checked_add(b));     // None
    println!("{}", a.wrapping_add(b));      // -2147483648
    println!("{}", a.saturating_add(b));    // 2147483647
    println!("{:?}", a.overflowing_add(b)); // (-2147483648, true)
    let c = a + b; // panics: debug build, "attempt to add with overflow"
    println!("{c}");
}
```

**The gap:** port a C++ hash function to Rust with plain `+` and `*`, and your debug build panics on the first input. That is not a Rust bug. That is Rust asking you to say "yes, I want wrapping here". Use `wrapping_*` methods or the `std::num::Wrapping<T>` type.

The opposite trap also exists: release builds wrap silently by default. If overflow would be a real bug in production, set `overflow-checks = true` in `[profile.release]` and pay the small cost.

## Everything is an expression

In Rust, `if`, `match`, and plain blocks all produce values. The ternary operator does not exist, because `if` already does its job, and the last expression of a function body is its return value.

The `switch` statement becomes `match`, and `match` must be **exhaustive**. Here is the C++ version. It compiles, with a `-Wswitch` warning (on by default in clang, part of `-Wall` in GCC):

```cpp
enum class Shape { Circle, Square, Triangle };

const char* name(Shape s) {
    switch (s) {
        case Shape::Circle: return "circle";
        case Shape::Square: return "square";
        // Triangle forgotten: a warning at best
    }
    return "unknown";
}
```

The same mistake in Rust is a hard error, not a warning:

```rust
// does not compile: E0004
enum Shape { Circle, Square, Triangle }

fn name(s: Shape) -> &'static str {
    match s {
        Shape::Circle => "circle",
        Shape::Square => "square",
    } // error[E0004]: non-exhaustive patterns: `Shape::Triangle` not covered
}
```

(`&'static str` means "a string slice that lives for the whole program", which is what a string literal is.)

`match` also has no fallthrough, and its patterns do much more than compare constants: alternatives, ranges, guards, and bindings.

```rust
fn classify(status: u16) -> &'static str {
    match status {
        200 | 204 => "ok",
        300..=399 => "redirect",
        s if s >= 500 => "server error",
        _ => "other",
    }
}

fn main() {
    println!("{} {} {}", classify(204), classify(302), classify(503));
}
```

Loops translate almost one to one, with two upgrades: `loop` can return a value through `break`, and labeled breaks replace the `goto` you use to escape nested loops.

| C++ | Rust |
|---|---|
| `for (const auto& x : v)` | `for x in &v` |
| `for (auto& x : v)` | `for x in &mut v` |
| `for (int i = 0; i < n; ++i)` | `for i in 0..n` |
| index + element | `for (i, x) in v.iter().enumerate()` |
| `while (cond)` | `while cond` |
| `for (;;)` / `while (true)` | `loop` |
| `goto found;` out of nested loops | `break 'label`; with a value only from `loop` or a labeled block |

```rust
fn main() {
    let grid = [[1, 2, 3], [4, 5, 6]];
    let found = 'search: {
        for (r, row) in grid.iter().enumerate() {
            for (c, &value) in row.iter().enumerate() {
                if value == 5 {
                    break 'search Some((r, c));
                }
            }
        }
        None
    };
    println!("{found:?}"); // Some((1, 1))
}
```

## Functions: no overloading, no default arguments

Rust has neither function overloading nor default arguments. Both are deliberate. Overload resolution combined with implicit conversions is one of the most complicated parts of the C++ standard, and in Rust a function name always means exactly one function.

```cpp
#include <string>
#include <utility>

struct Conn { std::string host; int port; int timeout_ms; bool tls; };

Conn connect(std::string host, int port = 443, int timeout_ms = 5000, bool tls = true) {
    return {std::move(host), port, timeout_ms, tls};
}

void log(int value);
void log(const std::string& value); // overload by type
```

The Rust replacements, from simplest to most flexible:

1. **Different names** for different things: `log_int`, `log_str`. Or one generic function over a trait (`fn log(value: impl Display)`), which Part 2 covers.
2. **An options struct with `Default`**, plus **struct update syntax** (`..Default::default()`) to override only some fields.
3. **A builder** when construction has rules or many optional parts.

```rust
#[derive(Debug)]
struct ConnectOptions {
    port: u16,
    timeout_ms: u32,
    tls: bool,
}

impl Default for ConnectOptions {
    fn default() -> Self {
        Self { port: 443, timeout_ms: 5000, tls: true }
    }
}

fn connect(host: &str, opts: ConnectOptions) -> String {
    format!("{host}:{} tls={} timeout={}ms", opts.port, opts.tls, opts.timeout_ms)
}

fn main() {
    println!("{}", connect("example.com", ConnectOptions::default()));
    println!(
        "{}",
        connect("localhost", ConnectOptions { port: 8080, tls: false, ..Default::default() })
    );
}
```

The options struct is more typing than `= 443`, but it ages better: the call site names every value it changes, and adding a new option does not break any caller.

To return several values, return a tuple, `fn min_max(v: &[i32]) -> (i32, i32)`, and destructure it with `let (lo, hi) = min_max(&v);`, like C++17 structured bindings.

## Strings: two types and a byte count

| C++ | Rust |
|---|---|
| `std::string` | `String`: owned, growable, always valid UTF-8 |
| `std::string_view`, `const std::string&` | `&str`: a borrowed view into UTF-8 text |
| `const char*` to or from C | `&CStr` / `CString`, only at FFI boundaries |
| `std::to_string(42)` | `42.to_string()`, `format!("{}", 42)` |
| `std::stoi(s)` (throws) | `s.parse::<i32>()` (returns a `Result`) |
| `s.size()` | `s.len()`, in **bytes** |
| `s[i]` | no direct equivalent; see below |
| `s.substr(pos, n)` | `&s[pos..pos + n]`, a byte range that must fall on character boundaries |
| `a + b` | `a + &b` (consumes `a`), or `format!("{a}{b}")` |

Function parameters that only read text should take `&str`, the same advice as "take `std::string_view`" in modern C++. A `&String` converts to `&str` automatically.

A Rust `String` is guaranteed to hold valid UTF-8, where a character can take one to four bytes. So "the i-th character" cannot be both O(1) and correct, and Rust refuses to pretend otherwise:

```rust
// does not compile: E0277
fn main() {
    let s = String::from("naïve");
    let c = s[0]; // error[E0277]: the type `str` cannot be indexed by `{integer}`
}
```

You say what you mean instead: bytes, characters, or a byte range.

```rust
fn main() {
    let s = String::from("naïve");
    println!("{} bytes, {} chars", s.len(), s.chars().count()); // 6 bytes, 5 chars
    println!("{:?}", s.chars().nth(2)); // Some('ï')
    println!("{}", &s[0..2]);           // "na"
    // &s[0..3] would panic: byte 3 is in the middle of 'ï'
    let n: i32 = "42".parse().unwrap();
    println!("{}", n + 1);
}
```

The second difference is lifetime. A `std::string_view` that outlives its string is a dangling pointer, and the compiler will not tell you:

```cpp
#include <print>
#include <string>
#include <string_view>

std::string_view first_word(std::string_view s) {
    return s.substr(0, s.find(' '));
}

int main() {
    auto w = first_word(std::string("hello world")); // the temporary dies at the ';'
    std::println("{}", w);                           // dangling view: undefined behavior
}
```

The same code in Rust does not compile, because the borrow checker knows that `w` points into a temporary:

```rust
// does not compile: E0716
fn first_word(s: &str) -> &str {
    s.split(' ').next().unwrap_or("")
}

fn main() {
    let w = first_word(&String::from("hello world")); // temporary dropped here...
    println!("{w}");                                  // ...while `w` still borrows it
}
```

This is your first look at the borrow checker. Part 2 is mostly about it.

## Containers

| C++ | Rust | Note |
|---|---|---|
| `T[N]`, `std::array<T, N>` | `[T; N]` | a value type, like `std::array` |
| `std::vector<T>` | `Vec<T>` | |
| `std::span<T>`, pointer + length | `&[T]`, `&mut [T]` | a **slice** always carries its length |
| `std::deque<T>` | `VecDeque<T>` | a ring buffer |
| `std::list<T>` | `LinkedList<T>` | rarely the right choice, in either language |
| `std::map<K, V>` | `BTreeMap<K, V>` | ordered; a B-tree, where `std::map` is usually a red-black tree |
| `std::unordered_map<K, V>` | `HashMap<K, V>` | SipHash 1-3 by default: resists HashDoS, slower for small keys |
| `std::set`, `std::unordered_set` | `BTreeSet`, `HashSet` | |
| `std::priority_queue<T>` | `BinaryHeap<T>` | both are max-heaps by default |
| `v.push_back(x)`, `v.emplace_back(args)` | `v.push(x)` | no `emplace`: see below |
| `v[i]` / `v.at(i)` | `v[i]` panics if out of range / `v.get(i)` returns `Option` | `get_unchecked` is the `unsafe` opt-out |

The most important container lesson is that in Rust, **reading never writes**. In C++, `operator[]` on a map inserts a default value when the key is missing, even when all you wanted was to look:

```cpp
#include <map>
#include <print>
#include <string>

std::map<std::string, int> stock{{"apples", 3}};
if (stock["pears"] > 0) { /* ... */ } // inserts "pears" -> 0 as a side effect
std::println("{}", stock.size());     // 2
```

In Rust, indexing a map with a missing key panics, and `get` returns an `Option`. When you want insert-or-update, the **entry API** says so out loud:

```rust
use std::collections::BTreeMap;

fn main() {
    let mut stock = BTreeMap::from([("apples", 3)]);
    // stock["pears"] would panic: indexing never inserts
    let pears = stock.get("pears").copied().unwrap_or(0);
    println!("{pears} {}", stock.len()); // 0 1
    *stock.entry("pears").or_insert(0) += 5;
    println!("{stock:?}"); // {"apples": 3, "pears": 5}
}
```

**The gap:** out-of-bounds access is a panic, not undefined behavior. The bounds checks are cheap and are often optimized out, especially when you iterate instead of indexing, which is the idiomatic style anyway (Part 2).

There is also no `emplace_back`: a Rust move is a plain copy of the bytes that never runs user code, so there is no constructor to forward arguments to. You build the value and `push` it.

## Structs and classes

A C++ class splits into two Rust pieces: a `struct` for the data and an `impl` block for the functions.

```cpp
#include <cstdint>
#include <string>
#include <utility>

class Account {
public:
    explicit Account(std::string owner) : owner_(std::move(owner)), balance_(0) {}
    void deposit(std::int64_t amount) { balance_ += amount; }
    std::int64_t balance() const { return balance_; }
private:
    std::string owner_;
    std::int64_t balance_;
};
```

```rust
pub struct Account {
    owner: String, // private: visible in this module and its child modules
    balance: i64,
}

impl Account {
    pub fn new(owner: String) -> Self {
        Self { owner, balance: 0 }
    }

    pub fn deposit(&mut self, amount: i64) {
        self.balance += amount;
    }

    pub fn balance(&self) -> i64 {
        self.balance
    }
}

fn main() {
    let mut acc = Account::new("ada".to_string());
    acc.deposit(100);
    println!("{} has {}", acc.owner, acc.balance()); // fine: same module
}
```

| C++ | Rust |
|---|---|
| constructor | an ordinary associated function, by convention called `new` |
| overloaded constructors | several named functions: `new`, `with_capacity`, `from_parts` |
| `this->field` | `self.field`, always explicit |
| `const` member function | `&self` |
| non-`const` member function | `&mut self` |
| `&&`-qualified member function | `self`: the method takes ownership and consumes the object |
| `static` member function | an associated function with no `self` |
| `private:` | the default, but private to the **module**, not to the type |
| `friend` | not needed: everything in the same module can see private fields |
| destructor | `impl Drop` (Part 2) |
| inheritance | traits and composition (Part 2) |

**The gap:** a Rust constructor is not special. A struct literal must set every field, so there is no half-built object, no member initialization order puzzle, and no exception escaping from the middle of a constructor.

The price is that "constructor" is now a naming convention, and nothing forces callers to go through `new` except privacy. That is why privacy matters: a type with a private field can only be created inside its own module (or a child module), which is how you protect an invariant.

## Enums: the enum class C++ wanted

A C++ `enum class` maps to a Rust `enum`, with explicit values when you need them:

```rust
#[derive(Debug, Clone, Copy, PartialEq)]
#[repr(u8)]
enum Level {
    Debug = 10,
    Info = 20,
    Warn = 30,
}

fn main() {
    let lvl = Level::Info;
    println!("{:?} = {}", lvl, lvl as u8); // Info = 20
    // let bad = 7 as Level;               // error[E0605]: non-primitive cast
}
```

Casting an enum to an integer is fine. The other way does not compile. In C++, `static_cast<Level>(7)` gives you a value that matches no enumerator, and every `switch` downstream has to deal with it. A Rust enum value is always one of its variants, so integer-to-enum conversions go through a `TryFrom` impl you write, and that impl can fail.

Rust enums can also **carry data**, one payload per variant. That makes them tagged unions, the job `std::variant` does in C++, but built into the language and checked by `match`:

```rust
enum Command {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
}

fn run(cmd: Command) -> String {
    match cmd {
        Command::Quit => "bye".to_string(),
        Command::Move { x, y } => format!("move to {x},{y}"),
        Command::Write(text) => text,
    }
}

fn main() {
    println!("{}", run(Command::Move { x: 1, y: 2 }));
}
```

Data-carrying enums are among the most used features in Rust. Part 2 compares them with `std::variant` and `std::visit` in detail.

## Null: `Option` instead of `nullptr`

A C++ pointer can always be null, and nothing in the type tells the caller whether it might be:

```cpp
#include <string>
#include <vector>

struct User { int id; std::string name; };

const User* find_user(const std::vector<User>& users, int id) {
    for (const auto& u : users)
        if (u.id == id) return &u;
    return nullptr; // the caller must remember to check
}
```

Rust references are never null. "Maybe a value" is a separate type, `Option<T>`, and you cannot reach the value inside without handling the `None` case:

```rust
struct User {
    id: u32,
    name: String,
}

fn find_user(users: &[User], id: u32) -> Option<&User> {
    users.iter().find(|u| u.id == id)
}

fn main() {
    let users = vec![User { id: 1, name: "ada".into() }];
    // find_user(&users, 1).name  // error[E0609]: no field `name` on type `Option<&User>`

    match find_user(&users, 1) {
        Some(u) => println!("found {}", u.name),
        None => println!("no such user"),
    }

    let guest = find_user(&users, 2).map(|u| u.name.as_str()).unwrap_or("guest");
    println!("{guest}");

    let Some(u) = find_user(&users, 1) else {
        return; // let-else: unwrap or leave early
    };
    println!("{}", u.name);
}
```

`|u| u.id == id` is a **closure**, Rust's lambda, and `.iter().find(...)` is the iterator form of `std::find_if`. Part 2 covers both.

This safety costs **zero bytes**. The standard library [guarantees](https://doc.rust-lang.org/std/option/index.html#representation) that `Option<&T>`, `Option<Box<T>>`, and a few others have the same size as the bare pointer, because the compiler uses the forbidden null value to encode `None`.

On this machine, `size_of::<Option<&u64>>()` is 8, the same as a pointer, while `sizeof(std::optional<int*>)` is 16. The type Rust uses to remove null pointers compiles back down to a null pointer.

## References: a first look

C++ references and Rust references look alike. `const T&` becomes `&T`, and `T&` becomes `&mut T`. One difference is visible right away, at the call site:

```cpp
#include <vector>

void scale(std::vector<double>& v, double k) {
    for (auto& x : v) x *= k;
}
// scale(data, 2.0);  -- nothing here says that `data` is modified
```

```rust
fn scale(v: &mut [f64], k: f64) {
    for x in v.iter_mut() {
        *x *= k;
    }
}

fn sum(v: &[f64]) -> f64 {
    v.iter().sum()
}

fn main() {
    let mut data = vec![1.0, 2.0, 3.0];
    scale(&mut data, 2.0); // the call says it: `data` may change here
    println!("{}", sum(&data));
}
```

The deeper difference is one rule, which the compiler checks everywhere: at any moment, a value has **either any number of `&T` readers or exactly one `&mut T` writer**, never both. Add "a reference can never outlive what it points to", and you have the core of the borrow checker.

Part 2 shows how this one rule removes iterator invalidation, dangling references, and a whole family of aliasing bugs, and what to do when it gets in your way.

## Printing and formatting

C++20 `std::format` and C++23 `std::print` use almost the same format-spec mini-language as Rust's `format!` and `println!`, so this section is mostly good news. The `!` marks a **macro**. Macros are how Rust checks the format string against the arguments at compile time, the job that the `consteval` format string does for `std::format` in C++20.

| C++ | Rust |
|---|---|
| `std::println("{} {}", a, b)` | `println!("{} {}", a, b)` or `println!("{a} {b}")` |
| `std::format("{:>8}", s)` | `format!("{:>8}", s)` |
| `std::cerr << ...` | `eprintln!(...)` |
| `operator<<` or a `std::formatter` specialization | `impl Display` (Part 2) |
| a debug dump of a struct | `#[derive(Debug)]` plus `{:?}`, or `{:#?}` for pretty output |

```rust
#[derive(Debug)]
struct Point {
    x: f64,
    y: f64,
}

fn main() {
    let p = Point { x: 3.14159, y: -2.0 };
    let label = "offset";
    println!("{label}: {p:?}");  // offset: Point { x: 3.14159, y: -2.0 }
    println!("[{:>8.2}]", p.x); // [    3.14]
    eprintln!("{p:#?}");        // pretty, multi-line, to stderr
}
```

**The gap:** one trap hides in the "almost". In Rust, `{:.2}` on a float means **two digits after the decimal point**. In C++, `{:.2}` without a type letter uses the general format, where the precision counts **significant digits**: `std::format("{:.2}", 3.14159)` gives `3.1`, and you need `{:.2f}` to get `3.14`. Port a format string without the `f` and your numbers change quietly.

## Cheat sheet

| C++ | Rust |
|---|---|
| `int`, `long`, `size_t` | `i32`, `i64`/`i32` (choose), `usize` |
| implicit conversion | `From` (lossless), `TryFrom` (fallible), `as` (truncating) |
| `const T x = v;` / `T x = v;` | `let x = v;` / `let mut x = v;` |
| `constexpr` value | `const` |
| `auto` | type inference with `let` |
| uninitialized variable | compile error until every path assigns it |
| signed overflow (undefined behavior) | panic in debug, wrap in release; `checked_`, `wrapping_`, `saturating_` |
| unsigned wraparound | `wrapping_*` or `Wrapping<T>` (plain `+` panics in debug) |
| `c ? a : b` | `if c { a } else { b }` |
| `switch` | `match`: exhaustive, no fallthrough, patterns and guards |
| range-for | `for x in &v` / `for x in &mut v` / `for x in v` |
| `goto` out of loops | labeled `break 'outer` |
| overloads | distinct names, or generics with traits |
| default arguments | `Default` + `..Default::default()`, or a builder |
| `std::pair`, structured bindings | tuples, `let (a, b) = ...` |
| `std::string` / `std::string_view` | `String` / `&str` |
| `const char*` | `&CStr`, `CString` (FFI only) |
| `std::stoi` | `s.parse::<i32>()` |
| `std::array` / `std::vector` / `std::span` | `[T; N]` / `Vec<T>` / `&[T]` |
| `std::map` / `std::unordered_map` | `BTreeMap` / `HashMap` |
| `m[k]` (inserts) | `m.get(&k)` (reads), `m.entry(k).or_insert(v)` (writes) |
| `v.at(i)` | `v[i]` (panics) or `v.get(i)` (`Option`) |
| `class` with constructor | `struct` + `impl` + `fn new` |
| `const` / non-`const` method | `&self` / `&mut self` |
| `private:` + `friend` | module privacy, `pub` |
| `enum class` | `enum` (`#[repr(u8)]` for a fixed layout) |
| `std::variant` | `enum` with data |
| `T*` that can be null, `std::optional<T>` | `Option<&T>`, `Option<T>` |
| `const T&` / `T&` | `&T` / `&mut T` (explicit at the call site) |
| `std::println`, `std::format` | `println!`, `format!` |
| `operator<<` for printing | `impl Display`, `#[derive(Debug)]` |

## Traps for C++ developers

1. **Unsigned arithmetic panics in debug builds.** Hashes and checksums need `wrapping_*`.
2. **Release builds wrap on overflow by default.** Turn on `overflow-checks` in release if overflow would be a real bug.
3. **`as` truncates silently.** Prefer `From` and `TryFrom`.
4. **`s.len()` counts bytes**, and string slices panic if a range cuts a character in half.
5. **Map indexing never inserts.** It panics on a missing key. Use `get` to read and `entry` to write.
6. **`{:.2}` means decimals in Rust** and significant digits in C++ (without `f`).
7. **Privacy is per module.** Code in the same module, and in its child modules, can see private fields.
8. **Immutability is deep.** There is no `const_cast`; Part 2 shows the legal escape hatch.

## What comes next

The syntax swap takes an afternoon. The defaults take longer, because each one removes something your C++ habits relied on: the implicit conversion, the uninitialized variable, the overflow that "never happens", the null that is "always checked".

In your first weeks, read every Rust compile error as a C++ assumption that someone finally wrote down. Most of the time the assumption was fine. Sometimes it was a bug that had been waiting in your C++ code all along, and in Rust it stops the build instead of reaching production.

Part 2 takes on the biggest default flip of all: **ownership**. It covers moves without moved-from objects, RAII with `Drop`, the borrow checker in depth, smart pointers, errors without exceptions, and how templates and virtual functions become generics and traits.

---

## References

1. [The Rust Programming Language](https://doc.rust-lang.org/book/), the official book
2. [The Rust Reference: Integer overflow](https://doc.rust-lang.org/reference/behavior-not-considered-unsafe.html#integer-overflow), overflow rules quoted above
3. [Cargo Book: Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html), default `overflow-checks` per profile
4. [std::option: Representation](https://doc.rust-lang.org/std/option/index.html#representation), the null pointer optimization guarantee
5. [std::collections::HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html), default hasher (SipHash 1-3) and HashDoS resistance
6. [std::fmt](https://doc.rust-lang.org/std/fmt/), Rust format syntax
7. [cppreference: Arithmetic operators, overflows](https://en.cppreference.com/w/cpp/language/operator_arithmetic.html#Overflows), signed overflow is undefined behavior
8. [cppreference: std::map::operator[]](https://en.cppreference.com/w/cpp/container/map/operator_at.html), inserts when the key is missing
9. [cppreference: Standard format specification](https://en.cppreference.com/w/cpp/utility/format/spec.html), precision with and without a type letter
10. [C++ to Rust Phrasebook](https://cel.cs.brown.edu/crp/), Brown University, a good companion to this series
11. [Comprehensive Rust](https://google.github.io/comprehensive-rust/), Google's free Rust course
12. [Clippy lints](https://rust-lang.github.io/rust-clippy/master/index.html), including `cast_possible_truncation`
13. [Herb Sutter: C++26 is done! Trip report, March 2026](https://herbsutter.com/2026/03/29/c26-is-done-trip-report-march-2026-iso-c-standards-meeting-london-croydon-uk/), C++26 status, erroneous behavior, and library hardening
14. [cppreference: C++26 compiler support](https://en.cppreference.com/w/cpp/compiler_support/26.html), which compilers ship which C++26 features
