Title: Torvalds on AI: It Is a Tool, and 100% of Your Code Was Always Written by Compilers
Date: 2026-06-09 00:00:00
Category: Engineering
Tags: ai, code-generation, open-source, llm, agents, maintainers
Slug: torvalds-ai-is-a-tool-not-a-replacement
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: Linus Torvalds says he gets angry hearing "99% of our code is AI", because 100% of it was already written by compilers and nobody brags about that. AI is a productivity tool in the compiler lineage, and its real cost in open source is maintainer burnout from drive-by bug reports.
Status: published
scratch: ['torvalds_ai_programming_productivity']

## TL;DR

At the Open Source Summit North America in late May 2026, Linus Torvalds spent part of his keynote pushing back on a now-familiar claim: that AI is about to make programmers redundant. His sharpest line was aimed at the boast you hear everywhere lately, "99% of our code is written by AI." It makes him angry, he said, because 100% of those same people's code was already written by **compilers**, and nobody ever brags about that. His point is not that AI is useless. It is that AI is a tool in a long line of tools, the same lineage as assemblers and compilers, and it does not remove the need to understand the system underneath. He even put rough numbers on it: compilers made programming maybe **1,000 times** more productive, and AI adds something like **10x** on top.

The part most hot takes skip is what comes next. The immediate cost of AI in open source is not bad code. It is **burnout**, the slow grind of maintainers drowning in AI-generated bug reports that show up without a fix attached.

A quick boundary before we go further: this post is not about whether LLMs can write code. They obviously can, and they are good at it. It is about the framing Torvalds is attacking, the idea that a percentage of "AI-written code" tells you anything useful, and about what the current AI surge is quietly doing to the people who maintain the software you depend on.

## The compiler argument

Torvalds' best move here is rhetorical, and it works because it is true. Every developer who says "AI wrote 99% of this" is already standing on a mountain of code generation they never think to mention.

Here is the thing. You write source code, and a **compiler** turns it into machine code. You did not place the registers, pick the instructions, or lay out the stack frames yourself. A tool did all of that, and it has for decades. So by the same logic the AI crowd is using, 100% of your output has been machine-written since long before anyone had heard of an LLM. The percentage was never the interesting number.

<pre class="mermaid">
flowchart LR
    classDef big fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef small fill:#40a02b,color:#ffffff,stroke:#2f7a20,stroke-width:2px;
    A[Machine code<br/>by hand] --> B[Assembler]
    B --> C[Compiler<br/>~1,000x]:::big
    C --> D[AI assist<br/>~10x]:::small
</pre>

What this framing does is put AI on a continuum instead of a cliff edge. Every step up the abstraction ladder, machine code to assembly, assembly to Fortran, raised productivity and pushed the human a little further from the metal. And honestly, the jump from hand-written assembly to a compiler was a far bigger deal than the one from a modern IDE to an AI assistant. Put Torvalds' rough figures next to each other, around 1,000x for compilers against 10x for AI, and the proportion speaks for itself. None of that means AI does not matter. It means we have lost the sense of scale.

The line worth keeping is this one: **"AI is changing programming, but it's not changing the fun."** The thing that makes programming engaging, getting to know a system well enough to bend it to your will, is exactly the part that does not get automated away.

## The skill gap does not close, it moves

The tempting story about AI coding tools is that they flatten expertise. Anyone can write a prompt, so everyone is a senior engineer now. Torvalds says the opposite, and I think he is right.

> "People who know what they're doing to understand systems will be able to prompt tools to write good code. People who don't understand the complexity of systems will also prompt systems and write processes that will fail."

The prompt is not the skill. The skill is the judgment: knowing whether the code that comes back is correct, safe, and something you will still want to maintain in five years. If you already have that judgment, AI raises your ceiling. If you do not, it mostly raises your confidence, and the output looks just as polished either way. That is the trap.

This is the same place I landed writing about [LLM agents from first principles](https://alexsavio.github.io/first-principles-llm-agents). The model is a stochastic text generator, and everything that actually carries weight (verification, state, control flow) lives in the system you build around it. Strip away the hype and the human's job has not really changed: understand the system, check the output, own the result.

## The part nobody tweets: maintainer burnout

This is where Torvalds shifts from a fun rhetorical jab to something genuinely important and weirdly underdiscussed.

AI turns out to be good at finding bugs in old code. The Linux kernel has more than **35 years** of history behind it, and AI tools are surfacing real, hidden issues. Sounds like a clean win, until you ask the obvious follow-up: who fixes them?

The kernel can cope, because it has people. The thousands of one-to-three-person projects sitting underneath your stack cannot. They are now getting a steady trickle of **AI-generated bug reports and pull requests** with no patch attached, and often no human on the other end who will answer when you ask a follow-up question.

> "Sometimes AI reports a bug, and when you ask for more information, the person has done that drive-by and doesn't even answer your question. So, that's the real burnout issue."

<pre class="mermaid">
flowchart TD
    classDef bad fill:#d20f39,color:#ffffff,stroke:#a30826,stroke-width:2px;
    A[AI scans open-source code] --> B[Finds real bug]
    B --> C{Patch included?}
    C -->|No, drive-by| D[Maintainer must triage,<br/>reproduce, fix, answer]
    C -->|No follow-up| E[Maintainer asks for info]
    E --> F[Silence]
    D --> G[Burnout]:::bad
    F --> G
</pre>

Torvalds is blunt about the incentive driving some of this. Companies spend "a lot of money and a lot of tokens" finding bugs in open source so they can put out a press release, and, as he points out, **none of them ship a patch**. Finding a vulnerability and dumping it on an unpaid maintainer is not a contribution. It is handing your work to someone who did not ask for it and calling it security research.

And this is not hypothetical. The kernel is actually the resilient case here. In early 2026, **Daniel Stenberg ended curl's HackerOne bug bounty** because his security team was drowning in what he called "AI slop", confident, fabricated vulnerability reports where the hit rate had fallen to something like one in twenty. A seven-person team, offering up to $10,000 for a critical bug, decided it was better to shut the program down than keep triaging machine-generated noise. There is a darker version of this too. The **xz-utils backdoor** (CVE-2024-3094) was planted by an attacker who spent more than two years quietly befriending a single, overworked maintainer, with sock-puppet accounts piling on exactly the "why are you so slow" pressure that wears an exhausted volunteer down. Drive-by AI reports do not just waste time. They burn the attention that is supposed to catch the real attack.

The kernel's own numbers show the strain. In the run-up to the **7.1** release, maintainers saw more commits during prep than in any release before it, roughly **20%** more submissions, and it turned out the bump came from AI use rather than a sudden surge of human interest. More throughput sounds great right up until you remember every one of those still needs a human to read it.

When someone asked which AI tools the kernel uses to review incoming patches, Torvalds named one and moved on. The specific tool barely matters. Even with it, humans still have to maintain, review, and vouch for every fix that lands. The bottleneck just moved, from writing the patch to standing behind it, and that part is still stubbornly human.

## Where the boosters have a point

In fairness to the other side, and it is worth being fair, AI genuinely does collapse a lot of work. Boilerplate, test scaffolding, glue code, translating between languages, poking around an unfamiliar API: all of it goes faster with a decent model in the loop. Torvalds is not denying any of that. He is the one who put the number at roughly 10x. The argument is not whether AI helps. It is about what the help actually means.

Where the boosters go wrong is the leap from "AI writes the easy 80% fast" to "AI writes 99% of what matters." That last 20%, the part where you need to understand why the system is shaped the way it is, is where the real engineering lives, and it is exactly the part that does not compress. Making the easy work instant does not make the hard work easy. It just leaves you with nothing but the hard work.

## What this means if you ship software

So what does all of this add up to if you actually ship software for a living?

- **Stop quoting "% AI-written."** It measures nothing. It never did for compilers and it does not now. The questions that matter are whether the code is understood, tested, and owned.
- **The bottleneck is review, not generation.** AI made writing cheap and turned review into the scarce resource, so budget for it. It is the same lesson from [building real agents](https://alexsavio.github.io/so-you-want-to-build-an-llm-agent): generation is the easy 80%, and verification is the 20% that breaks in production.
- **If you point AI at open source, bring a patch.** A bug report with no fix and no human to follow up is a tax on a volunteer. If your company harvests vulnerabilities for marketing, you are the burnout Torvalds is describing.
- **Expertise compounds, it does not evaporate.** AI rewards the people who understand systems and quietly punishes the ones who do not. Invest in the understanding, not the prompt library.

Strip it all back and the "99% of our code is AI" boast is really a status claim wearing the costume of a metric. Torvalds' reply cuts through it cleanly: you have been generating code with tools your whole career, so the only questions worth asking are whether you understand what comes out the other end, and who pays when it breaks. AI changed the tooling. It did not change the job, and it did not change the fun.

---

## References

1. [Why Linux creator Linus Torvalds gets angry hearing "99% of code is AI"](https://thenewstack.io/torvalds-ai-programming-productivity/), B. Cameron Gain, The New Stack, 2026-05-29, Original source
2. [Open Source Summit North America](https://events.linuxfoundation.org/open-source-summit-north-america/), where the keynote was delivered
3. [The end of the curl bug-bounty](https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/), Daniel Stenberg, on ending curl's bounty over AI slop
4. [XZ Utils backdoor (CVE-2024-3094)](https://en.wikipedia.org/wiki/XZ_Utils_backdoor), the single-maintainer social-engineering supply-chain attack
5. [First Principles: LLM Agents](https://alexsavio.github.io/first-principles-llm-agents), Related post on what survives when you strip the agent hype
6. [So You Want To Build An LLM Agent](https://alexsavio.github.io/so-you-want-to-build-an-llm-agent), Related post on why verification, not generation, is the hard part
