# 负责从向量库中检索与分析问题相关的业务知识。

from typing import Any

from langchain_core.vectorstores import InMemoryVectorStore
from rag.config import (
    DEFAULT_TOP_K,
    MIN_SIMILARITY_SCORE
)

def retrieve_knowledge(
    vector_store: InMemoryVectorStore,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    min_score: float = MIN_SIMILARITY_SCORE
) -> list[dict[str, Any]]:

    results = (
        vector_store.similarity_search_with_score(
            query=query,
            k=top_k
        )
    )

    retrieved_results = []

    for document, score in results:

        content = document.page_content.strip()

        if not content:
            continue

        if score < min_score:
            continue

        retrieved_results.append(
            {
                "content": content,
                "source": document.metadata.get(
                    "source"
                ),
                "page": document.metadata.get(
                    "page"
                ),
                "score": float(score)
            }
        )

    return retrieved_results