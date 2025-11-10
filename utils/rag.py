from pathlib import Path
from typing import List
import re

from langchain_core.documents import Document
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from enums import FileType


# 文档加载器
def load_doc(file_path: str | Path) -> List[Document]:
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    try:
        if suffix in FileType.Doc.suffix:
            return TextLoader(str(file_path), encoding="utf-8").load()
        elif suffix in FileType.Md.suffix:
            return UnstructuredMarkdownLoader(
                str(file_path),
            ).load()
        elif suffix in FileType.Pdf.suffix:
            return PyPDFLoader(str(file_path)).load()
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
    except Exception as e:
        raise ValueError(f"加载文件失败: {e}")


# 常规文档切割
def split_doc(
    doc: Document, chunk_size: int = 1204, chunk_overlap: int = 50
) -> List[Document]:
    # 使用MD文件的切割器
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
    return splitter.split_documents(doc)


# 父子文档切割
def split_doc_with_parents(
    docs: list[Document],
    parent_chunk_size: int = 1024,
    child_chunk_size: int = 512,
    parent_chunk_overlap: int = 200,
    child_chunk_overlap: int = 50,
):
    cleaned_docs = []
    for d in docs:
        text = normalize_whitespace(d.page_content)
        cleaned_docs.append(Document(page_content=text, metadata=d.metadata))
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_chunk_overlap,
        separators=["\n\n", "\r\n\r\n", "\n", "\r\n", " "],
        keep_separator="end",
        add_start_index=True,
    )

    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap,
        separators=["\n", "\r\n", " "],
        keep_separator="end",
        add_start_index=True,
    )

    parent_chunks = parent_splitter.split_documents(cleaned_docs)
    for idx, pc in enumerate(parent_chunks):
        pc.metadata["parent_id"] = f"parent_{idx}"

    child_chunks = []
    for pc in parent_chunks:
        cc_list = child_splitter.split_documents([pc])
        for cc in cc_list:
            # 把 parent_id 传给 child
            cc.metadata["parent_id"] = pc.metadata["parent_id"]
            child_chunks.append(cc)
    return child_chunks


def normalize_whitespace(text: str) -> str:
    # 将任意多个空白字符（空格、制表、换行）替换为一个空格
    text = re.sub(r"\s+", " ", text)
    return text.strip()
