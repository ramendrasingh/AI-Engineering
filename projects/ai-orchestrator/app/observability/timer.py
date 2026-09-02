import time
from functools import wraps

from app.logger.logger import logger


class Timer:
    def __init__(self, name: str):
        self.name = name
        self.elapsed_ms = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = (time.perf_counter() - self.start) * 1000

    @staticmethod
    def timed(name: str):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()

                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    logger.info(f"operation={name} latency_ms={elapsed_ms:.2f}")

            return wrapper

        return decorator
