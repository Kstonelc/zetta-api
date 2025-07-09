from typing import Any, Optional, List, Iterator

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_community.llms.tongyi import Tongyi
from langchain_core.outputs import GenerationChunk

from config import settings
from enums import QWModelType


class ChatQW(LLM):
    client: Tongyi = None
    model_name: str = ""

    def __init__(
        self,
        api_key: str = settings.QIANWEN_API_KEY,
        model_name=QWModelType.qw_plus,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.client = Tongyi(api_key=api_key, model=self.model_name)

    @property
    def _identifying_params(self):
        return {"model_name": self.model_name}

    @property
    def _llm_type(self):
        return "qwen"

    def _call(
        self, prompt: str, stop: Optional[list[str]] = None, **kwargs: Any
    ) -> str:
        resp = self.client.generate(prompts=[prompt], stop=stop, **kwargs)
        gen = resp.generations[0][0]
        return (
            getattr(gen, "message", None).content
            if hasattr(gen, "message")
            else gen.text
        )

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> Iterator[GenerationChunk]:
        stop_signal = kwargs.pop("stop_signal", False)
        for chunk_str in self.client.stream(input=prompt, stop=stop, **kwargs):
            if stop_signal:
                break
            chunk = GenerationChunk(text=chunk_str)
            yield chunk
