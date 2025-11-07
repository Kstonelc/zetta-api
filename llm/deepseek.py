from typing import Any, Dict, Iterator, List, Optional

from pydantic import Field, PrivateAttr
from openai import OpenAI

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    FunctionMessage,
    ChatMessage,
    AIMessageChunk,
)
from langchain_core.outputs import (
    ChatGeneration,
    ChatGenerationChunk,
    ChatResult,
)


class DeepseekProvider(BaseChatModel):
    """OpenAI 兼容 Chat 模型的 LangChain 适配器（阻塞与流式）"""

    model: str = Field(default="deepseek-v3.1", description="模型名")
    api_key: Optional[str] = Field(default=None, description="API Key")
    base_url: Optional[str] = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="Base URL",
    )
    temperature: float = Field(default=0.2)
    max_tokens: Optional[int] = Field(default=None)
    request_timeout: int = Field(default=60, description="请求超时时间")

    enable_deep_think: bool = Field(default=False, description="是否启用深度思考模式")

    _client: OpenAI = PrivateAttr()

    # ===== 生命周期 =====
    def model_post_init(self, __context: Any) -> None:
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.request_timeout,
        )

    # ===== BaseChatModel 必需属性 =====
    @property
    def _llm_type(self) -> str:
        return "openai-compatible-chat"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "request_timeout": self.request_timeout,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_deep_think": self.enable_deep_think,
        }

    # ===== 公用：消息转换 =====
    def _lc_to_openai_messages(
        self, messages: List[BaseMessage]
    ) -> List[Dict[str, Any]]:
        """
        LangChain BaseMessage -> OpenAI ChatCompletion 格式
        """
        out: List[Dict[str, Any]] = []
        for m in messages:
            if isinstance(m, HumanMessage):
                out.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                out.append({"role": "assistant", "content": m.content})
            elif isinstance(m, SystemMessage):
                out.append({"role": "system", "content": m.content})
            elif isinstance(m, ToolMessage):
                out.append({"role": "tool", "content": m.content, "name": m.tool_name})
            elif isinstance(m, FunctionMessage):
                out.append({"role": "function", "content": m.content, "name": m.name})
            elif isinstance(m, ChatMessage):
                out.append({"role": m.role, "content": m.content})
            else:
                out.append({"role": "user", "content": m.content})
        return out

    # ===== 阻塞：_generate =====
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        阻塞调用：返回完整的 ChatResult
        """
        oai_messages = self._lc_to_openai_messages(messages)
        extra_body = {"enable_thinking": True} if self.enable_deep_think else {}

        resp = self._client.chat.completions.create(
            model=self.model,
            messages=oai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
            stop=stop,
            extra_body=extra_body,
            **kwargs,
        )

        msg_content = resp.choices[0].message.content or ""
        reasoning = getattr(resp.choices[0].message, "reasoning_content", None)

        ai_msg = AIMessage(
            content=msg_content,
            additional_kwargs={"reasoning_content": reasoning} if reasoning else {},
        )

        gen = ChatGeneration(message=ai_msg)
        return ChatResult(generations=[gen], llm_output={"raw": resp})

    # ===== 流式：_stream =====
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        oai_messages = self._lc_to_openai_messages(messages)
        extra_body = {"enable_thinking": True} if self.enable_deep_think else {}

        stream = self._client.chat.completions.create(
            model=self.model,
            messages=oai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            stop=stop,
            extra_body=extra_body,
            **kwargs,
        )

        for ev in stream:
            delta = ev.choices[0].delta

            # 1) 思考阶段（若有）
            r = getattr(delta, "reasoning_content", None)
            if r and self.enable_deep_think:
                if run_manager:
                    run_manager.on_llm_new_token(r, metadata={"phase": "thinking"})
                yield ChatGenerationChunk(
                    message=AIMessageChunk(
                        content=r,
                        additional_kwargs={"phase": "thinking"},
                    ),
                )

            # 2) 最终回答阶段
            c = getattr(delta, "content", None)
            if c:
                if run_manager:
                    run_manager.on_llm_new_token(c, metadata={"phase": "answer"})
                yield ChatGenerationChunk(
                    message=AIMessageChunk(
                        content=c,
                        additional_kwargs={"phase": "answer"},
                    ),
                )
