# The Unofficial Guide — Project 1

---

## Domain

This project focuses on Ivy League admissions advice from admitted students, student blogs, interviews, and public admissions reflections. The guide is useful for high school applicants, parents, and counselors because official admissions websites explain requirements and policies, but they do not always show the full picture of how successful applicants actually built their applications. Student-generated advice helps reveal patterns around essays, extracurricular depth, interviews, research, leadership, testing, and common mistakes.
<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
One complete admissions entry per chunk whenever possible. In practice, chunks ranged from approximately 137–287 words (average: 202 words). The chunker was configured to split entries only if they exceeded 1200 words.
**Overlap:**
100–150 words of overlap for oversized entries that required splitting. No entries exceeded the 1200-word threshold in the final corpus, so overlap was not used in practice.
**Why these choices fit your documents:**
The corpus consists of structured admissions advice entries rather than long articles. Each entry contains a Source, School, Advice/Story, and Key Takeaway section that forms a complete, self-contained idea. Using one entry per chunk preserves context, source attribution, and semantic meaning while avoiding the retrieval problems that occur when unrelated admissions advice is merged together. Before chunking, the pipeline removed document-level introductions, footer sections, "Sources Used" lists, and "SUMMARY OF RECURRING THEMES" sections to prevent noise from being embedded and retrieved.

**Final chunk count:**
241 chunks across 10 topic-based documents.

---



<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->
## Embedding Model

**Model used:**
I used `sentence-transformers/all-MiniLM-L6-v2`. I chose it because it runs locally, does not require an API key, is fast enough for a small university RAG project, and produces good semantic embeddings for short text chunks like admissions advice entries.

**Production tradeoff reflection:**
For a real deployed system, I would compare stronger embedding models based on accuracy, context length, latency, cost, and multilingual support. Since applicants are expected to understand English, the main system can use an English-focused model. However, parents and counselors may not always have the same English fluency, so multilingual support could make the system more useful for families outside the U.S. I would also consider API-hosted models for better retrieval accuracy, but they would introduce cost, latency, and privacy tradeoffs compared with a local model.

---

## Grounded Generation

**System prompt grounding instruction:**

The system uses a retrieval-augmented generation (RAG) pipeline. Before calling the LLM, the system retrieves the top 5 most relevant chunks from ChromaDB and passes them as context. The system prompt explicitly instructs the model:

> "Answer the question using only the provided context. Do not use outside knowledge. Do not guess or infer information that is not present in the retrieved documents. If the retrieved documents do not contain enough information to answer the question, respond with: 'I don't have enough information on that.'"

This prompt is designed to prevent the model from relying on its training data and instead ground its response in the retrieved admissions advice corpus.

**How source attribution is surfaced in the response:**

Source attribution is generated programmatically rather than relying on the LLM. After retrieval, the system collects metadata from the retrieved chunks, including the filename, topic, school, source name, and source URL. These sources are displayed alongside the generated answer in the Gradio interface. This ensures that citations always correspond to the actual retrieved documents and cannot be hallucinated by the model.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 |What three academic metrics make up the "Academic Index" that Harvard uses as an initial screening filter? |GPA, test scores, and class rank |The three academic metrics that make up the "Academic Index" are GPA, test scores, and class rank. |Relevant | Accurate|
| 2 | Which two Ivy League schools currently maintain explicitly evaluative interviews where the written report is reviewed alongside the application file?|Yale and Dartmouth | Yale and Dartmouth are the two Ivy League schools that currently maintain explicitly evaluative interviews with written reports reviewed alongside the application file.| Relevant| Accurate|
| 3 | According to the analysis of over 1,100 admitted student profiles, what is the ideal number of deep, sustained extracurricular commitments an applicant should have?| Two to three deep|two to three |Relevant | Accurate|
| 4 | According to Cornell's Common Data Set for 2024-2025, what is considered the single highest-weighted academic factor in their admissions decisions?| Course rigor| Course rigor| Relevant|Accurate |
| 5 |Which program allows eligible low-income students to apply early to multiple Ivy League schools simultaneously, bypassing the single-school restriction of traditional Early Decision?  |The QuestBridge Program |The QuestBridge Program | Relevant| Accurate|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

Can a 1220 SAT score have a chance at Ivy League admissions?

**What the system returned:**

"I don't have enough information on that."

**Root cause (tied to a specific pipeline stage):**

This was a generation-stage failure rather than a retrieval failure. The retrieval system successfully returned highly relevant chunks discussing competitive SAT score ranges for Ivy League admissions. The retrieved documents stated that scores between 1550–1600 are highly competitive, 1500–1550 are typical for strong applicants, and scores below 1450 face significant academic headwinds. However, the grounding prompt was intentionally strict and required the model to rely only on explicitly stated information. Because none of the retrieved chunks directly mentioned a 1220 SAT score, the model declined to answer instead of drawing a reasonable conclusion from the retrieved score ranges.

**What you would change to fix it:**

I would revise the grounding prompt to allow simple evidence-based inferences from retrieved documents while still prohibiting outside knowledge. For example, the prompt could instruct the model to use retrieved facts to make logical conclusions when the answer is strongly supported by the context. This would allow the system to explain that a 1220 SAT score is well below the score ranges discussed in the retrieved documents without requiring the score to be explicitly mentioned.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The planning document acted like a roadmap throughout the project. By deciding on the domain, chunking strategy, retrieval approach, and evaluation questions before writing code, I always knew what component I was building and why. This made implementation more focused and prevented me from making random design decisions while coding.

**One way your implementation diverged from the spec, and why:**

One area where the implementation diverged from the original plan was the document preparation and chunking process. As I collected and cleaned the admissions advice documents, I found that some sources needed to be reorganized and reformatted so that each entry could become a meaningful retrieval chunk. I also discovered that the natural structure of the documents worked better than forcing larger chunk sizes, so the final chunking approach was adjusted to preserve complete admissions advice entries while maintaining retrieval quality.

---

## AI Usage

**Instance 1**

- *What I gave the AI:*
  I gave Claude Code my planning.md sections, including the Chunking Strategy, Document Sources, and Architecture diagram. I also explained the structure of my admissions advice corpus, where each entry contained a Source, School, Advice/Story, and Key Takeaway section.

- *What it produced:*
  Claude Code generated the ingestion and chunking pipeline (milestone3_ingest.py), including document loading, cleaning, metadata extraction, chunk creation, and JSON export.

- *What I changed or overrode:*
  After testing the output, I noticed that source URLs were not consistently attached to entries and that footer sections such as "Sources Used" and "SUMMARY OF RECURRING THEMES" were leaking into chunks. I used Claude Chat to help identify the issue, then directed Claude Code to update the parser and modified the corpus files so URLs were attached directly to the correct entries before rerunning the pipeline.

**Instance 2**

- *What I gave the AI:*
  I gave Claude Code the Retrieval Approach section from planning.md, the architecture diagram, and the Milestone 4 requirements specifying all-MiniLM-L6-v2 embeddings, ChromaDB storage, and top-k retrieval.

- *What it produced:*
  Claude Code generated the embedding and retrieval pipeline (milestone4_retrieval.py), including embedding generation, ChromaDB storage, metadata handling, and semantic retrieval.

- *What I changed or overrode:*
  Instead of accepting the initial version as-is, I directed Claude Code to make the retrieval system interactive so I could ask my own questions and inspect retrieval quality. I manually evaluated the returned chunks and distance scores and used those results to verify that retrieval was working before moving on to the generation stage.
