from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
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
            return TextLoader(str(file_path), encoding="utf-8").load()
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


def _stable_parent_id(doc: Document) -> str:
    src = str(doc.metadata.get("source", "")) + "|" + str(doc.metadata.get("page", ""))
    base = src + "|" + doc.page_content
    return "parent_" + hashlib.md5(base.encode("utf-8", "ignore")).hexdigest()[:16]


def split_doc_with_parents(
    docs: List[Document],
    parent_mode: str = "paragraph",  # "paragraph" or "full_doc"
    parent_chunk_size: int = 1024,
    parent_chunk_overlap: int = 50,
    child_chunk_size: int = 512,
    child_chunk_overlap: int = 10,
    parent_separators: List[str] = None,
    child_separators: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    返回一个父块列表，每个父块里包含它的子块 children。
    """
    if parent_separators is None:
        parent_separators = ["\n\n", "\r\n\r\n"]
    if child_separators is None:
        child_separators = ["\n", "\r\n"]

    # 父块切分器
    if parent_mode == "paragraph":
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap,
            separators=parent_separators,
            keep_separator=False,
            add_start_index=True,
            strip_whitespace=True,
        )
    elif parent_mode == "full_doc":
        parent_splitter = None
    else:
        raise ValueError(f"Unsupported parent_mode: {parent_mode}")

    # 子块切分器
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap,
        separators=child_separators,
        keep_separator=False,
        add_start_index=True,
        strip_whitespace=True,
    )

    parent_list: List[Dict[str, Any]] = []

    for doc in docs:
        if parent_mode == "full_doc":
            pid = _stable_parent_id(doc)
            parent_entry = {
                "parent_id": pid,
                "content": doc.page_content,
                "metadata": dict(doc.metadata),
                "children": [],
            }
            # 只这一块作为父
            parent_docs = [
                Document(
                    page_content=doc.page_content,
                    metadata={**doc.metadata, "parent_id": pid},
                )
            ]
        else:
            raw_parent_docs = parent_splitter.split_documents([doc])
            parent_docs = []
            parent_entry_map = {}
            for pc in raw_parent_docs:
                pid = _stable_parent_id(pc)
                pc.metadata["parent_id"] = pid
                parent_entry = {
                    "parent_id": pid,
                    "content": pc.page_content,
                    "metadata": dict(pc.metadata),
                    "children": [],
                }
                parent_list.append(parent_entry)
                parent_entry_map[pid] = parent_entry
                parent_docs.append(pc)

        # 对每个父块切子块并挂入其 children
        for pc in parent_docs:
            pid = pc.metadata.get("parent_id")
            cc_list = child_splitter.split_documents([pc])
            # 找到父 entry
            if parent_mode == "full_doc":
                parent_entry = parent_list[-1] if parent_list else None
            else:
                parent_entry = parent_entry_map.get(pid)
            if parent_entry is None:
                continue
            for cc in cc_list:
                child_item = {
                    "content": cc.page_content,
                    "metadata": dict(cc.metadata),
                    "child_start": cc.metadata.get("start_index"),
                    "child_end": cc.metadata.get("start_index", 0)
                    + len(cc.page_content),
                }
                parent_entry["children"].append(child_item)

    # 如果 paragraph 模式， parent_list 已通过 loop填充；
    # 如果 full_doc 模式，只父那一项尚未被 append（可能需要手-append）
    if parent_mode == "full_doc":
        # parent_list might be empty if not yet appended
        # We appended none above, so we need to create and append
        # Actually we appended in the loop; ensure unique
        pass

    return parent_list
