# Search Modality Selection Reference

## Purpose

Guide the derivation engine in composing search modalities at query time. Semantic search (vector) and keyword search (BM25) are both always enabled; this document explains when each contributes most, how they fall back to each other, and how hybrid scoring resolves disagreements.

---

## Core Questions

1. **What is the expected vocabulary breadth?** Single-domain systems have consistent vocabulary; cross-disciplinary systems have divergent vocabulary that BM25 alone cannot bridge.
2. **What is the linking style?** Explicit-only linking relies on the graph; explicit+implicit linking leans on semantic search for discovery.

---

## Curated Claims

### Modality Foundations

#### BM25 provides the baseline for all text retrieval

**Summary:** BM25 (Best Matching 25) is a probabilistic ranking function that scores documents by term frequency, inverse document frequency, and document length normalization. It is the standard algorithm behind keyword search. BM25 excels when the searcher knows the exact vocabulary used in the target document — it is fast (sub-second on large corpora), deterministic, requires no model loading or embedding computation, and works on any system with a text index.

**Derivation Implication:** Every generated system gets keyword search as the floor. Keyword search is the universal fallback that never fails — it requires only filesystem access.

**Source:** Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond" (2009). Validated operationally in the vault's qmd `search` mode.

---

#### Embedding similarity captures meaning across vocabulary boundaries

**Summary:** Vector embeddings project text into a high-dimensional space where semantic similarity corresponds to geometric proximity. Two notes about "friction in learning systems" and "errors as pedagogical feedback" share no significant keywords but occupy nearby regions in embedding space. This is the core value proposition of semantic search: it finds connections that keyword search structurally cannot, because keyword search requires vocabulary overlap that semantic relatedness does not guarantee.

**Derivation Implication:** Vector search (`qmd query $'vec: …'`) is always enabled and contributes most where vocabulary divergence is largest — typically in cross-domain systems and in pipelines with heavy processing that reformulates source material. The derivation engine does not toggle vector search on or off; it weights how much signal the vector component carries relative to BM25.

**Source:** Mikolov et al., "Efficient Estimation of Word Representations in Vector Space" (2013). Operationally confirmed: the vault's qmd vector-search catches duplicates that BM25 misses entirely.

---

#### Query expansion amplifies semantic search by generating alternative phrasings

**Summary:** Query expansion takes the user's original query and generates alternative formulations before searching. "Knowledge management friction" might expand to "obstacles in personal knowledge systems," "note-taking workflow bottlenecks," and "PKM failure patterns." Each expanded query runs against the embedding index, and results are merged. This compensates for the single-query blind spot where the searcher's phrasing might not match the embedding space's optimal representation of the concept.

**Derivation Implication:** Query expansion is a feature of hybrid search mode (the default `qmd query "…"` form). It adds latency (~5-15 seconds) but significantly improves recall for exploratory searches. Generated systems should use expansion for connection-finding and deep exploration, not for quick lookups.

**Source:** Operational experience with qmd's expansion pipeline. Grounded in Rocchio relevance feedback (1971) adapted for neural retrieval.

---

#### LLM reranking evaluates genuine conceptual connection beyond surface similarity

**Summary:** After BM25 and vector search produce candidate results, an LLM evaluates each candidate against the original query for genuine conceptual relevance. This is the most expensive step but also the most valuable for connection-finding. Vector similarity can be fooled by topical overlap — two notes about "context windows" might score high even if one is about UI design and the other about LLM architecture. The LLM reranker distinguishes surface overlap from deep connection by reasoning about the semantic relationship.

**Derivation Implication:** LLM reranking is the highest-quality search mode and should be reserved for tasks where connection quality matters most: connect (finding connections for new notes and reconsidering older ones) and exploratory research. It should NOT be the default for routine lookups.

**Source:** Nogueira & Cho, "Passage Re-ranking with BERT" (2019). Operationally validated in the vault's default `qmd query "…"` mode, which uses LLM reranking as the final stage.

---

### Task-to-Modality Mapping

#### Finding known notes requires keyword search, not semantic search

**Summary:** When the agent knows what it is looking for — a specific filename, a known term, a particular YAML field value — keyword search is strictly superior. It is faster (0.2s vs 5-20s), deterministic (same query always returns same results), and more precise (no false positives from embedding noise). Semantic search adds latency and potential noise when the target is lexically identifiable.

**Derivation Implication:** Generated context files should instruct agents to use keyword search (grep/ripgrep) for: checking if a filename exists, querying YAML fields (`rg '^content_type: tension'`), finding exact phrases, and looking up known note titles. The search modality instruction should be task-specific, not "always use the best search."

**Source:** Operational pattern in the vault: `/seed` uses keyword search to check if a source was already processed. No semantic search needed — filenames are exact-match targets.

---

#### Exploring concepts requires semantic search to cross vocabulary boundaries

**Summary:** When the agent is exploring a concept without knowing which notes are relevant, semantic search finds candidates that keyword search misses. Searching for "how agents maintain identity across sessions" might surface notes titled "session handoff creates continuity without persistent memory" and "closure rituals create clean breaks" — neither of which contains the words "identity" or "maintain" but both are deeply relevant. This is the canonical use case for embedding-based retrieval.

**Derivation Implication:** Generated systems should route conceptual exploration to semantic search (`qmd query $'vec: …'`, or the default `qmd query "…"` when reranking helps). This applies to: the connect phase (finding connections for a new note), pre-creation duplicate detection (does this claim already exist under different words?), and ad-hoc research queries. The context file should teach the agent when to switch from keyword to semantic.

**Source:** Vault operational experience. The claim "vector proximity measures surface overlap not deep connection" documents both the value and limitations of this modality.

---

#### Connection finding requires hybrid search with LLM reranking

**Summary:** Finding genuine connections between notes is the highest-value search task in a knowledge system. It requires the full pipeline: BM25 for exact-term matches, vector search for vocabulary-divergent matches, query expansion for coverage, and LLM reranking to evaluate which candidates represent genuine conceptual connections rather than surface similarity. Each layer catches what the previous one misses. Skipping the reranking step produces connection suggestions that are topically related but not genuinely connected — the difference between "both mention context windows" and "this note's argument depends on that note's claim."

**Derivation Implication:** Every generated system runs hybrid retrieval (BM25 + vector) for connection-finding work in the connect phase. LLM reranking is added on top of the always-on hybrid pipeline when connection quality justifies the latency; it is a scoring refinement, not an enablement decision.

**Source:** Vault operational experience. The connect skill calls `qmd query` (bare form — full hybrid with expansion and reranking) because connection quality justifies the ~20s latency.

---

#### Duplicate detection requires semantic search because duplicates use different words

**Summary:** The most dangerous duplicates are semantic duplicates: notes that make the same claim in different vocabulary. "Curation becomes the work when creation is easy" and "AI makes creation cheap so filtering becomes expensive" are semantic duplicates — same insight, different framing. BM25 will not catch this because the notes share almost no significant terms. Only vector embedding similarity reliably detects semantic duplicates, because the notes occupy nearby regions in embedding space despite lexical divergence.

**Derivation Implication:** Any generated system with a processing pipeline (reduce phase) should include semantic duplicate detection. The reduce skill should check each extracted claim against the existing note corpus via semantic search before creating a new note. This is a quality gate, not an optional convenience.

**Source:** Vault operational experience. The reduce skill calls `qmd query $'vec: …'` (pure vector, no reranking) for duplicate detection, and regularly catches duplicates that would be invisible to keyword search.

---

#### Description quality testing requires semantic search without reranking

**Summary:** Testing whether a note's description enables retrieval means searching for the note using only its description, without the title. If semantic search (without LLM reranking) finds the note from its description alone, the description is doing its job as a retrieval filter. If it fails, the description needs improvement. Using reranking would hide bad descriptions behind the LLM's ability to infer relevance — the test must use raw vector similarity to expose weak descriptions.

**Derivation Implication:** Generated systems with a verify or recite phase should use pure vector search (`qmd query $'vec: …'`, not the bare `qmd query "…"` form that reranks) for description quality testing. The absence of reranking is intentional — it tests what agents will actually encounter during routine search.

**Source:** Vault operational experience. The recite and verify skills call `qmd query $'vec: …'` to test description findability, specifically avoiding the rerank stage that a bare `qmd query` would apply.

---

### Implementation Guidance

#### Semantic search requires embedding infrastructure with maintenance

**Summary:** Deploying semantic search means running an embedding model, maintaining a vector index, and keeping that index synchronized with the filesystem. Embeddings go stale when notes are created, modified, or deleted without re-indexing. A stale index is worse than no index — it gives the agent false confidence that search is comprehensive when recent content is invisible. Any generated system with semantic search must include index maintenance procedures.

**Derivation Implication:** When generating semantic search configuration, always include: (1) the embedding tool or service, (2) index update commands, (3) a freshness check protocol (compare indexed document count against actual file count), and (4) instructions for what to do when the index is stale. The vault's Phase 0 freshness check pattern should be adapted for the generated system.

**Source:** Vault operational experience. The Phase 0 freshness check was added after search results missed recently created notes, causing connect to miss connections.

---

#### Fallback chains prevent search failures from blocking work

**Summary:** Search infrastructure can fail: the qmd CLI may be missing from PATH, embedding models may fail to load, vector indices may become corrupt or stale. A system that depends entirely on semantic search for connection-finding will be blocked when semantic search fails. Dual discovery paths — semantic search plus structural navigation (MOC traversal + keyword search) — ensure that work continues regardless of search infrastructure state. The fallback is not a degraded mode; it is a parallel path that is always available.

**Derivation Implication:** Every generated system must include a fallback chain in its context file. The pattern: try semantic search first (`qmd query` via Bash), fall back to keyword search + MOC traversal if qmd is unavailable or its index is stale. Never let search failure block work.

**Source:** Vault operational experience. The two-tier fallback pattern (qmd CLI -> grep/MOC) collapsed from an earlier three-tier MCP-based fallback once every invocation standardized on the CLI, which works uniformly from the main agent and subagents.

---

### Semantic Search via CLI

#### Invoke qmd as a CLI subprocess

**Summary:** Every processing skill calls `qmd query` via Bash. The CLI standardizes behavior across contexts: the main agent, custom subagents spawned via Agent tool, and hook scripts all invoke the binary the same way, so there is no MCP-in-subagents limitation to work around. Model cold-start cost is real (roughly 5-10 seconds on first query per session) but is paid once per worker, not per query, because qmd keeps its embedding process warm for the duration of a batch.

**Derivation Implication:** No `.mcp.json` is generated and no MCP autoapprove list is needed. Processing skills declare `Bash` in `allowed-tools` and call `qmd query "…"` directly. The context file documents the structured query grammar (`lex:`, `vec:`, `hyde:`, `expand:`) and records which mode each skill uses.

**Source:** Vault operational experience. The MCP-based invocation pattern was replaced with CLI calls to eliminate the subagent permission gap and the `.mcp.json` + autoapprove maintenance burden.

---

### Search Quality and Failure Modes

#### Vector proximity measures surface overlap, not deep connection

**Summary:** Embedding similarity has a fundamental limitation: it measures vocabulary and topic similarity, not genuine conceptual connection. Two notes about "context windows" — one about LLM architecture, one about UI design — may score high vector similarity because they share vocabulary, but they are not meaningfully connected. Conversely, a note about "friction in learning" and a note about "errors as pedagogical feedback" are deeply connected but may score low because they share few terms. This is why LLM reranking exists: to evaluate what vector similarity cannot — whether the conceptual relationship is genuine.

**Derivation Implication:** Generated context files should include a search quality warning: "High similarity scores do not guarantee genuine connections. When using semantic search results, evaluate each candidate: does this note's argument actually relate to what you are searching for, or does it just use similar vocabulary?" This is especially important for the connect phase where false connections degrade graph quality.

**Source:** Research claim: "vector proximity measures surface overlap not deep connection." Vault operational experience: connect phases using `qmd query $'vec: …'` without reranking occasionally propose surface-similar but conceptually unrelated connections.

---

#### Stale indices produce false confidence that is worse than no index

**Summary:** When the semantic search index falls out of sync with the filesystem — notes created after the last index update, notes modified without re-embedding, notes deleted but still in the index — the agent receives search results that omit recent content. The danger is not the missing results themselves but the agent's trust in search comprehensiveness. An agent that believes "I searched and found nothing similar" when the search actually missed 10 recently created notes will create a duplicate without realizing it. No index is honest; a stale index lies.

**Derivation Implication:** Every generated system with semantic search must include an index staleness detection mechanism. The minimum viable implementation: compare the count of indexed documents against the count of actual files. If they differ, run index update before trusting search results. The context file should frame this as a mandatory pre-search step, not an optional maintenance task. The vault's Phase 0 freshness check is the reference pattern.

**Source:** Vault operational failure. Notes created during a processing batch were invisible to connect phases that ran before index sync, producing duplicate notes and missing connections.

---

#### BM25 query dilution occurs when full descriptions are used as search queries

**Summary:** BM25 scores documents by term frequency and inverse document frequency. When the search query itself is long (e.g., a full 150-character description), the query contains many terms, each with low individual weight. This dilution effect means that long queries return fewer and lower-quality BM25 results compared to short, focused keyword queries. The solution is to use condensed keywords or phrases for BM25 search, reserving full-text descriptions for semantic search where the embedding model handles longer inputs gracefully.

**Derivation Implication:** Generated context files that instruct agents on search usage should distinguish between query formulation for keyword search (short, focused terms) and query formulation for semantic search (natural language descriptions). A single instruction like "search for your concept" is insufficient — the agent needs to know how to phrase queries differently for each modality.

**Source:** Vault operational experience. Full-length descriptions used as BM25 queries via `qmd query $'lex: …'` frequently returned zero results, while the same descriptions used via `qmd query $'vec: …'` returned accurate matches.

---

### Search Mode Selection Matrix

#### Composition at query time

The default hybrid retrieval order: semantic search (vector) first for recall, BM25 re-ranking on the top-K candidates for precision, MOC traversal as a final fallback when the query is navigational rather than content-seeking.

Both modalities always run. Disagreement between them is a signal, not a problem: when BM25 ranks a document high and vector search does not (or vice versa), the hybrid scorer exposes the discrepancy rather than hiding it.

---

#### Domain breadth determines how quickly vocabulary diverges

**Summary:** A narrow-domain system (e.g., tracking one sport's strategy) uses consistent terminology. "Opening move," "midgame position," and "endgame technique" are standard vocabulary that all notes share. Keyword search works well because the vocabulary is constrained. A broad or cross-domain system (e.g., tools for thought research that draws from cognitive science, information retrieval, software engineering, and philosophy) accumulates vocabulary divergence rapidly because each source domain brings its own terminology for overlapping concepts. "Context window" (LLM architecture), "working memory" (cognitive science), and "attention budget" (productivity) all describe related limitations but use completely different terms.

**Derivation Implication:** The derivation engine should ask about domain breadth during init and weight hybrid scoring accordingly. Cross-domain systems rely more heavily on the vector component of hybrid search because BM25 alone cannot bridge terminological gaps between source domains; single-domain systems see BM25 and vector contributions converge because vocabulary is consistent.

**Source:** Information retrieval research on vocabulary mismatch in cross-domain corpora. Vault operational experience: the vault draws from 6+ source domains and experienced vocabulary divergence early.

---

#### Processing intensity amplifies vocabulary divergence

**Summary:** Heavy processing (extraction, reformulation, synthesis) generates more varied phrasings of the same concepts than light processing. Each reduce pass produces notes that reformulate source material in the agent's own words. Each connect pass's backward sub-phase may further rephrase claims as understanding deepens. This compounding reformulation means heavy-processing systems accumulate vocabulary divergence faster than light-processing systems, increasing the weight the hybrid scorer should place on the vector component.

**Derivation Implication:** Processing intensity shifts where semantic search contributes most within the always-on hybrid pipeline. Heavy processing produces more reformulations, so the vector component carries more signal relative to BM25; light processing keeps vocabulary closer to source material, so BM25 hits more often dominate. Both modalities still run; the hybrid scorer's weighting reflects this shift.

**Source:** Vault operational observation. After heavy /reduce processing of sources, the vault exhibited significant vocabulary divergence — concepts expressed in source-author vocabulary, vault-native vocabulary, and synthesized vocabulary.

---

### Modality Cost-Benefit Analysis

#### The cost structure of search modalities follows an exponential curve

**Summary:** Keyword search costs O(n) where n is corpus size — essentially free on modern hardware. Semantic search (vector similarity) costs O(1) per query against a pre-built index, but building and maintaining the index costs O(n) per update and requires ~2GB of model memory. Hybrid search with LLM reranking adds O(k) where k is the number of candidates reranked — each candidate requires an LLM inference pass. The practical costs: keyword ~0.2s, semantic ~5s, hybrid ~20s. The quality improvement at each step is diminishing: keyword to semantic is a large jump, semantic to hybrid is a smaller jump, but hybrid catches connections that semantic alone misses in ~15% of cases.

**Derivation Implication:** The cost-quality tradeoff informs which search mode to default to. For routine operations (file lookup, YAML queries), keyword is the only rational choice. For standard discovery (exploring related notes), semantic provides the best cost-quality ratio. For high-stakes connection finding (connect — both forward and backward sub-phases), hybrid is justified by the quality premium. Generated context files should encode this cost awareness so agents do not default to the most expensive mode for routine tasks.

**Source:** Vault operational measurements. The 0.2s / 5s / 20s benchmarks are from qmd running on Apple Silicon with models kept warm.

---

#### Search configuration should be generated as a decision table, not a default

**Summary:** Rather than setting a single default search mode, the generated context file should include a decision table mapping tasks to modalities. The agent should know: "For this task, use this search mode, because X." This is more effective than a global default because different tasks within the same session require different modalities. A single session might use keyword search for YAML queries, semantic search for duplicate checking, and hybrid search for connection finding — three modalities in one session, each justified by the task at hand.

**Derivation Implication:** Generate a task-to-modality mapping table in every context file that includes search instructions. The table should list the system's operational tasks (the ones defined by its processing pipeline and maintenance routine) and the appropriate search modality for each. This is the search equivalent of the pre-task context router — it routes tasks to appropriate search modes.

**Source:** Vault CLAUDE.md "Which mode for which skill" table. This task-specific routing replaced an earlier pattern where agents defaulted to hybrid search for everything, wasting 20 seconds on lookups that keyword search handles in 0.2 seconds.

---

## Exclusion Notes

**Excluded from this reference:**

- Full-text search engine comparisons (Elasticsearch, Solr, Meilisearch) — these are infrastructure choices, not derivation decisions. The derivation engine selects modalities, not implementations.
- Embedding model selection (which model to use for vectors) — implementation detail that belongs in platform-specific documentation, not derivation reference.
- RAG (Retrieval Augmented Generation) pipeline architecture — the vault's wiki-link graph is explicitly NOT a RAG system. Wiki links provide curated edges; RAG provides automated chunk retrieval. Different paradigms.
- Image or multimodal search — the vault is text-only. Multimodal search is a future consideration, not a current derivation concern.
- Real-time indexing vs batch indexing trade-offs — operational concern for the search tool maintainer, not a derivation decision.

---

## Version

- Last curated: 2026-02-12
- Sources reviewed: 22
- Claims included: 23
- Claims excluded: 5
- Cross-references: `kernel.yaml` (semantic-search primitive), `interaction-constraints.md` (linking dimension), `components.md` (Search component blueprint)
