# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This project focuses on Ivy League admissions advice from admitted students, student blogs, interviews, and public admissions reflections. The guide is useful for high school applicants, parents, and counselors because official admissions websites explain requirements and policies, but they do not always show the full picture of how successful applicants actually built their applications. Student-generated advice helps reveal patterns around essays, extracurricular depth, interviews, research, leadership, testing, and common mistakes.
<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |PrepScholar - "How to Get Into Harvard and the Ivy League"(Allen Cheng, Harvard Alumnus) | Introduces the "Spike" strategy and provides a framework for building a highly differentitated Ivy League applicaton|https://blog.prepscholar.com/how-to-get-into-harvard-and-the-ivy-league-by-a-harvard-alum |
| 2 |CollegeVine Admissions Guides and Student Interview Series |Student admissions profiles, interview advice, application strategy, and admitted-student experiences | https://www.collegevine.com/guidance|
| 3 |Princeton Admissions- Helpful Tips for Applicants |official Princeton guidance discussing academics, extracurricular involvement, leadership, family responsibilities, and admissions evaluation |https://admission.princeton.edu/apply/before-you-apply/helpful-tips |
| 4 |Yale Undergraduate Admissions | Official Yale admissions resources covering leadership, extracurriculars, application evaluation, interviews, and what Yale looks for in applicants|https://admissions.yale.edu/ |
| 5 |Cornell Admissions and Student Stories  | Official cornell student reflection, and admission perspective , particularly valuable for research, intellectual curiosity, and academic fit.|https://admissions.cornell.edu/community/student-stories |
| 6 | Ivy Coach- Early Decision Strategy for Ivy League Admissions|This source discusses the specific application strategy for the five Ivy League schools that offer a binding Early Decision (ED) program: Brown, Columbia, Dartmouth, Cornell, and UPenn |https://www.ivycoach.com/the-ivy-coach-blog/ivy-league/do-ivy-leagues-prefer-early-applicants/ |
| 7 | IvyWise - Brown University Admissions Analysis| Emphasizes aligning supplemental essays with Brown's Open curriculum by demonstrating self-directed learning and ability to navigate academic freedom. Warning that vague enthusiasm for the university's prestige is ineffective. | IvyWise KnowledgeBase / Brown University Admissions Analysis
 URL: https://www.ivywise.com/blog/how-to-get-into-brown-university-all-you-need-to-know/|
| 8 |CollegeEssayAdvisors/University of Pennsylvania Admissions Guidance | Advices connecting personal goals to highly specific UPenn resources such as faculty work, resource centers, or student clubs, rather than expressing generic enthusiasm for the brand name while highlighting personal stories that showcase curiosity and collaboration.|https://www.collegeessayadvisors.com/supplemental-essay/university-of-pennsylvania-upenn-supplemental-essay-prompt-guide/ |
| 9 |AdmitReport Blog/Application strategy guide for Columbia | Explains that admission officers look for a love of learning and a genuine enthusiasm for Columbia's famous core curriculum, warning that generic essays treating Columbia as interchangeable with other Ivy League schools will fail. |https://admitreport.com/blog/how-to-get-into-columbia-university |
| 10 | Admission decision substack/ Ssuccess Story: Accepted to Harvard". | Note that near-perfect grades and test score only meet the minimum threshold for serious consideration, emphasizing that final acceptance depends on distinctive non-academic factors, deep extracurricular commitments, and essays started early enough to allow for thorough revision. | https://admissionsdecisions.substack.com/p/success-story-accepted-to-harvard|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
One complete entry per chunk when possible, with a target size of about 800-1200 words
**Overlap:**
100-150 words when an entry is too long and must be split.
**Reasoning:**
My documents are organized into repeated entries with a Source, School, Advice section, and Key Takeaway. Each entry usually focuses on one admissions lesson, such as essays, interviews, leadership, research, or test scores. Chunking by complete entry keeps the source, explanation, and takeaway together, which makes each chunk meaningful on its own. Smaller chunks could separate the advice from the key takeaway, while larger chunks could combine unrelated entries and make retrieval less precise.
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
sentence-transformers/all-MiniLM-L6-v2
**Top-k:**
5 chunks per query
**Production tradeoff reflection:**
I am using all-MiniLM-L6-v2 because it is free, fast, runs locally, and performs well on an English-language admissions corpus. For this project, English retrieval is sufficient because students applying to Ivy League universities are generally expected to read, write, and communicate in English throughout the admissions process and their college education. However, if this system were deployed for real users, I would consider a multilingual embedding model because parents and counselors may not have the same level of English proficiency as applicants. Supporting multiple languages could make admissions advice more accessible to families around the world, though this would require balancing multilingual support against retrieval accuracy, latency, and computational cost.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What three academic metrics make up the "Academic Index" that Harvard uses as an initial screening filter?|GPA, test scores, and class rank |
| 2 |Which two Ivy League schools currently maintain explicitly evaluative interviews where the written report is reviewed alongside the application file? | Yale and Dartmouth|
| 3 |According to the analysis of over 1,100 admitted student profiles, what is the ideal number of deep, sustained extracurricular commitments an applicant should have? | Two to three deep, sustained commitments over multiple years |
| 4 |According to Cornell's Common Data Set for 2024-2025, what is considered the single highest-weighted academic factor in their admissions decisions? | Course rigor(taking the most demanding curriculum available)|
| 5 |Which program allows eligible low-income students to apply early to multiple Ivy League schools simultaneously, bypassing the single-school restriction of traditional Early Decision? | The QuestBridge Program|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Chunk size may be uneven because some advice entries are much longer than others. If chunks are too small, the advice may be separated from its key takeaway; if chunks are too large, multiple ideas may be mixed together and create noisy retrieval results.

2. Retrieving top-k = 5 may add noise for narrow questions. If a topic only has two highly relevant chunks, the remaining three retrieved chunks may be only loosely related and could make the LLM include less precise information.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
  ```mermaid
flowchart LR
  subgraph ING["① Document Ingestion"]
    A["📄 Source Corpus\ndocuments/*.txt\n──────────────\n10 topic files · plain text\nessays, ECs, research…"]
  end

  subgraph CHK["② Chunking"]
    B["✂️ Entry-Based Chunker\nRecursiveCharacterTextSplitter\n──────────────\nChunk size: 800–1000 words\nOverlap: 100–150 words"]
  end

  subgraph EMB["③ Embedding + Vector Store"]
    C["🔢 Embedding Model\nsentence-transformers\nall-MiniLM-L6-v2\n──────────────\n384-dim vectors"]
    D["🗄️ Vector Database\nChromaDB\n──────────────\nPersistent local store\nCosine similarity index"]
    C --> D
  end

  subgraph RET["④ Retrieval"]
    E["🔍 Semantic Search\nQuery Encoder\n──────────────\nTop-k = 5 chunks"]
  end

  subgraph GEN["⑤ Generation"]
    F["🧠 LLM\nGroq · Llama 3.3 70B Versatile\n──────────────\nContext window: 128k tokens\nTemp: 0.2 · max tokens: 1024"]
  end

  subgraph OUT["⑥ Response"]
    G["✅ Final Answer\nStructured Output\n──────────────\nAnswer + source citations\nSchool · topic · entry ref"]
  end

  H(["👤 User Query"])

  A --> B
  B --> C
  D --> E
  H --> E
  E --> F
  F --> G
```  
---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**

I planned to use Claude Code to implement the document ingestion and chunking pipeline. I provided the Documents section, Chunking Strategy section, and Architecture diagram from planning.md as input. I expected it to generate code that loads all corpus files, cleans the text, extracts metadata, and creates chunks following my entry-based chunking strategy. I verified the output by inspecting sample chunks, checking chunk counts, confirming metadata extraction, and ensuring there were no footer or introduction leaks in the final chunks.

**Milestone 4 — Embedding and retrieval:**

I planned to use Claude Code to implement the embedding and retrieval pipeline. I provided the Retrieval Approach section, Architecture diagram, and Milestone 4 requirements as input. I expected it to generate code that embeds chunks using all-MiniLM-L6-v2, stores them in ChromaDB with metadata, and retrieves the top-k most relevant chunks for a query. I verified the output by running evaluation questions, inspecting retrieved chunks and distance scores, and confirming that retrieval returned relevant admissions advice from the correct sources.

**Milestone 5 — Generation and interface:**

I planned to use Claude Code to implement grounded generation and the user interface. I provided the Architecture diagram, Retrieval Approach, Evaluation Plan, and grounding requirements from planning.md. I expected it to generate code that retrieves relevant chunks, sends them to Groq's Llama 3.3 70B model, enforces grounding through a system prompt, and displays answers and sources through a Gradio interface. I verified the output by testing covered and uncovered questions, confirming that source attribution was displayed correctly, and checking that the system responded with "I don't have enough information on that." when the retrieved context did not support an answer.