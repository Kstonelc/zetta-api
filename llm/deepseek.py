from typing import Any, Dict, Iterator, List, Optional
from pydantic import Field, PrivateAttr
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, AIMessageChunk


class DeepseekProvider(LLM):
    model: str = Field(default="deepseek-v3.1", description="模型名")
    api_key: Optional[str] = Field(default=None, description="API Key")
    base_url: Optional[str] = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="Base URL",
    )
    temperature: float = Field(default=0.2)
    max_tokens: Optional[int] = Field(default=None)
    request_timeout: int = Field(default=60, description="请求超时时间")

    _client: ChatOpenAI = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._client = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.request_timeout,
        )

    @property
    def _llm_type(self) -> str:
        return "openai-compatible"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "request_timeout": self.request_timeout,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        assert self._client is not None, "LangChain ChatOpenAI not initialized"

        # ChatOpenAI 正确用法：invoke
        msg: AIMessage = self._client.invoke(prompt, stop=stop, **kwargs)
        return msg.content if isinstance(msg.content, str) else str(msg.content)

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        assert self._client is not None, "LangChain ChatOpenAI not initialized"

        for chunk in self._client.stream(prompt, stop=stop, **kwargs):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                text = chunk.content
                if run_manager and text:
                    run_manager.on_llm_new_token(text)
                yield GenerationChunk(text=text)

    def test_api_key(self, test_prompt: str = "你好") -> bool:
        try:
            self._client.invoke(test_prompt)
            return True
        except Exception as e:
            return False
