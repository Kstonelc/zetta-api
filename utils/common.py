"""
@File        : utils/common.py
@Description : 通用函数
@Author      : Kstone
@Date        : 2025/07/11
"""

from passlib.context import CryptContext
from cryptography.fernet import Fernet
import random
import tldextract


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fixed_key = b"wL5Zlll5xxkU_PbgG0l8kxvFR3QtBy9J3RysFGqgF8E="
fernet = Fernet(fixed_key)


# region 密码加密解密
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# endregion


# region 通用
def generate_random_code(length: int = 6) -> str:
    x = random.randint(0, 999999)
    return f"{x:06d}"


def encrypt(plaintext: str) -> str:
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return fernet.decrypt(ciphertext.encode()).decode()


# endregion


# region 网站


def get_domain(url: str) -> str:
    ext = tldextract.extract(url)
    main_domain = f"{ext.domain}.{ext.suffix}"
    return main_domain


# endregion
