from langchain_core.language_models.llms import LLM

LLM_REGISTRY = {}


def register_llm(name):
    def deco(cls):
        LLM_REGISTRY[name.lower()] = cls
        return cls

    return deco


def create_llm(name: str, **kwargs) -> LLM:
    if name not in LLM_REGISTRY:
        raise ValueError("Unknown model")
    return LLM_REGISTRY[name](**kwargs)
