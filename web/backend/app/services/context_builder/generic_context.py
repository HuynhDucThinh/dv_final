from typing import List, Dict, Any
from langchain_core.documents import Document

class GenericContextBuilder:
    """Generic context builder implementation."""
    
    @property
    def strategy_name(self) -> str:
        return "generic_context"
        
    def build_context(self, docs: List[Document]) -> List[Document]:
        """Simply return the documents as-is without any nested building."""
        return docs
