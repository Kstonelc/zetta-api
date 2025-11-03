from enum import Enum, IntEnum


# 数字枚举
class NumberEnum(IntEnum):
    def __new__(cls, value, text):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.text = text
        return obj


class QWModelType(str, Enum):
    qw_plus = "qwen-plus"
    qw_turbo = "qwen-turbo"


class LLMProvider(str, Enum):
    QW = "qwen"
    Deepseek = "deepseek"

    @property
    def logo(self):
        if self == LLMProvider.QW:
            return "./assets/models/qw.svg"
        elif self == LLMProvider.Deepseek:
            return "./assets/models/deepseek.svg"
        else:
            return None


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


class WikiType(NumberEnum):
    Structured = (1 << 0, "结构化")
    Unstructured = (1 << 1, "非结构化")


class FileType(Enum):
    Md = (1 << 0, [".md", ".txt"], "md")
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


class SenderType(NumberEnum):
    User = (1 << 0, "user")
    Assistant = (1 << 1, "assistant")
    System = (1 << 2, "system")


class ConversationStatus(NumberEnum):
    Active = (1 << 0, "active")
    Archived = (1 << 1, "archived")
    Temporary = (1 << 2, "temporary")
