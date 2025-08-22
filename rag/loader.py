from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from enums import FileType


class FileLoader:

    def load(self, file_path: str | Path) -> List[Document]:
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix in FileType.Doc.suffix:
            return TextLoader(str(file_path), encoding="utf-8").load()
        elif suffix in FileType.Md.suffix:
            return UnstructuredMarkdownLoader(str(file_path)).load()
        elif suffix in FileType.Pdf.suffix:
            return PyPDFLoader(str(file_path)).load()
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
