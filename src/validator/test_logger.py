"""Isolated Logging Subsystem for Test Runs.

Provides a dedicated logger and buffer capture mechanism to record
detailed validation traces during tests without cluttering standard stdout.
"""

from __future__ import annotations

import io
import logging


class IsolatedTestLogger:
    """Isolated logging handler buffering messages in memory."""

    def __init__(self, name: str = "validator.test") -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._stream = io.StringIO()
        self._handler = logging.StreamHandler(self._stream)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self._handler.setFormatter(formatter)
        self.logger.addHandler(self._handler)

    def get_logs(self) -> str:
        """Retrieve recorded logs as a single string."""
        return self._stream.getvalue()

    def clear(self) -> None:
        """Reset internal log buffer."""
        self._stream.seek(0)
        self._stream.truncate(0)

    def close(self) -> None:
        """Close and remove handler."""
        self.logger.removeHandler(self._handler)
        self._handler.close()


def get_test_logger(name: str = "validator.test") -> IsolatedTestLogger:
    """Factory creating an isolated test logger instance."""
    return IsolatedTestLogger(name=name)
