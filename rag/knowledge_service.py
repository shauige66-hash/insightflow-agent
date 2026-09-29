# 统一组织业务知识文档的加载、切分、向量化和检索流程。

from rag.chunker import split_documents
from rag.document_loader import load_knowledge_document
from rag.retriever import retrieve_knowledge
from rag.vector_store import create_vector_store


def build_and_retrieve_knowledge(
    knowledge_sources: list[str],
    query: str,
    top_k: int = 3
) -> list[str]:

    if not knowledge_sources:
        return []

    documents = []

    for source_path in knowledge_sources:

        source_documents = (
            load_knowledge_document(
                source_path
            )
        )

        documents.extend(
            source_documents
        )

    if not documents:
        return []

    chunks = split_documents(
        documents
    )

    if not chunks:
        return []

    vector_store = create_vector_store(
        chunks
    )

    retrieved_knowledge = retrieve_knowledge(
        vector_store=vector_store,
        query=query,
        top_k=top_k
    )

    return retrieved_knowledge