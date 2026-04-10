Title: First Principles: Distributed Systems (Most of Yours Should Not Exist)
Date: 2026-04-09 18:00:00
Category: Software Development
Tags: distributed-systems, first-principles, software-engineering, architecture, backend, scalability
Slug: first-principles-distributed-systems
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Distributed systems thinking is drowning in inherited wisdom — microservices by default, horizontal scaling as a reflex, eventual consistency as a catchphrase. Strip it down to six irreducible truths and most of that architectural baggage falls away. The uncomfortable conclusion: the first, cheapest, most reliable distributed system is the one you did not build.
Status: published

## TL;DR

Distributed systems thinking is drowning in inherited wisdom: microservices by default, horizontal scaling as a reflex, eventual consistency as a catchphrase. Strip the topic down to its irreducible truths, the six things that are actually provable, and most of that architectural baggage falls away. The uncomfortable conclusion: the first, cheapest, most reliable distributed system is the one you did not build. Everything else is a tax you should only pay when you can prove it buys you something.

*This is the fifth post in my First Principles series, where I take a concept the industry treats as settled and strip it back to what's actually provable. Previous entries: [Software Observability]({filename}/first_principles_software_observability.md), [Software Design]({filename}/first_principles_software_design.md), [DevOps]({filename}/first_principles_devops.md), and [Data Engineering]({filename}/first_principles_data_engineering.md). Distributed systems felt like the right next target because few topics have a wider gap between what engineers repeat and what they've actually measured.*

---

## The Conventional View

Ask any backend engineer how to scale a system and the answer comes out reflexively: split the work across nodes, replicate for reliability, reach for consensus when you need agreement, accept that complexity is the price of scale. *"You need a distributed system"* has quietly become the default answer for any non-trivial backend. Microservices are "modern". A monolith is "legacy". Kubernetes is table stakes.

This post is not about how to build a better service mesh. It is about whether you should be building one at all, and what distributed systems look like when you stop copying the architecture of a company 1,000× your size and reason forward from the things that are actually true.

## What People Just Assume

Before you can tear something down, you have to name the inherited thinking. Here are the beliefs most engineers carry into distributed systems without ever having checked them:

| #  | Assumption                                                   | Where it came from                  | Verdict                |
|----|--------------------------------------------------------------|-------------------------------------|------------------------|
| 1  | You need a distributed system to scale                      | SaaS-era orthodoxy, FAANG blog posts | Baggage                |
| 2  | Microservices are the modern way                            | Netflix and Uber conference talks    | Baggage                |
| 3  | The network is reliable most of the time                    | LAN intuition, local dev            | Baggage (Fallacy #1)   |
| 4  | Latency between services is negligible                      | Same-datacenter hand-waving         | Baggage (Fallacy #2)   |
| 5  | Consensus protocols are required for correctness           | Coursework memory                   | Heuristic              |
| 6  | CAP forces a binary CP vs AP choice                          | Pop-sci reading of Brewer           | Heuristic              |
| 7  | Eventually consistent is good enough                        | DynamoDB and Cassandra marketing    | Heuristic              |
| 8  | More nodes equals more reliability                          | Replication intuition               | Heuristic (often inverted) |
| 9  | Clocks across machines can be trusted with some slop        | NTP familiarity                     | Baggage (Fallacy #6)   |
| 10 | Partial failure is an edge case                             | Single-machine mental model         | Baggage                |

The point of that table is not contrarianism. It is compression. Most of what engineers treat as "distributed systems knowledge" is a mix of convention dressed up as constraint and heuristics borrowed from companies operating at a scale you do not have.

## What Actually Survives Scrutiny

Six things remain once you strip the heuristics and the baggage. These are irreducible, true regardless of era, stack, or cloud provider.

**1. The network is not a reliable communication medium.** Packets are dropped, reordered, duplicated, and delayed. This is a property of shared infrastructure and the speed of light, not a bug you can engineer around. Every message you send may or may not arrive, may arrive late, and may arrive more than once.

**2. You cannot distinguish a crashed node from a slow one.** This is the famous FLP impossibility result in plain clothes. No timeout is "correct". You are always choosing between declaring live nodes dead (false positive) and waiting forever on dead ones (false negative).

**3. There is no global now.** Independent clocks drift. NTP bounds the drift but does not eliminate it. Two events on two machines cannot be totally ordered without a protocol, and every protocol costs round trips.

**4. Every coordination step costs at least one round trip.** Round trips do not compose. They add up linearly in your latency budget and explode non-linearly under failure.

**5. Failure modes multiply, they do not add.** One machine at 99.9% uptime is straightforward. *N* machines each at 99.9% uptime gives you a failure probability that approaches certainty as *N* grows. Redundancy only helps if the failures are genuinely independent and the coordination layer is not itself the bottleneck.

**6. State is the hard part, compute is trivial.** Moving code across nodes is easy: it is just bytes. Moving or sharing state is where every hard problem lives: consistency, ordering, replication, recovery.

That is the whole bedrock. Six statements. Notice what is *not* on the list: microservices, Kubernetes, consensus, eventual consistency, horizontal scaling. None of those are fundamental. They are tools, patterns, or rebrandings of organizational choices.

## What Falls Away

Once you stop at "only what is provably true", the conventional architecture advice starts looking suspicious.

- **"You need a distributed system to scale."** A modern single machine has 128+ cores, terabytes of RAM, and NVMe pushing millions of IOPS. A well-written monolith on one big box handles workloads that teams reflexively shard across Kubernetes clusters. The assumption persisted because cloud vendors sell horizontal, not vertical, and because it justified résumé-driven architecture.

- **"Microservices are the modern way."** Microservices were an *organisational* answer to having thousands of engineers at Netflix and Amazon, and the answer got rebranded as a *technical* pattern. For teams of 5 to 50, you trade a tractable problem (one codebase) for an intractable one (*N* codebases communicating over an unreliable network).

- **"Partial failure is an edge case."** In a real distributed system, something is always failing. It is steady state, not exception. The assumption persists because single-machine intuition treats "up" and "down" as binary. Distributed systems do not.

- **"More nodes equals more reliability."** Only if the nodes fail independently *and* the coordination layer is itself more reliable than a single node. In practice, adding nodes often *decreases* reliability because the blast radius of a bad deploy, a misconfigured network policy, or a coordination bug grows with *N*.

- **"CAP forces a binary choice."** CAP describes what happens *during a partition*. Most systems are not partitioned most of the time. The real tradeoff every day is latency vs. consistency (PACELC), and blast-radius vs. coordination cost.

## Rebuilt From Scratch

If you only started from the six truths and never heard of Kubernetes, this is what you would design.

**Default to one machine.** The cheapest, fastest, most reliable distributed system is the one you did not build. Scale vertically until the machine itself is the bottleneck, not until your conference talk demands horizontal scaling. A single node has zero coordination cost, zero network unreliability, one clock, and trivially consistent state.

And "one machine" in 2026 is not what it was in 2012. An AWS `m7i.48xlarge` gives you 192 vCPUs, 768 GiB of RAM, and 50 Gbps of network. If you need to go further, `u7in-32tb.224xlarge` offers 896 vCPUs and 32 TiB of RAM, enough to hold almost any OLTP working set entirely in memory. Most teams have never done the math on what actually fits on a single box because they never considered it an option. That is the assumption talking, not the hardware.

Stack Overflow is the steelman for this whole argument. For years one of the top-100 websites on the internet, hovering in the top 50 on Alexa at its peak, ran on a handful of servers. Nick Craver's 2016 architecture post is explicit: 9 active IIS web servers (11 total), a .NET monolith serving every Q&A site from a single application, two SQL Server clusters on Dell R720xd boxes with 384 GB of RAM and 4 TB of PCIe SSD, Dapper as the ORM, and exactly one stored procedure in the entire database. Question pages averaged 22.71 ms to render. The homepage averaged 11.80 ms. That setup handled around 209 million HTTP requests per day. No Kubernetes. No service mesh. No eventual consistency. A monolith, a big database, and people who understood both. The reason that story feels exotic is that the industry stopped treating it as the default, not that it stopped working.

**When you must distribute, distribute along natural boundaries of independence.** The only honest reason to cross a network boundary is that the work on the other side is *genuinely independent*: different users, different shards, different geographies. Services that talk to each other on every request should live in the same process.

**Make coordination explicit and rare.** Every round trip has a cost. Design systems where the hot path is coordination-free (local reads, local writes, local compute) and coordination happens only at boundaries: checkpoints, commits, cross-shard operations. The goal is not "eventually consistent". It is "locally authoritative, rarely coordinated".

**Treat partial failure as steady state.** Instead of exception handling bolted onto a success path, model the system as a state machine where every message is "maybe delivered, maybe duplicated, maybe late". Idempotency and at-least-once delivery become the contract, not the workaround.

**Use time as a budget, not a clock.** Do not ask "what time is it?". Ask "how long am I willing to wait before assuming failure?". Every operation has a deadline. Every deadline is a choice between false-positive and false-negative failure detection. Make that choice explicit per call-site.

**Keep state small and local. Keep compute mobile.** The worst architecture is one where both compute and state are distributed and both are mobile. Every operation pays the round-trip tax and the coordination tax at once.

**Measure everything in round trips, not milliseconds.** "This request does 14 round trips" tells you more than "this request takes 200ms", because round trips compose under failure and milliseconds do not.

Here is what coordination cost looks like when you map it visually instead of hiding it inside a latency graph. Every arrow is one round trip (`1 RT`); the client that pays the latency is highlighted in blue, the single source of truth the whole chain revolves around is highlighted in red.

<pre class="mermaid">
flowchart LR
    classDef client fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef db fill:#d20f39,color:#ffffff,stroke:#a30826,stroke-width:2px;
    A[Client]:::client -->|1 RT| B[API Gateway]
    B -->|1 RT| C[Auth Service]
    B -->|1 RT| D[User Service]
    D -->|1 RT| E[Profile Service]
    D -->|1 RT| F[Cache]
    E -->|1 RT| G[Postgres]:::db
    B -->|1 RT| H[Analytics]
    H -->|1 RT| I[Kafka]
    I -->|1 RT| J[Warehouse]
</pre>

Nine round trips for one logical request. Half of them exist because somebody wanted a microservice on their résumé. This is the picture you should draw for every request path in your system. Most teams have never drawn it.

## What Changes When You Think This Way

- **Vertical scaling stops being a dirty word.** The first question is not "how do we shard?". It is "what does this look like on one very large machine with good observability?".
- **Microservices become a last resort, not a first instinct.** You adopt them when the team structure demands it (Conway's Law) or when you have genuinely independent workloads.
- **"Eventually consistent" becomes suspect.** It is often a euphemism for "we gave up on defining the semantics". If you cannot answer *"eventually, bounded by what?"*, you do not have a consistency model. You have a hope.
- **Database-as-coordinator becomes respectable again.** A single Postgres with boring replication is a better substrate for most systems than a mesh of microservices plus Kafka plus a service registry plus a distributed tracer to debug why any of it works.
- **Consensus protocols become specialised tools.** You use Raft when you genuinely need a linearizable log. You do not build every service on top of one.

Eli Bendersky's [Raft implementation series](https://eli.thegreenplace.net/2020/implementing-raft-part-0-introduction/) makes this point in plain language: Raft is "much better suited for coarse-grained distributed primitives, like implementing a lock server, electing leaders for higher-level protocols, replicating critical configuration data". Not for user-facing transactional workloads. Not for the hot path of your API. Every Raft round trip writes to durable storage on a majority of replicas before a client hears back. That is the right price for etcd and Kubernetes coordination. It is the wrong price for your `/users/profile` endpoint.

The complexity tax becomes visible. Most teams pay it and get nothing back because their workload never needed distribution in the first place.

## When You Actually Need Distribution

To be fair to the other side: distribution is sometimes the right answer. Here are the only honest triggers. If none of them apply, you are paying the tax for no reason.

1. **Your working set does not fit on one machine.** Your database plus hot cache plus in-flight state cannot physically live on a single node, even a very large one. This is rarer than people think once you actually do the arithmetic.
2. **Your compute budget does not fit on one machine.** CPU or GPU demand genuinely exceeds what a single box can deliver, and the work parallelises cleanly. Training a large model is the canonical example. Serving a CRUD API is not.
3. **You need geographic distribution.** Users in multiple regions, latency budgets that require presence near the user, or data residency laws that forbid a single location. This is the most common legitimate driver, and it is a policy or physics problem, not a scale problem.
4. **Your organisation genuinely requires independent deploys.** Conway's Law made flesh: multiple teams that must ship on independent cadences without coordinating every release. This is an organisational trigger, not a technical one, and it should be named as such.

Notice what is *not* on the list: "we want to learn Kubernetes", "everyone else is doing microservices", "the architect diagram will look impressive in the design review". Those are not engineering reasons. Those are social reasons dressed up as engineering ones.

## The Honest Architectural Test

Before your next design review, try one exercise. Draw your current architecture on a whiteboard. Then delete half the boxes, any half, and ask: *"what survives, and was the rest worth the coordination cost?"* If the answer is "most of the value survives", the boxes you just deleted were baggage, not architecture.

Distributed systems are not a badge of sophistication. They are an expensive last resort with well-understood failure modes and a coordination cost that grows faster than the benefit for most workloads. The engineers who ship boring, single-machine systems and scale them for years are not behind the curve. They are the ones who read the curve carefully and decided not to buy into somebody else's scaling story.

First principles thinking is not about rejecting everything popular. It is about refusing to pay for complexity you cannot justify. Next time someone on your team says "we need to split this into services", ask them which of the six fundamentals forced that decision. If they cannot answer, you just found a box to delete.

## References

1. [Fallacies of Distributed Computing](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing). Peter Deutsch's original list, still correct.
2. [Impossibility of Distributed Consensus with One Faulty Process (FLP)](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf). Fischer, Lynch, Paterson, 1985.
3. [A Critique of the CAP Theorem](https://arxiv.org/abs/1509.05393). Martin Kleppmann, 2015.
4. [PACELC](https://en.wikipedia.org/wiki/PACELC_theorem). Abadi's extension to CAP that captures the latency-consistency tradeoff.
5. [Implementing Raft: Part 0 — Introduction](https://eli.thegreenplace.net/2020/implementing-raft-part-0-introduction/). Eli Bendersky on where Raft fits and where it does not.
6. [Stack Overflow: The Architecture — 2016 Edition](https://nickcraver.com/blog/2016/02/17/stack-overflow-the-architecture-2016-edition/). Nick Craver's server counts, render times, and SQL Server setup.
7. [First Principles: Software Observability]({filename}/first_principles_software_observability.md). Part 1 of this series.
8. [First Principles: Software Design]({filename}/first_principles_software_design.md). Part 2 of this series.
9. [First Principles: DevOps]({filename}/first_principles_devops.md). Part 3 of this series.
10. [First Principles: Data Engineering and ETLs]({filename}/first_principles_data_engineering.md). Part 4 of this series.
