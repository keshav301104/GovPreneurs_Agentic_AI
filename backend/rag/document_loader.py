import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

class DocumentProcessor:
    def __init__(self):
        # We use your local Ollama for zero-cost, highly secure embeddings!
        # Make sure Ollama is running in the background.
        self.embeddings = OllamaEmbeddings(model="llama3") 
        
        # Recursive splitting ensures we don't chop legal clauses in half.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def ingest_pdf(self, pdf_path: str):
        """Loads a PDF file and splits it into manageable semantic chunks."""
        if not os.path.exists(pdf_path):
            return []
            
        print(f"Loading PDF from {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        print("Chunking document...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks.")
        return chunks

    def create_vector_store(self, chunks):
        """Converts text chunks into vectors and stores them in FAISS."""
        if not chunks:
            return None
        print("Embedding chunks into local FAISS vector database...")
        vector_store = FAISS.from_documents(chunks, self.embeddings)
        return vector_store

    def retrieve_relevant_chunks(self, vector_store, query: str, k: int = 4) -> str:
        """Searches the FAISS database for the most relevant RFP sections."""
        if not vector_store:
            return "No RFP text available."
            
        results = vector_store.similarity_search(query, k=k)
        
        # We include the Page Number in the output so the UI can cite its sources later!
        context = "\n\n".join([f"[Source: Page {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}" for doc in results])
        return context