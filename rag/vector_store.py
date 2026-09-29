# 负责把业务知识文本转换为向量，并构建本地内存向量库。

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def create_vector_store(
    documents: list[Document]
) -> InMemoryVectorStore:

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vector_store = InMemoryVectorStore(
        embedding=embeddings
    )

    vector_store.add_documents(
        documents=documents
    )

    return vector_store