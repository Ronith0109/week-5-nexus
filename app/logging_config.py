import inspect
import json
import logging
import os
import sys
import time
import traceback
import uuid
from functools import wraps

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
PREVIEW_LIMIT = 500

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.propagate = False
    return logger

def _preview(value, limit=PREVIEW_LIMIT):
    try:
        text = repr(value)
    except Exception:
        text = "<unrepresentable>"
    return text if len(text) <= limit else text[:limit] + "...<truncated>"

def _qualified_name(func):
    return f"{func.__module__}.{func.__qualname__}"

def trace(logger, redact=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            call_id = str(uuid.uuid4())
            started = time.perf_counter()

            try:
                bound = inspect.signature(func).bind(*args, **kwargs)
                bound.apply_defaults()
                bound_args = dict(bound.arguments)
            except Exception:
                bound_args = {
                    "args": args,
                    "kwargs": kwargs,
                }

            if redact is not None:
                bound_args = redact(bound_args)

            logger.debug(json.dumps({
                "event": "ENTER",
                "function": _qualified_name(func),
                "call_id": call_id,
                "arguments": bound_args,
            }, default=str))

            try:
                result = func(*args, **kwargs)
                duration_ms = round((time.perf_counter() - started) * 1000, 3)

                logger.debug(json.dumps({
                    "event": "EXIT",
                    "function": _qualified_name(func),
                    "call_id": call_id,
                    "duration_ms": duration_ms,
                    "return_preview": _preview(result),
                }, default=str))
                return result

            except Exception as exc:
                duration_ms = round((time.perf_counter() - started) * 1000, 3)

                logger.error(json.dumps({
                    "event": "FAILED",
                    "function": _qualified_name(func),
                    "call_id": call_id,
                    "duration_ms": duration_ms,
                    "exception_type": type(exc).__name__,
                    "exception": str(exc),
                    "traceback": traceback.format_exc(),
                }, default=str))
                raise

        return wrapper
    return decorator
