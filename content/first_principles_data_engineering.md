Title: First Principles: Data Engineering and ETLs
Date: 2026-04-08 20:58:00
Category: Engineering
Tags: first-principles, data-engineering, etl, pipelines, polars, rust
Slug: first-principles-data-engineering
Series: First Principles
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: ETL is not a law of nature, it is a convention born from constraints that no longer exist. Strip data engineering down to its irreducible truths and rebuild it from scratch. What emerges is a discipline centered on contracts and observability, not pipelines and orchestrators.
Status: published

## TL;DR

Most of what we call "data engineering" is a set of conventions inherited from an era of expensive compute and scarce storage. When you strip it down to first principles, only five truths survive: producers and consumers operate in different contexts, data must cross boundaries, semantic alignment is unavoidable, computation trades off time against money against complexity, and data without provenance is unreliable. Everything else, from the sacred ETL ordering to the "collect everything" data lake mentality, is implementation detail that should be questioned.

*This is the fourth post in my First Principles series, where I take a concept the industry treats as settled and strip it back to what's provably true. The first one tackled [Software Observability]({filename}/first_principles_software_observability.md), the second [Software Design]({filename}/first_principles_software_design.md), and the third [DevOps]({filename}/first_principles_devops.md). Data engineering is the next natural target, because few disciplines have calcified around tooling as fast as this one.*

---

## The Conventional View

Data engineering is about building **pipelines** that Extract data from sources, Transform it into a usable shape, and Load it into a destination (usually a warehouse). Teams invest heavily in orchestrators like Airflow, maintain complex DAGs, enforce strict schemas, and treat the warehouse as the single source of truth.

The discipline is defined by its tooling and its three-letter acronym.

But is any of that fundamental?

## The Assumptions We Carry

I identified ten assumptions that most practitioners treat as self-evident. Here's how each one fares under scrutiny.

| # | Assumption | Origin | Verdict |
|---|-----------|--------|---------|
| 1 | Data must be extracted, transformed, then loaded, in that order | Mainframe-era batch processing constraints | **Baggage** |
| 2 | You need a centralized data warehouse as the single source of truth | 1990s Kimball/Inmon movement | **Heuristic** |
| 3 | Pipelines should be orchestrated as DAGs with a scheduler | Airflow's popularity + CI/CD analogy | **Heuristic** |
| 4 | Schema should be enforced at write time | RDBMS tradition | **Heuristic** |
| 5 | Data engineers build pipelines; analysts consume them | Org chart convention | **Baggage** |
| 6 | Batch processing is the default; streaming is advanced | Batch was historically cheaper | **Baggage** |
| 7 | Transformations belong in a dedicated processing layer | Vendor-driven categories (Spark, dbt) | **Heuristic** |
| 8 | Raw data should be preserved immutably (bronze/silver/gold) | Lambda architecture + compliance | **Heuristic** |
| 9 | More data is better, collect everything | Big data hype era, cheap storage | **Baggage** |
| 10 | Data quality is a pipeline problem | Analogy to software testing | **Heuristic** |

The classification:

- **Fundamental truth**: survives all tests. Keep it.
- **Useful heuristic**: sometimes true, context-dependent. Worth questioning.
- **Inherited baggage**: convention masquerading as truth. Discard it.

Four of the ten are outright baggage. The rest are heuristics, useful in some contexts but dangerously treated as universal truths.

### When the heuristics break

The six assumptions I classified as heuristics aren't wrong, they're just conditional. Here's when each one stops working:

- **Centralized warehouse as single source of truth** breaks when your producers change faster than your warehouse team can review PRs. It also fails for real-time use cases where the warehouse is always stale by definition.
- **DAG orchestration with a scheduler** breaks when most of your data flows are event-driven or near-real-time. You end up polling for "is the data there yet?" instead of reacting to its arrival.
- **Schema-on-write** breaks when you're exploring a new domain and the schema is genuinely unknown. It also breaks when upstream producers change schemas without coordination (which is always).
- **Dedicated transformation layer** breaks when the people writing dbt models don't understand what the source fields mean. You get syntactically correct SQL that's semantically wrong.
- **Immutable raw data (bronze/silver/gold)** breaks when compliance requires you to *delete* data (GDPR right to erasure), or when storage costs actually matter at scale. "Keep everything forever" is a luxury, not a principle.
- **Data quality as a pipeline problem** breaks because it treats quality as a gate you pass once, not a property that degrades over time. Your data can pass every pipeline test and still be wrong if the source changed its semantics without telling you.

## What Survives Scrutiny

After stripping away heuristics and baggage, five irreducible truths remain.

### 1. Producers and consumers operate in different contexts

The system generating data has different goals, schemas, and timelines than whoever needs to use it. This mismatch is **the** fundamental problem data engineering exists to solve. Without this gap, the entire discipline is unnecessary.

### 2. Data must cross context boundaries

Whether physically copied or virtually federated, the consumer needs access to data they don't own. The mechanism is negotiable. The need is not.

### 3. Semantic alignment is unavoidable

Two systems calling something `customer_id` doesn't mean they refer to the same entity. Reconciliation of **meaning**, not just format, is the hard part. This is why "just dump it in a lake" fails: you've moved bytes across a boundary without bridging the semantic gap.

### 4. Computation trades off time, money, and complexity

You can process data faster (streaming) at higher complexity, or cheaper (batch) with higher latency. This tradeoff is physics, not preference. There is no free lunch.

### 5. Data without provenance is unreliable

You must know where data came from and how recently it reflects reality. Without that, downstream conclusions are untrustworthy. This is epistemological, not technical.

## The Airflow Cargo Cult

Before diving into what falls away, a concrete example of inherited thinking in action.

I've seen teams adopt Apache Airflow as their first infrastructure decision when starting a data project. Not because they analyzed their scheduling needs and concluded that a DAG orchestrator was the right fit, but because "that's what data teams use".

The result is predictable: a handful of simple SQL queries that run once a day, wrapped in Airflow operators, deployed on a Kubernetes cluster, monitored by a dedicated instance. The entire orchestration layer exists to run `cron`-equivalent jobs with 100x the operational overhead. A cron job, a dbt Cloud schedule, or even a simple GitHub Actions workflow would have done the same thing with a fraction of the complexity.

This happens because teams reason from tools instead of from problems. They ask "which orchestrator should we use?" instead of "do we have a coordination problem that requires orchestration?" Often the answer is no. You don't need a DAG scheduler until you have actual dependencies between data flows that require sequencing. Running three independent queries on a timer is not orchestration, it's scheduling.

The same pattern repeats everywhere. Kafka gets adopted for event streaming when a database trigger would suffice. **Spark** and **PySpark** get deployed as distributed compute clusters for datasets that fit in a single PostgreSQL instance, because "we're a big data team". **dbt** gets adopted as "the transformation layer" before anyone asks whether the transformations need a dedicated tool or could just be views in the warehouse. Data lakes get stood up for flexibility when a well-modeled warehouse would have been both simpler and more useful.

The lesson: if your tool choice precedes your problem definition, you're carrying baggage.

## What Falls Away

### "ETL" as the defining paradigm

The three-letter ordering (Extract, Transform, Load) was an artifact of expensive compute. When compute was scarce, you transformed data before loading because you couldn't afford to store or re-process raw data. That constraint is largely gone.

ELT, streaming, reverse ETL, materialized views: these aren't variations on ETL. They're evidence that the paradigm was never fundamental.

### "More data is better"

Driven by the 2010s Hadoop era, when storage became nearly free and FOMO ruled. In practice, data you never use has **negative value**: it costs money to store, creates security and compliance surface area, and generates noise.

The fundamental truth is that *relevant, reliable data* is better. Collection should be driven by known or plausible use cases.

### "Data engineers build, analysts consume"

This is an org chart artifact, not a truth about the work. The fundamental problem is context-crossing, getting data from producer to consumer in a usable form. Who does that work is a staffing decision. The rise of analytics engineering (dbt) already proved that the producer/consumer boundary is arbitrary.

### "Batch is default, streaming is special"

This is a cost artifact, not a fundamental distinction. Batch isn't more "natural". It's just historically cheaper. As streaming infrastructure has matured, the cost gap narrows, and the distinction becomes about choosing your **latency tolerance**, not picking a paradigm.

## Rebuilt From Scratch

Starting from only the five irreducible truths, here's what data engineering looks like designed from zero.

### Start with data contracts, not pipelines

Since the core problem is context mismatch between producers and consumers, the first thing you build isn't a pipeline. It's a **contract**. Producers declare what they emit (schema, semantics, freshness guarantees). Consumers declare what they need. The engineering is in bridging the gap, and the contract makes the gap explicit.

If you're coming from backend engineering, the mental model is simple: **data contracts are OpenAPI for data**. The same way an API contract lets frontend and backend evolve independently as long as both sides honor the spec, a data contract lets producers and consumers evolve independently as long as the agreed-upon schema, semantics, and freshness guarantees hold. Nobody would ship a public API without documenting its shape, yet data teams routinely ship tables with no documented contract at all.

This isn't theoretical. Tools like Andrew Jones' [Data Contract CLI](https://github.com/datacontract/datacontract-cli) let you define contracts in YAML and validate them in CI. Protobuf and JSON Schema work for schema enforcement. The format matters less than the practice of making the producer-consumer agreement explicit and testable.

A contract without a version is just a snapshot. Real contracts need semantic versioning, deprecation windows, and an answer to "what happens when the producer needs to break compatibility?" Skip this and you recreate the schema-on-write failure mode one layer up: every upstream change becomes a silent incident for some consumer who was pinning to yesterday's assumptions. Treat contract evolution with the same discipline you'd apply to a public API: additive changes are safe, breaking changes require a new major version and a migration path.

<pre class="mermaid">
graph LR
    P[Producer] -->|declares| C[Contract]
    C -->|schema + semantics + SLA| M[Mechanism]
    M -->|batch / stream / CDC / API| D[Consumer]
    D -->|declares needs| C
</pre>

### The pipeline is a consequence, not the product

Once you have contracts, the implementation follows: you need some mechanism to get data from A to B while honoring the contract. This might be a batch job, a streaming consumer, a materialized view, a CDC feed, or a simple API call. The mechanism is chosen per-contract based on the latency-cost-complexity tradeoff, not imposed by a global architecture diagram.

### Transform at the boundary, not in a dedicated layer

Transformations exist to reconcile semantic mismatches. They should live as close to the boundary-crossing as possible: either at the producer (who understands the source context) or at the consumer (who understands the target context). A centralized "transformation layer" is an organizational crutch that obscures who owns the meaning.

This is the same argument Zhamak Dehghani made for **data mesh**: push ownership to the domain that understands the data. The first-principles version doesn't require adopting the full data mesh organizational model. It just requires that whoever owns the meaning also owns the transformation that encodes it. The boundary is where semantics get negotiated, and the negotiation should happen between parties who actually understand both sides.

### Observe data, don't just test it

Data quality isn't a test suite problem. It's an **observability** problem. Tests check known failure modes; observation surfaces unknown ones. You need continuous monitoring of distributions, volumes, freshness, and lineage, not just `assert not null`.

This connects directly to [the observability principles]({filename}/first_principles_software_observability.md) I wrote about earlier. In that post, I argued that the "three pillars" (logs, metrics, traces) describe data formats, not observability itself. The same pattern appears here: "ETL" describes a data flow ordering, not data engineering itself. In both cases, vendor categories got mistaken for fundamentals. The fix is the same too: explore instead of monitor, alert on invariants rather than thresholds, and treat quality as a design property rather than an afterthought.

There's a deeper problem, though. Data engineering as a discipline has a **testing gap** that would be unacceptable in software engineering. Most pipeline code has zero unit tests. Transformations that encode critical business logic run without integration tests against realistic data. The entire testing culture amounts to "check if the DAG ran without errors," which tells you nothing about whether the *output* is correct.

Software engineers learned decades ago that "it compiled" is not a quality signal. Data engineers are still treating "the job succeeded" the same way. A dbt model can produce syntactically valid SQL, run without errors, and silently double-count revenue because of a bad join. Without unit tests on transformation logic and integration tests against known-good datasets, you're flying blind and calling it confidence.

Tools like [Great Expectations](https://greatexpectations.io/) and [Soda](https://www.soda.io/) address the observability side, but they're not substitutes for actual test coverage on the transformation code. The industry needs both: tests for known invariants and observation for unknown drift.

### Collect data when you can articulate who will use it

Instead of "ingest everything, schema later," the rebuilt approach: every data source entering the system has a declared consumer and use case. If you can't name one, don't ingest it. You can always add it later. This inverts the "data lake" mentality.

### Make lineage and freshness first-class

Since data without known provenance is unreliable, lineage tracking isn't a nice-to-have dashboard. It's part of the data itself. Every record carries (or can be traced to) its origin, the transformations applied, and when it last reflected reality.

[OpenLineage](https://openlineage.io/) is the emerging standard here, and it's worth adopting for the same reason OpenTelemetry won in observability: vendor-neutral metadata that any tool can emit and any tool can consume. Lineage captured in a proprietary format is lineage you'll lose when you change vendors. Lineage captured in an open standard travels with your data.

## The Tooling Is Catching Up

The incumbent stack tells a story about its era. **Spark** was built for a world where data didn't fit on one machine, so you distributed it across a cluster. **PySpark** made that accessible to Python-native data teams, but at the cost of JVM overhead, serialization penalties, and cluster management complexity that most workloads never needed. **dbt** made SQL transformations testable and version-controlled, which was a genuine leap forward, but it also cemented the idea that transformations are a separate "layer" rather than a boundary responsibility.

All three tools solved real problems. But they solved them with the constraints and assumptions of their time: JVM-based runtimes, Python's GIL, single-threaded execution models, and the assumption that "big data" meant "distributed data".

The **Rust data ecosystem** is quietly rewriting those assumptions.

**Polars** is the most visible example. It processes DataFrames with the same API ergonomics as pandas but runs on a multithreaded Rust engine with zero-copy memory, lazy evaluation, and query optimization. Workloads that required a PySpark cluster can often run faster on a single machine with Polars, because the bottleneck was never data volume: it was runtime inefficiency.

But Polars is just one piece. **DataFusion** provides a query engine that can be embedded in any application, not locked behind a cluster manager. **Arrow** gives a common in-memory columnar format that eliminates serialization overhead between tools. **Delta-rs** brings Delta Lake table management without the JVM dependency. Together, they form a stack where contract validation, schema enforcement, and transformation can happen at native speed, in the same process, with type safety the JVM never offered.

What this means for the first-principles approach:

- **Data contracts become cheaper to enforce.** When schema validation runs at Rust speed instead of PySpark speed, you can validate at every boundary without worrying about performance overhead. Contracts stop being "nice but expensive" and become default.
- **The "you need a cluster" assumption dies faster.** If Polars on a single node outperforms a 10-node Spark cluster for your workload, the entire distributed compute layer was inherited baggage. Vertical scaling wins until it actually doesn't.
- **Transformation and validation merge.** In a Rust-native pipeline, the transformation step and the contract validation step can be the same compiled binary. No orchestrator shuffling data between "validate" and "transform" stages. No serialization penalty between Python and JVM.
- **Testing becomes tractable.** Rust's type system catches entire categories of errors at compile time that PySpark surfaces at runtime (or never). Combined with fast execution, you can run unit and integration tests against your transformation logic in seconds, not minutes. The testing gap in data engineering gets smaller when the tooling makes testing cheap.

This isn't about Rust zealotry. It's about recognizing that the performance characteristics of your tools shape which architectural patterns are practical. When validation is expensive, you do it rarely. When it's cheap, you do it everywhere. The Rust data ecosystem makes the first-principles approach (contracts at every boundary, test everything, observe continuously) not just theoretically correct but practically feasible.

## Smell Test: Are You Carrying Baggage?

Quick diagnostic. If any of these sound familiar, you're optimizing conventions instead of solving problems:

- **Your pipeline has no known consumer.** Someone requested it two years ago, they left the company, and it still runs every night.
- **You chose your orchestrator before defining your data flows.** "We're an Airflow shop" is a statement about identity, not architecture.
- **You chose Kafka before asking about latency needs.** If your consumers check a dashboard once a day, you don't need sub-second event delivery.
- **Your transformation logic has zero unit tests.** You test that the job ran, not that the output is correct. A passing DAG is not a passing test.
- **Your data lake has no access logs.** You're storing "everything" but can't name who queried what in the last 90 days.
- **Your schema changes break consumers without warning.** No contract means every upstream change is a surprise.
- **You have a "data quality" team instead of quality built into every step.** Separating quality from production is like separating "driving safely" from "driving".
- **Your Spark cluster processes datasets that fit in a laptop's RAM.** The tool should match the problem, not the resume.
- **You measure data team success by pipeline count, not consumer outcomes.** "We shipped 40 pipelines this quarter" tells you nothing about whether anyone made a better decision because of them. The output metric is tables; the outcome metric is decisions. Confuse the two and you'll optimize for the wrong thing forever.

## What Changes

| Conventional Thinking | First-Principles Thinking |
|---|---|
| Build pipelines, then document them | Define contracts first, derive pipelines from them |
| Choose batch or streaming as an architecture | Choose latency per data flow based on consumer needs |
| Centralized transformation layer (dbt/Spark) | Transform at the producer-consumer boundary |
| Data lake: store everything, figure it out later | Collect only what has a declared consumer |
| Data quality = pipeline tests | Data quality = continuous observability |
| Data engineer builds, analyst consumes | Anyone who bridges the context gap is doing data engineering |
| Orchestrator (Airflow) is the center of gravity | Contract registry is the center of gravity |

## Implications

**Start your next data project by writing contracts, not DAGs.** Define what producers emit and what consumers need before writing a single line of pipeline code. Tools like Protobuf, JSON Schema, or even a shared spreadsheet work. The format matters less than the practice.

**Audit your existing pipelines.** Ask: "who consumes this and when do they need it?" Any pipeline without a clear answer is a candidate for decommissioning. You'll likely find 20-40% of pipelines serve no active consumer.

**Stop treating streaming as advanced.** For new data flows, evaluate latency needs first. Sometimes batch is the right call, but it should be a conscious decision, not a default.

**Push transformation ownership to semantic owners.** If the marketing team defines what "qualified lead" means, they should own (or at minimum co-own) the transformation that computes it, not a data engineer guessing from a Jira ticket.

**Invest in lineage and freshness metadata as infrastructure.** If you can't programmatically answer "where did this number come from and how old is it?" for any metric in your warehouse, that's a higher priority than building new pipelines.

---

## References

1. First-principles analysis by the author, based on industry experience and reasoning from fundamentals
2. [First Principles: Software Observability]({filename}/first_principles_software_observability.md) - First post in this series, applying the same method to observability
3. [First Principles: Software Design]({filename}/first_principles_software_design.md) - Second post in this series, stripping software design to its irreducible core
4. [First Principles: DevOps]({filename}/first_principles_devops.md) - Third post in this series, questioning the conventions of modern DevOps
5. [Data Contract CLI](https://github.com/datacontract/datacontract-cli) - Open-source tool for defining and validating data contracts
6. [Great Expectations](https://greatexpectations.io/) - Data validation and profiling framework
7. [Soda](https://www.soda.io/) - Data quality monitoring platform
8. [OpenLineage](https://openlineage.io/) - Open standard for lineage metadata collection
9. [Polars](https://pola.rs/) - Fast DataFrame library built on Rust
10. [Apache Arrow DataFusion](https://datafusion.apache.org/) - Embeddable query engine in Rust
11. [Delta-rs](https://github.com/delta-io/delta-rs) - Delta Lake implementation in Rust, no JVM required
12. Zhamak Dehghani, *Data Mesh: Delivering Data-Driven Value at Scale* - Origin of the domain-ownership argument applied to data
