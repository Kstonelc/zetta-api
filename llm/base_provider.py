from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseLLMProvider(ABC):
    """
    通用大模型提供者基类。所有模型提供者应继承此类并实现其方法。
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        与大模型进行对话，返回响应文本。
        :param messages: 聊天上下文，格式为[{"role": "user", "content": "hi"}, ...]
        :return: 大模型的回复
        """
        pass

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        获取输入文本的向量嵌入表示。
        :param texts: 多个输入文本
        :return: 每个文本对应的向量嵌入
        """
        pass

    def supports(self) -> Dict[str, bool]:
        """
        声明当前模型支持哪些能力，例如 chat、embed、rerank 等。
        """
        return {
            "chat": hasattr(self, "chat"),
            "embed": hasattr(self, "embed"),
        }

    def get_config(self) -> Dict[str, Any]:
        """
        获取当前模型的配置，用于前端显示。
        """
        return {
            "model_name": self.model_name,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "features": self.supports(),
        }
