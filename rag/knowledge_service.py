# 统一组织业务知识文档的加载、切分、向量化和检索流程。

from rag.chunker import split_documents
from rag.document_loader import load_knowledge_document
from rag.retriever import retrieve_knowledge
from typing import Any
from rag.config import DEFAULT_TOP_K
from rag.cache_key import (build_knowledge_cache_key)
from rag.vector_store import (
    create_and_cache_vector_store,
    get_cached_vector_store
)


def build_and_retrieve_knowledge(
    knowledge_sources: list[str],
    query: str,
    top_k: int = DEFAULT_TOP_K
) -> list[dict[str, Any]]:

    if not knowledge_sources:
        return []

    cache_key = build_knowledge_cache_key(
    knowledge_sources
)

    vector_store = get_cached_vector_store(
        cache_key
    )

    if vector_store is None:

        documents = []

        for source in knowledge_sources:
            documents.extend(
                load_knowledge_document(
                    source
                )
            )

        chunks = split_documents(
            documents
        )

        vector_store = (
            create_and_cache_vector_store(
                documents=chunks,
                cache_key=cache_key
            )
        )

    retrieved_knowledge = retrieve_knowledge(
        vector_store=vector_store,
        query=query,
        top_k=top_k
    )

    return retrieved_knowledge