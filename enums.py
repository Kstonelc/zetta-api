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


class ModelType(NumberEnum):
    TextEmbedding = (1 << 0, "textEmbedding")
    TextGeneration = (1 << 1, "textGeneration")
    ReRank = (1 << 2, "reRank")


class ModelProviderUpdateType(NumberEnum):
    Update = (1 << 0, "update")
    Clear = (1 << 1, "clear")


class UserStatus(NumberEnum):
    Pending = (1 << 0, "pending")
    Active = (1 << 1, "active")
    Banned = (1 << 2, "banned")


class UserRole(NumberEnum):
    Admin = (1 << 0, "admin")
    Editor = (1 << 1, "editor")
    Normal = (1 << 2, "normal")
    Owner = (1 << 3, "owner")


class WikiType(NumberEnum):
    Structured = (1 << 0, "结构化")
    Unstructured = (1 << 1, "非结构化")


class WikiChunkType(NumberEnum):
    Classical = (1 << 0, "classical")
    ParentChild = (1 << 1, "parentChild")


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
