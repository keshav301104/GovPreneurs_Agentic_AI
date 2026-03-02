# Part 1: Data Integration Strategy - Ingestion & Updates

## 1. The Reality of SAM.gov Data
[cite_start]While modern SaaS platforms rely heavily on webhooks for real-time updates[cite: 89], government APIs like SAM.gov are generally legacy systems. Native, reliable webhooks for individual solicitation updates do not currently exist at scale. Therefore, proposing a webhook-only architecture is a technical risk. [cite_start]We must build a smart, asynchronous polling strategy to keep data fresh[cite: 87, 88, 89].

## 2. The Hybrid "Delta Sync" Strategy
[cite_start]To keep the data fresh without hitting government API rate limits[cite: 87], we will implement a two-tier ingestion pipeline using Python and a task queue (like Celery + Redis):

* **Nightly Baseline Load:** A scheduled cron job runs daily during off-peak hours to ingest the bulk data archives from SAM.gov, ensuring baseline consistency and catching any anomalies across our MongoDB database.
* **High-Frequency Delta Polling:** A lightweight worker polls the SAM.gov API every 1-2 hours. [cite_start]Instead of pulling everything, it strictly queries using the `modifiedDate` parameters to only fetch delta changes—capturing newly posted opportunities and recently updated notices[cite: 89].

## 3. Handling "Modified" Notices 
[cite_start]When the government changes a deadline [cite: 88] or alters the scope of work, our system handles it via safe **Upsert** logic:
* [cite_start]**Idempotent Updates:** When the polling script detects a modified notice[cite: 89], it checks the incoming `opportunity_id`. It compares the incoming `last_modified` timestamp with our stored timestamp. If newer, it updates (upserts) the existing MongoDB document.
* **Audit Trails:** For critical fields like `response_deadline`, we don't just overwrite the data. [cite_start]We push the old date into an `update_history` array within the JSON document so the user can see exactly when and how the government changed the timeline[cite: 88].

## 4. Triggering Downstream AI Updates (The RAG Connection)
Updating the database isn't enough; the AI needs to know about the change. [cite_start]If a "modified" notice [cite: 89] includes a new PDF attachment or an updated description:
1.  **Vector Invalidation:** The backend automatically deletes the outdated text embeddings for that specific `opportunity_id` in our vector database.
2.  **Re-Processing:** An event is emitted to trigger our RAG document loader to download the new PDF, chunk it, and vectorize the fresh data.
3.  **Proactive User Alerts:** If a user has already started drafting a proposal for this opportunity, the system flags the UI: *"Alert: The government modified the requirements for this solicitation. Click here to have the AI re-evaluate your draft against the new guidelines."*

# Part 2: RAG Workflow (The "Brain")

## The "Auto-Proposal" RAG Architecture
To generate a highly accurate, compliant proposal, we must move beyond naive vector search. This pipeline utilizes Semantic Chunking, Hybrid Search, and an LLM-as-a-Judge Evaluator.

### Phase 1: Ingestion & Intelligent Chunking
1. [cite_start]**Inputs Loaded:** The system pulls the structured SAM.gov JSON and downloads the attached solicitation PDFs[cite: 96]. [cite_start]Simultaneously, it loads the user's "SafeGuard Security" profile (Capabilities Statement, Past Performance, Certifications)[cite: 92, 96].
2. **Document Parsing:** The PDF is parsed using OCR/document-intelligence tools (like LlamaParse) to retain document structure (tables, headers, lists) rather than just raw text.
3. [cite_start]**Semantic Chunking:** Instead of splitting the document every 500 tokens, the system chunks the text semantically based on document headers (e.g., keeping the entire "Section M - Evaluation Factors" in one chunk, and "Scope of Work" in another)[cite: 97].
4. **Embedding:** These chunks are converted into vector embeddings (e.g., via OpenAI `text-embedding-3-small`) and stored in a vector database (like MongoDB Atlas Vector Search).

### Phase 2: Retrieval (The Matchmaker)
1. **Query Generation:** When the user clicks "Draft Proposal", the system uses the user's Capabilities Statement to formulate a search query.
2. **Hybrid Search:** The system searches the vector database using a combination of:
   * **Semantic Search (Dense):** To understand the conceptual meaning of the requirements.
   * **Keyword Search (Sparse/BM25):** Critical for government documents to ensure specific acronyms (e.g., "NIST 800-171", "FIPS 140-2") are matched exactly.
3. [cite_start]**Re-ranking:** The retrieved chunks are passed through a Cross-Encoder (re-ranker) to ensure the most relevant constraints and evaluation criteria are pushed to the very top of the context window[cite: 97].

### Phase 3: Context Assembly & Generation
1. **Prompt Construction:** The system compiles the final context window:
   * [cite_start]**System Prompt:** Dictating tone and strict anti-hallucination rules.
   * **Context A:** Top 5-7 most relevant RFP chunks (Requirements).
   * **Context B:** The User's Profile (Experience).
2. [cite_start]**LLM Generation:** The primary LLM (e.g., GPT-4o or Claude 3.5 Sonnet) drafts the proposal, explicitly mapping SafeGuard Security's past performance to the retrieved RFP constraints[cite: 97]. 

### Phase 4: The Guardrail (Evaluator Step)
1. **LLM-as-a-Judge:** Before the user sees the draft, a secondary, smaller LLM (the "Evaluator") scans the generated proposal. 
2. **Verification:** It cross-references the draft against the original retrieved RFP chunks to ensure:
   * No made-up past performance metrics.
   * All mandatory compliance clauses from the RFP were addressed.
3. **Output:** The verified draft is passed to the Next.js frontend for user review.