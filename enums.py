from enum import Enum


class QWModelType(str, Enum):
    qw_plus = "qwen-plus"
    qw_turbo = "qwen-turbo"


class ModelType(str, Enum):
    TextEmbedding = "textEmbedding"
    TextGeneration = "textGeneration"
    ReRank = "reRank"


class ModelProviderUpdateType(str, Enum):
    Update = "update"
    Clear = "clear"


class UserStatus(str, Enum):
    Pending = "pending"
    Active = "active"
    Banned = "banned"


class UserRole(str, Enum):
    Admin = "admin"  # 超级管理员
    Editor = "editor"  # 可以编辑
    Normal = "normal"  # 可以使用
    Owner = "owner"  # 所有者


class WikiType(Enum):
    Structured = (1 << 0, "结构化")
    Unstructured = (1 << 1, "非结构化")

    def __init__(self, value, text):
        self.text = text


class FileType(Enum):
    Md = (1 << 0, [".md", ".markdown"], "md")
    Doc = (1 << 1, [".doc", ".docx"], "doc")
    Pdf = (1 << 2, [".pdf"], "pdf")

    def __init__(self, value, suffix, text):
        self.suffix = suffix
        self.text = text

    @staticmethod
    def get_suffixs():
        all_suffixes = []
        for file_type in FileType:
            all_suffixes.extend(file_type.suffix)
        return all_suffixes


class SenderType(str, Enum):
    User = "user"
    Assistant = "assistant"
