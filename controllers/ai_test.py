from fastapi import APIRouter

from config import settings
from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from enums import QWModelType
from llm.qwen import ChatQW
from utils.chroma import ChromaWrapper

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/demo1")
async def demo1():
    # 提示 + 模型 + 输出解析器
    prompt = ChatPromptTemplate.from_template(
        "请根据下面的主题写一篇小红书的营销短文: {topics}"
    )
    llm = Tongyi(api_key=settings.QIANWEN_API_KEY)
    output_parser = StrOutputParser()
    # langchain 管道符 链式调用
    chain = prompt | llm | output_parser
    # 直接调用
    # print(chain.invoke({"topics": "小米Yu7"}))
    # 流式调用
    for chunk in chain.stream({"topics": "小米Yu7"}):
        print(chunk, end="", flush=True)
    return {"ok": True}


@router.post("/demo2")
async def demo2():
    llm = ChatQW(model_name=QWModelType.qw_turbo)
    for chunk in llm.stream("中国的首都是啥? 请用中文回答"):
        print(chunk, end="", flush=True)
    return {"ok": True}


@router.post("/demo3")
async def demo3():
    chroma_client = ChromaWrapper(collection_name="docs")
    # 添加数据
    chroma_client.add(
        doc_id="2",
        content="中国是一个伟大的国家111",
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    )
    # 查数据
    data = chroma_client.collection.get(include=["embeddings"])
    print(data)
    pass
