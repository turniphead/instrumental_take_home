import time
from unittest import mock

import event_counter


def mock_time(desired_time):
    return mock.patch.object(time, 'time', return_value=desired_time)


def test_basic_functionality():
    counter = event_counter.EventCounter(60)
    event_times = [28.6, 31.1, 33.1]
    for event_time in event_times:
        with mock_time(event_time):
            counter.record_event()
    with mock_time(50):
        assert counter.request_event_count(30) == 3
        assert counter.request_event_count(20) == 2
        assert counter.request_event_count(10) == 0
