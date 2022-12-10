def get_logger_config() -> dict:
    return {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }
