from enum import Enum


class QWModelType(str, Enum):
    qw_plus = "qwen-plus"
    qw_turbo = "qwen-turbo"


class ModelType(str, Enum):
    TextEmbedding = "TextEmbedding"
    TextGeneration = "TextGeneration"
    ReRank = "ReRank"


class ModelProviderUpdateType(str, Enum):
    Update = "update"
    Clear = "clear"


class UserStatus(str, Enum):
    Pending = "pending"
    Unintialized = "unintialized"
    Active = "active"
    Banned = "banned"
    Closed = "closed"


class TenantUserRole(str, Enum):
    Owner = "owner"
    Admin = "admin"
    Editor = "editor"
    Normal = "normal"
    DatasetOperator = "datasetOperator"


class WikiType(Enum):
    # 前端多语言Key
    Structured = (1 << 0, "结构化")
    Unstructured = (1 << 1, "非结构化")

    def __init__(self, value, text):
        self._value_ = value
        self.text = text
