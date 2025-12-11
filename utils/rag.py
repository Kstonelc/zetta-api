from pathlib import Path
from typing import List, Dict, Any, Tuple
import hashlib
import re

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    CharacterTextSplitter,
)
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from enums import FileType


# region 文件类型判断


def _is_markdown(doc: Document) -> bool:
    """根据 source 后缀或正文特征做一个轻量判定。"""
    src = str(doc.metadata.get("source", "")).lower()
    if src.endswith(".md") or src.endswith(".markdown"):
        return True
    # 兜底：检测常见 markdown 结构
    return bool(re.search(r"(^|\n)#{1,3}\s+\S+", doc.page_content))


def _is_pdf(doc: Document) -> bool:
    """根据 source 后缀或正文特征做一个轻量判定。"""
    src = str(doc.metadata.get("source", "")).lower()
    if src.endswith(".pdf"):
        return True
    # 兜底：检测常见 pdf 特征
    return bool(re.search(r"^%PDF-", doc.page_content))


# endregion


# 文档加载器
def load_doc(file_path: str | Path) -> List[Document]:
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    try:
        if suffix in FileType.Doc.suffix:
            return TextLoader(str(file_path), encoding="utf-8").load()
        elif suffix in FileType.Md.suffix:
            return UnstructuredMarkdownLoader(str(file_path), encoding="utf-8").load()
        elif suffix in FileType.Pdf.suffix:
            return PyPDFLoader(str(file_path)).load()
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
    except Exception as e:
        raise ValueError(f"加载文件失败: {e}")


# 固定字符数分块
def split_to_fixed_chunks(
    doc: Document, chunk_size: int = 1204, chunk_overlap: int = 50
) -> List[Document]:
    splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(doc)


def _stable_parent_id_from_text(text: str, meta: Dict[str, Any]) -> str:
    src = str(meta.get("source", "")) + "|" + str(meta.get("page", ""))
    base = src + "|" + text
    return "parent_" + hashlib.md5(base.encode("utf-8", "ignore")).hexdigest()[:16]


def normalize_pdf_text(s: str) -> str:
    # 统一换行
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # 去软连字符 & 多余空白
    s = s.replace("\u00ad", "")  # soft hyphen
    s = re.sub(r"[ \t\u00A0\u3000]+", " ", s)  # NBSP/全角空格 -> 普通空格
    # 各类项目符号统一为换行 + 连字符
    bullets = r"[\u2022\u25CF\u25CB\u25A0\u25AA\u25E6\u2043\u2219\uF0B7]"  # •●○■▪◦⁃∙
    s = re.sub(rf"\s*{bullets}\s*", "\n- ", s)
    # 常见中文编号（1. / 1、 / （1））前插入换行，便于切分
    s = re.sub(r"(?<!\n)(\n?\s*)(\(?\d{1,3}\)|\d{1,3}[\.、])\s*", r"\n\2 ", s)
    return s


# preview 模式下使用
def preview_doc_with_parents(
    docs: List[Document],
    parent_chunk_size: int = 1000,
    parent_chunk_overlap: int = 100,
    child_chunk_size: int = 400,
    child_chunk_overlap: int = 50,
) -> List[Dict[str, Any]]:
    """
    仅区分 Markdown 与 非 Markdown 的父子切分：
    - Markdown：按 H1/H2/H3 切父块，并把标题文本回填到父块 content 顶部
    - 非 Markdown：用递归切父块（偏段落）
    - 子块：统一递归切分，优先换行，再标点
    返回：[{parent_id, content, metadata, children:[{content, metadata, child_start, child_end}]}]
    """
    # 非 MD 父块切分（偏段落）
    parent_splitter_generic = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_chunk_overlap,
        separators=["\n\n", "\r\n\r\n", "\n", "\r\n", " "],
        keep_separator=False,
        add_start_index=True,
        strip_whitespace=True,
    )

    # 子块统一切分器（优先换行，再中英标点，最后空格）
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap,
        separators=[
            "\n\n",
            "\n",  # 段/行
            "- ",  # 归一化后的项目符号行
            "。",
            "！",
            "？",
            ".",
            "!",
            "?",  # 句读
            " ",  # 兜底
        ],
        keep_separator=False,
        add_start_index=True,
        strip_whitespace=True,
    )

    results: List[Dict[str, Any]] = []

    for doc in docs:
        # 预处理 pdf 文件 TODO
        if _is_pdf(doc):
            doc.page_content = normalize_pdf_text(doc.page_content)
        if _is_markdown(doc):
            # 1) Markdown：标题切父块
            md_headers = [
                ("#", "H1"),
                ("##", "H2"),
                ("###", "H3"),
                ("####", "H4"),
                ("#####", "H5"),
            ]
            md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=md_headers)
            sections = md_splitter.split_text(doc.page_content)

            for sec in sections:
                # 回填标题文本，避免丢失层级上下文
                h1 = sec.metadata.get("H1")
                h2 = sec.metadata.get("H2")
                h3 = sec.metadata.get("H3")
                h4 = sec.metadata.get("H4")
                h5 = sec.metadata.get("H5")
                header_lines = []
                if h1:
                    header_lines.append(f"# {h1}")
                if h2:
                    header_lines.append(f"## {h2}")
                if h3:
                    header_lines.append(f"### {h3}")
                if h4:
                    header_lines.append(f"#### {h4}")
                if h5:
                    header_lines.append(f"##### {h5}")
                header_text = "\n".join(header_lines)
                parent_text = (header_text + "\n\n" if header_text else "") + (
                    sec.page_content or ""
                )

                parent_meta = {**doc.metadata, **sec.metadata}
                parent_id = _stable_parent_id_from_text(parent_text, parent_meta)

                # 2) 子块：对 parent_text 再做一次统一子分 chunk
                parent_doc = Document(page_content=parent_text, metadata=parent_meta)
                children_docs = child_splitter.split_documents([parent_doc])

                parent_entry = {
                    "parent_id": parent_id,
                    "content": parent_text,
                    "metadata": dict(parent_meta),
                    "children": [],
                }

                for cc in children_docs:
                    start = int(cc.metadata.get("start_index", 0) or 0)
                    end = start + len(cc.page_content)
                    child_meta = dict(parent_meta)
                    parent_entry["children"].append(
                        {
                            "content": cc.page_content,
                            "metadata": child_meta,
                            "child_start": start,
                            "child_end": end,
                        }
                    )

                results.append(parent_entry)

        else:
            # 非 Markdown：直接段落式父块
            parent_docs = parent_splitter_generic.split_documents([doc])

            for pc in parent_docs:
                parent_meta = dict(pc.metadata)
                parent_text = pc.page_content
                parent_id = _stable_parent_id_from_text(parent_text, parent_meta)

                # 子块
                parent_doc = Document(page_content=parent_text, metadata=parent_meta)
                children_docs = child_splitter.split_documents([parent_doc])

                parent_entry = {
                    "parent_id": parent_id,
                    "content": parent_text,
                    "metadata": parent_meta,
                    "children": [],
                }

                for cc in children_docs:
                    start = int(cc.metadata.get("start_index", 0) or 0)
                    end = start + len(cc.page_content)
                    child_meta = dict(parent_meta)
                    parent_entry["children"].append(
                        {
                            "content": cc.page_content,
                            "metadata": child_meta,
                            "child_start": start,
                            "child_end": end,
                        }
                    )

                results.append(parent_entry)

    return results


# rag 分块
def split_docs_with_parents(
    docs: List[Document],
    parent_chunk_size: int = 1000,
    parent_chunk_overlap: int = 100,
    child_chunk_size: int = 400,
    child_chunk_overlap: int = 50,
    return_parent_docs: bool = False,
) -> Tuple[List[Document], List[Document]]:

    parent_splitter_generic = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_chunk_overlap,
        separators=["\n\n", "\n"],
        keep_separator=False,
        add_start_index=True,
        strip_whitespace=True,
    )

    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap,
        separators=["\n\n", "\n"],
        keep_separator=False,
        add_start_index=True,
        strip_whitespace=True,
    )

    parent_docs: List[Document] = []
    child_docs: List[Document] = []

    # 一个原始 doc 内部的父块序号累加器
    for doc in docs:
        text = doc.page_content or ""
        base_meta = dict(doc.metadata or {})

        if _is_pdf(doc):
            text = normalize_pdf_text(text)

        parent_index_counter = 0  # 当前 document 内父块 index

        if _is_markdown(doc):
            md_headers = [
                ("#", "H1"),
                ("##", "H2"),
                ("###", "H3"),
                ("####", "H4"),
                ("#####", "H5"),
            ]
            md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=md_headers)
            sections: List[Document] = md_splitter.split_text(text)

            for sec in sections:
                # 拼标题
                h1 = sec.metadata.get("H1")
                h2 = sec.metadata.get("H2")
                h3 = sec.metadata.get("H3")
                h4 = sec.metadata.get("H4")
                h5 = sec.metadata.get("H5")
                header_lines = []
                if h1:
                    header_lines.append(f"# {h1}")
                if h2:
                    header_lines.append(f"## {h2}")
                if h3:
                    header_lines.append(f"### {h3}")
                if h4:
                    header_lines.append(f"#### {h4}")
                if h5:
                    header_lines.append(f"##### {h5}")
                header_text = "\n".join(header_lines)

                parent_text = (header_text + "\n\n" if header_text else "") + (
                    sec.page_content or ""
                )

                # 原 splitter 没给 markdown 段落 start_index，这里就不算偏移，给个 None
                start_offset = sec.metadata.get("start_index")
                if start_offset is None:
                    start_offset = 0
                end_offset = start_offset + len(parent_text)

                parent_index = parent_index_counter
                parent_index_counter += 1

                parent_id = _stable_parent_id_from_text(parent_text, base_meta)

                parent_meta = {
                    **base_meta,
                    **sec.metadata,
                    "parent_id": parent_id,  # 逻辑父 ID，用来做映射
                    "parent_index": parent_index,  # -> ParentChunk.index
                    "start_offset": start_offset,  # -> ParentChunk.start_offset
                    "end_offset": end_offset,  # -> ParentChunk.end_offset
                    "type": 1,  # 自定义：1=markdown父块
                    "is_parent": True,
                }

                if return_parent_docs:
                    parent_docs.append(
                        Document(page_content=parent_text, metadata=parent_meta)
                    )

                # 子块切分
                tmp_parent_doc = Document(
                    page_content=parent_text, metadata=parent_meta
                )
                children = child_splitter.split_documents([tmp_parent_doc])

                for idx_in_parent, cc in enumerate(children):
                    start = int(cc.metadata.get("start_index", 0) or 0)
                    end = start + len(cc.page_content or "")

                    child_meta = {
                        **parent_meta,
                        "is_parent": False,
                        "child_start": start,  # 在父块内的 offset
                        "child_end": end,
                        "index_in_parent": idx_in_parent,  # -> ChildChunk.index_in_parent
                    }

                    child_docs.append(
                        Document(
                            page_content=cc.page_content,
                            metadata=child_meta,
                        )
                    )

        else:
            # 普通文本 / PDF：先按 parent_splitter 切父块
            original_doc = Document(page_content=text, metadata=base_meta)
            generic_parents: List[Document] = parent_splitter_generic.split_documents(
                [original_doc]
            )

            for pc in generic_parents:
                parent_text = pc.page_content or ""
                pm = dict(pc.metadata or {})

                start_offset = int(pm.get("start_index", 0) or 0)
                end_offset = start_offset + len(parent_text)

                parent_index = parent_index_counter
                parent_index_counter += 1

                parent_id = _stable_parent_id_from_text(parent_text, base_meta)

                parent_meta = {
                    **base_meta,
                    **pm,
                    "parent_id": parent_id,
                    "parent_index": parent_index,
                    "start_offset": start_offset,
                    "end_offset": end_offset,
                    "type": 0,  # 自定义：0=普通父块
                    "is_parent": True,
                }

                if return_parent_docs:
                    parent_docs.append(
                        Document(page_content=parent_text, metadata=parent_meta)
                    )

                tmp_parent_doc = Document(
                    page_content=parent_text, metadata=parent_meta
                )
                children = child_splitter.split_documents([tmp_parent_doc])

                for idx_in_parent, cc in enumerate(children):
                    start = int(cc.metadata.get("start_index", 0) or 0)
                    end = start + len(cc.page_content or "")

                    child_meta = {
                        **parent_meta,
                        "is_parent": False,
                        "child_start": start,
                        "child_end": end,
                        "index_in_parent": idx_in_parent,
                    }

                    child_docs.append(
                        Document(
                            page_content=cc.page_content,
                            metadata=child_meta,
                        )
                    )

    return (parent_docs, child_docs)
