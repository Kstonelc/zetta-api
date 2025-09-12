from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)
from enums import FileType


def load_doc(file_path: str | Path) -> List[Document]:
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix in FileType.Doc.suffix:
        return TextLoader(str(file_path), encoding="utf-8").load()
    elif suffix in FileType.Md.suffix:
        docs = TextLoader(str(file_path), encoding="utf-8").load()
        return docs
    elif suffix in FileType.Pdf.suffix:
        return PyPDFLoader(str(file_path)).load()
    else:
        raise ValueError(f"不支持的文件类型: {suffix}")


def split_doc(
    doc: Document, chunk_size: int = 1204, chunk_overlap: int = 50
) -> List[Document]:
    print(chunk_size, chunk_overlap)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n## ",
            "\n### ",
            "\n#### ",
            "\n\n",
            "\n",
            "。",
            ".",
            "!",
            "?",
            "；",
            ";",
            "，",
            ",",
            " ",
        ],
    )
    chunks = splitter.split_documents(doc)
    return chunks
