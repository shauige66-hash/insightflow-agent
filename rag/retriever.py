# 负责根据用户分析需求，从向量库中检索最相关的业务知识。

from langchain_core.vectorstores import InMemoryVectorStore


def retrieve_knowledge(
    vector_store: InMemoryVectorStore,
    query: str,
    top_k: int = 3
) -> list[str]:

    documents = vector_store.similarity_search(
        query=query,
        k=top_k
    )

    return [
        document.page_content.strip()
        for document in documents
        if document.page_content.strip()
    ]