import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
)

logger = logging.getLogger("AI_Orchestrator")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(event: str, **fields):
    field_values = " ".join(f"{key}={value}" for key, value in fields.items())

    logger.info(f"event={event}" + (f" {field_values}" if field_values else ""))
