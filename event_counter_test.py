import time
from typing import Any, List
from unittest import mock

import pytest

import event_counter


def mock_time(desired_time):
    # type: (float) -> Any
    return mock.patch.object(time, 'time', return_value=desired_time)


def record_event_times(counter, event_times):
    # type: (event_counter.EventCounter, List[float]) -> None
    """Record specific event times into counter

        Args:
            counter: An event counter with which we want to record events.
            event_times: A list of times at which singular events occur.
        """
    for event_time in event_times:
        with mock_time(event_time):
            counter.record_event()


def test_request_timespan_with_multiple_events():
    # type: () -> None
    max_timespan = 60
    counter = event_counter.EventCounter(max_timespan)
    event_times = [28.6, 31.1, 33.1]
    record_event_times(counter, event_times)
    with mock_time(50):
        assert counter.request_event_count(30) == 3
        assert counter.request_event_count(20) == 2
        assert counter.request_event_count(10) == 0
    with mock_time(88):
        assert counter.request_event_count(max_timespan) == 3
    with mock_time(91):
        assert counter.request_event_count(max_timespan) == 2
    with mock_time(93):
        assert counter.request_event_count(max_timespan) == 1
    with mock_time(94):
        assert counter.request_event_count(max_timespan) == 0


def test_multiple_events_during_same_second():
    counter = event_counter.EventCounter(60)
    for t in range(100, 120):
        event_time = t / 10.0
        with mock_time(event_time):
            counter.record_event()
    with mock_time(13):
        assert counter.request_event_count(3) == 20
        assert counter.request_event_count(2) == 10
        assert counter.request_event_count(1) == 0


def test_multiple_event_addition_at_once():
    # type: () -> None
    counter = event_counter.EventCounter(60)
    event_times_and_counts = [(10.1, 4), (21.1, 3), (33.3, 2), (45, 1)]
    for event_time, number in event_times_and_counts:
        with mock_time(event_time):
            counter.record_event(number_of_events=number)
    with mock_time(50):
        assert counter.request_event_count(10) == 1
        assert counter.request_event_count(20) == 3
        assert counter.request_event_count(30) == 6
        assert counter.request_event_count(40) == 10


def test_not_counting_events_once_past_max_timespan():
    max_timespan = 10
    counter = event_counter.EventCounter(max_timespan)
    # note: last number in this list must round down, otherwise this test will fail due to rounding / resolution. See
    # EventCounter.request_event_count docstring for more information.
    event_times = [1.1, 2.2, 3.3]
    record_event_times(counter, event_times)

    with mock_time(sorted(event_times)[-1] + max_timespan):
        assert counter.request_event_count(max_timespan) == 1


def test_rounding_down_due_to_resolution_includes_extra_events():
    counter = event_counter.EventCounter(10)
    event_times = [13.0, 13.2, 13.3, 13.9, 14.1, 14.2, 15.0, 15.49]
    record_event_times(counter, event_times)
    with mock_time(15.49):
        assert counter.request_event_count(2) == len(event_times)


def test_rounding_up_due_to_resolution_misses_some_events():
    counter = event_counter.EventCounter(10)
    event_times = [13.0, 13.2, 13.3, 13.9, 14.1, 14.2, 15.0, 15.49, 15.9, 16.0]
    record_event_times(counter, event_times)
    with mock_time(16):
        # Since the starting time (13.5) will round up, we miss all events that happened during 13.x
        assert counter.request_event_count(2.5) == 6


def test_event_counted_when_same_time_as_request():
    counter = event_counter.EventCounter()
    with mock_time(5432.1):
        counter.record_event()
        assert counter.request_event_count(1) == 1


def test_returns_zero_when_nonpositive_request_timespan():
    counter = event_counter.EventCounter()
    event_times = [1, 2, 3, 4, 5]
    record_event_times(counter, event_times)
    with mock_time(sorted(event_times)[-1]):
        assert counter.request_event_count(0) == 0
        assert counter.request_event_count(-10) == 0


def test_old_event_doesnt_affect_count():
    max_timespan = 10
    counter = event_counter.EventCounter(max_timespan)
    start_time = 20
    event_times = list(range(start_time, start_time + max_timespan * 2))
    record_event_times(counter, event_times)
    with mock_time(event_times[-1]):
        assert counter.request_event_count(max_timespan) == max_timespan + 1
        counter.record_event(timestamp=start_time - 1)
        # make sure the number of events hasn't changed after receiving an old event.
        assert counter.request_event_count(max_timespan) == max_timespan + 1


def test_raises_value_error_when_requested_timespan_too_large():
    max_timespan = 10
    counter = event_counter.EventCounter(max_timespan)
    with pytest.raises(ValueError):
        counter.request_event_count(max_timespan + 0.01)


def test_raises_value_error_when_recorded_event_is_from_the_future():
    counter = event_counter.EventCounter(10)
    current_time = 500
    with mock_time(current_time):
        with pytest.raises(ValueError):
            counter.record_event(timestamp=current_time + 0.0001)
