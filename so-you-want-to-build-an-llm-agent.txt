Title: So You Want To Build An LLM Agent
Date: 2026-05-08 00:00:00
Category: Engineering
Tags: ai, agents, llm, prompt-engineering, litellm, python
Slug: so-you-want-to-build-an-llm-agent
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Most agent demos are toys: the tweet-thread prototype works, production breaks in week one. A vendor-neutral 30-line ReAct loop, the six failure modes that kill prototypes, and the patterns that actually save you in production.
Status: published

## TL;DR

Most agent demos are toys. The tweet-thread prototype works, production breaks in week one. An LLM agent is a loop: model call, parse, tool, observe, repeat. The hard part is not the loop, it is the six failure modes that kill prototypes (no step budget, no output validation, no retry, no traces, no eval, hallucinated APIs) and the patterns that prevent them. Build the 30-line vendor-neutral version with LiteLLM first, add patterns when production proves the need.

*Companion piece, written the same day: [First Principles: LLM Agents (Most of Yours Are Chatbots Wearing a Hat)]({filename}/2026-05-08_first_principles_llm_agents.md). That one strips the topic to its irreducible truths. This one is the practical build guide.*

---

## What An Agent Actually Is

Strip the mystique. Agent = loop:

```
perceive → reason → act → observe → repeat (until goal)
```

LLM call, parse output, run tool, feed result back, LLM call again. That's it.

Five things separate an agent from a chatbot:

1. **Tools**: act on the world, not just talk.
2. **Loop**: multi-step, not single-shot.
3. **Memory**: state across turns.
4. **Goal**: explicit terminate condition.
5. **Self-correction**: critique plus retry.

If your "agent" lacks any of these, you have a chatbot wearing a hat.

---

## The 5-Minute Version (Vendor-Neutral)

Working ReAct loop using **LiteLLM**: one API, 100+ providers. Swap models with one string.

```bash
pip install litellm
```

```python
from litellm import completion
import json
import os

os.environ["ANTHROPIC_API_KEY"] = "..."
# or OPENAI_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY, etc.

TOOLS = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate math expression",
        "parameters": {
            "type": "object",
            "properties": {"expr": {"type": "string"}},
            "required": ["expr"],
        },
    },
}]

def calculator(expr: str) -> str:
    return str(eval(expr, {"__builtins__": {}}, {}))

def agent(prompt, model="claude-sonnet-4-6", max_steps=10):
    msgs = [{"role": "user", "content": prompt}]
    for _ in range(max_steps):
        r = completion(model=model, messages=msgs, tools=TOOLS, max_tokens=2048)
        msg = r.choices[0].message
        msgs.append(msg.model_dump())

        if not msg.tool_calls:
            return msg.content

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = calculator(**args)
            msgs.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
    raise RuntimeError("step budget exhausted")

# Same code, different backends:
print(agent("17*23+41", model="claude-sonnet-4-6"))
print(agent("17*23+41", model="gpt-5"))
print(agent("17*23+41", model="gemini-2.5-pro"))
print(agent("17*23+41", model="ollama/llama3.3"))                     # local
print(agent("17*23+41", model="together_ai/meta-llama/Llama-3.3-70B-Instruct"))
```

> **Warning.** The `eval` in `calculator` is a teaching shortcut, not a sandbox. `().__class__.__mro__[1].__subclasses__()` escapes it in two lines. For real math tools use [`simpleeval`](https://pypi.org/project/simpleeval/); for general user code, run it in a separate process or container. Never expose raw `eval` to model output in production.

The loop, drawn:

<pre class="mermaid">
flowchart LR
    classDef trust fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef untrust fill:#d20f39,color:#ffffff,stroke:#a30826,stroke-width:2px;
    U[User prompt]:::trust --> C[Context]
    C --> M[LLM call]
    M --> P[Parse + validate]
    P -->|tool call| T[Tool executor]
    P -->|final answer| O[Result]
    T --> R[Tool result]:::untrust
    R --> C
    O --> V[Verification]
    V -->|pass| D[Deliver]
    V -->|fail| C
</pre>

Five working boxes. Two trust boundaries: untrusted content entering context (red), output before delivery (verification gate). Everything else is decoration.

Run it. Works. Looks like magic.

Now ship it.

---

## Picking The LLM Backend

Three valid approaches. Pick by need.

### LiteLLM, Universal Wrapper (default)

100+ providers behind one API. Format conversion automatic. Fallback chains built-in.

```python
from litellm import completion

resp = completion(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "hi"}],
    fallbacks=["gpt-5", "gemini-2.5-pro"],  # auto-fallback on rate-limit / outage
)
```

Best for: multi-provider hedging, production with outage resilience, A/B testing across models, vendor neutrality.

Cost: extra dep. Occasional lag on bleeding-edge features.

### OpenAI SDK + `base_url`, De-Facto Standard

Many providers serve OpenAI-compatible endpoints. Same SDK, swap base URL:

```python
from openai import OpenAI

# OpenAI native
client = OpenAI(api_key="...")

# Groq (fast inference)
client = OpenAI(api_key="...", base_url="https://api.groq.com/openai/v1")

# Together AI
client = OpenAI(api_key="...", base_url="https://api.together.xyz/v1")

# OpenRouter (access ~300 models with one key)
client = OpenAI(api_key="...", base_url="https://openrouter.ai/api/v1")

# Local: Ollama / vLLM / LM Studio
client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
```

Best for: single-provider deployments, when you want one well-known SDK shape.

Cost: tool-call format quirks vary by backend; not all providers fully OpenAI-compatible.

### Provider-Native SDKs, Best Fidelity

```python
# OpenAI
from openai import OpenAI

# Google Gemini
from google import genai

# Anthropic
from anthropic import Anthropic

# Mistral
from mistralai import Mistral

# Local Ollama
import ollama
```

Best for: cutting-edge features (Anthropic prompt caching, OpenAI structured-output strict mode, Gemini 1M context). Features land in native SDK first.

Cost: N SDKs = N code paths. Vendor lock. Rewriting code on provider switch.

### Trade-Off Table

| Approach | Pros | Cons |
|---|---|---|
| **LiteLLM** | One API, 100+ providers, format conversion, fallback chains, cost tracking | Extra dep, occasional version lag |
| **OpenAI SDK + base_url** | One SDK, native to many providers, well-known shape | Format quirks per backend; partial OAI compatibility |
| **Provider-native** | Latest features first, best per-vendor docs | N SDKs, vendor lock |

For most production agents: **LiteLLM is the right default**. Code stays vendor-neutral. Switch winner-of-the-month with a string change. Local fallback to Ollama costs nothing.

The rest of this post uses LiteLLM. Same patterns work with any backend.

---

## What This Costs

Numbers move every quarter; orders of magnitude do not. May 2026 list prices, single-turn ≈ 500 input + 100 output tokens:

| Model | Input ($/1M tok) | Output ($/1M tok) | Single-turn ≈ |
|---|---|---|---|
| Claude Haiku 4.5 | $1 | $5 | $0.001 |
| Claude Sonnet 4.6 | $3 | $15 | $0.003 |
| Claude Opus 4.7 | $15 | $75 | $0.015 |
| GPT-5 | $5 | $15 | $0.004 |
| Gemini 2.5 Pro | $2.50 | $10 | $0.002 |

Real agents look different from the single-turn number in two ways that matter.

1. **Context grows step by step; total cost grows quadratically.** Every iteration appends the prior tool call plus its result, so per-call input grows `O(n)`. The agent re-pays for the full prefix on each step, summed across `n` steps that is `O(n²)` total. Step 10 of a 10-step loop sees the entire history on every call.
2. **Frontier models cost 5x to 50x more than cheap ones.** A 1k-task batch on Sonnet runs ~$20; on Haiku ~$4; on Opus ~$100. Pick by which step needs which tier, not by which name impressed the team.

Worked example: a 10-step Sonnet 4.6 loop with growing context (avg 2k input by step 10, 200 output) runs roughly $0.10 per task. Run it 10k times a day and that is $1k/day, $30k/month. The math kills products that did not budget for it.

---

## Cut Cost With Prompt Caching

Most production agents send the same prefix on every call (system prompt + tool definitions + few-shot examples), then a small variable suffix (the user's question). Anthropic, OpenAI, and Gemini all support caching that prefix. Cache hits cost roughly 10% of normal input. For a 5k-token prefix at 100 calls per day, that is 90% of input cost gone.

Anthropic explicit cache:

```python
from anthropic import Anthropic

client = Anthropic()
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": LONG_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},  # ~5 min TTL
    }],
    tools=TOOLS,
    messages=[{"role": "user", "content": question}],
)
```

OpenAI auto-caches prefixes ≥ 1024 tokens automatically. LiteLLM passes Anthropic `cache_control` through unchanged. Order matters: cache prefix first, variable content last. Putting the question above the system prompt invalidates the cache on every call.

Single biggest cost lever in production. Currently underused because the docs hide it.

---

## Where Prototypes Die

Same six failures, every time.

**1. No step budget.** Loop runs forever. Burns API budget at 3am. The math nails it: `p(success)^n` collapses. Five 90% steps = 59% overall. Cap iterations. Fail fast.

**2. No output validation.** LLM returns "the answer is approximately 391". Your code does `int(response)`. Crash. Use Pydantic at every boundary. Parse, don't validate. Schema as guardrail.

```python
from pydantic import BaseModel, Field, ValidationError

class Result(BaseModel):
    answer: int
    confidence: float = Field(ge=0, le=1)

raw = completion(model="...", messages=[...]).choices[0].message.content
try:
    result = Result.model_validate_json(raw)
except ValidationError as e:
    raise ValueError(f"LLM output invalid: {e}")
```

**3. No retry, no rollback.** Tool times out. Whole run aborts. Partial side effects leak (email half-sent, DB row half-written). Production needs:

- Classify failures: transient (retry with backoff) vs permanent (escalate) vs catastrophic (rollback plus alert).
- Checkpoint state before risky ops.
- Idempotent tool calls.

**4. No traces.** Agent fails. You stare at the final error. Useless. Log every LLM call: input tokens, output tokens, latency, stop reason, tool calls. Without traces you are blind. Trajectory log is the debugger.

**5. No eval.** Ship "feels good" code. Regress silently next sprint. Build a golden test set. Three eval modes:

- **Outcome-based**: did the agent achieve the goal? Pass / fail.
- **Process-based**: efficient, logical path? Right tools?
- **LLM-as-Judge**: separate model scores 1 to 5.

**6. Hallucinated APIs.** Model confidently imports `langchain.agents.create_react_agent_v3`. Doesn't exist. Always verify against current docs before depending on a non-trivial API. Pin versions. Never `latest`.

---

## Pick A Trace Backend Before Day Two

Failure mode #4 (no traces) is the one that compounds fastest. Every LLM call is non-deterministic; without a trace UI you read JSONL by hand at 3am. Pick a backend on day two, not after the first incident.

| Tool | Stance | Setup |
|---|---|---|
| **Arize Phoenix** | Open-source, OTel-native, runs locally or self-hosted | `pip install arize-phoenix` |
| **Langfuse** | Open-source self-host plus hosted SaaS, prompt management built in | `docker compose up`, then SDK |
| **Helicone** | Hosted proxy, transparent: change `base_url` and you have traces | One env var |
| **OpenTelemetry direct** | Vendor-neutral, ship to Jaeger, Tempo, Datadog | More wiring, no LLM-specific UI |

Phoenix is the cheapest start: zero infra, runs in a notebook, OTel under the hood, integrates with LiteLLM out of the box.

```python
import phoenix as px
from phoenix.otel import register

px.launch_app()
register(project_name="my-agent", auto_instrument=True)
# Every LiteLLM call now appears at http://localhost:6006
```

For the deeper grounding on what to trace and why (logs, metrics, traces as three pillars; trace IDs in every log line; SLOs over raw error counts), see [First Principles: Software Observability]({filename}/2026-03-19_first_principles_software_observability.md). LLM agents are not a special observability domain; they just have more state per span and more probabilistic failure modes per request. Same discipline, applied harder.

---

## The Patterns That Actually Save You

21 patterns in Gulli's *Agentic Design Patterns*. Group into 4 buckets matching what an agent actually does.

### Bucket 1: Core Execution (decompose + run)

- **Prompt Chaining**: output of one step = input of next. Linear DAG.
- **Routing**: conditional path. LLM-as-router or rule classifier.
- **Parallelization**: independent sub-tasks concurrent. ThreadPool or `asyncio.gather`.
- **Planning**: high-level goal, numbered sub-tasks. Re-plan on failure.

When task = "single LLM call too small, full DAG too big", these compose.

### Bucket 2: External World (act + retrieve)

- **Tool Use / Function Calling**: JSON schema, model emits structured call, you execute.
- **MCP** (Model Context Protocol): wire protocol for tool servers. JSON-RPC over STDIO/SSE. Decouples tool dev from agent dev. When tool count grows past 5, you want this.
- **RAG**: retrieve relevant docs, inject as context, generate. Chunk 200 to 500 tokens, hybrid BM25 + vector for production. Mitigates hallucination, extends knowledge past cutoff.

Tools are hands. RAG is senses. Both required for grounded operation.

### Bucket 3: State + Self-Improvement

- **Memory Management**: short-term (conversation buffer) plus long-term (persisted facts). Three sub-types: episodic (past interactions), semantic (facts), procedural (skills).
- **Reflection / Self-Correction**: generator plus critic. Two flavors: "check your work" (same agent reviews self) vs "internal critic" (separate critic agent, more rigorous).
- **Learning / Adaptation**: agent updates behaviour from feedback. Online learning. Rare in practice; usually fine-tune offline instead.
- **Goal Setting + Monitoring**: SMART criteria. Without an explicit done-condition, the agent drifts.
- **Exception Handling + State Rollback**: transactional state. Checkpoint, try, rollback on error.

Reflection alone often beats fancier patterns. "Draft, critique, revise" gives 20 to 40 percent quality lift on hard tasks. Cheap. Proven.

### Bucket 4: Collaboration

- **Multi-Agent**: specialist team (Researcher + Writer + Critic). Modularity, reduced complexity, simulated brainstorming.
- **A2A** (Agent-to-Agent): `/.well-known/agent.json` discovery, JSON-RPC `sendTask` / `sendTaskSubscribe` (streaming). Cross-org standard.
- **HITL** (Human-in-the-Loop): pause for approval at critical junctures. Plan approval, destructive tool confirmation, ambiguity resolution, final output review.
- **Resource-Aware Optimisation**: route by complexity. Cheap models for classify, mid-tier for standard agent, frontier for hard reasoning. Pair with budget cap per request.
- **Guardrails**: 5 layers, input validation plus output filtering plus tool restrictions plus behavioural constraints plus checkpoint/rollback.

Multi-agent feels powerful. Often overkill. Default = single agent + tools. Split into specialists only when a single prompt exceeds 1000 tokens or contains conflicting instructions.

---

## Composition > Single-Pattern Mastery

True power = composing patterns. Research-assistant example from the book.

User asks: *"Analyze quantum computing impact on cybersecurity."*

Composition:

- **Planning** decomposes into 4 research steps.
- **Tool Use** drives each step (search, ArXiv API).
- **Multi-Agent**: Researcher gathers, Writer synthesises, Critic reviews.
- **Reflection**: Critic catches logic errors, fact errors, Writer revises.
- **Memory**: persist plan, info, drafts, feedback across the multi-step run.

Five patterns woven together. None individually impressive. Together: an autonomous research system.

That's the craft. Not "I know ReAct." It's "I see the canvas as a whole."

---

## Hard-Won Lessons

**Frontier models for quality-critical paths.** Cheap models truncate context, lose subtle reasoning. Use cheap tier for classify / extract / route only. Cost saved < quality lost on the actual reasoning step.

**Untrusted content is data, never instructions.** Tool output, retrieved docs, user files all enter the prompt. Prompt injection is structural, not a bug. Wrap retrieved content in delimiters. Verify intent against the original user request, not against the retrieved text.

**Pin everything in version control.** Model version (`claude-sonnet-4-6`, not "latest"). Prompts as `.md` files in `/prompts/`. Treat prompts as code: review, version, diff.

**Goals before loops.** Without an explicit done-condition, the agent burns budget on infinite "let me also check..." Add `success_criteria: list[str]`. Verify before each iteration.

**Rollback before retry.** Partial state from a failed op corrupts the next attempt. `with transactional(state):` pattern. Checkpoint, try, rollback on exception.

**Run before claim.** Generated code "looks right", plausible syntax, plausible imports, may not execute. There is no truth signal in the distribution. Run tests, build, lint, type-check, the actual feature.

**LiteLLM fallbacks save 3am pages.** Provider has an outage, traffic shifts to a fallback model automatically. Cost: one extra arg per call.

```python
completion(
    model="claude-sonnet-4-6",
    fallbacks=["gpt-5", "gemini-2.5-pro", "ollama/llama3.3"],
    messages=[...],
)
```

---

## The Shift Coming

Three trends from the book worth tracking.

**1. Human-in-the-loop becomes human-on-the-loop.** Today: agent pauses, asks human at every fork. Tomorrow: agent runs autonomously, reports only on completion or critical exception. Scope of trust expands as eval and guardrails mature.

**2. Standardisation via MCP plus A2A.** Today: tool integration is per-framework, glue code everywhere. Tomorrow: MCP for tools, A2A for agents. Agent marketplaces. Hire-able specialist agents (research agent, travel agent). The "Awesome Agents" repo on GitHub is already curating this.

**3. Neuro-symbolic blend.** Pure LLM = pattern match plus probabilistic. Add classical AI (logic, planning, constraint solving) for rigor. Best of both. Watch for SR 11-7-grade model governance demands as agents enter regulated domains.

---

## Practical Path

Build in this order. Stop when the problem is solved.

| Stage | Add |
|---|---|
| Hello world | LiteLLM + tools + ReAct loop (30 lines) |
| Useful demo | + Pydantic structured output + memory |
| Beta | + Planning + Reflection + traces |
| Production | + Guardrails + Exception handling + Eval suite |
| Scale | + Resource-aware routing + Multi-agent (when needed) |
| Cross-org | + MCP + A2A |

Most projects stop at "Production". That's fine. Resist the urge to add multi-agent before a single-agent prompt exceeds 1000 tokens. Three similar lines beats premature abstraction.

---

## Don't Use A Framework Until You've Built Without One

Build the 30-line ReAct loop first. Understand the mechanism: tools as JSON schema, stop reasons, tool_use blocks, tool_result feedback, message accumulation.

Then evaluate frameworks (LangGraph, CrewAI, ADK, Strands) against actual needs. They hide the mechanism, ship faster, but you debug what you don't understand.

LiteLLM ≠ framework. It's a thin SDK wrapper. Keep it under your code, not over it. The patterns above are yours to compose.

From-scratch teaches mechanism. Framework hides mechanism. Both valid. Order matters.

---

## Bottom Line

Agents are not magic. Loop, tools, memory, goal, self-correction. Composition of well-known patterns. The hard part isn't any single pattern, it's running the resulting system reliably in production.

Six failure modes kill prototypes. Five buckets of patterns prevent them. Build the 30-line version today. Add patterns when production need is proven, not anticipated.

Pick LiteLLM by default. Vendor-neutral code outlives the model-of-the-month.

The canvas is in front of you. Patterns are in your hands. Now go build.

## References

1. [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). Anthropic, 2024. The single best argument for "start simple, add complexity only when proven necessary".
2. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). Yao et al., 2022. Original ReAct paper.
3. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366). Shinn et al., 2023. Quantifies the lift from self-reflection.
4. [Agentic Design Patterns](https://www.amazon.com/Agentic-Design-Patterns-Hands-Intelligent/dp/3032014018). Antonio Gulli, 2025. The 21 patterns referenced throughout this post.
5. [LiteLLM Documentation](https://docs.litellm.ai/). Vendor-neutral SDK used in the example loop.
6. [Model Context Protocol Specification](https://modelcontextprotocol.io/). Wire protocol for tool servers.
7. [A2A Protocol](https://a2aproject.github.io/A2A/). Cross-org agent-to-agent discovery and task standard.
8. [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/). Prompt injection (LLM01) and excessive agency (LLM06) bite agent designs hardest.
9. [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/). Alexis King, 2019. The original phrase, applied to schema validation at boundaries.
10. [SR 11-7, Model Risk Management](https://web.archive.org/web/2026/https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm). US Federal Reserve, 2011 (Wayback mirror, federalreserve.gov returning 404 as of 2026-05-08). Governance regime for any model used in regulated decisions.
11. [Arize Phoenix](https://docs.arize.com/phoenix). Open-source LLM observability, OTel-native, runs locally.
12. [Langfuse](https://langfuse.com/docs). Open-source self-hostable LLM observability with prompt management.
13. [Helicone](https://docs.helicone.ai/). Proxy-based LLM observability, single env-var integration.
14. [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching). Cache reuse up to 90% input cost savings.
15. [simpleeval](https://pypi.org/project/simpleeval/). Sandboxed expression evaluator for the calculator-tool case.
16. [First Principles: Software Observability]({filename}/2026-03-19_first_principles_software_observability.md). The three-pillar discipline that grounds the trace-backend section.
17. [First Principles: LLM Agents (Most of Yours Are Chatbots Wearing a Hat)]({filename}/2026-05-08_first_principles_llm_agents.md). Companion piece, same day, conceptual frame.
