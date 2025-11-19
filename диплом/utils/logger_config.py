"""
Настройка логгера для проекта с форматированием логов в JSON и ротацией файлов.
"""
import logging
import logging.handlers
import json


class JsonFormatter(logging.Formatter):
    """
    Форматировщик логов, преобразующий записи в JSON формат с заданными полями.
    """
    def format(self, record):
        """
        Формирует JSON-запись лога.

        Args:
            record (logging.LogRecord): Запись лога.

        Returns:
            str: Лог в формате JSON.
        """
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        return json.dumps(log_record, ensure_ascii=False)


def setup_logger(log_file="bot.log") -> logging.Logger:
    """
    Настраивает логгер с ротацией файлов и JSON форматированием.

    Args:
        log_file (str): Имя файла лога.

    Returns:
        logging.Logger: Настроенный логгер.
    """
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    formatter = JsonFormatter(datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


#Глобальный экземпляр логгера для использования по всему проекту
logger = setup_logger()
