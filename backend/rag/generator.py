import os
from openai import OpenAI

# Import our custom RAG tools
from rag.knowledge_graph import DynamicKnowledgeGraph
from rag.document_loader import DocumentProcessor

class ProposalGenerator:
    def __init__(self):
        # Using your local Ollama setup for zero-cost, private generation
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama" 
        )
        self.model_name = "llama3" # Swap to "mistral" if preferred
        
        # Initialize our real PDF loader and vector store
        self.doc_processor = DocumentProcessor()
        
    def _load_system_prompt(self) -> str:
        """Loads the advanced XML-structured prompt from our docs folder."""
        prompt_path = os.path.join(os.path.dirname(__file__), '../../docs/4_system_prompt.txt')
        try:
            with open(prompt_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "You are an expert Federal Proposal Writer."

    def generate(self, opportunity_data: dict, user_profile_data: dict, pdf_path: str = None) -> str:
        """
        Injects context into the prompt and generates the draft via local LLM.
        Now uses REAL vector search and REAL graph traversal.
        """
        opp_id = opportunity_data.get("opportunity_id", "Unknown")
        print(f"Initiating dynamic RAG generation using {self.model_name} for opportunity: {opp_id}...")
        
        # --- 1. REAL PDF RETRIEVAL (Vector Search) ---
        rfp_chunks = "No RFP constraints provided."
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"Processing PDF for {opp_id}...")
            chunks = self.doc_processor.ingest_pdf(pdf_path)
            vector_store = self.doc_processor.create_vector_store(chunks)
            
            # Search the PDF using the user's capabilities to find relevant clauses
            capabilities = user_profile_data.get('capabilities_statement', '')
            search_query = f"Requirements and evaluation factors related to {capabilities}"
            
            rfp_chunks = self.doc_processor.retrieve_relevant_chunks(vector_store, search_query)
        else:
            print("No PDF path provided or file not found. Skipping vector search.")
        
        # --- 2. DYNAMIC GRAPH RETRIEVAL (Entity Resolution) ---
        print("Traversing Knowledge Graph for verified past performance...")
        kg = DynamicKnowledgeGraph()
        verified_graph_experience = kg.build_and_match(opportunity_data, user_profile_data)
        
        # --- 3. CONTEXT ASSEMBLY ---
        # Combine the user's flat text profile with the highly specific Graph facts
        capabilities_stmt = user_profile_data.get('capabilities_statement', '')
        augmented_user_profile = f"Capabilities: {capabilities_stmt}\n\n{verified_graph_experience}"
        
        system_prompt = self._load_system_prompt()
        
        # Inject our dynamic variables into the XML tags
        system_prompt = system_prompt.replace("{{RFP_CHUNKS_FROM_VECTOR_DB}}", rfp_chunks)
        system_prompt = system_prompt.replace("{{USER_CAPABILITY_STATEMENT_AND_PAST_PERFORMANCE}}", augmented_user_profile)

        # --- 4. LLM GENERATION ---
        print("Sending payload to local LLM...")
        try:
            response = self.client.chat.completions.create(
                model=self.model_name, 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Draft the proposal based on my profile and the RFP requirements."}
                ],
                temperature=0.1 # Low temperature for factual compliance
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"Error connecting to local LLM: {str(e)}"
            print(error_msg)
            return error_msg