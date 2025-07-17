from enum import Enum


class QWModelType(str, Enum):
    qw_plus = "qwen-plus"
    qw_turbo = "qwen-turbo"


class ModelType(str, Enum):
    TextEmbedding = "TextEmbedding"
    TextGeneration = "TextGeneration"
    ReRank = "ReRank"
