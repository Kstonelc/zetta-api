"""
@File        : utils/logger.py
@Description : logger封装
@Author      : Kstone
@Date        : 2025/07/11
"""

import sys
from loguru import logger

logger.remove()

# 控制台输出
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
)


# 日志文件输出
logger.add(
    "logs/prod.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="10 MB",
    retention="7 days",
    enqueue=True,
    backtrace=False,  # 完整回溯
    diagnose=False,  # 异常诊断信息
)
