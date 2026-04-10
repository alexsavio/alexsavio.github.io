Title: First Principles: Software Observability
Date: 2026-03-19 20:45:00
Category: Engineering
Tags: first-principles, observability, monitoring, logging, metrics, tracing
Slug: first-principles-software-observability
Series: First Principles
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Everyone knows observability means logs, metrics, and traces. But what if you strip away the vendor marketing, the inherited conventions, and the cargo-culted dashboards? What's actually true? A first-principles deconstruction of software observability.
Status: published

## TL;DR

The "three pillars" of observability (logs, metrics, traces) describe data formats, not observability itself. When you strip the concept down to what's provably true and rebuild from scratch, you get a fundamentally different approach: instrument decisions instead of outcomes, explore instead of monitor, alert on invariants instead of thresholds, and treat observability as a design property, not an ops afterthought.

---

## The Conventional View

Ask any engineer what "observability" means and you'll get the same answer: logs, metrics, and traces, the "three pillars". Ship them to Datadog or Grafana, build dashboards, set up alerts, and you're observable. This is the version you'll hear at every conference talk and read in every vendor blog post.

The framing traces back to Peter Bourgon's 2017 blog post ["Metrics, tracing, and logging"][bourgon-2017], which drew a Venn diagram of the three signal types and their overlaps. It was a useful taxonomy for a talk. Then the vendor ecosystem adopted it as gospel, and now teams treat it like a checklist: ✓ logs ✓ metrics ✓ traces → done.

But how much of this is actually true, and how much is convention dressed up as truth?

## The Assumptions We Carry

Before deconstructing, let's name the baggage. These are beliefs most engineers treat as self-evident:

| # | Assumption | Origin | Verdict |
|---|-----------|--------|---------|
| 1 | Observability = logs + metrics + traces | Industry vendors, circa 2017-2018 | **Heuristic** - useful taxonomy, but the pillar count is arbitrary |
| 2 | More data means better observability | Analogy from data science ("collect everything, decide later") | **Baggage** - more data often means more noise and higher cost |
| 3 | You need a centralized observability platform | Vendor marketing + operational convenience | **Heuristic** - centralization helps, but the platform isn't the observability |
| 4 | Dashboards are how you understand systems | Inherited from physical control rooms | **Baggage** - dashboards show what you already know to ask about |
| 5 | Alerts should fire when thresholds are breached | Infrastructure monitoring (Nagios era) | **Heuristic** - works for known failure modes, useless for novel ones |
| 6 | Observability is an ops/SRE concern | Historical "build it" vs "run it" separation | **Baggage** - broken feedback loop if builders can't observe |
| 7 | Instrumentation is overhead that slows development | Perception that observability is separate from feature work | **Baggage** - confuses bad instrumentation with instrumentation itself |
| 8 | You should monitor everything in production | Defensive posture ("we might need it someday") | **Baggage** - monitoring everything is monitoring nothing with extra cost |
| 9 | Observability is about finding bugs in production | Narrow framing from incident response culture | **Heuristic** - incident response is one use case, not the definition |
| 10 | Sampling loses important information | Fear from teams burned by missing data | **Heuristic** - true for rare events, false for high-volume steady-state |

Three categories emerge: **fundamental truths** that survive scrutiny, **useful heuristics** that are context-dependent, and **inherited baggage**, conventions masquerading as truth.

## What Survives Scrutiny

After stripping away heuristics and baggage, five things are provably, irreducibly true about observability.

### 1. A system is observable if you can determine its internal state from its external outputs

This is the control-theory definition, and it's the real one. Rudolf Kalman formalized it in 1960 in his work on linear dynamical systems [Kalman, 1960][kalman-1960]: a system is observable if, for every possible sequence of state transitions, the current state can be determined in finite time using only the outputs. It says nothing about tools, pillars, or vendors. It's a property of the *system itself*, not of the monitoring infrastructure bolted onto it.

The distinction matters. When you buy a monitoring platform, you haven't made your system observable. You've added a receiver for signals your system may or may not be emitting. The observability is in the system's design. The platform is just a lens.

### 2. You cannot debug what you cannot distinguish

This is the insight Charity Majors and the Honeycomb team have been hammering on for years [Honeycomb, "Observability: A Manifesto"][charity-observability]: the fundamental purpose of observability data is to tell apart *this request* from *that request*, *this state* from *that state*. If your data collapses distinct behaviors into pre-aggregated metrics, you've lost the ability to reason about specifics.

This is why high-cardinality, high-dimensionality data matters. It preserves the ability to ask questions you didn't anticipate. A metric that says "p99 latency is 800ms" tells you there's a problem. An event that says "request abc123 from user xyz, hitting service-payments via endpoint /charge, took 1200ms because the database query plan chose a sequential scan on a 4M-row table" tells you *why*.

### 3. The value of observability is proportional to the speed of the feedback loop

Data that arrives 10 minutes after the fact is categorically less useful than data available in real time. The faster you can go from "something is wrong" to "I understand why," the less damage the system takes. MTTR (Mean Time To Recovery) directly correlates with blast radius.

The Google SRE book makes this concrete in its chapter on monitoring distributed systems [Beyer et al., 2016][google-sre-monitoring]: the ideal monitoring system minimizes the time between a problem occurring, being detected, being understood, and being fixed. Every delay in that chain compounds.

### 4. Systems fail in ways you didn't predict

If you could enumerate all failure modes in advance, you'd prevent them. Observability exists precisely because you can't. This is what Charity Majors calls the distinction between "known unknowns" and "unknown unknowns" [Majors, 2020][charity-unknown-unknowns]. Monitoring handles the former, observability handles the latter.

Any approach that only works for anticipated failures (static dashboards, threshold-based alerts, pre-built runbooks) is structurally incomplete. It's building a flashlight that only illuminates rooms you've already been in.

### 5. Signal costs attention, and attention is finite

Every metric, log line, and alert competes for a human's cognitive bandwidth. An observability system that produces more signal than a human can process is functionally equivalent to one that produces none.

This is the overlooked constraint that makes "collect everything" actively harmful. More data doesn't mean better observability. It means more noise to filter before you can think. The art is in emitting the right signals, not all signals.

## What Falls Away

With only five truths remaining, the conventional view takes some hits.

**"Three pillars" as a definition.** This taxonomy describes data formats, not observability. You can have all three pillars and still be blind to production issues if the data lacks context, correlation, or queryability. Cindy Sridharan made this point in *Distributed Systems Observability* [Sridharan, 2018][sridharan-2018]: the pillars framework tricks teams into thinking the job is done once they've checked three boxes. It conflates the *representation* of signals with the *property* of being observable.

**"Collect everything".** This is storage-vendor thinking. It produces massive cost, massive noise, and a false sense of security. Teams drown in data they never query while missing the specific signals that would have caught the outage. The constraint from Truth #5 (attention is finite) kills this approach on contact.

**"Dashboards = understanding".** Dashboards are answers to questions you've already asked. They excel at confirming known patterns and fail completely at surfacing unknown ones. Over-reliance on dashboards creates a dangerous illusion: the team feels informed because the screens look green, but the failure mode that takes them down won't have a panel.

**"Observability is an ops problem".** If the developer who writes the code doesn't think about how it will be observed in production, no amount of post-hoc instrumentation fixes it. Observability is a design property (Truth #1), not an operational afterthought. Separating "who builds it" from "who observes it" guarantees that the wrong things get instrumented.

## Rebuilt From Scratch

Starting from only the five fundamental truths, here's what observability looks like when designed from zero, as if the existing tools and conventions had never existed.

### Build systems that explain themselves

Observability isn't a layer you add. It's a property you design in (Truth #1). Every meaningful state transition, decision branch, and external interaction should emit a structured event that captures enough context to reconstruct *why* the system did what it did. Not "log everything". Emit the *decisions*.

When a rate limiter throttles a request, that's a decision. When a circuit breaker opens, that's a decision. When a feature flag routes a user to variant B, that's a decision. When a cache lookup misses, *that's diagnostic information*. These are the events that matter.

### One event model, not three pillars

Instead of separate logs, metrics, and traces, emit **rich structured events** with high-cardinality fields: user ID, request ID, feature flag state, query plan, service version, deployment SHA, whatever gives you the ability to distinguish (Truth #2). From these events:

- **Metrics** are aggregations derived from events (count events where `status=500`, compute p99 of `duration_ms`)
- **Traces** are events correlated by a shared `trace_id`
- **Logs** are events rendered as text

The underlying primitive is the same: a timestamped, context-rich structured event. This isn't theoretical. It's the architecture Honeycomb was built on, and it's the direction [OpenTelemetry][otel] is converging toward with its unified signal model.

### Explore, don't monitor

The primary interaction model should be ad-hoc querying (Truth #4, failures are unpredicted). "Show me all requests from user X that hit service Y in the last hour, broken down by response code and latency percentile". Dashboards become saved queries that proved useful, not the starting point. The system should support questions you've never asked before.

This is a fundamental shift in posture: from passive monitoring ("stare at dashboards and wait for red") to active exploration ("I have a hypothesis, let me test it against production data").

### Alerts from invariants, not thresholds

Instead of "alert when latency > 500ms" (a threshold you guessed), define **invariants**: relationships that should always hold.

- "Every request must complete within the SLO budget"
- "Error rate should be proportional to traffic, not absolute"
- "No single dependency should account for >40% of total latency"
- "No data ingested for entity X in 2× the expected interval"

Invariant violations are structurally more robust than static thresholds because they encode *relationships*, not *numbers* (Truth #4). "No data in 2× the expected interval" adapts automatically when you change the ingestion schedule. "Data count < 100" breaks the moment your input set changes size.

Rob Ewaschuk's influential "My Philosophy on Alerting" [Ewaschuk, 2013][ewaschuk-alerting] laid the groundwork for this thinking at Google: alert on symptoms (user-visible impact), not causes or static numbers. SLO-based alerting, burn rate alerts on error budgets as described in the Google SRE Workbook [Beyer et al., 2018][google-sre-workbook], is one concrete implementation of this principle. Instead of alerting on individual threshold violations, you alert on the *rate at which you're consuming your error budget*.

### Cost is proportional to questions answered, not data stored

Intelligent sampling keeps costs bounded while preserving diagnostic power (Truth #5). The strategy:

- **100% capture** for state transitions, errors, slow requests, and new deployments
- **Sample broadly** (1-10%) for routine, healthy traffic
- **Dynamic instrumentation** to temporarily increase detail in areas of interest

The optimization target is "can I answer the question I have right now?", not "did I store everything?"

### The developer is the operator

Instrumentation is part of the code review. "How will we know this works in production?" is a design question, asked at the same time as "how will we test this?" The feedback loop runs from code → production → understanding → code. If the person who writes the code can't observe it running, the loop is broken (Truth #3).

## The Delta

Here's what changes when you swap conventional thinking for first-principles thinking:

| Conventional | First Principles |
|---|---|
| Adopt a platform, instrument with its SDK | Design systems to emit rich structured events; the platform is a queryable store |
| Three separate pipelines (logs, metrics, traces) | One event pipeline, derive metrics and traces from events |
| Build dashboards for every service | Default to ad-hoc exploration; save queries that prove useful |
| Alert on static thresholds | Alert on invariant violations and SLO burn rates |
| Collect everything, filter later | Emit decisions and boundaries; sample intelligently |
| Ops team owns observability | Developers own observability of what they build |
| "We need more monitoring" | "We need better questions" |

## What You Can Do Monday Morning

This isn't abstract philosophy. Here's what changes in practice:

1. **Instrument decisions, not just outcomes.** When your system skips an item, when a rule evaluates but doesn't fire, when a candidate is considered but filtered out, those non-events are often more diagnostic than the events you're already logging. The question to ask at every code review: "if this path executes in production and something goes wrong, do we have enough context to understand why?"

2. **Before adding a dashboard panel, write down the question it answers.** If you can't state the question, you're adding noise. Audit your existing dashboards with this lens. You'll likely find panels nobody looks at and gaps where real questions go unanswered.

3. **Encode relationships in your alerts.** Replace absolute thresholds with relative invariants that adapt to your system's current configuration. "Error rate > 1% of traffic" beats "errors > 50/min" because it scales with your system. Your future self, debugging at 2am, will thank you.

4. **Design for correlation.** Every event should carry enough context to link it to the request, user, deployment, and feature flags that were active. When something goes wrong at step 5 of a pipeline, you should be able to follow the thread back to step 1 without guessing.

5. **Capture 100% of state transitions, sample everything else.** This is the scaling strategy that preserves diagnostic power while keeping costs bounded. Every order fill, every state change, every error, captured. Every routine health check on a quiet Tuesday, sampled.

The goal isn't more data. It's better questions.

---

## References

1. [Rudolf Kalman, "On the General Theory of Control Systems," *Proceedings of the First IFAC Congress*, 1960][kalman-1960] - The original formalization of observability and controllability in linear dynamical systems.
2. [Peter Bourgon, "Metrics, tracing, and logging," 2017][bourgon-2017] - The blog post that introduced the widely adopted "three pillars" Venn diagram.
3. [Honeycomb, "Observability: A Manifesto"][charity-observability] - Honeycomb's case for why observability is about asking new questions, not collecting known signals.
4. [Charity Majors, "Observability is a Many-Splendored Thing," 2020][charity-unknown-unknowns] - The case for observability as the tool for unknown unknowns.
5. [Cindy Sridharan, *Distributed Systems Observability*, O'Reilly, 2018][sridharan-2018] - Free book providing a thorough treatment of observability beyond the three-pillar framing.
6. [Betsy Beyer et al., "Monitoring Distributed Systems," *Site Reliability Engineering*, O'Reilly, 2016][google-sre-monitoring] - Google's approach to monitoring, including the white-box vs. black-box distinction and the four golden signals.
7. [Betsy Beyer et al., "Alerting on SLOs," *The Site Reliability Workbook*, O'Reilly, 2018][google-sre-workbook] - Practical guide to burn-rate alerting and SLO-based operational practices.
8. [Rob Ewaschuk, "My Philosophy on Alerting," 2013][ewaschuk-alerting] - Influential Google SRE document arguing alerts should be based on symptoms and user-visible impact, not static thresholds.
9. [Honeycomb, "How Are Structured Logs Different From Events?"][honeycomb-events] - Why wide structured events, not log lines or pre-aggregated metrics, are the correct primitive for observability.
10. [OpenTelemetry Project][otel] - The CNCF project converging logs, metrics, and traces into a unified observability framework.

[kalman-1960]: https://doi.org/10.1016/S1474-6670(17)70094-8
[bourgon-2017]: https://peter.bourgon.org/blog/2017/02/21/metrics-tracing-and-logging.html
[charity-observability]: https://www.honeycomb.io/blog/observability-a-manifesto
[charity-unknown-unknowns]: https://charity.wtf/2020/03/03/observability-is-a-many-splendored-thing/
[sridharan-2018]: https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/
[google-sre-monitoring]: https://sre.google/sre-book/monitoring-distributed-systems/
[google-sre-workbook]: https://sre.google/workbook/alerting-on-slos/
[ewaschuk-alerting]: https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/edit
[honeycomb-events]: https://www.honeycomb.io/blog/how-are-structured-logs-different-from-events
[otel]: https://opentelemetry.io/
