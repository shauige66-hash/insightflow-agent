# 负责加载 RAG 使用的业务知识文档，并转换为统一 Document 结构。

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


def load_knowledge_document(
    source_path: str
) -> list[Document]:

    path = Path(source_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge source not found: {path}"
        )

    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:

        content = path.read_text(
            encoding="utf-8"
        )

        return [
            Document(
                page_content=content,
                metadata={
                    "source": str(path)
                }
            )
        ]

    if suffix == ".pdf":

        reader = PdfReader(
            str(path)
        )

        documents = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": str(path),
                        "page": page_number
                    }
                )
            )

        return documents

    raise ValueError(
        f"Unsupported knowledge source: "
        f"{path.suffix}"
    )# 负责加载 RAG 使用的业务知识文档，并转换为统一 Document 结构。

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


def load_knowledge_document(
    source_path: str
) -> list[Document]:

    path = Path(source_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge source not found: {path}"
        )

    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:

        content = path.read_text(
            encoding="utf-8"
        )

        return [
            Document(
                page_content=content,
                metadata={
                    "source": str(path)
                }
            )
        ]

    if suffix == ".pdf":

        reader = PdfReader(
            str(path)
        )

        documents = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": str(path),
                        "page": page_number
                    }
                )
            )

        return documents

    raise ValueError(
        f"Unsupported knowledge source: "
        f"{path.suffix}"
    )