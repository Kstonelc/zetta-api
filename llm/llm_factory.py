from typing import Any
from .deepseek import DeepseekProvider
from .qwen import QWProvider
from enums import LLMProvider


class LLMFactory:
    _registry = {
        LLMProvider.Deepseek: DeepseekProvider,
        LLMProvider.QW: QWProvider,
    }

    @classmethod
    def create(cls, provider: str, **kwargs: Any):
        if provider not in cls._registry:
            raise ValueError(f"provider not found: {provider}")
        return cls._registry[provider](**kwargs)
