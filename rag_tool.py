from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import os

class RAGSearchSchema(BaseModel):
    """Input for RAGSearchTool."""
    query: str = Field(..., description="The cybersecurity query or anomaly description to search for in the MITRE ATT&CK base.")

class RAGSearchTool(BaseTool):
    name: str = "MITRE ATT&CK RAG Search"
    description: str = "Search the NOVA Knowledge Base for MITRE ATT&CK tactics, techniques, and threat intelligence."
    args_schema: type[BaseModel] = RAGSearchSchema
    
    # Tool attributes
    persist_dir: str = ".nova_knowledge"
    collection_name: str = "mitre_attack"
    embedding_model: Optional[Any] = None
    client: Optional[Any] = None
    collection: Optional[Any] = None

    def __init__(self, **data):
        super().__init__(**data)
        self._setup_knowledge_base()

    def _setup_knowledge_base(self):
        """Initialize local ChromaDB and embedding model."""
        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)
            
        # Load embedding model once
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def _run(self, query: str) -> str:
        """Search the knowledge base for the given query."""
        if not self.collection:
            return "Knowledge base not initialized."
            
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No matching threat intelligence found in the knowledge base."
            
        formatted_results = "\n---\n".join(results['documents'][0])
        return f"Top MITRE ATT&CK matches for '{query}':\n\n{formatted_results}"

    def add_knowledge(self, documents: List[str], ids: List[str], metadatas: Optional[List[Dict]] = None):
        """Helper to add information to the knowledge base."""
        embeddings = self.embedding_model.encode(documents).tolist()
        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

