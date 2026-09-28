Title: Jev: An AI Model That Returns Types, Not Text
Date: 2026-09-28 00:00:00
Category: Engineering
Tags: ai, llm, agents, evaluation, architecture, structured-output
Slug: jev-system-one-models-types-not-text
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: TypeSafe AI's Jev is a "System One model": it takes state and typed questions and returns calibrated probabilities instead of text, in one parallel pass. The speed claims are self-tested, but its evals hide a better lesson: small typed questions glued together by code beat a bigger model with a longer prompt.
Status: published
scratch: ['introducing_system_one_models_jev']

## TL;DR

On 15 September 2026, TypeSafe AI, a startup led by InstructGPT co-author Diogo Almeida, released **Jev**, which it calls the first **System One model**. Jev does not generate text. You send it some state and a set of typed questions (pick one of these options, rate this on a scale, is this statement true?) and it returns a probability for every possible answer, all computed in one parallel pass. Under the hood it most likely keeps the prompt-reading half of an LLM and drops the token-by-token writing half. Input costs $0.042 per million tokens, output is free, and TypeSafe quotes response times of 70 to 500 ms. The headline multipliers, 193.6x faster and 444.6x cheaper, come from TypeSafe's own evals, and TypeSafe itself calls them the high end. The more durable lesson sits in the same eval data: averaged over TypeSafe's four tasks, every model tested, cheap or frontier, got more accurate, cheaper, and faster when the task was split into small typed questions glued together by code.

## What Jev is not

Jev is not a smaller LLM, and it is not JSON mode. Every major LLM API can already return JSON that matches a schema by masking invalid tokens during decoding. That is still text generation with a fence around it: one token at a time, each one billed, parsed and validated afterwards. Almeida argued in the Hacker News launch thread that this kind of **constrained decoding** makes models dumber: if a model puts probability on an invalid token, it is already confused, and the mask only hides that.

Jev drops strings entirely. There is no decoder producing text, so there is nothing to constrain. Answers are values from a set you define up front, which means the model cannot return a malformed response or an option you did not list. That is the precise meaning behind the "can't hallucinate" marketing line, and we will get to where the line stops being true.

## The interface: state in, typed decisions out

A request has two parts. The **state** is whatever the decision is about: a string, a JSON object, or an array of text. The **questions** are typed, and there are three types:

| Primitive | Asks | Returns | Maps to in code |
| --- | --- | --- | --- |
| **Choice** | Pick one option from a list | the choice, a probability per option, a confidence | `match` |
| **Score** | Rate the state on an ordered rubric | a score, a probability per level, a confidence | sorting |
| **Noul** | Is this statement true? | one probability between 0 and 1 | `if` |

The last column is Almeida's own framing from the launch thread: "choice maps to 'match' statement, 'score' maps to sorting, 'noul' short for bernoulli maps to if-statements". That is the whole pitch in one line. Jev is a **smart if-statement**: a branch condition that can read a support ticket.

Notice that you declare every possible answer before the model sees anything. The question schema is a contract between the model and your code. It is the same move I argued for in [First Principles: Data Engineering and ETLs](https://alexsavio.github.io/first-principles-data-engineering): make the agreement between producer and consumer explicit, and the gap between them becomes something you can test.

The official Python SDK makes the shape obvious:

```python
from typesafe_sdk import Choice, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "category": Choice(
                instructions="What is this ticket about?",
                criteria={"billing": None, "technical": None, "other": None},
            ),
        },
    )

print(response.choices["category"].choice)
```

<pre class="mermaid">
flowchart LR
    classDef input fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef model fill:#8839ef,color:#ffffff,stroke:#6c2bd9,stroke-width:2px;
    classDef code fill:#40a02b,color:#ffffff,stroke:#2f7a20,stroke-width:2px;
    S[State<br/>ticket, account, policy]:::input --> J
    Q[Typed questions<br/>Choice, Score, Noul]:::input --> J
    J[Jev<br/>one parallel pass]:::model --> C[Choice + probabilities]
    J --> SC[Score + probabilities]
    J --> N[Noul probability]
    C --> M[match]:::code
    SC --> SO[sort or threshold]:::code
    N --> I[if]:::code
</pre>

Every question is evaluated in isolation against the same state, in the same pass. The docs say adding questions "barely changes the response time" and does not create context rot between them. That flips how you write prompts. Instead of one long instruction that tries to cover every case, you ask every question you might need, including speculative ones, and let your code ignore the answers that do not apply. TypeSafe calls this **speculative fan-out**.

## How it works under the hood

TypeSafe has not published Jev's architecture. Almeida said on Hacker News that it is "close to the chest for now". So this section keeps three kinds of evidence apart: what TypeSafe states, what outsiders measured against the live API, and what is an educated guess. Most of the measurements come from Archer Hume's [Jev's Architecture Unmasked](https://archerhume.com/posts/jevs-architecture-unmasked/), which probed `jev-1.13.0` with more than a thousand instrumented requests on 17 September 2026. Hume treated Jev as a sealed box and worked out its internal state from its external outputs alone: latency, token counts, and probabilities. That is the control-theory definition of observability I built on in [First Principles: Software Observability](https://alexsavio.github.io/first-principles-software-observability), applied to someone else's model.

The short version: **Jev most likely keeps the reading half of an LLM and throws away the writing half.** An LLM processes your whole prompt in one parallel sweep, the **prefill**. Then it spends most of its wall-clock time writing the answer one token at a time, the **decode loop**. Jev stops after the sweep and reads the answer straight out of the model's internal state.

<pre class="mermaid">
flowchart LR
    classDef state fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef branch fill:#8839ef,color:#ffffff,stroke:#6c2bd9,stroke-width:2px;
    classDef out fill:#40a02b,color:#ffffff,stroke:#2f7a20,stroke-width:2px;
    classDef skip fill:#d20f39,color:#ffffff,stroke:#a30826,stroke-width:2px;
    S[State tokens]:::state --> PF[Prefill once<br/>pretrained transformer]:::state
    PF --> KV[(Shared KV cache)]:::state
    PF -. skipped .-> DEC[LLM decode loop<br/>one token at a time]:::skip
    subgraph BATCH[One batch: each branch sees the state, never the other branches]
        direction TB
        Q1[Question 1 + option list]:::branch --> R1[Readout at the<br/>decision position]:::branch
        Q2[Question 2 + option list]:::branch --> R2[Readout at the<br/>decision position]:::branch
        QN[Question N + option list]:::branch --> RN[Readout at the<br/>decision position]:::branch
    end
    KV --> Q1
    KV --> Q2
    KV --> QN
    R1 --> SM[softmax: one probability<br/>per option slot]:::out
    R2 --> SM
    RN --> SM
    SM --> J[Plain code: confidence<br/>arithmetic + JSON]:::out
</pre>

**What TypeSafe states.** Jev "outputs all probabilities in parallel instead of autoregressively generating by token". Its AI primer draws RLCD as a post-training path that starts from a pretrained language model, and Almeida told the Latent Space podcast that even with a billion dollars he "wouldn't pre-train". The docs say Jev "ingests the state once and evaluates every question against it in parallel", with a budget of 64k tokens per request and 32k for the state plus the longest single question.

**What outsiders measured.**

- **Extra questions are almost free, up to a point.** Server time stayed flat up to about 100 questions, and 1,500 questions came back in a median of 610 ms.
- **Questions cannot see each other.** A secret code placed in one question was invisible to a sibling question (probability 0.00). Moved into the state, the same probe found it at 0.90 to 0.92.
- **Options are read together.** Adding an irrelevant fifth option ("bad weather caused it") changed the odds between two existing options in all ten test blocks. Fixed per-option scores behind an unchanged softmax cannot do that. Hume reads it as the options influencing each other, and leaves a list-dependent temperature open as the other explanation.
- **Order matters.** Reversing an option list moved one probability from about 0.84-0.89 to 0.93-0.96. Test permutations before you fix a threshold.
- **`output_tokens` is a billing number.** It is computed from the serialized response after inference, and latency does not follow it.
- **The tokenizer is not a public one.** It matched none of 192 public tokenizers; Qwen came closest, agreeing on 348 of 415 probes.
- **Calibration looks good on average.** On a 1,200-item MMLU sample, the expected calibration error was 0.031. Most of that sample (990 items) sat above 0.9 confidence, and two sparse middle bins (28 and 6 items) were off by 13 and 30 points. Laya's README quotes third-party figures for Jev of 0.144 on its typed-decisions set and 0.246 in a comparison table that does not name the dataset. Calibration depends on the data you measure it on.

<pre class="mermaid">
%%{init: {"themeVariables": {"xyChart": {"plotColorPalette": "#1e66f5"}}}}%%
xychart-beta
    title "Jev server time vs questions per request (median ms, short state)"
    x-axis "questions per request" ["1", "25", "50", "100", "175", "250", "375", "500", "625", "750", "875", "1000", "1125", "1250", "1375", "1500"]
    y-axis "median server time (ms)" 0 --> 700
    line [86.5, 72, 81, 82, 99.5, 132, 162, 181, 213, 245.5, 315.5, 453.5, 358.5, 483, 395.5, 610]
</pre>

Data from Archer Hume's latency sweep: eight requests per size, one at a time, timed with the API's upstream service header. The x-axis is not to scale. The zigzag above 875 questions is probably load noise: the service was shared with other users, and the source does not explain it.

**The likely reconstruction.** Put those facts together and a plausible design falls out:

1. A pretrained causal transformer (Hume bets on a sparse mixture-of-experts) runs the prefill on the state once and keeps its **KV cache**, the stored keys and values that later tokens attend to.
2. Each question (instructions, the option list, and a decision position) runs as its own branch. It attends to the shared state but not to other branches, the same shared-prefix trick that [Hydragen](https://arxiv.org/abs/2402.05099) makes fast. The documented limits fit this shape: 32k tokens per branch, 64k per request, with the state counted once.
3. At the decision position, a small **readout** turns the hidden vector into one number per option slot, and a softmax turns those numbers into probabilities. The 255-option cap is 2^8 - 1. A Noul needs one number and a sigmoid. A Score is a distribution over levels, reported as its probability-weighted average.
4. Ordinary code writes the JSON. There is no decode loop, so there are no generated tokens to pay for.
5. RLCD trains the backbone and the readout against outcomes, probably with a **proper scoring rule** such as log loss, which rewards honest probabilities over confident ones.

Confidence is not a second model either. TypeSafe's own adapter computes Choice confidence as `(p_max - 1/K) / (1 - 1/K)`: how far the top answer sits above a uniform guess over `K` options. Check it on the docs' quick-start example: 0.85 for the top of three options gives 0.775, and the API returns 0.78.

### An open blueprint: Laya

Jev was not the first model to answer with a probability instead of text. In March 2025, Nandakishor M published [SalesRLAgent](https://arxiv.org/abs/2503.23303), a reinforcement-learning model that reads a sales conversation and returns the probability that the sale converts. It works on frozen 3,072-dimension Azure OpenAI embeddings, trains on synthetic conversations generated with GPT-4o, and answers in 85 ms against 3,450 ms for GPT-4. A [September 2025 follow-up](https://arxiv.org/abs/2510.01237) used confidence signals to route LLM queries before generation. That is Jev's core idea (a trained model that returns a number, reinforcement learning, synthetic data), but for one fixed question instead of any typed question you write.

Three days after Jev launched, the same author released **[Laya](https://laya.convaiinnovations.com/)**, an open model (Apache 2.0) with Jev's interface: Choice, Score, and Noul questions over any state. His Hacker News post, "I built non-autoregressive decision models with RL a year ago", reached 1,360 points and became the place where the argument about who did it first played out.

Laya does not tell us how Jev works. What it does give us is one complete, working design for the same interface, in code short enough to read in an afternoon ([`laya/common.py`](https://github.com/NandhaKishorM/laya/blob/9d955671415fc19f069b9cc998928075c1f255ec/laya/common.py)):

<pre class="mermaid">
flowchart LR
    classDef input fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef model fill:#8839ef,color:#ffffff,stroke:#6c2bd9,stroke-width:2px;
    classDef out fill:#40a02b,color:#ffffff,stroke:#2f7a20,stroke-width:2px;
    classDef train fill:#df8e1d,color:#ffffff,stroke:#b8741a,stroke-width:2px;
    SEQ["One sequence per question<br/>[CLS] type + instructions [SEP]<br/>[MASK] opt 1 [MASK] opt 2 ... [SEP]<br/>state [SEP]"]:::input --> ENC[Bidirectional encoder<br/>ModernBERT-large, 421M]:::model
    ENC --> TE[+ question-type<br/>embedding]:::model
    TE --> HEAD[2 extra<br/>transformer layers]:::model
    HEAD --> G[Hidden state at each<br/>option's MASK marker]:::model
    G --> SC[Small MLP:<br/>one logit per option]:::model
    SC --> SM[softmax with a<br/>per-type temperature]:::out
    RW[Training reward: proper scoring rules<br/>log + spherical score,<br/>+ ranked probability score for Score]:::train -. scores these probabilities .-> SM
</pre>

Three details are worth stealing:

- **Options are tokens in the same sequence as the state.** Each option starts with a marker token, the model reads everything at once, and the answer for an option is read from its marker position. In Laya, this design is why options can influence each other. For Jev, it stays a guess: it is one of the two readouts Hume listed as candidates.
- **The state is encoded again for every question.** In a bidirectional encoder the state's tokens also attend to the question, so there is no question-free prefix to cache. That is the price of this design. A causal backbone with a shared state cache, as in the reconstruction above, would avoid it. That would be consistent with Jev's flat latency up to about 100 questions, but it is not proof: Hume notes that his tests cannot tell a causal model from a bidirectional one.
- **The reward is a proper scoring rule.** Log score plus spherical score, and a ranked probability score for ordered Score questions. It is a concrete example of what "RLCD" can mean.

Laya's own numbers are self-reported by a competitor, so read them as such. They still make the most useful point in this whole story. On a set of 2,000 typed decisions across four workflows, zero-shot Laya scores 0.362: barely above random guessing (0.318) and below always picking the most common answer (0.461). Jev scores 0.727. Fine-tuned on that set's training split, Laya reaches 0.766. On Banking77, Laya scores 0.425 on 77 labels against 0.870 for Jev on 72 of them, and its README blames the shared 192 to 256-token budget for all options.

The even cheaper version of the trick needs no new model at all: put numbered options in a prompt to any open LLM, run one forward pass, read the logits of the option-label tokens, and softmax them. [Several open clones](https://sgnt.ai/p/jev/) did exactly that within days of the launch. The early side-by-side tests collected there, most of them from one clone, show the clones trailing Jev by a little on easy yes/no sets and by a lot on harder multiple-choice ones.

Put Laya and the clones together and the lesson is clear. The interface and the single-pass readout are cheap: a 421M encoder and about four hours of fine-tuning on free Kaggle GPUs get you there. Zero-shot judgment on questions nobody trained you for is expensive. You pay for it either with a big pretrained backbone, which is what Jev appears to do, or with fine-tuning data from your own domain, which is what Laya asks of you.

## Calibration is the product

The training method is **RLCD**, reinforcement learning for calibrated decisions. Set it next to the two methods you already know. RLHF trains a model to produce the text people prefer, which made chatbots. RLVR trains on tasks with checkable answers, which made reasoning models good at math and slow. RLCD trains the probabilities themselves: across many answers the model rates at 0.8, about 80% should turn out right.

That sounds academic until you try to automate something. The launch post puts it bluntly: "If a model can do a task 95% of the time but doesn't say when it's in the 5%, it can't automate that task." A calibrated probability gives your code a second axis to branch on. The docs suggest a pattern like this one, where the bar to act rises with the cost of being wrong:

<pre class="mermaid">
flowchart LR
    classDef stop fill:#d20f39,color:#ffffff,stroke:#a30826,stroke-width:2px;
    classDef go fill:#40a02b,color:#ffffff,stroke:#2f7a20,stroke-width:2px;
    A[Choice answer<br/>+ confidence] --> B{confidence<br/>below 0.5?}
    B -- yes --> H[Route to a human]:::stop
    B -- no --> C{Which action?}
    C -- check balance<br/>low stakes --> S[Show balance]:::go
    C -- approve transfer<br/>high stakes --> D{confidence<br/>above 0.9?}
    D -- yes --> E[Confirm, then execute]:::go
    D -- no --> F[Ask the user to confirm]:::stop
</pre>

In [First Principles: LLM Agents](https://alexsavio.github.io/first-principles-llm-agents) I argued that probabilistic output cannot be trusted and must be verified. Calibration does not change that. It hands you a number to verify against, and a threshold is a policy you can review, test, and change in one line.

Almeida's framing for why chat-trained models are the wrong tool here comes from his essay "The Bitterest Lesson": **doing the right task > data > compute > algorithms**. He learned it on InstructGPT, where GPT-2-sized models, over 100x smaller than GPT-3, beat GPT-3 because they were trained on what people actually wanted. RLHF was the right task for chat. His bet is that it is the wrong task for automation.

## The receipts, and the fine print

TypeSafe built four business workflows (security alert triage, agent trace review, invoice processing, customer service) and ran every model through each one. The overall averages, from the [evals site](https://evals.typesafe.ai/):

| Model (vendor) | Mode | Accuracy | Cost per case | Time per case |
| --- | --- | --- | --- | --- |
| Jev (TypeSafe) | workflow | 67.8% | $0.0004 | 0.4 s |
| luna (OpenAI) | workflow | 66.8% | $0.0033 | 12.9 s |
| terra (OpenAI) | workflow | 67.9% | $0.0304 | 10.1 s |
| sol (OpenAI) | workflow | 74.1% | $0.0836 | 23.3 s |
| Opus 5 (Anthropic) | workflow | 73.1% | $0.1761 | 37.8 s |
| Opus 5 (Anthropic) | prompt | 64.8% | $0.3417 | 70.5 s |
| Haiku 4.5 (Anthropic) | workflow | 53.6% | $0.0195 | 12.5 s |
| Haiku 4.5 (Anthropic) | prompt | 18.1% | $0.0363 | 21.2 s |

Read it carefully. Jev is not the most accurate model on the chart: sol and Opus 5 beat it by 6.3 and 5.3 points. What Jev does is match GPT-5.6 Terra's accuracy for roughly 75x less money and 25x less time per case. It owns the cheap end of the frontier, not the top of it.

Now the fine print, most of which TypeSafe discloses itself:

- **No ground truth.** Reference labels are the average of GPT-6 Astra's and Fable 5.1's answers. Accuracy here means "agrees with the two biggest models".
- **Home-grown tasks.** TypeSafe's own team wrote the four workflows and admits "some bias could exist".
- **Self-reported multipliers.** The 193.6x and 444.6x figures come from these workflows, and TypeSafe expects them to be "on the higher end of real world gains".
- **A 0% error rate by construction.** Jev's 0% structured-output and tool-call error rate is a guarantee of the output format, not a measurement. The LLM rates next to it (up to 45.5% for Haiku 4.5 structured outputs) come from OpenRouter traffic, which TypeSafe says is biased.
- **Closed box.** No public benchmarks by policy, no architecture paper, no weights.

Early outside reports lean positive but not uniformly. TechCrunch reported that a Vercel engineer replaced OpenAI's Luna 5.6 command-safety classifier with Jev and got results 5 to 18 times faster, with better accuracy. Bryo AI's CTO found Gemini slightly more accurate for classifying business emails, but 10 to 20 times more expensive.

## The surprising part: structure beats model size

This is the finding I would keep even if Jev disappeared tomorrow. Every LLM in the evals ran each task twice: once as a **workflow** (small typed questions, with code making the final call) and once as a **prompt** (the whole policy in one prompt, reasoned through in chain-of-thought). Averaged over the four workflows, every single model was more accurate, cheaper, and faster as a workflow.

The gaps are not small. Haiku 4.5 goes from 18.1% as a prompt to 53.6% as a workflow. Opus 5, one of the strongest models on the chart, scores 64.8% when handed the prompt, below Jev running the workflow at 67.8%, at roughly 850x the cost per case.

One honest caveat: the reference labels come from running the workflow's questions through Astra and Fable, so the workflow mode plays at home. A prompt that reads an ambiguous policy differently gets scored as wrong. The rule is also an average. Per task, 5 of the 96 workflow-versus-prompt comparisons go the other way: DS v4 flash (DeepSeek) and DS v4 pro each scored higher as a prompt on one task, and Opus 5, sol, and Haiku 4.5 each ran faster as a prompt on one task. Even so, the direction matches what I have seen building agents. As I wrote in [So You Want To Build An LLM Agent](https://alexsavio.github.io/so-you-want-to-build-an-llm-agent), generation is the easy part and verification is the part that breaks. It is also plain software design. In [First Principles: Software Design](https://alexsavio.github.io/first-principles-software-design) I described design as choosing how to decompose one transformation into parts small enough to hold in your head. A typed question is one of those parts. Small typed questions are verification-shaped. Each one can be logged, tested against examples, and thresholded on its own.

## Where it breaks

To TypeSafe's credit, its docs publish a list of nine known failure modes for Jev 1.13. The ones that matter most in practice:

- **Math, counting, and dates.** Jev reads numbers and dates as text. Keep arithmetic and date comparisons in code and ask Jev only for the judgment.
- **Big, noisy state.** Accuracy falls as the state fills with irrelevant detail. Filter first.
- **Inputs it cannot read.** Confidence cannot warn you when a model cannot read the input. Laya's 51-language test shows it best: its English checkpoint scored 0.000 accuracy on Khmer at 0.952 mean confidence. Jev's docs say English is its primary training language and that other languages "are handled but not equally well". Test your own languages before you trust a threshold.
- **Adversarial content.** Text in the state that argues for its own classification "can move the answer". Test prompt injection yourself.
- **No structural guarantees.** Ask "is the customer asking for a refund?" as a Noul and you get 0.22. Ask it as a yes/no Choice on the same ticket and "yes" gets 0.01. Do not assume identities between separate questions hold.

And "can't hallucinate" means it cannot invent a value outside your schema. It can still pick the wrong value, confidently. Almeida agreed on HN: "because these models are probabilistic, it's also possible to be confidently wrong". A commenter there summed Jev up as "basically a zero-shot classifier that can accept raw text". I think that is a fair description, and it is not an insult. A zero-shot classifier with frontier-level judgment, calibrated probabilities, and a price of $42 per billion input tokens is a new building block, whatever you call it.

Where I would reach for it first:

- **Guardrails in agent loops.** Score every tool call or agent trace before it runs. At these prices, you can check every step instead of sampling.
- **Routing and triage.** Tickets to teams, alerts to close, queue, or act, requests to the right model.
- **Classification over large datasets.** Map millions of records into features.

Where I would not: anything that needs generated text, exact arithmetic, or multi-hop reasoning. Keep an LLM for those.

The chat interface made LLMs famous, and it also taught us to bolt a conversation onto places that only needed a decision. Jev's bet is that most automation is an if-statement that has to read. Whether or not TypeSafe's multipliers survive independent testing, the design move works today with any model: turn the policy into small typed questions, let code own the control flow, and gate every action on a probability you can check.

---

## References

1. [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), Diogo Almeida, TypeSafe AI, 2026-09-15, Original source
2. [Workflow evals](https://evals.typesafe.ai/), TypeSafe AI, the four-workflow evaluation and its data
3. [TypeSafe docs](https://docs.typesafe.ai/), primitives, confidence, pricing, and patterns
4. [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13), TypeSafe's own list of known failure modes
5. [The Bitterest Lesson](https://typesafe.ai/blog/bitterest-lesson), Diogo Almeida, on why the right task beats data, compute, and algorithms
6. [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155), the InstructGPT paper
7. [TypeSafe Python SDK](https://github.com/typesafe-ai/typesafe-sdk-python), source of the code example
8. [A new kind of AI model from a ChatGPT inventor is thrilling developers](https://techcrunch.com/2026/09/18/a-new-kind-of-ai-model-from-a-chatgpt-inventor-is-thrilling-developers/), Tim Fernholz, TechCrunch, early developer reports
9. [Introducing System One Models and Jev](https://news.ycombinator.com/item?id=49717558), Hacker News launch thread with replies from the CEO
10. [Jev's Architecture Unmasked](https://archerhume.com/posts/jevs-architecture-unmasked/), Archer Hume, 2026-09-17, black-box probes of the live API and a reconstruction
11. [You could have built Jev](https://sgnt.ai/p/jev/), sgnt.ai, on the single-token logit trick and the open clones
12. [Hydragen: High-Throughput LLM Inference with Shared Prefixes](https://arxiv.org/abs/2402.05099), shared-prefix attention
13. [confidence_metrics.py](https://github.com/typesafe-ai/system-one-adapter-python/blob/fb52b1030b7fc1f4f1cf39910afa5da54f9835e3/src/system_one_adapter/_utils/confidence_metrics.py), TypeSafe's confidence formulas
14. [Jev: System One Models for Prod, Not God](https://www.latent.space/p/jev), Latent Space podcast with Diogo Almeida
15. [Laya: 33ms Multilingual System 1 Decision Engine with Calibrated Probabilities](https://laya.convaiinnovations.com/), Nandakishor M, an open model with Jev's interface
16. [Laya source code](https://github.com/NandhaKishorM/laya), Apache 2.0, including the decision head in `laya/common.py`
17. [SalesRLAgent: A Reinforcement Learning Approach for Real-Time Sales Conversion Prediction and Optimization](https://arxiv.org/abs/2503.23303), Nandakishor M, 2025-03-30, an earlier probability-not-text model for one fixed question
18. [Confidence-Aware Routing for Large Language Model Reliability Enhancement](https://arxiv.org/abs/2510.01237), Nandakishor M, 2025-09-23
19. [I built non-autoregressive decision models with RL a year ago](https://news.ycombinator.com/item?id=49765348), Hacker News thread on Laya and prior work
20. [First Principles: LLM Agents](https://alexsavio.github.io/first-principles-llm-agents), Related post on why probabilistic output must be verified
21. [So You Want To Build An LLM Agent](https://alexsavio.github.io/so-you-want-to-build-an-llm-agent), Related post on why verification, not generation, is the hard part
22. [First Principles: Software Observability](https://alexsavio.github.io/first-principles-software-observability), Related post on inferring internal state from external outputs
23. [First Principles: Data Engineering and ETLs](https://alexsavio.github.io/first-principles-data-engineering), Related post on explicit contracts between producers and consumers
24. [First Principles: Software Design](https://alexsavio.github.io/first-principles-software-design), Related post on design as decomposition
