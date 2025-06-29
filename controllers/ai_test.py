from fastapi import APIRouter

from config import settings
from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from enums import QWModelType
from llm.qwen import ChatQW

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/demo1")
async def test():
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
async def test():
    llm = ChatQW(model_name=QWModelType.qw_turbo)
    for chunk in llm.stream("中国的首都是谁"):
        print(chunk, end="", flush=True)
    return {"ok": True}
