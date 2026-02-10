from .settings import *
import os
from pathlib import Path

# ==============================
# BASE DIR
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==============================
# STATIC FILES
# ==============================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ==============================
# LOGGING DIRECTORY (Render SAFE)
# ==============================
LOGGING_DIR = BASE_DIR / "logs"

logging_structure = {
    "debug_logs": {
        "dir": "/debug_logs",
        "file": "/debug.log",
    },
    "warning_logs": {
        "dir": "/warning_logs",
        "file": "/warning.log",
    },
    "error_logs": {
        "dir": "/error_logs",
        "file": "/error.log",
    },
    "info_logs": {
        "dir": "/info_logs",
        "file": "/info.log",
    },
    "critical_logs": {
        "dir": "/critical_logs",
        "file": "/critical.log",
    },
}

# Create log folders & files
for key, value in logging_structure.items():
    log_dir = LOGGING_DIR / value["dir"].strip("/")
    os.makedirs(log_dir, exist_ok=True)
    open(log_dir / value["file"].strip("/"), "a").close()

# ==============================
# DJANGO LOGGING CONFIG
# ==============================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_DIR / "debug_logs/debug.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "standard",
        },
        "warning": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_DIR / "warning_logs/warning.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "standard",
        },
        "error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_DIR / "error_logs/error.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "standard",
        },
        "info": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_DIR / "info_logs/info.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "standard",
        },
        "critical": {
            "level": "CRITICAL",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_DIR / "critical_logs/critical.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "standard",
        },
        # Render console logs (important)
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": [
                "debug",
                "warning",
                "error",
                "info",
                "critical",
                "console",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
