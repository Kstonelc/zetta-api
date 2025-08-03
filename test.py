from langchain_community.document_loaders import UnstructuredMarkdownLoader
from pathlib import Path
from typing import List
from langchain_text_splitters import (
    CharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.schema import Document

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from llm.qwen import QWProvider

# 记载 md 文档


# 切分文档


"""
1 separator: str= "\n\n"
2 is_separator_regex: bool 默认当普通字符串处理 True 为 正则表达式匹配
3 chunk_size: int 4000 每个 chunk 的最大长度 
4 chunk_overlap: int = 200 相邻两个 chunk 中的重叠字符数
5 keep_separator: bool 是否保留分隔符
6 add_start_index 是否在 metadata 中 记录 chunk 在原文中的起始索引
7 strip_whitespace: bool 是否在.strip()处理 chunk 前后的空白符
"""


def split_md(filepath: str) -> List[Document]:
    """加载 .md 并按标题 + 长度分段，保持结构清晰与内容完整"""
    text = Path(filepath).read_text(encoding="utf-8")
    # 确保开头没丢 “## ”
    if "## " not in text:
        print(f"⚠️ 文件中未检测到 '## '，是否格式不标准？请先 inspect text:\n{text!r}")
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,  # 保留标题行到 chunk.text 中，便于检索上下文一致性 :contentReference[oaicite:6]{index=6}
    )
    header_docs = splitter.split_text(text)
    rec_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    final = []
    for doc in header_docs:
        content = doc.page_content.strip()
        if not content:
            continue
        if len(content) > 800:
            final.extend(rec_splitter.split_documents([doc]))
        else:
            final.append(doc)
    return final


chunks = split_md("data/test.md")
print("一共切分出", len(chunks), "个 chunk：")
for i, c in enumerate(chunks):
    print(f"=== Chunk {i} metadata:", c.metadata)
    print(c.page_content.splitlines())  # 打印首行（通常是 header）

# 3. Embeddings & Qdrant 客户端
# client = QdrantClient(
#     url="http://121.5.5.83:8001",
#     api_key="Beyond#11",
#     prefer_grpc=True,
# )
#
# """
# Distance.COSINE: 计算向量相似度的方式 余弦相似度
# """
# if not client.collection_exists("zetta"):
#     client.create_collection(
#         collection_name="zetta",
#         vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
#     )
#
#
# llm = QWProvider()
#
# # 4. 存储到 Qdrant
# vectorstore = QdrantVectorStore(
#     client=client, collection_name="zetta", embedding=llm.get_embedding()
# )
# vectorstore.add_documents(documents=chunks)
#
# # 5. Retriever
# retriever = vectorstore.as_retriever(
#     search_type="mmr", search_kwargs={"k": 1, "fetch_k": 1}
# )
# # 6. 测试问答流程
#
# relevant_docs = retriever.invoke("install Package")
# most_similar_doc = relevant_docs[0]
# print(most_similar_doc.page_content)
