from typing import Any, Dict, Iterator, List, Optional
import json, requests
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun

DEFAULT_BASE_URL = "https://api.deepseek.com"
TIMEOUT = 60


class DeepseekProvider(LLM):
    model_name: str
    api_key: Optional[str] = None
    base_url: str = DEFAULT_BASE_URL
    request_timeout: int = TIMEOUT

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        request_timeout: int = TIMEOUT,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.api_key = api_key
        if base_url:
            self.base_url = base_url
        self.request_timeout = request_timeout

    @property
    def _llm_type(self) -> str:
        return "deepseek"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        if stop:
            payload["stop"] = stop

        # 允许外部传入常见参数：temperature/top_p/max_tokens/tools/response_format 等（DeepSeek支持）:contentReference[oaicite:3]{index=3}
        payload.update({k: v for k, v in kwargs.items() if v is not None})

        resp = requests.post(
            url, headers=headers, json=payload, timeout=self.request_timeout
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        if stop:
            payload["stop"] = stop
        payload.update({k: v for k, v in kwargs.items() if v is not None})

        with requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=self.request_timeout,
        ) as r:
            r.raise_for_status()
            for raw in r.iter_lines(decode_unicode=True, delimiter="\n"):
                if not raw:
                    continue
                if raw.startswith("data: "):
                    data = raw[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                        # OpenAI/DeepSeek 兼容流式字段：choices[0].delta.content / reasoning_content（后者仅 reasoner 有）:contentReference[oaicite:4]{index=4}
                        delta = obj.get("choices", [{}])[0].get("delta", {}) or {}
                        txt = (delta.get("content") or "") + (
                            delta.get("reasoning_content") or ""
                        )
                        if txt:
                            yield GenerationChunk(text=txt)
                            if run_manager:
                                run_manager.on_llm_new_token(txt)
                    except Exception:
                        # 忽略异常行以增强健壮性
                        continue

    def test_api_key(self, test_prompt: str = "你好") -> bool:
        try:
            self._call(test_prompt)
            return True
        except Exception as e:
            return False
