---
marp: true
title: AI for Research
paginate: true
---

# AI for Research

- How do LLMs work
- What are they good at
- Where do they break
- How should researchers and scientists use them

<!--
Deck note:
- This deck keeps the user's original notes visible, then expands them.
- Sources are hidden in HTML comments so they do not affect slide compilation.
-->

---

# How do LLMs work

- **Original:** `# How do LLMs work`
- At a high level, modern LLMs are usually **Transformer** models trained to predict tokens from context.
- The base recipe is simple to state, even if the systems are huge in practice:
  - break text into tokens
  - train on massive corpora
  - predict the next token, or reconstruct masked tokens
  - repeat across enormous amounts of text and compute
- The crucial idea is that next-token prediction is not just memorizing phrases. To do well, the model often has to represent syntax, facts, style, and rough world structure.
- **GPT-style models** are typically autoregressive: they generate text token by token.
- **BERT-style models** are typically bidirectional encoders: they look left and right and are especially useful for classification, search, and representation learning.
- Quarto deck note:
  - add a modal explainer link to `https://poloclub.github.io/transformer-explainer/`
- Post-training matters a lot:
  - instruction tuning
  - preference tuning / RLHF / RLAIF
  - tool use
  - retrieval
  - system prompts
- In use, the model only sees a limited **context window**. It does not have magical durable memory unless memory is added outside the core model.
- Quarto deck note:
  - add a modal on this slide opening the *Attention Is All You Need* PDF

<!--
Sources

1) Vaswani et al., "Attention Is All You Need"
URL: https://arxiv.org/abs/1706.03762
Quote: "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
Ref: turn18view0 lines 39-40

2) Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
URL: https://arxiv.org/abs/1810.04805
Quote: "BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers."
Ref: turn18view1 lines 39-41

3) IBM, "What is a context window?"
URL: https://www.ibm.com/think/topics/context-window
Quote: "The context window ... is the amount of text, in tokens, that the model can consider or 'remember' at any one time."
Ref: turn19view7 lines 220-222
-->

---

# Perspectives on LLMs

- **Original:** `# Perspectives on llms`
- **Original:** `Stochastic Parrot/automplete`
  - Skeptical lens: LLMs can reproduce patterns impressively without grounded understanding, and can also reproduce social biases and dataset artifacts.
  - Useful corrective: fluent output is not the same thing as truth.
- **Original:** `Sherlock Holmes novel (Suzkever?)`
  - Charitable lens: if the last line of a detective novel is "the culprit is ___", predicting the next token may require tracking the whole plot.
  - This is the intuition behind the Sutskever-style "detective novel" argument.
- **Original:** `Compression`
  - Another lens says language modeling is a form of compression.
  - A model that predicts text well has discovered a compact structure of the data.
- **Original:** `Shogoth`
  - Cultural / alignment metaphor: a friendly chat interface can hide a strange, opaque underlying system.
  - Useful as a meme, not as a technical theory.
- **Original:** `LLMs don't predict the most likely word like walking is controlled falling, theyg dance around the likely path`
  - Nice intuition: generation is not always greedy argmax.
  - Sampling, temperature, beam search, reasoning steps, and tool calls let the model explore several plausible continuations.
  - In practice, strong outputs often come from navigating a landscape of likely continuations rather than selecting the single top token at every step.
- Quarto deck note:
  - use a fragment-driven square image stack on this slide
  - one dramatic halftone photograph per perspective
  - switch image as each bullet appears
- Quarto deck note:
  - add a modal on this slide opening the *Stochastic Parrots* PDF

<!--
Sources

1) Bender et al., "On the Dangers of Stochastic Parrots"
URL: https://dl.acm.org/doi/10.1145/3442188.3445922
Quote: "In this paper, we take a step back and ask: How big is too big? What are the possible risks associated with this technology and what paths are available for mitigation?"
Ref: turn17search2

2) Delétang et al., "Language Modeling Is Compression"
URL: https://arxiv.org/abs/2309.10668
Quote: Paper title itself states the thesis: "Language Modeling Is Compression."
Ref: turn18view2 lines 33-37

3) Ilya Sutskever detective-novel analogy, secondary references
URL: https://www.reddit.com/r/OpenAI/comments/1g1hypo/ilya_sutskever_says_predicting_the_next_word/
Quote: "say you read a detective novel ... 'that person's name is _____'"
Ref: turn22search0
Note: This is a social-media / transcript-style secondary source, included because the user's note explicitly points to this analogy.

4) Shoggoth meme explainer, cultural reference
URL: https://knowyourmeme.com/memes/shoggoth-with-smiley-face-artificial-intelligence
Quote: "conversational AI tools' true powers are being masked in order to allow commercial public consumption"
Ref: turn24search1
-->

---

# A Note on Names

- **Original:** `# A Note on Names`
- It helps to separate **architectures**, **models**, **products**, and **companies**.
- **Original:** `Architectures:`
  - **Original:** `GPT, BERT`
  - Better distinction:
    - **GPT** is a style of autoregressive Transformer language model.
    - **BERT** is a bidirectional encoder architecture.
- **Original:** `Models:`
  - **Original:** `GPT-4, GPT-4o, o1, o3, GPT-5 -> 5.3`
  - Current naming is fluid and vendor-specific. A rough distinction is:
    - mainline general models
    - reasoning models
    - smaller / faster variants
    - multimodal variants
  - For OpenAI, current public naming includes **GPT-5**, **GPT-5.3 Instant**, and **GPT-5.4**.
  - For Anthropic, current public naming includes **Claude Opus 4.6**, **Claude Sonnet 4.6**, and **Claude Haiku 4.5**.
  - For Google, current public naming includes **Gemini 2.5 Pro**, **Gemini 2.5 Flash**, and image models such as **Nano Banana**.
  - Open model ecosystems include **Llama**, **Mistral**, **DeepSeek**, **Kimi / Moonshot**, and others.
- **Original:** `Products:`
  - **Original:** `ChatGPT`
  - A **product** wraps one or more models in an interface, safety layer, memory system, tool layer, and billing plan.
- **Original:** `Companies:`
  - **Original:** `OpenAI, Anthropic, Deepseek? Mistral`
  - Companies build or host models, but the company name is not the model name.
- **Original:** `Sizes no parameters, run on gpus`
  - Parameter count used to be a common shorthand, but many frontier labs no longer publish it.
  - What still matters in practice:
    - latency
    - context length
    - tool support
    - cost
    - modality
    - hardware footprint
  - Yes, these systems run on GPUs or other AI accelerators, and compute is a first-class constraint.

<!--
Sources

1) OpenAI, "Introducing GPT-5"
URL: https://openai.com/index/introducing-gpt-5/
Quote: "We are introducing GPT-5 ... It is a unified system that knows when to respond quickly and when to think longer."
Ref: turn18view21 lines 34-43

2) OpenAI, "GPT-5.3 Instant"
URL: https://openai.com/index/gpt-5-3-instant/
Quote: "Today, we're releasing an update to ChatGPT's most-used model ... GPT-5.3 Instant"
Ref: turn18view20 lines 114-123

3) OpenAI, "Introducing GPT-5.4"
URL: https://openai.com/index/introducing-gpt-5-4/
Quote: "Today, we're releasing GPT-5.4 in ChatGPT ... the API, and Codex."
Ref: turn18view19 lines 41-42

4) Anthropic docs, "Intro to Claude"
URL: https://platform.claude.com/docs/en/intro
Quote: "The latest generation of Claude models: Claude Opus 4.6 ... Claude Sonnet 4.6 ... Claude Haiku 4.5"
Ref: turn19view4 lines 201-206

5) Google AI docs, "Models"
URL: https://ai.google.dev/gemini-api/docs/models
Quote: "Gemini 2.5 Pro ... Our most advanced model for complex tasks" and "Nano Banana ... State-of-the-art native image generation and editing"
Ref: turn19view5 lines 223-230 and turn19view6 lines 195-199

6) Mistral AI, "Introducing Mistral 3"
URL: https://mistral.ai/news/mistral-3
Quote: "Mistral 3 includes ... Mistral Large 3 ... with 41B active and 675B total parameters."
Ref: turn18view17 lines 11-15

7) DeepSeek homepage
URL: https://www.deepseek.com/en/
Quote: "Launching DeepSeek-V3.2 - Reasoning-first models built for agents."
Ref: turn18view18 lines 2-6
-->

---

# Extending LLMs

- **Original:** `# Extending LLMs`
- **Original:** `RAG, search`
  - Retrieval-augmented generation gives the model external documents at answer time.
  - This often matters more than a smarter base model when the task is grounded Q&A over specific documents.
  - RAG is not obsolete just because context windows are longer.
- **Original:** `Scale on test-time: Reasoning models`
  - A big current trend is spending more compute **at inference time**.
  - Reasoning models can allocate extra internal tokens, try multiple paths, and self-correct more before answering.
  - This often helps on coding, math, planning, and multi-step problems.
  - Quarto deck note:
    - add a modal image link to `images/test_time_compute.png`
- **Original:** `Agents, harnesses & the command line`
  - An agent is usually an LLM plus tools, memory, state, and a control loop.
  - A harness is the engineering scaffold around the model:
    - retries
    - tool permissions
    - logging
    - evaluation
    - state management
    - cost controls
  - The command line matters because many real research and engineering tasks reduce to files, scripts, tests, package managers, and shell tools.

<!--
Sources

1) Li et al., "Long Context vs. RAG for LLMs: An Evaluation and Revisits"
URL: https://arxiv.org/abs/2501.01880
Quote: "Extending context windows ... and using retrievers ... are the two main strategies to enable LLMs to incorporate extremely long external contexts."
Ref: turn23search0

2) OpenAI reasoning docs
URL: https://developers.openai.com/api/docs/guides/reasoning/
Quote: "the reasoning.effort parameter guides the model on how many reasoning tokens to generate before creating a response"
Ref: turn18view9 lines 701-702

3) Anthropic Claude Code docs, common workflows
URL: https://docs.anthropic.com/en/docs/claude-code/tutorials
Quote: "Extended thinking controls how much internal reasoning Claude performs before responding."
Ref: turn23search8

4) Merrill et al., "Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces"
URL: https://arxiv.org/abs/2601.11868
Quote: "Terminal-Bench 2.0 ... composed of 89 tasks in computer terminal environments inspired by problems from real workflows."
Ref: turn19view8 lines 41-41
-->

---

# How smart are they

- **Original:** `# How smart are they`
- **Original:** `Strawberry and colorblindness`
  - They can solve hard tasks and still fail on weirdly small ones.
  - "How many r's are in strawberry?" became famous because token-based systems can lose direct access to character-level structure.
  - Quarto deck note:
    - add a modal image link to `images/strawberry.png`
  - Vision-language systems can also fail on adversarial color / perception tasks that are easy for humans.
- **Original:** `Problem of context: Autowaschanlage beispiel`
  - Context is everything.
  - Compound words, niche domains, multilingual ambiguity, and hidden assumptions can derail an otherwise strong answer.
  - If this is your own example, keep it: it is a good reminder that local context often beats general intelligence.
  - Quarto deck note:
    - add a modal image link to `images/carwash.png`
- **Original:** `ARC- test`
  - ARC and ARC-AGI try to test abstract reasoning on novel tasks, not just memorized internet patterns.
  - These benchmarks are hard because they are "easy for humans, hard for AI".
- **Original:** `Ragged capability frontier`
  - Better known as the **jagged** capability frontier.
  - LLM ability is uneven: excellent on some tasks, brittle on neighboring tasks that look similar to us.
  - This is one of the central facts to communicate to researchers.
  - Quarto deck note:
    - add a modal image link to `images/capability_frontier.jpeg`

<!--
Sources

1) Cosma et al., "The Strawberry Problem: Emergence of Character-level Understanding in Tokenized Language Models"
URL: https://arxiv.org/html/2505.14172v1
Quote: "LLMs ... often fail at very basic character-level manipulation"
Ref: turn18view6 lines 32-33

2) Ling et al., "ColorBlindnessEval: Can Vision-Language Models Pass Color Blindness Tests?"
URL: https://arxiv.org/abs/2509.19070
Quote: "evaluate the robustness of Vision-Language Models ... in visually adversarial scenarios inspired by the Ishihara color blindness test"
Ref: turn23search4 and turn23search14

3) Chollet et al., "ARC-AGI-2"
URL: https://arxiv.org/abs/2505.11831
Quote: "a challenging benchmark for evaluating the general fluid intelligence of artificial systems via a set of unique, novel tasks"
Ref: turn18view5 lines 39-40

4) Dell'Acqua et al., "Navigating the Jagged Technological Frontier"
URL: https://www.hbs.edu/ris/Publication%20Files/24-013_d9b45b68-9e74-42d6-a1c6-c72fb70c7282.pdf
Use in talk: the key lesson is that AI performance expands unevenly across tasks, not smoothly.
Ref: cited in turn17search27 and related snippets
-->

---

# Ethics / Economics

- **Original:** `# Ethics Economics`
- **Original:** `* environmental impact`
  - Per query, impact can be modest.
  - At system scale, aggregate energy, water, and hardware demand are substantial.
  - Efficiency is improving fast, which changes the economics but does not make the footprint disappear.
- **Original:** `* Copyright.`
  - Copyright questions are not settled.
  - The main fault lines are training data, fair use, licensing, outputs, and market substitution.
  - This is a live legal and policy area, not a solved technical footnote.
- **Original:** `H200 pricing.`
  - A useful teaching point: frontier AI is still deeply constrained by compute prices.
  - As of early 2026, public market quotes for NVIDIA H200s are still expensive enough to matter for labs, startups, and universities.
- **Original:** `"You get (more) than what you pay for"`
  - Inference can be cheap relative to expert labor on narrow tasks.
  - But the real bill often includes evaluation, review, integration, security, and governance.
  - Cheap tokens do not imply cheap systems.

<!--
Sources

1) Stanford HAI, 2025 AI Index Report
URL: https://hai.stanford.edu/ai-index/2025-ai-index-report
Quote: "the inference cost for a system performing at the level of GPT-3.5 dropped over 280-fold between November 2022 and October 2024 ... energy efficiency has improved by 40% each year"
Ref: turn19view0 line 168

2) U.S. Copyright Office, "Copyright and Artificial Intelligence, Part 3: Generative AI Training"
URL: https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf
Quote: "These issues are the subject of intense debate. Dozens of lawsuits are pending in the United States"
Ref: turn18view8 lines 63-68

3) Reuters / public reporting on H200 pricing
URL: https://www.reuters.com/world/china/nvidia-requires-full-upfront-payment-h200-chips-china-sources-say-2026-01-08/
Quote: "H200 chips ... priced at around $27,000 each"
Ref: turn21search13

4) Jarvislabs pricing guide
URL: https://docs.jarvislabs.ai/blog/h200-price
Quote: "The NVIDIA H200 GPU costs $30K-$40K to buy outright and $3.72-$10.60 per GPU hour to rent"
Ref: turn21search1

5) Epoch AI, training-cost trend
URL: https://epoch.ai/blog/how-much-does-it-cost-to-train-frontier-ai-models
Quote: "The cost of training frontier AI models has grown by a factor of 2 to 3x per year"
Ref: turn21search3
-->

---

# What to do with LLMs

- **Original:** `# What to do with LLMS`
- **Original:** `Proofreading setup`
  - Treat the model as a configurable reviewer.
  - Good prompt pattern:
    - role: exact reviewer persona
    - target: what kind of output you want
    - constraints: tone, audience, length
    - failure mode: what to be harsh about
  - Example: "Act as a skeptical but constructive reviewer. Find vagueness, unsupported claims, and tone problems. Preserve my voice."
- **Original:** `How do they remember`
  - Three different things get mixed together:
    - **weights**: what the model learned in training
    - **context window**: what it can use right now
    - **external memory**: chats, notes, vector stores, files, product features
  - This distinction is worth teaching explicitly.
- **Original:** `https://x.com/alexolegimas/status/2020871624212328872`
  - Keep this as a discussion prompt or example if it supports your live framing.
  - If useful, annotate it in speaker notes with the key takeaway you want.

<!--
Sources

1) IBM, "What is a context window?"
URL: https://www.ibm.com/think/topics/context-window
Quote: "The context window ... is the amount of text ... that the model can consider or 'remember' at any one time."
Ref: turn19view7 lines 220-222

2) OpenAI reasoning docs
URL: https://developers.openai.com/api/docs/guides/reasoning/
Quote: reasoning effort controls how many reasoning tokens are used before responding.
Ref: turn18view9 lines 701-702

3) OpenAI cookbook, context personalization / long-term memory notes
URL: https://developers.openai.com/cookbook/examples/agents_sdk/context_personalization/
Quote: "post-session memory distillation ... memories are extracted at the end of the session using the full execution trace"
Ref: turn23search32

4) User-supplied live link
URL: https://x.com/alexolegimas/status/2020871624212328872
Note: included as provided by the user.
-->

---

# Uses around research

- **Original:** `# Uses around research`
- **Original:** `Mot juste`
  - LLMs are often good at helping you find the right wording, especially when you know roughly what you mean but not the best phrasing.
  - Best use: ask for 5 to 10 alternatives with different tones and levels of precision.
- **Original:** `One usage: Check my work!`
- **Original:** `Find the error/mistake`
  - This is one of the highest-value uses.
  - Ask the model to:
    - search for algebra slips
    - look for hidden assumptions
    - challenge causal leaps
    - find unit errors
    - attack edge cases
    - propose counterexamples
- **Original:** `Getting other people's bad research code to work...`
  - Extremely practical use.
  - Give it the traceback, the environment file, the README, and the desired output.
  - Ask for a minimal reproduction and a prioritized debugging plan.
- **Original:** `Heuristic usage`
  - Treat it as a fast heuristic assistant, not a final authority.
  - Great for first-pass triage, bad for unverified certainty.
- **Original:** `Catching tone problems, eg in EMails. (This sounds like )`
  - Strong use case: rewrite for diplomacy without becoming bland.
  - Ask for:
    - more direct
    - less passive-aggressive
    - warmer but still professional
    - suitable for collaborator / student / referee / admin
- **Original:** `![[Screenshot 2026-03-12 at 11.52.32.png]]`
  - Keep as a visual example if your slide tooling can embed it.
  - Otherwise convert it to a normal image link later.
- **Original:** `Diagrams via Nano-Banana`
  - Image models are increasingly useful for figures, workflows, posters, and explanatory diagrams.
  - They are especially strong for iterative visual prototyping.
  - In the Quarto deck, keep modal links for the hand-drawn sketch and the cleaned-up version side by side on this point.

<!--
Sources

1) Google DeepMind, "Nano Banana Pro"
URL: https://deepmind.google/models/gemini-image/pro/
Quote: "Generate clear text for posters and intricate diagrams"
Ref: turn19view11 lines 121-123

2) Same page
Quote: "Annotate pictures, represent data as infographics, or turn handwritten notes into diagrams."
Ref: turn19view11 lines 185-185

3) GPT-5 prompting guide
URL: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide/
Quote: "Prompted planning is likewise more important"
Ref: turn23search22
Note: useful as backing for structured proofreading and code-debugging prompt setups.
-->

---

# AI detection in practice

- New workshop note:
  - First-generation AI detectors were very bad.
  - Current detectors are somewhat better.
  - Quarto deck note:
    - point the live Pangram modal to `https://maxnoichl-pangram-api-tester.hf.space`
  - They are still unreliable enough that they should not be treated as proof on their own.
  - Make the "tells" point into an exercise:
    - identify the tells
    - but do not stop at phrase X
    - ask why it is written that way
    - ask how the claims connect
    - ask whether the author can explain the passage
  - Quarto deck note:
    - add a modal screenshot link to `images/Screenshot_detection.png`

<!--
Author note

- Keep this practical and skeptical.
- Run this as an in-room exercise rather than a detector claim.
- Good place for a live example or a short detector screenshot later.
-->

---

# Speech to text: Whisper and NVIDIA

- **Original:** `Speech to text whisper, and the nvidia model`
- Whisper is still a very practical default for local multilingual transcription.
- Whisper can also do speech translation and language identification, which makes it a good all-purpose baseline for teaching.
- For NVIDIA it is useful to separate the current speech families:
  - **Canary** for multilingual speech-to-text plus speech translation.
  - **Parakeet** for strong ASR in the NVIDIA / NeMo ecosystem.
- Good uses in research:
  - interviews
  - lectures
  - workshop recordings
  - meeting notes
  - oral-history material
- Strong workflow:
  - transcribe first
  - then clean, summarize, structure, or search with an LLM
- Important warning:
  - always verify names, numbers, jargon, and speaker boundaries
- Quarto deck note:
  - the rendered workshop deck should include a modal transcript pad for live demos

<!--
Sources

1) OpenAI Whisper GitHub
URL: https://github.com/openai/whisper
Quote: "Whisper is a general-purpose speech recognition model."
Ref: turn1view0 lines 275-279

2) Same source
Quote: "can perform multilingual speech recognition, speech translation, and language identification."
Ref: turn1view0 lines 279-284

3) NVIDIA NeMo ASR models docs
URL: https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html
Quote: "Canary is the latest family of models from NVIDIA NeMo."
Ref: turn2view0 lines 178-180

4) Same source
Quote: "supporting automatic speech-to-text recognition (ASR) in 25 EU languages as well as translation"
Ref: turn2view0 lines 180-180

5) Same source
Quote: "Parakeet is the name of a family of ASR models"
Ref: turn2view1 lines 204-206
-->

---

# Vision / OCR models

- **Original:** `Vision/OCR models`
- General vision-language models are often good enough for quick research tasks:
  - read screenshots
  - inspect slide photos
  - summarize charts
  - answer questions about a scanned page
- Specialized OCR models become more useful when structure matters:
  - headers
  - paragraphs
  - lists
  - tables
  - multi-page PDFs
- Good uses:
  - making scans searchable
  - pulling text from screenshots
  - extracting tables from PDFs
  - reading whiteboards and archival documents
- A useful practical distinction:
  - use a general vision model for fast, flexible reading
  - use a dedicated OCR pipeline when layout fidelity and scale matter
- Typical failure modes:
  - multi-column layouts
  - handwriting
  - formulas
  - low-quality scans
  - hallucinated structure

<!--
Sources

1) OpenAI vision docs
URL: https://developers.openai.com/api/docs/guides/images-vision
Quote: "If there is text in an image, the model can also understand the text."
Ref: turn2view2 lines 695-698

2) Mistral OCR docs
URL: https://docs.mistral.ai/capabilities/document_ai/basic_ocr
Quote: "powered by our latest OCR model `mistral-ocr-latest`"
Ref: turn2view3 lines 89-91

3) Same source
Quote: "maintaining document structure and hierarchy"
Ref: turn2view4 lines 101-109
-->

---

# Usage as scientists

- **Original:** `# Usage as scientists`
- **Original:** `* Data labelling (for social science)`
  - This is real and already useful.
  - Give the model a codebook, examples, and a clear output schema.
  - Then spot-check aggressively.
  - Important caveat: good label accuracy does **not** automatically imply valid downstream inference.
- **Original:** `* APIs`
  - Research use gets much better once you move beyond the chat box.
  - APIs let you batch, evaluate, cache, log, and reproduce workflows.
- **Original:** `* Set spending limits!`
  - Essential advice.
  - Put budgets, rate limits, alerts, and kill switches in place before students or collaborators start experimenting at scale.
- Suggested scientist workflow:
  - prototype in chat
  - stabilize in scripts
  - evaluate on held-out examples
  - add human review where mistakes are costly
  - document prompts, model versions, and failure cases

<!--
Sources

1) Egami et al., "How to Use LLMs as Text Classifiers"
URL: https://naokiegami.com/paper/dsl_ss.pdf
Quote: "Instead of providing the codebook to trained expert coders, we can supply the same codebook to LLMs"
Ref: turn20view0 lines 218-220

2) Same paper
Quote: "prediction errors in LLM classification are particularly difficult to understand"
Ref: turn20view1 lines 298-302

3) Same paper
Quote: "the LLM-only estimation ignores differential prediction errors"
Ref: turn20view1 lines 710-712

4) Nature npj AI review on science workflows
URL: https://www.nature.com/articles/s44387-025-00019-5
Quote: "LLMs are redefining the scientific method ... across different stages of the scientific cycle"
Ref: turn19view10 lines 66-68
-->

---

# Practical closing slide

- LLMs are best understood as **powerful, uneven, tool-using probabilistic systems**.
- For research, the winning posture is usually:
  - use them aggressively for drafts, checks, coding help, and labeling
  - use them cautiously for claims, citations, and conclusions
  - keep a human in the loop where error costs are high
- The right question is usually not:
  - "Are they intelligent?"
- The better questions are:
  - what are they good at
  - what kind of errors do they make
  - how do we build workflows that make those errors visible and manageable

<!--
Optional extra sources for a concluding discussion

1) Dell'Acqua et al., jagged frontier framing
2) Terminal-Bench for real-world agent difficulty
3) AI Index 2025 for cost and efficiency trends
-->
