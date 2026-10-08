# 负责创建和缓存 RAG 向量库，并复用 Embedding 模型实例。

from collections import OrderedDict
from functools import lru_cache

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from rag.config import VECTOR_STORE_CACHE_SIZE


EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


_VECTOR_STORE_CACHE: OrderedDict[
    str,
    InMemoryVectorStore
] = OrderedDict()


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


def get_cached_vector_store(
    cache_key: str
) -> InMemoryVectorStore | None:

    vector_store = _VECTOR_STORE_CACHE.pop(
        cache_key,
        None
    )

    if vector_store is None:
        return None

    _VECTOR_STORE_CACHE[
        cache_key
    ] = vector_store

    return vector_store


def create_and_cache_vector_store(
    documents: list[Document],
    cache_key: str
) -> InMemoryVectorStore:

    embeddings = get_embedding_model()

    vector_store = InMemoryVectorStore(
        embedding=embeddings
    )

    vector_store.add_documents(
        documents=documents
    )

    _VECTOR_STORE_CACHE[
        cache_key
    ] = vector_store

    while (
        len(_VECTOR_STORE_CACHE)
        > VECTOR_STORE_CACHE_SIZE
    ):
        _VECTOR_STORE_CACHE.popitem(
            last=False
        )

    return vector_store