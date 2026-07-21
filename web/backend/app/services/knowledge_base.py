"""
Generic Knowledge Base Stub.
Replaces the old legal-specific knowledge_base.py to prevent import errors in the generic backend.
"""
from typing import Dict, Any, Optional

KNOWLEDGE_BASE: Dict[str, Any] = {}
LAW_METADATA: Dict[str, Any] = {}
ALL_LAWS_CATEGORY = "all"

def load_knowledge_base() -> None:
    pass

def determine_category(law_name: str) -> str:
    return ALL_LAWS_CATEGORY

def normalize_category(category: str) -> str:
    return ALL_LAWS_CATEGORY

def document_matches_category(metadata: Dict[str, Any], target_category: str) -> bool:
    return True

def resolve_reference_data(ref_id: str) -> Optional[Dict[str, Any]]:
    return None
