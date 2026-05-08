Title: First Principles: LLM Agents (Most of Yours Are Chatbots Wearing a Hat)
Date: 2026-05-08 12:00:00
Category: Engineering
Tags: first-principles, llm, agents, ai, architecture, prompt-engineering
Slug: first-principles-llm-agents
Series: First Principles
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: LLM agent design is buried under framework worship, multi-agent fantasies, and vector-DB orthodoxy. Strip it back to what is provably true and only six things survive. Most of the architecture teams reach for is a chatbot wearing a hat.
Status: published

## TL;DR

LLM agents are drowning in inherited wisdom: pick a framework, spin up a crew of specialists, plug a vector database in for "memory", watch the demo work, and ship. Strip the topic down to what is actually true about a language model in a loop, and only six irreducible facts survive. Most of the multi-agent, framework-first, RAG-by-default architecture that engineers reach for is overhead, not substance. The uncomfortable conclusion: the first agent worth building is a 30-line ReAct loop with a step budget, not a "crew" of personas powered by a graph DSL.

*This is the sixth post in my First Principles series, where I take a concept the industry treats as settled and strip it back to what is actually provable. Previous entries: [Software Observability]({filename}/2026-03-19_first_principles_software_observability.md), [Software Design]({filename}/2026-03-21_first_principles_software_design.md), [DevOps]({filename}/2026-03-30_first_principles_devops.md), [Data Engineering]({filename}/2026-04-08_first_principles_data_engineering.md), and [Distributed Systems]({filename}/2026-04-09_first_principles_distributed_systems.md). LLM agents felt like the right next target because few topics have calcified around tooling as fast, with as little benchmark evidence to back it up.*

[TOC]

---

## The Conventional View

Ask a builder how to ship an LLM agent in 2026 and the answer comes out like a Lego instruction sheet. Pick a framework (LangGraph, CrewAI, AutoGen, ADK). Wire a "crew" of specialist agents (Researcher, Writer, Critic, Manager). Plug a vector database in for "long-term memory". Wrap it all in an orchestrator. Add MCP servers for the tools you do not want to write yourself. Watch the demo loop produce a paragraph that sounds plausible. Ship.

The discipline is defined by its frameworks, its acronyms (RAG, MCP, A2A, ReAct, ToT, GoT), and its conference-talk reference architectures. *Multi-agent* is "modern". A single ReAct loop is "naive". Without a vector DB you do not have "memory". Without a framework you are "reinventing the wheel".

This post is not about which framework to pick. It is about whether most of that machinery is doing any work at all, and what an LLM agent looks like when you stop copying the architecture of an investor deck and reason forward from the things that are actually true about a language model.

## What People Just Assume

Before you can tear something down, you have to name the inherited thinking. Here are the beliefs most engineers carry into agent building without ever having checked them.

| #  | Assumption                                                              | Where it came from                          | Verdict                |
|----|-------------------------------------------------------------------------|---------------------------------------------|------------------------|
| 1  | More agents = better outcomes                                           | AutoGen / Swarm / CrewAI demos              | Baggage                |
| 2  | RAG is required for any non-trivial agent                               | LangChain tutorials, vector-DB marketing    | Heuristic              |
| 3  | A framework ships you faster                                            | YC pitch decks, conference talks            | Baggage                |
| 4  | Long context windows solve "memory"                                     | Gemini 1M / Claude 200K announcements       | Heuristic              |
| 5  | Vector DB = "memory"                                                    | Pinecone / Weaviate launch posts            | Baggage                |
| 6  | Reflection and self-critique are optional polish                        | "Agents just work" hype                     | Heuristic (often inverted) |
| 7  | A frontier model is enough; eval can wait                               | Vibes-based shipping                        | Baggage                |
| 8  | Tool calls are reliable                                                 | OpenAI / Anthropic docs read optimistically | Heuristic              |
| 9  | An autonomous agent should run unattended in production                 | Gen-AI investor narratives                  | Baggage                |
| 10 | "Agentic" is a meaningful spec                                          | Twitter / LinkedIn                          | Baggage                |

The point of that table is not contrarianism. It is compression. Most of what gets repeated as "agent engineering knowledge" is a mix of vendor marketing, framework documentation taken as physics, and pattern names imported from research papers without the experimental conditions that made them work.

## What Actually Survives Scrutiny

Six things remain once you strip the heuristics and the baggage. These are properties of the underlying technology, not of any specific framework or model.

**1. A language model produces text from context. That is the entire mechanism.** Every call is stateless. There is no "goal", no "memory", no "self". The model receives a context window and emits tokens that are likely given that context. Anything that looks like persistent state is plumbing built around that one call. Forget this and you start arguing with the wrong layer of the stack.

**2. Probabilistic output cannot be trusted. It must be verified.** There is no truth signal inside the distribution. Plausible-looking is the only thing the model optimises for, and "plausible" is not the same as "correct". Hallucinated APIs compile cleanly in your head and break on import. If you do not have a verification step, you do not have an agent, you have a confident speaker.

**3. Tokens are the only currency the runtime recognises.** Context window, latency, and cost are all measured in tokens. Out-of-window content does not exist for the model regardless of how cleverly you stored it. Long prompts are slow, expensive, and degrade quality through "lost in the middle" effects. Token budget discipline is not optimisation, it is correctness.

**4. Tools are the only way to act on the world.** Without tools, the model can describe an action but cannot perform one. Tools are the boundary between language model and reality. The schema is the contract; the executor is the mechanism. Everything else (planning, reflection, critique) is text shuffled inside the same context window.

**5. Loops compose multiplicatively, not additively.** A loop of `n` steps with per-step success probability `p` succeeds end-to-end with probability `p^n`. Five steps at 90% individual success give you 59% overall. Ten give you 35%. Without verification at each step and a hard step budget, longer chains do not get smarter, they get exponentially less reliable.

**6. Untrusted content in the context is an instruction injection vector.** The model cannot distinguish "user instructions" from "data the user pasted in" from "documents the agent retrieved". Anything in the prompt is an instruction candidate. Prompt injection is structural, not a bug to patch. This is OWASP LLM01 and it is not going away with a smarter model.

That is the whole bedrock. Six statements. Notice what is *not* on the list: multi-agent crews, vector databases, frameworks, RAG, MCP, "agent memory", planning patterns, reflection, ReAct, ToT. None of those are fundamental. They are tools, patterns, or rebrandings.

## What Falls Away

Once you stop at "only what is provably true", the conventional architecture advice starts looking suspicious.

- **"More agents = better outcomes."** Multi-agent systems multiply the failure modes from truth #5. A "Researcher → Writer → Critic" chain is three loops, not three minds. If a single well-prompted call cannot do the job, three of them dressed in role names usually cannot either; they just cost three times as much and fail in three places. The real reason multi-agent persists is that *role personas* read better in demos than *steps in a function*.

- **"RAG is required for any non-trivial agent."** RAG is a workaround for the fact that you cannot fit your corpus in the context window and cannot fine-tune cheaply. It is a useful workaround in those cases. It is not a fundamental property of agents. If your knowledge fits in the context window, RAG is overhead. If your problem does not need external knowledge at all, RAG is theatre.

- **"A framework ships you faster."** A framework hides the mechanism. The mechanism (tool schema, stop reasons, tool-use blocks, tool-result feedback, message accumulation) is exactly what you have to debug when the agent misbehaves. You debug what you do not understand. Frameworks are accelerators *after* you know the underlying loop, not before.

- **"Long context windows solve memory."** Throwing 200K tokens at the model on every turn pays token cost as RAM cost, with worse retrieval characteristics than an actual database, plus a "lost in the middle" recall curve on top. Context length and memory are different problems. The same context length that "solves memory" also burns latency and money on every call.

- **"Vector DB = memory."** A vector database is approximate similarity search over embeddings. That is a useful retrieval primitive. It is not memory in any cognitive sense. Calling it memory is marketing, and treating it as memory leads to architectures where the agent forgets what it just did because the embedding for "what just happened" was not similar enough to whatever the next query searched for.

- **"Reflection is optional polish."** Reflection ("draft, critique, revise") routinely buys 20 to 40 percent quality on hard tasks for the price of one extra LLM call. Treating it as a nice-to-have means you are leaving the cheapest, best-evidenced reliability gain on the table. By contrast, multi-agent setups often add no measurable lift over a single agent with reflection.

- **"Eval can wait."** "Feels good" is not a contract. Without a golden set and a regression run, every prompt change and every model upgrade is a coin flip. Teams discover this the first time a model provider silently rolls a point release and their agent quietly drops 15 points on the metric nobody was watching.

- **"Autonomous unattended agents."** Truth #5 plus truth #6 makes unattended autonomy in any consequential domain a liability story waiting to happen. Today's agents are best modeled as power tools with a kill switch, not employees.

## Rebuilt From Scratch

If you only started from the six truths and never heard of LangGraph, this is what you would build.

**Default to the smallest possible loop.** A working ReAct agent is 30 lines: send a message, parse the response, if there is a tool call execute it, append the result, send again, stop on a final answer or a step-budget breach. That is the entire substrate. Build it once by hand before you ever import a framework.

```python
from litellm import completion
import json

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
```

LiteLLM is a thin SDK wrapper, not a framework. It buys vendor neutrality (one API, 100+ providers, automatic fallback chains) without hiding the mechanism. Swap models with a string. Fall back to a local model on outage with one extra argument. Same code, different backends.

**Make verification explicit at every step.** Truth #2 says probabilistic output cannot be trusted; truth #5 says unverified intermediate steps compound multiplicatively. Validate every model output against a schema before acting on it. Pydantic at every boundary. Parse, do not believe.

```python
from pydantic import BaseModel, Field, ValidationError

class Result(BaseModel):
    answer: int
    confidence: float = Field(ge=0, le=1)

try:
    result = Result.model_validate_json(raw)
except ValidationError as e:
    raise ValueError(f"LLM output invalid: {e}")
```

**Hard-cap the loop.** Step budget is a numerical safety bound that follows directly from truth #5. Without it the agent burns money or runs forever. There is no scenario where unbounded iteration is correct.

**Trace every call.** Input tokens, output tokens, latency, stop reason, tool calls, tool results. Without traces you have a black box. With traces you have a debugger. This is the same observability rule from [First Principles: Software Observability]({filename}/2026-03-19_first_principles_software_observability.md), specialised for non-deterministic outputs.

**Reflection beats fancier patterns.** "Generate, critique, revise" inside a single agent gives you most of the quality lift that multi-agent setups claim, at one or two extra calls instead of N. Add reflection before you add personas.

**Treat retrieved content as data, never as instructions.** Truth #6. Wrap it in delimiters. Verify intent against the original user request, not against the retrieved text. This is OWASP LLM01 in plain code.

**Pin the model version.** `claude-sonnet-4-6`, not `claude-sonnet-latest`. Pin the prompts as files in a `prompts/` directory and treat them as code: review, version, diff. A "latest" tag in production is a silent regression vector.

Here is what the loop actually looks like when you draw it. Note where verification has to live, and where untrusted content enters the trust boundary.

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

Five boxes do real work. Two boundaries (untrusted content entering context, output before delivery) are where the entire safety story lives. Most of what frameworks add is decoration around this picture.

## What Changes When You Think This Way

- **The 30-line ReAct loop stops being "naive". It is the *correct* substrate.** Frameworks are evaluated against actual needs, not adopted before the loop exists.
- **Multi-agent becomes a last resort, not a first instinct.** You reach for it when a single prompt truly exceeds 1000 tokens of conflicting instructions, and only after reflection has been tried.
- **RAG becomes a tool, not a default.** First question: does the knowledge fit in the context window? Second: does the task even need external knowledge? Skip RAG when both answers say so.
- **Vector DBs stop being called "memory".** They are similarity search, used where similarity search is the right primitive. State and history live in plain databases, where they belong.
- **"Eventually consistent agent reasoning" becomes suspect.** If you cannot say what success looks like, you do not have a goal, you have a wish. Add explicit success criteria and verify against them per iteration.
- **Eval becomes table stakes.** Every prompt change ships with a golden-set run. Every model upgrade is gated by an eval.
- **Single-agent + tools + reflection + traces becomes the boring default.** That stack outperforms most multi-agent crews in production, at a fraction of the cost.

## When You Actually Need an Agent

To be fair to the other side: agentic loops are sometimes the right answer. Here are the only honest triggers.

1. **The task genuinely needs multi-step decomposition.** A single prompt cannot do it because intermediate observations change the next step. Code-fix loops, search-and-summarise loops, browser-driven loops qualify.
2. **You need to call tools at all.** If the work is pure text-in / text-out, you have a structured prompt, not an agent. Stop adding agentic complexity to a function call.
3. **Side effects are gated by a human or by transactional rollback.** Either a human approves consequential actions, or every action is idempotent and revertible. If neither holds, you are accumulating risk.

Notice what is *not* on the list: "we want to use AutoGen", "the architecture diagram needs more boxes", "the demo will look more impressive with three personas". Those are social reasons in engineering clothes. They produce the same kind of résumé-driven architecture the [Distributed Systems]({filename}/2026-04-09_first_principles_distributed_systems.md) post took apart, just dressed in a different jacket.

## The Honest Test

Before your next agent design review, try this exercise. Take your architecture diagram. Cross out every component that is not the LLM call, the tool executor, or the message log. What is left should still answer the question "how does work get done?". If most of the diagram disappeared and the answer is still yes, the rest was decoration. If the answer is no, you have a dependency tree to question, not validate.

Then run the second test. Implement the same task as a 30-line ReAct loop with one tool, one reflection pass, and a step budget of 8. Compare the output against the multi-agent crew. In most cases the simple version is within 5 percent of the complex one, runs in a third of the time, and costs a fifth as much.

LLM agents are not a badge of sophistication. They are a stateless function in a loop with verification, a step budget, and a kill switch. The engineers who ship boring single-agent systems with traces, eval suites, and pinned model versions are not behind the curve. They are the ones who read the curve carefully and refused to pay for complexity they could not justify.

First principles thinking is not about rejecting frameworks. It is about refusing to import a framework before you can write the loop without one. Next time someone says "we need a multi-agent system", ask which of the six truths forces that decision. If they cannot answer, you just found a box to delete.

## References

1. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). Yao et al., 2022. Original ReAct paper.
2. [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). Anthropic, 2024. The single best argument for "start simple, add complexity only when proven necessary".
3. [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/). OWASP, 2025. LLM01 (prompt injection) and LLM06 (excessive agency) are the two that bite agent designs hardest.
4. [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172). Liu et al., 2023. Empirical evidence that long-context retrieval degrades sharply outside the start and end of the window.
5. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366). Shinn et al., 2023. Quantifies the lift from self-reflection.
6. [Agentic Design Patterns](https://www.amazon.com/Agentic-Design-Patterns-Hands-Intelligent/dp/3032014018). Antonio Gulli, 2025. Catalogues the 21 patterns the conventional view treats as orthodoxy.
7. [LiteLLM Documentation](https://docs.litellm.ai/). The vendor-neutral SDK referenced in the example loop.
8. [Model Context Protocol Specification](https://modelcontextprotocol.io/). The wire protocol for tool servers when tool count grows past trivial.
9. [First Principles: Software Observability]({filename}/2026-03-19_first_principles_software_observability.md). Part 1 of this series.
10. [First Principles: Software Design]({filename}/2026-03-21_first_principles_software_design.md). Part 2 of this series.
11. [First Principles: DevOps]({filename}/2026-03-30_first_principles_devops.md). Part 3 of this series.
12. [First Principles: Data Engineering and ETLs]({filename}/2026-04-08_first_principles_data_engineering.md). Part 4 of this series.
13. [First Principles: Distributed Systems (Most of Yours Should Not Exist)]({filename}/2026-04-09_first_principles_distributed_systems.md). Part 5 of this series.
