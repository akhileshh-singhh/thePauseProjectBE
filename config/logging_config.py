"""
Add this to your settings.py (or split into settings/dev.py and settings/prod.py)
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)  # auto-create logs/ dir

ENV = os.environ.get("DJANGO_ENV", "development")  # set this in your environment

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # ------------------------------------------------------------------ #
    # Formatters                                                           #
    # ------------------------------------------------------------------ #
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {process:d} {thread:d} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[{asctime}] {levelname} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    # ------------------------------------------------------------------ #
    # Filters                                                              #
    # ------------------------------------------------------------------ #
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },

    # ------------------------------------------------------------------ #
    # Handlers                                                             #
    # ------------------------------------------------------------------ #
    "handlers": {
        # Console — always on, simple format
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },

        # General app log — rotates at 10 MB, keeps 5 backups
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "app.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },

        # Errors only — separate file so you can tail just failures
        "file_errors": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "errors.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",
        },

        # Auth events
        "file_auth": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "auth.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },

        # Admin CRUD actions
        "file_admin": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "admin_actions.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },

        # Requests log
        "file_requests": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "requests.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },

        # Production: email admins on ERROR (disable in dev)
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
            "level": "ERROR",
            "formatter": "verbose",
        },
    },

    # ------------------------------------------------------------------ #
    # Loggers                                                              #
    # ------------------------------------------------------------------ #
    "loggers": {
        # Your app — catches everything from your views/middleware
        "workshop": {
            "handlers": ["console", "file_app", "file_errors"],
            "level": "DEBUG" if ENV == "development" else "INFO",
            "propagate": False,
        },

        # Auth-specific logger
        "workshop.auth": {
            "handlers": ["console", "file_auth", "file_errors"],
            "level": "DEBUG" if ENV == "development" else "INFO",
            "propagate": False,
        },

        # Admin action logger
        "workshop.admin": {
            "handlers": ["console", "file_admin", "file_errors"],
            "level": "INFO",
            "propagate": False,
        },

        # Request logger (used by middleware)
        "workshop.requests": {
            "handlers": ["console", "file_requests"],
            "level": "DEBUG" if ENV == "development" else "INFO",
            "propagate": False,
        },

        # Django internals
        "django": {
            "handlers": ["console", "file_app"],
            "level": "WARNING",
            "propagate": False,
        },

        # DB queries — dev only (very noisy)
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG" if ENV == "development" else "WARNING",
            "filters": ["require_debug_true"],
            "propagate": False,
        },

        # Unhandled exceptions in prod → email
        "django.request": {
            "handlers": ["file_errors", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
