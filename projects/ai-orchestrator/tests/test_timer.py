import time

import pytest

from app.observability.timer import Timer


def test_timed_decorator():
    @Timer.timed("test_operation")
    def sample():
        time.sleep(0.01)
        return "done"

    result = sample()

    assert result == "done"


def test_timer_context_manager():
    with Timer("test_operation") as timer:
        time.sleep(0.01)

    assert timer.elapsed_ms >= 10


def test_timed_decorator_on_exception():

    @Timer.timed("failing_operation")
    def failing():
        raise ValueError("failure")

    with pytest.raises(ValueError):
        failing()
