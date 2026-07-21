from typing import List, Dict, Any
from langchain_core.documents import Document

class GenericChunker:
    """Generic chunker implementation for non-legal text."""
    
    @property
    def strategy_name(self) -> str:
        return "generic_chunker"
        
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Document]:
        """Convert raw dict data to LangChain documents."""
        docs = []
        for doc in documents:
            text = doc.get("text", doc.get("content", ""))
            meta = doc.get("metadata", {})
            docs.append(Document(page_content=text, metadata=meta))
        return docs
