from typing import Any, Dict, Iterator, List, Optional
from pydantic import Field, PrivateAttr
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import AIMessage  # 用于 _call 返回类型

import os
from openai import OpenAI  # 直接使用 openai-python SDK


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

    enable_deep_think: bool = Field(default=False, description="是否启用深度思考模式")

    _client: OpenAI = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        """初始化底层 OpenAI 客户端"""
        # 设置环境变量或直接传 api_key/base_url
        client = OpenAI(
            api_key=self.api_key or os.getenv("OPENAI_API_KEY"),
            base_url=self.base_url,
            timeout=self.request_timeout,
        )
        self._client = client

    @property
    def _llm_type(self) -> str:
        return "openai-compatible"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "request_timeout": self.request_timeout,
            "enable_deep_think": self.enable_deep_think,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # 一次性调用（非流式）
        extra = {"enable_thinking": True} if self.enable_deep_think else {}
        messages = [{"role": "user", "content": prompt}]
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
            extra_body=extra,
            stop=stop,
            **kwargs,
        )
        # 假设 SDK 返回标准结构
        answer = response.choices[0].message.content
        return answer

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        extra = {"enable_thinking": True} if self.enable_deep_think else {}
        messages = [{"role": "user", "content": prompt}]
        # 流式调用
        stream_resp = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            extra_body=extra,
            stop=stop,
            **kwargs,
        )
        thinking_buf = []
        answer_buf = []
        is_answering = False

        for chunk in stream_resp:
            # chunk 结构可能依 SDK 版本不同
            # 我们假设 chunk.choices[0].delta 有两字段： reasoning_content / content
            delta = chunk.choices[0].delta
            # 捕捉思考内容
            r = getattr(delta, "reasoning_content", None)
            if r is not None and not is_answering:
                print(222, r)
                thinking_buf.append(r)
                # 可选：立刻把思考 token 输出
                yield GenerationChunk(text=r)
            # 捕捉答案内容
            c = getattr(delta, "content", None)
            if c is not None:
                print(444, c)
                # 第一次出现 content，标记为回答阶段
                if not is_answering:
                    is_answering = True
                # 回调每个 token 给 run_manager
                if run_manager:
                    run_manager.on_llm_new_token(c)
                answer_buf.append(c)
                yield GenerationChunk(text=c)
