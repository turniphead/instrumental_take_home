from typing import Optional
import time


class EventCounter:

    def __init__(self, max_timespan=300):
        # type: (Optional[int]) -> None
        """Create an object to count events.

        Note: This class will maintain a list of length `max_timespan`; be reasonable about how large you make this.

        :param max_timespan: The maximum amount of time, in seconds, for which we can query event counts.
        """
        self._max_timespan = max_timespan
        # Initialize a list of length `max_timespan`, where each element is a tuple that represents:
        # (an integer timestamp in seconds since Unix Epoch, the number of events that happened during that second)
        self._event_history = [(0, 0)] * max_timespan

    def record_event(self, timestamp=None):
        # type: (Optional[float]) -> None
        """Signal that an event happened to add it to our count.

        :param timestamp: The time, seconds since Unix Epoch, that our event occurred. If no timestamp is provided, take
        the current time instead.
        :return:
        """
        if timestamp is None:
            timestamp = time.time()
        # truncate the timestamp to an integer. Note: this rounds down.
        timestamp_int = int(timestamp)
        index = timestamp_int % self._max_timespan
        existing_timestamp, existing_count = self._event_history[index]
        if existing_timestamp == timestamp_int:
            new_count = existing_count + 1
        else:
            new_count = 1
        self._event_history[index] = (timestamp_int, new_count)

    def request_event_count(self, timespan):
        # type: (int) -> int
        """Request a count of all recorded events that happened in the past `timespan` seconds.

        :param timespan:
        :return:
        """
        assert timespan <= self._max_timespan, \
            'Timespan requested ({} seconds) was greater than the max timespan provided during EventCounter ' \
            'Initialization ({} seconds)'.format(timespan, self._max_timespan)
        now = int(time.time())
        # Add one because we include the current second in the past `timespan` seconds.
        start_time = now - int(timespan) + 1
        total_count = 0
        for t in range(start_time, now + 1):
            index = t % self._max_timespan
            timestamp, count = self._event_history[index]
            if timestamp >= start_time:
                total_count += count
        return total_count
