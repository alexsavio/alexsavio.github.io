Title: I Built a Full Trading Bot in 16 Days With AI: Here Is What Actually Happened
Date: 2026-03-22
Category: Engineering
Tags: ai, agents, claude-code, rust, trading, code-generation
Slug: building-a-trading-bot-in-16-days-with-ai
Author: Alexandre M. Savio
Summary: From zero to a 225-commit Rust trading platform in 16 days — the real story of building begiravela with AI coding agents, including a database crisis that forced a full migration mid-sprint.
Status: draft

## TL;DR

I built **begiravela** — a fully automated trading platform in Rust — in 16 calendar days, producing 225 commits across three crates, eleven Grafana dashboards, a Telegram bot with 26 commands, and integrations with both Interactive Brokers and Kraken. The project was built almost entirely with AI coding agents (Claude Code + Specify). The most interesting part was not the speed — it was what went wrong. A database corruption bug in QuestDB forced a complete persistence layer swap on Day 11, and the AI handled the migration cleanly. This post is the honest account of what worked, what broke, and what I learned.

## The Setup

I have been trading for years and wanted a system that would do three things: ingest market data on a schedule, compute a deep stack of technical indicators, and alert me via Telegram when something interesting happens — with the option to execute trades directly from the chat. Nothing off-the-shelf did exactly what I wanted without vendor lock-in or monthly fees.

I chose **Rust** because financial calculations need precision (no floating-point rounding errors), the type system catches bugs at compile time, and I wanted the system to run reliably on a single VPS without babysitting.

The stack:
- **Rust** (edition 2024) with `tokio` for async
- **Interactive Brokers** TWS API via the `ibapi` crate
- **Kraken** REST + WebSocket v2 API (custom HMAC-SHA256 implementation)
- **PostgreSQL 17** via `sqlx` (more on why later)
- **Telegram** via `teloxide` for the user interface
- **Grafana** for dashboards and alerting
- **Vector + Loki** for structured log aggregation
- **Docker Compose** for the full deployment

## The Timeline

### Days 1-3: The Big Bang

I started from a [Specify](https://github.com/github/spec-kit) template, which scaffolded the initial project structure and plan. The first real commit on Day 2 was enormous — the full Rust workspace with three crates (`shared`, `ingester`, `telegram-bot`), QuestDB as the timeseries database, Grafana provisioning, Docker Compose, GitHub Actions CI, and a working Telegram bot.

Then came reality. Seven consecutive CI fix commits across two days: coverage thresholds wrong, container health checks failing, `wget` vs `curl` in Alpine containers, `tarpaulin` flags incompatible with the test setup. CI is where ambition meets the filesystem.

### Days 4-6: Making It Actually Useful

This phase was about turning a "it compiles" prototype into something that generates value:

- **Grafana dashboards** — eight provisioned dashboards covering market watch, trading overview, trend analysis, pipeline health, alerts, and portfolio tracking
- **Scheduled ingestion** — three cron schedules (daily, hourly at 15-min intervals, and independent indicator refresh)
- **Catch-up backfill** — on startup, the ingester detects missing data and backfills automatically
- **Per-bar indicator history** — storing the full time series of computed indicators, not just the latest snapshot

The indicator stack grew rapidly:

| Indicator | What It Does |
|---|---|
| RSI-14 | Wilder-smoothed momentum oscillator |
| MACD (12/26/9) | Trend momentum via EMA crossover |
| ADR-14 | EMA-smoothed average daily range |
| LL/MM Trend | Dual-EMA with ATR noise filter (Bull/Bear/Neutral) |
| Pivot Detection | Swing highs/lows by surrounding-bar comparison |
| S/R Clustering | ATR-based zone merging from detected pivots |
| Floor/Camarilla/Fibonacci Pivots | Classic price level systems |
| Fibonacci Retracement & Extension | Key retracement and extension levels |
| ADR Projection | Upper/lower targets from daily open |
| Standard Deviation Zones | 1/2/3-sigma bands |
| Market Phase | Impulse/Corrective/Reversal detection |
| Psychological Levels | Round number price levels |

All computed across four timeframes: Hour, Day, Week, and BiWeek.

### Days 7-8: Production Hardening

The system worked but was fragile. This phase added:

- **Full-history indicator computation** — computing indicators across the entire bar history, not just the latest bar
- **Exponential backoff retry** — broker connections fail; the system recovers gracefully
- **Pipeline failure alerts** — if the ingestion pipeline crashes, Grafana fires a Telegram alert
- **Hot-reload configuration** — TOML config watched via `notify` + `ArcSwap`, swapped atomically with zero downtime
- **Security hardening** — Docker ports bound to localhost only

One commit in this phase contained 30 fixes from a single code review pass. The AI generated a lot of code quickly in the first phase; the hardening phase was about going back and applying the lessons.

### Days 9-11: The QuestDB Crisis

This is where it gets interesting.

I originally chose **QuestDB** as the timeseries database — it seemed like a natural fit. ILP (InfluxDB Line Protocol) for fast writes, PostgreSQL wire protocol for reads, built-in deduplication. In theory, perfect.

In practice, the problems escalated day by day:

```
Day 4:   fix(grafana): use QuestDB LATEST ON syntax in watchlist queries
Day 6:   fix(docker): pin QuestDB to existing tag 9.3.3
Day 8:   fix(grafana): fix alerts dashboard QuestDB compatibility
Day 10:  fix(db): shorten PG pool lifetime to 60s to prevent stale connections
Day 10:  fix(db): harden PG pool against QuestDB stale connection errors
Day 10:  fix(db): correct QuestDB PG wire timeout from 600ms to 600s
Day 10:  fix(grafana): switch to native QuestDB datasource plugin and fix all dashboards
```

Every day brought a new compatibility issue. `LATEST ON` instead of standard SQL. Stale connections requiring pool lifetime hacks. WAL race conditions between ILP writes and PG reads. Custom Grafana datasource plugins because the standard PostgreSQL datasource could not handle QuestDB's SQL dialect.

Then came the kill shot. QuestDB 9.3.3 has a bug where ILP writes with `DEDUP UPSERT` corrupt in-memory partition file descriptors. All subsequent reads fail until you restart the server. At my scale (5 symbols, ~6500 rows), this was unacceptable.

On Day 11, I ripped out QuestDB entirely and migrated to **PostgreSQL 17**. The commit message tells the story:

> *QuestDB 9.3.3 has a critical bug where ILP writes with DEDUP UPSERT corrupt in-memory partition file descriptors, making all subsequent reads fail until the server is restarted. At our scale, PostgreSQL eliminates this bug and gives us standard SQL, proper transactions, and native sqlx type bindings.*

The migration touched 15 test files, rewrote all 8 writer functions, replaced `LATEST ON` with `DISTINCT ON`, and removed the `questdb-rs` dependency entirely. The codebase actually got simpler. Standard SQL is a feature.

### Days 11-12: The Strategy Engine

With a stable database layer, I built the most ambitious piece: a **configurable strategy resolution engine**. When an alert fires, the system:

1. Filters strategy definitions matching the alert rule
2. Applies market phase and timeframe guards
3. Resolves entry tranches at Fibonacci/pivot levels nearest to current price
4. Computes exit levels (targets and stops)
5. Sizes positions by risk percentage of portfolio value
6. Scores confluence — how many technical factors align
7. Returns plans sorted by confluence descending

This is where the Telegram bot becomes a trading desk. `/buy` and `/sell` commands execute trades directly through IBKR, with a confirmation dialogue in live mode.

### Days 13-14: Order Lifecycle & Operational Commands

With strategies generating plans, the next step was making those plans executable end-to-end. This phase turned the bot from an alerting system into a full position management tool:

- **Strategy instance state machine** — each strategy plan becomes a tracked instance that moves through Pending → Active → Filled → Closed states
- **Order lifecycle monitoring** — the system tracks every order from submission through fill, with automatic status updates
- **Scale-in / scale-out commands** — `/scale_in` and `/scale_out` let me adjust position sizes on the fly without cancelling the whole strategy
- **Recovery re-entry detection** — if price revisits an entry level after a stop-out, the system detects the setup and re-arms
- **Advanced order types** — Kraken bracket orders (entry + stop-loss + take-profit) submitted atomically
- **Operational commands** — `/pause` and `/resume` for suspending entry orders, `/abort` for emergency teardown, `/config` for verifying hot-reloaded settings

The schema was also consolidated in this phase — the migration machinery was removed in favor of a single DDL file, since PostgreSQL's `CREATE TABLE IF NOT EXISTS` handles idempotency cleanly.

### Days 15-16: Observability & Market Context

The system was functionally complete but operationally blind. This phase added two things: the ability to see what the system is doing, and the ability to factor in macro context.

**Observability:**

- **Vector → Loki → Grafana** log pipeline — structured logs from all containers flow through Vector, get stored in Loki, and are queryable in Grafana
- **Unified structured event model** — every decision point (alert evaluation, strategy resolution, order submission) emits a structured event with sampling to control volume
- **Strategy logging** — a `strategy_log` table records every resolution attempt, making it possible to replay why a strategy fired or was suppressed
- **Kraken WebSocket v2** — real-time fill detection via the executions channel, replacing polling

**Market context:**

- **VIX volatility regime** — the pipeline now fetches VIX data and classifies the regime (Low/Normal/Elevated/High/Extreme), adding it to alert messages so I can adjust risk appetite
- **Year-anchor reference levels** — year-open prices for major indices and commodities, with alerts when price crosses into correction or recovery zones relative to the yearly open
- **Relationship-based alerts** — replaced static threshold alerts with dynamic ones that fire based on relationships between indicators (e.g., RSI crossing a level while trend is bearish)

## What the AI Did Well

**Speed of scaffolding**. Going from zero to a compiled, tested, deployed Rust workspace in one commit is something that would have taken me a week manually. The AI generated the domain types, database schema, Docker Compose topology, CI pipeline, and Telegram command handlers all in one shot.

**The QuestDB migration**. This was the most impressive moment. I described the problem, and the AI produced a clean migration: standard SQL replacements, updated all 8 Grafana dashboards, rewrote the persistence layer, and updated 15 test files. No regressions.

**Technical depth**. Implementing Newton's method for `Decimal` square roots (needed for standard deviation on `rust_decimal` values), HMAC-SHA256 signing for Kraken's API, ATR-based zone merging for support/resistance clustering — these are non-trivial algorithms that the AI implemented correctly.

## What Required Human Judgment

**The decision to leave QuestDB**. The AI could fix each individual symptom — the stale connections, the SQL compatibility, the WAL races. But the judgment call to abandon QuestDB entirely rather than keep patching came from me. Pattern recognition across a week of escalating issues is still a human skill.

**Architecture choices**. Three crates vs. a monolith. Hot-reload config vs. restart-on-change. Cron scheduling vs. continuous polling. The AI proposed options; I made the calls.

**Trading domain knowledge**. Which indicators matter, how to combine them into a confluence score, what constitutes a valid entry signal — this is domain expertise that the AI implemented but did not originate.

## The Numbers

| Metric | Value |
|---|---|
| Calendar days | 16 |
| Total commits | 225 |
| Rust crates | 3 |
| Grafana dashboards | 11 |
| Technical indicators | 16+ |
| Timeframes | 4 (Hour, Day, Week, BiWeek) |
| Broker integrations | 2 (IBKR, Kraken) |
| Telegram commands | 26 |
| Database migrations | 1 (QuestDB to PostgreSQL) |
| CI pipeline stages | 7 |

## Lessons Learned

**Start with boring technology**. QuestDB was the "right" choice for a timeseries use case. PostgreSQL was the right choice for a 5-symbol personal trading system. Know your scale.

**AI accelerates the build, not the design**. The hard problems — architecture, technology selection, domain modeling — still require human judgment. The AI makes execution nearly free, which shifts the bottleneck to thinking clearly about what to build.

**CI fixes are half the battle**. A significant chunk of commits were CI/infrastructure fixes — coverage thresholds, container health checks, build ordering to avoid OOM. This ratio is probably universal.

**Hot-reload everything you can**. Being able to tune indicator parameters and alert thresholds without restarting the system is a massive quality-of-life improvement. `ArcSwap` + `notify` in Rust makes this surprisingly clean.

**Test with real databases**. The `testcontainers` crate lets you spin up a real PostgreSQL instance in tests. Mocking the database is how you end up with tests that pass and code that does not work.

**Observability is not optional**. Adding Vector → Loki → Grafana on Day 15 immediately surfaced issues that had been invisible — silent failures in order monitoring, duplicate bar writes, strategy resolutions that fired but were suppressed. You cannot debug a trading system by reading logs on a terminal.

---

## References

1. [Specify (GitHub Spec-Kit)](https://github.com/github/spec-kit) — Project scaffolding template
2. [ibapi crate](https://crates.io/crates/ibapi) — Rust client for Interactive Brokers TWS API
3. [teloxide](https://crates.io/crates/teloxide) — Telegram bot framework for Rust
4. [rust_decimal](https://crates.io/crates/rust_decimal) — Arbitrary precision decimal type
5. [testcontainers](https://crates.io/crates/testcontainers) — Container-based test infrastructure
6. [QuestDB](https://questdb.com/) — Time-series database (the one we migrated away from)
7. [Vector](https://vector.dev/) — Log aggregation pipeline
8. [Loki](https://grafana.com/oss/loki/) — Log storage and querying
