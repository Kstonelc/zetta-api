from langchain_core.messages import HumanMessage
from llm.deepseek import DeepseekProvider

provider = DeepseekProvider(
    api_key="sk-72b635b190514c8b90cfcbfe750fa61a", enable_deep_think=True
)

for chunk in provider.stream([HumanMessage(content="来一段唐诗并展示思考过程")]):
    # 兼容兜底：chunk 可能是 AIMessageChunk 或 str
    if hasattr(chunk, "content"):
        ak = getattr(chunk, "additional_kwargs", None) or {}
        phase = ak.get("phase")  # "thinking" or "answer" or None

        if phase == "thinking":
            print("[thinking] ", end="")

        # 统一输出 content（思考/答案都走这里）
        if chunk.content:
            print(chunk.content, end="", flush=True)
    else:
        # 退化为纯文本流（拿不到 phase，就不加前缀了）
        print(str(chunk), end="", flush=True)

print()
