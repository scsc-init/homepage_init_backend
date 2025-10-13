import logging
import time
from contextvars import ContextVar

request_id_var = ContextVar("request_id", default="")


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "info_only": {
            "()": InfoFilter,
        },
        "correlation_id": {
            "()": RequestIdFilter,
        },
    },
    "formatters": {
        "verbose": {
            "()": UTCFormatter,
            "format": "%(levelname)-10s - %(asctime)s - %(request_id)s - %(module)-15s : %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["correlation_id"],
        },
        "file_access": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/http_access.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
            "filters": ["correlation_id"],
        },
        "file_app_info": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app_info.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
            "filters": ["info_only", "correlation_id"],
        },
        "file_app_error": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app_error.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
            "filters": ["correlation_id"],
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "file_app_info", "file_app_error"],
            "level": "INFO",
            "propagate": False,
        },
        "http_access": {
            "handlers": ["file_access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
