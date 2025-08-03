from fastapi import APIRouter
from uuid import uuid4

from config import settings
from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from enums import QWModelType
from llm.qwen import QWProvider
from utils.vector_db import vector_client

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
    llm = QWProvider(model_name=QWModelType.qw_turbo)
    for chunk in llm.stream("中国的首都是啥? 请用中文回答"):
        print(chunk, end="", flush=True)
    return {"ok": True}


@router.post("/demo3")
async def demo3():

    # 插入向量
    vector_client.insert(
        [
            {
                "id": str(uuid4()),
                "vector": [0.01] * 768,
                "payload": {"text": "说明文档", "source": "API"},
            }
        ]
    )

    # 搜索
    # results = store.search(
    #     query_vector=[0.1, 0.2, ...], limit=3, filter_payload={"source": "API"}
    # )

    # 删除
    # store.delete_by_id("doc1")

    # 更新
    # store.update(
    #     "doc1",
    #     new_vector=[0.3, 0.4, ...],
    #     new_payload={"text": "更新文档", "source": "manual"},
    # )
    return {"ok": True}
