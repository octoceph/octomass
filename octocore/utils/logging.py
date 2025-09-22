"""
Локальная настройка логирования с использованием loguru.
Комментарии на русском объясняют, зачем это нужно.
"""
from loguru import logger
import sys

# Удаляем стандартные обработчики и добавляем наш, удобный для разработки.
logger.remove()
logger.add(sys.stderr, level="INFO", colorize=True, backtrace=True, diagnose=True)
