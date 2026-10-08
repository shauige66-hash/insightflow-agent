# 根据知识文件名称和内容生成稳定的 RAG 缓存标识。

import hashlib
from pathlib import Path


def build_knowledge_cache_key(
    knowledge_sources: list[str]
) -> str:

    file_fingerprints = []

    for source in knowledge_sources:

        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(
                f"Knowledge source not found: "
                f"{path}"
            )

        content_hash = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        fingerprint = (
            f"{path.name}:{content_hash}"
        )

        file_fingerprints.append(
            fingerprint
        )

    combined = "|".join(
        sorted(file_fingerprints)
    )

    return hashlib.sha256(
        combined.encode("utf-8")
    ).hexdigest()