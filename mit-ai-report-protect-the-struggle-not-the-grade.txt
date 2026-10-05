Title: MIT's AI Report: Protect the Struggle, Not the Grade
Date: 2026-10-05 00:00:00
Category: Engineering
Tags: ai, llm, education, code-generation, productivity
Slug: mit-ai-report-protect-the-struggle-not-the-grade
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: MIT's AI committee says AI broke the proxies we use to measure learning. It rejects detectors and one campus-wide rule, and asks for AI-aware courses and assessment.
Status: published
scratch: ['mit_ai_use_in_teaching_learning_and_research_training']

## TL;DR

On 13 August 2026, MIT's **Ad Hoc Committee on AI Use in Teaching, Learning, and Research Training** published its final report after five months of meetings, surveys, and listening sessions. Asked for an AI use policy, it came back with a bigger claim: generative AI can already produce credible answers to almost any written assignment in MIT's undergraduate curriculum, so problem sets, take-home exams, and essays no longer prove that anyone learned anything, and students can skip the **productive struggle** where the learning actually happens. The committee rejects a single campus-wide AI rule, AI detectors, and grade rationing, and recommends instead a four-option course policy menu with a stated rationale, more oral and project-based assessment, in-person social learning, protected research apprenticeships, and permanent machinery to keep revising all of it.

The outside evidence, much of it from short trials and preprints, points the same way. In the largest field experiment, a chatbot that handed out answers raised practice scores and lowered unassisted exam scores. Trials of AI that makes students explain and think found gains instead, more than double in one Harvard physics study. The biggest takeaway: AI did not break learning by itself. It broke the **proxy** we used to measure learning, and used as an answer machine, it lets students skip the learning too.

## What this report is not

This is not a "university bans ChatGPT" story, and it is not an AI cheerleading memo either. The committee explicitly argues against policing: no reliance on AI detectors, no lockdown browsers for now, no grade rationing. It also does not ask anyone to stop using AI. Some courses, it says, should *require* it.

What it is: a five-month attempt by students, faculty from every school, and staff (including the MIT Libraries and the Teaching and Learning Lab) to answer a harder question than "is this cheating?" The question is what an education is for when a chatbot can produce the deliverables. If you lead an engineering team that hires juniors, most of this report applies to you too.

## AI broke the proxy first

A problem set was never the point. It was evidence. You struggled through it, the struggle built understanding, and the answers you handed in were a cheap way for an instructor to check that the struggle had happened. That chain held for decades because there was no way to get the answers without doing the work.

Now there is. In the report's words, these technologies "can produce credible solutions and provide reasonable responses to almost any written assignment in our undergraduate curriculum, including essays, math and science problems, proofs, and coding assignments." Using a chatbot to do your problem set is like sending a robot to the gym on your behalf. The logbook fills up. Your muscles do not change.

That is not only a metaphor. In a field experiment with nearly 1,000 Turkish high school students ([Bastani et al., PNAS 2025](https://doi.org/10.1073/pnas.2422633122)), access to GPT-4 during practice sessions raised practice grades by 48%. On the unassisted exam that followed, the same students scored 17% lower than classmates who never had access. A second version of the chatbot, told to give teacher-designed hints instead of answers, raised practice grades by 127% and only erased the harm: no gain on the exam. The proxy went up while the learning went down.

<pre class="mermaid">
flowchart LR
    classDef work fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef learn fill:#2f7a20,color:#ffffff,stroke:#1f5216,stroke-width:2px;
    classDef skip fill:#d20f39,color:#ffffff,stroke:#a10c2d,stroke-width:2px;
    subgraph Before["Before: the answers are evidence"]
        A1[Problem set]:::work --> S1[Productive struggle]:::work
        S1 --> L1[Learning]:::learn
        S1 --> O1[Answers handed in]:::work --> G1[Grade]:::work
    end
    subgraph After["With unrestricted AI"]
        A2[Problem set]:::work --> C2[Chatbot]:::skip --> O2[Answers handed in]:::work --> G2[Grade]:::work
        A2 -.-> L2[Learning skipped]:::skip
    end
</pre>

Why does skipping the struggle cost so much? Because the struggle is where the learning happens, and that is not a romantic idea. A meta-analysis of 53 studies found that students who wrestle with a problem before they are taught the solution learn more than students who are taught first (Hedges' g of 0.36), as long as instruction follows the struggle ([Sinha and Kapur, 2021](https://doi.org/10.3102/00346543211019105)).

The committee names the failure mode **cognitive surrender**: falling back on AI at the first hint of struggle. Students told the committee the temptation peaks when they fear missing a deadline. Getting the right answer from a chatbot, the report warns, "can create the illusion of learning."

The preprint behind that term puts numbers on it ([Shaw and Nave, 2026](https://doi.org/10.31234/osf.io/yk25n_v1)). Across three preregistered experiments with 1,372 people, participants solved reasoning puzzles with an AI assistant that was secretly wrong on some of them. In the first study, people who consulted it followed its wrong answers 79.8% of the time, and access to the AI raised their confidence by 11.7 percentage points. Persistence suffers too. In randomized trials with 1,222 people ([Liu, Christian and colleagues, COLM 2026](https://arxiv.org/abs/2604.04721)), about ten minutes of AI help was enough. In the first trial, once the AI was taken away, participants had a solve rate of 0.57 against 0.73 for a control group, and they skipped more problems.

The damage is social as well as cognitive. In less than three years, the report says, AI has driven decreased attendance at office hours, reduced participation in online discussions, and, anecdotally, fewer in-person study groups. Meanwhile instructors feel like police, and students fear false accusations of cheating while resenting instructors who use AI to grade. The committee's phrase for this is memorable: "an underground river of mutual suspicion."

## Eight principles before any rules

Before it recommends anything, the report sets out eight principles. They are worth reading as a set, because they rule out most of the knee-jerk responses.

| Principle | What it means in practice |
|---|---|
| Be humble | Generative AI became usable in late 2022, so public use is less than four years old. Expect course corrections. |
| Be bold | No "patches and duct tape". Redesign courses, assessments, and curricula. |
| Put humanity front and center | Protect the community and its relationships, even when AI is faster or cheaper. |
| Lean into learning | Struggle is the process. The product of an education is the student, not the GPA. |
| Teach with intentionality | Use **backward design**: define what students should know, do, and value, then design assessments to match. |
| No one size fits all | A poetry seminar, a proof course, and a design studio need different AI policies. |
| Augmentation not automation | AI should expand what students can think about, not do the thinking for them. |
| Think beyond the classroom | Students carry the habits they learn here into work and society. |

The "augmentation not automation" principle borrows from MIT economists Daron Acemoglu, David Autor, and Simon Johnson, who argue for **pro-worker AI**: systems that make people more effective at existing tasks and help them learn new ones, instead of replacing them. The committee's version is "pro-learner" AI. It is the same stance Linus Torvalds took when he called AI [a tool in the compiler lineage, not a replacement]({filename}/2026-06-09_torvalds-ai-is-a-tool-not-a-replacement.md).

Recent randomized trials split along exactly this line. The same technology helps or hurts depending on whether it does the thinking or prompts it:

| Study | Setup | Result |
|---|---|---|
| [Shen and Tamkin, Anthropic, 2026](https://arxiv.org/abs/2601.20245) (preprint) | 52 mostly junior developers learn a new Python library, with or without AI | The AI group scored 50% on the follow-up quiz against 67% without AI, and was not significantly faster. Developers who only asked conceptual questions kept their learning; delegating the code is what hurt. |
| [Contractor and Reyes, 2026](https://arxiv.org/abs/2607.08849) (preprint) | 211 undergraduates use off-the-shelf AI in one session, then are tested unaided a week later | AI raised test scores by 0.27 standard deviations, and the gains persisted. Essay gains a week later were larger for students who used AI to explain concepts; for students who used it to generate text, the short-run gains vanished once AI was removed. |
| [Kestin et al., Scientific Reports 2025](https://doi.org/10.1038/s41598-025-97652-6) | Harvard intro physics: a custom AI tutor built on teaching research vs an in-class active-learning lesson | Median learning gains were more than double, with a median 49 minutes on task against a 60-minute class. |
| [Wang et al., Tutor CoPilot](https://arxiv.org/abs/2410.03017) (preprint) | 900 human tutors and 1,800 K-12 students; the AI coaches the tutor, not the student | Students were 4 percentage points more likely to master topics, and 9 points more for students of lower-rated tutors. |
| [Liu et al., 2026](https://doi.org/10.26300/y3f8-vh05) (working paper) | 2,379 undergraduates at a large US public university; an AI tutor built into the course | Tutor access lowered final grades by 0.27 to 0.37 standard deviations, with the clearest evidence among sections of the same course, and larger losses for first-generation students. |

The last row is the warning label. Calling something a "tutor" does not make it one, and the students who lost the most were first-generation students, often the ones a free tutor is meant to help. What matters is whether the design makes the student do the thinking, and that is what the committee means by augmentation.

One caution on all of this evidence: most of these studies are short, several are preprints or working papers, and none was run on MIT courses. Read them as a direction, not a dose.

## The obvious fix is a trap

Here is the counter-intuitive part. When take-home work stops being trustworthy, the instinct is to move the weight of the grade into timed, in-class exams. Many instructors are already doing exactly that.

The committee argues this backfires. Students lose the incentive to invest in the difficult problem sets and projects that build mastery, and a time-limited exam caps how much thought anyone can put in. In the report's words, quick, high-stakes evaluations "embody the opposite of the signal we want to convey." It also risks narrowing what an MIT degree has long signaled: that its graduates "are capable of difficult, independent, and thought-intensive problem solving, not just acing exams on paper."

The same logic kills **grade rationing**. Limit the number of A's, and students who want to protect their GPA get an even stronger reason to cut corners with AI. The committee goes further and floats a thought experiment: if MIT had no grades, many of the incentives behind AI cheating would disappear.

What it recommends instead:

- **Assessments that resist AI and teach at the same time**: oral exams, semester portfolios, and out-of-class work paired with in-class conversations about it.
- **Process evidence**: platforms that record a version history, so a submission that appears minutes after the assignment opens stands out. Students also use these histories to reflect on how their thinking evolved.
- **Experiential and project work**: in MIT's capstone software engineering class, students can now reasonably build near production-quality software in a single term with AI coding tools. Raise the ambition instead of fighting the tools.
- **A regular in-person social component in every subject**: group work with check-ins, TA-guided problem sessions, graded discussions.

## A policy menu, not a rule

Students told the committee that AI guidance is confusing and varies wildly between instructors. The committee still refuses a single campus rule, because any uniform rule would be too permissive for some courses and too strict for others. Its answer is a shared menu, chosen per course or per assignment, with a traffic-light icon for each option:

<pre class="mermaid">
flowchart TD
    classDef step fill:#1e66f5,color:#ffffff,stroke:#1e4ed8,stroke-width:2px;
    classDef green fill:#2f7a20,color:#ffffff,stroke:#1f5216,stroke-width:2px;
    classDef yellow fill:#df8e1d,color:#1e1e2e,stroke:#b5730f,stroke-width:2px;
    classDef red fill:#d20f39,color:#ffffff,stroke:#a10c2d,stroke-width:2px;
    G[Learning goals: what students should know, do, and value]:::step --> A[Assessments that measure those goals]:::step
    A --> P{Pick an AI policy per course or assignment}:::step
    P --> U[Unrestricted use]:::green
    P --> S[Support tool only]:::yellow
    P --> R[Required use]:::green
    P --> X[Strictly prohibited]:::red
    U --> W[Post it in the syllabus, with the rationale]:::step
    S --> W
    R --> W
    X --> W
</pre>

| Policy | Rule | Best suited for |
|---|---|---|
| Unrestricted | Any GenAI system, any purpose | Courses assessed in class, or projects too ambitious for current tools |
| Support tool only | Tutor, editor, debugger; no full or substantial solutions | Courses where independent problem solving is central |
| Required | Use the designated tools and workflow, document the interactions | AI-assisted programming, prompt engineering, critique of model outputs |
| Strictly prohibited | No GenAI in any form | Not stated; the committee warns it is hard to enforce outside class |

Two details make this work. First, every policy needs a **rationale tied to the course's learning goals**. Declaring AI use to be cheating teaches nothing. Explaining that AI skips the exact skill the exam will test teaches students to think about their own learning. Second, the committee admits the middle option is the hardest: students and faculty disagree about whether an AI-written outline counts as "support".

MIT is not alone in refusing a single rule. Brown's July 2026 committee report puts it plainly: "There is no one-size-fits-all approach." Harvard's faculty also set policy course by course, but lean much harder toward restriction. In The Harvard Crimson's 2026 survey of Faculty of Arts and Sciences members, 64% said AI had a negative effect on their courses, and 24% now prohibit AI entirely, the one option MIT's committee calls hard to enforce.

## No detectors, and not these lockdown browsers

The committee recommends against relying on **AI detectors**. They miss mixed work, such as an AI-drafted outline. They invite an arms race with "AI humanizers". And they can mistake the writing of non-native English speakers or neurodivergent students for AI output. Even MIT's Committee on Discipline does not consider detector output alone sufficient evidence.

The evidence is on the committee's side. In a 2023 peer-reviewed test of seven detectors of that time ([Liang et al., Patterns 2023](https://doi.org/10.1016/j.patter.2023.100779)), the average false-positive rate on 91 TOEFL essays by non-native speakers was 61.22%, while essays by US eighth graders were classified almost perfectly. OpenAI withdrew its own AI-text classifier on 20 July 2023 "due to its low rate of accuracy"; at launch it caught 26% of AI-written text. A 2026 preprint from Notre Dame ([Karr et al.](https://arxiv.org/abs/2608.11256)) shows the arms race in one result: after a humanizer pass, fewer than 4% of AI rewrites were still flagged, while light, guideline-style AI edits were flagged 38 to 80% of the time. Honest AI editing, the authors write, "results in a higher sanction risk than humanizer-assisted evasion." Brown's report found the same consensus among its peers: of 13 Ivy Plus and Public Ivy institutions with medical schools, seven recommended against, discouraged, or did not endorse detection software, and none endorsed it.

**Lockdown browsers** get a softer no. The committee asks MIT to study them, but calls the current generation "buggy, error-prone and feels like surveillance." For now, in-person proctored exams are the better choice, which means MIT needs more physical space for them.

The report also turns the mirror on instructors. Students notice when an instructor uses AI for slides, feedback, or grading while restricting students, and they read it as a double standard. One refrain the committee heard: "Why should I bother coming to class or doing the work if the teacher is just going to give an AI-generated lecture?" The fix is disclosure: if AI generates course content or touches grading, say so and explain why. AI graders can still be useful, as a feedback tool handed to students along with the assignment, not as the final judge.

## The part engineers should read twice: apprenticeship

MIT's **Undergraduate Research Opportunities Program (UROP)** started in 1969 and today directly engages 93% of undergraduates and 58% of faculty. In a listening session, the committee learned that some instructors were considering AI agents as research assistants instead of hiring undergraduates.

The committee's answer is blunt. UROP exists to educate, not to supply research labor. Learning by doing "may produce seeming 'inefficiencies,' but that's a feature, not a bug." Replace novices with agents and students lose more than research hours. They lose the path into a research community: joining a lab, presenting at group meetings, learning how credit is shared and how mistakes are handled.

The report does not say this, but every word transfers to software teams. The ticket a junior engineer needs three days to close is their apprenticeship. An agent can close it faster, and the sprint looks better for it. Do that for a few years and you have no mid-level engineers to promote, because nobody got the reps. The "inefficiency" was the training program. It is the same point I took from Torvalds: [the skill gap does not close, it moves]({filename}/2026-06-09_torvalds-ai-is-a-tool-not-a-replacement.md). If you already have the judgment, AI raises your ceiling. If you do not, it mostly raises your confidence. Shaw and Nave saw that second half in the lab: access to AI raised confidence on reasoning puzzles even though about half of its answers were wrong.

The labor data points the same way, though none of it proves that AI is the cause. Working from ADP payroll records, Stanford's Digital Economy Lab finds that employment of 22-to-25-year-olds in AI-exposed occupations now sits 19% below where it would be had it kept pace with less-exposed peers, while experienced workers show no comparable gap ([Brynjolfsson, Chandar and Chen, August 2026 update](https://digitaleconomy.stanford.edu/news/canariesaug26/)). The authors call these early, descriptive indicators rather than causal estimates. The gap comes "primarily through reduced hiring of young workers rather than increased separations": fewer people get onto the entry rung, while the people already on it stay. A Harvard working paper sees the same inside firms: after generative AI adoption, junior employment at adopting firms fell 7.7% relative to controls within six quarters, driven by slower hiring ([Hosseini and Lichtinger, 2025](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5425555)). Software sits at the extreme. In Indeed's postings data, software development had the lowest entry-level share of any sector in Q1 2026, 4.5%, and the highest senior share, 69.3% ([Indeed Hiring Lab](https://hiringlab.indeed.com/2026/07/23/the-labor-market-is-tilting-toward-seniority/)). Indeed itself lists remote work and interest rate hikes as competing explanations. Still, the direction matches the committee's UROP worry.

The survey data hints that students feel this already. In MIT's spring 2026 Quality of Life survey, undergraduates felt more replaceable than capable because of AI (40% vs 34%), while grad students, postdocs, and faculty leaned the other way by a wide margin. The only other group leaning replaceable was service and support staff:

<pre class="mermaid">
%%{init: {"themeVariables": {"xyChart": {"plotColorPalette": "#d20f39"}}}}%%
xychart-beta
    title "AI makes me feel more replaceable (% rating 1 or 2)"
    x-axis ["Total", "Admin", "Faculty", "Grads/Postdocs", "Undergrads", "Service/Support"]
    y-axis "% of respondents" 0 --> 50
    bar [27, 24, 20, 26, 40, 36]
</pre>

| Group | More capable (4 or 5) | More replaceable (1 or 2) |
|---|---|---|
| Total (n=8,207) | 40% | 27% |
| Admin (n=2,572) | 40% | 24% |
| Faculty/Instructors (n=701) | 46% | 20% |
| Grad Students/Postdocs (n=2,344) | 49% | 26% |
| Undergrads (n=1,360) | 34% | 40% |
| Service/Support (n=806) | 24% | 36% |

*Values read from the report's published chart. The report's text states the totals and the undergraduate 40% vs 34% split. Undergraduates and service and support staff are the only groups where the replaceable share is larger than the capable share.*

## Teach AI, and make access fair

The committee wants AI skills taught on purpose, in three layers. **Effective** use: how to specify a problem, how to verify an output, when a model is likely to hallucinate, and when not to reach for AI at all. **Responsible** use: knowing the difference between augmentation and automation, and disclosing AI's contribution honestly. **Ethical** use: training data provenance, bias, homogenized outputs, environmental cost, and authorship. Verification is the layer most people skip, and it is the one I keep coming back to when [building LLM agents]({filename}/2026-05-08_so_you_want_to_build_an_llm_agent.md). Order matters too: build the agent loop by hand before you reach for a framework, because you cannot debug what you do not understand. The report makes the same distinction: a first-year student "building foundational skills and judgment" stands in a different relationship to AI than a doctoral candidate speeding up a literature review in a field they already know.

The demand is real. In The Tech's fall 2025 survey, 70% of responding students agreed that AI proficiency will matter in their careers, but only 25% believed MIT is preparing students to use it professionally. The same survey found 46% of undergraduates use LLMs daily, and 90% are somewhat or very concerned about overreliance, 67% very concerned.

Access is the other half. Top-tier commercial plans cost as much as $200/month (as of June 2026), and some students pay it while their peers cannot. MIT's model-agnostic platform, **Parley**, gives everyone up to $30/month in free credits across commercial and open models, and it added API access for coding tools in the summer of 2026. The committee wants it kept model-agnostic, with more access where courses need it. It also flags a problem every company running an internal LLM gateway should recognize: an MIT-run system can, in theory, see every prompt. People already use these tools for emotional support, as they did with MIT's own ELIZA, so MIT needs an explicit policy on logging and auditing before an incident forces one.

## The machinery to keep revising

Because the technology moves faster than any report, the committee asks for permanent structures:

- An **ongoing AI and education committee** for strategy, monitoring, and policy.
- **AI Leads** in each school and the college, or in each department.
- **AI Fellows and an AI Implementation Team** to help instructors redesign courses, since the Teaching and Learning Lab is already at capacity.
- An **AI Pilot Fund** for AI credits, TAs, UROPs, and summer support, including funding for deliberately AI-free experiences.
- Training built by MIT's own community, not "checking the box" with generic third-party courses.
- **Metrics** on AI use, engagement, and student satisfaction, plus published estimates of what AI use costs in money and environmental impact.

Theses get a concrete rule: every thesis should include a statement on how AI was used, and AI should never be listed as a co-author. The committee practices this itself. Its appendix states that none of the report's text was generated with AI. ChatGPT checked early drafts for redundant sections, Codex generated some of the survey graphs, and members used AI to synthesize data and reports, such as summaries of other schools' published positions, for their discussions.

MIT's leadership has picked the report up. In a letter on 25 August 2026, President Sally Kornbluth wrote that the opportunities and risks generative AI poses for MIT's model of education and research "now constitute such a watershed for MIT." She listed "ensuring that every class has an AI use policy suited to its purpose" among the practical changes ahead, and wrote that the Institute is "aggressively developing guidance, instruction, models, pilot funding, and 'communities of practice' to help meet the moment."

## Where the report is thin

The diagnosis is sharp. A few parts deserve pushback.

- **Its own data cuts against "students are confused."** In the Quality of Life survey, 72% of undergraduates agreed MIT had given them adequate guidance on AI, and the report notes the other groups reported much lower levels. In The Tech's survey, 75% of undergraduates found faculty expectations clear. The bigger guidance gap may sit with instructors and staff, which is where the AI Leads and Fellows should start.
- **The costs are named, not priced.** Oral exams, smaller classes, more TAs, and staffed lab spaces all cost money and instructor time. The report admits the redesign effort "is likely to be significant" but gives no budget.
- **The committee's own survey is self-selected.** It received 1,632 responses, a 12% response rate. Treat its percentages as a signal, not a census.
- **Graduate students want a seat at the table.** The Tech reports that MIT's Graduate Student Union has proposed contract language to stop MIT from using AI to replace graduate student labor, and argues that MIT "can't have the right to unilaterally impose these changes on the graduate population without further discussion." Teaching and research assistants are apprentices too, so this is the UROP argument from the other side.

## Protect the struggle

The line I would put on every syllabus, and in every engineering onboarding doc, is this one: the most important product of an education "is not a GPA or a diploma but *themselves*." Grades, problem sets, and closed tickets were always proxies for that growth. AI made the proxies cheap, so the committee wants MIT to defend the growth directly, with conversations, projects, mentors, and honest policies instead of detectors. Companies face the same choice with their juniors. Let an agent take every hard ticket and you save a sprint and lose a future senior engineer. Protect the struggle, not the grade.

---

## References

1. [Report of MIT's Ad Hoc Committee on AI Use in Teaching, Learning, and Research Training](https://aiandeducation.mit.edu/report/), MIT, 2026-08-13, Original source ([PDF](https://aiandeducation.mit.edu/files/2026/09/AI-Committee-Final-Report-Aug-13.pdf))
2. [Appendices: committee process, sample AI policies for syllabi, and survey results](https://aiandeducation.mit.edu/appendices/), MIT, 2026-08-13, Original source
3. [Ad Hoc Committee on AI Use in Teaching, Learning, and Research Training](https://facultygovernance.mit.edu/committee/ad-hoc-committee-ai-use-teaching-learning-and-research-training), MIT Faculty Governance, the committee's charge
4. [When Problem Solving Followed by Instruction Works: Evidence for Productive Failure](https://doi.org/10.3102/00346543211019105), Tanmay Sinha and Manu Kapur, Review of Educational Research, 2021, meta-analysis of 53 studies ([open copy](https://www.research-collection.ethz.ch/handle/20.500.11850/490417))
5. [Generative AI without guardrails can harm learning: Evidence from high school mathematics](https://doi.org/10.1073/pnas.2422633122), Hamsa Bastani et al., PNAS, 2025 ([open copy](https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635/))
6. [Thinking, Fast, Slow, and Artificial: How AI is Reshaping Human Reasoning and the Rise of Cognitive Surrender](https://doi.org/10.31234/osf.io/yk25n_v1), Steven D. Shaw and Gideon Nave, PsyArXiv preprint, 2026, the report's source for "cognitive surrender"
7. [AI Assistance Reduces Persistence and Hurts Independent Performance](https://arxiv.org/abs/2604.04721), Grace Liu, Brian Christian, Tsvetomira Dumbalska, Michiel A. Bakker, and Rachit Dubey, COLM 2026
8. [Building pro-worker AI](https://www.brookings.edu/articles/building-pro-worker-ai/), Daron Acemoglu, David Autor, and Simon Johnson, Brookings, the "pro-worker AI" argument
9. [How AI Impacts Skill Formation](https://arxiv.org/abs/2601.20245), Judy Hanwen Shen and Alex Tamkin, Anthropic, 2026 ([summary](https://www.anthropic.com/research/AI-assistance-coding-skills))
10. [Experimental Evidence on the Learning Impact of Generative AI](https://arxiv.org/abs/2607.08849), Zara Contractor and Germán Reyes, 2026
11. [AI tutoring outperforms in-class active learning: an RCT introducing a novel research-based design in an authentic educational setting](https://doi.org/10.1038/s41598-025-97652-6), Greg Kestin et al., Scientific Reports, 2025
12. [Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise](https://arxiv.org/abs/2410.03017), Rose E. Wang, Ana T. Ribeiro, Carly D. Robinson, Susanna Loeb, and Dora Demszky
13. [The Effects of Course-Integrated AI Tutoring on Student Performance and Engagement: A Randomized University Trial](https://doi.org/10.26300/y3f8-vh05), Jing Liu et al., EdWorkingPaper 26-1598, 2026
14. [Where to Start: Backward Design](https://tll.mit.edu/teaching-resources/course-design/where-to-start-backward-design/), MIT Teaching + Learning Lab
15. [Generative AI in Teaching and Learning (GAITL) Committee Final Report and Recommendations](https://provost.brown.edu/sites/default/files/GAITL_Committee_Report_FNL.pdf), Brown University, July 2026
16. [More than 60 Percent of Harvard Faculty Say AI Harms Their Courses](https://www.thecrimson.com/article/2026/9/14/fas-2026-survey-AI/), The Harvard Crimson, 2026-09-14
17. [GPT detectors are biased against non-native English writers](https://doi.org/10.1016/j.patter.2023.100779), Weixin Liang, Mert Yuksekgonul, Yining Mao, Eric Wu, and James Zou, Patterns, 2023
18. [New AI classifier for indicating AI-written text](https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/), OpenAI, 2023, withdrawn on 2023-07-20 ([archived copy](https://web.archive.org/web/20260929162626/https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/))
19. [Why AI Detection Fails for Academic Integrity](https://arxiv.org/abs/2608.11256), Jonathan A. Karr Jr., Grigorii Khvatskii, Ting Hua, and Nitesh V. Chawla, University of Notre Dame, 2026
20. [Undergraduate Research Opportunities Program](https://urop.mit.edu/), MIT UROP
21. [Canaries in the Coal Mine? Six Facts about the Recent Employment Effects of Artificial Intelligence](https://digitaleconomy.stanford.edu/publication/canaries-in-the-coal-mine-six-facts-about-the-recent-employment-effects-of-artificial-intelligence/), Erik Brynjolfsson, Bharat Chandar, and Ruyu Chen, Stanford Digital Economy Lab ([August 2026 update](https://digitaleconomy.stanford.edu/news/canariesaug26/))
22. [Generative AI as Seniority-Biased Technological Change: Evidence from U.S. Résumé and Job Posting Data](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5425555), Seyed M. Hosseini and Guy Lichtinger, Harvard, 2025 ([archived copy](https://web.archive.org/web/20261002195414/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5425555))
23. [The Labor Market Is Tilting Toward Seniority](https://hiringlab.indeed.com/2026/07/23/the-labor-market-is-tilting-toward-seniority/), Indeed Hiring Lab, 2026-07-23
24. [Parley](https://parley.mit.edu/), MIT IS&T's model-agnostic AI platform
25. [Over a thousand MIT affiliates respond to The Tech's LLM usage survey](https://thetech.com/2025/11/25/llm-survey-results), The Tech, 2025-11-25, the fall 2025 survey
26. [2026 MIT Quality of Life Survey](https://qol.mit.edu/), source of the spring 2026 AI questions
27. [Explained: Generative AI's environmental impact](https://news.mit.edu/2025/explained-generative-ai-environmental-impact-0117), MIT News, 2025-01-17
28. [AI and education: A watershed moment for MIT](https://orgchart.mit.edu/letters/ai-and-education-watershed-moment-mit), Sally Kornbluth, MIT, 2026-08-25
29. [MIT AI report takes first step towards an Institute-wide response](https://thetech.com/2026/09/17/ai-committee-report), The Tech, 2026-09-17
30. [Torvalds on AI: It Is a Tool, and 100% of Your Code Was Always Written by Compilers](https://alexsavio.github.io/torvalds-ai-is-a-tool-not-a-replacement), Related post on AI as a tool, not a replacement
31. [So You Want To Build An LLM Agent](https://alexsavio.github.io/so-you-want-to-build-an-llm-agent), Related post on why verification, not generation, is the hard part
