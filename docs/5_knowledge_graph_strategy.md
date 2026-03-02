# Part 5 (Bonus): Advanced Entity Resolution via Knowledge Graph (Neo4j)

## The Limitation of Standard RAG
While vector databases excel at semantic similarity, they struggle with hierarchical government structures and strict Boolean compliance constraints. If a user queries "Navy experience," a vector search might miss projects labeled "NAVAIR" or "DoD."

## The Graph RAG (GraphRAG) Solution
To build a truly intelligent Auto-Proposal Engine, we must map the procurement ecosystem using a property graph database like Neo4j. This allows the AI to perform complex, multi-hop reasoning before drafting the proposal.

### 1. Core Schema (Ontology)
* **Nodes:** `[Agency]`, `[Opportunity]`, `[NAICS_Code]`, `[Contractor]`, `[PastPerformance]`, `[Certification]`
* **Edges:** `(Agency)-[:ISSUES]->(Opportunity)`, `(Opportunity)-[:REQUIRES_NAICS]->(NAICS_Code)`, `(Contractor)-[:HAS_COMPLETED]->(PastPerformance)`, `(PastPerformance)-[:ALIGNS_WITH]->(NAICS_Code)`

### 2. The Cypher Retrieval Advantage
Before the LLM writes a single word, the backend executes a Cypher query to retrieve verifiable graph data. 

**Example AI Context Query:**
```cypher
MATCH (c:Contractor {name: "SafeGuard Security"})-[:HAS_COMPLETED]->(p:PastPerformance)-[:ALIGNS_WITH]->(n:NAICS_Code {code: "541512"})
MATCH (o:Opportunity {id: "SAM_12345"})-[:REQUIRES_NAICS]->(n)
RETURN p.project_name, p.value, p.agency_client