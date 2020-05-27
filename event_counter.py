import time
from typing import Optional


class EventCounter:

    def __init__(self, max_timespan=300):
        # type: (Optional[int]) -> None
        """Create an object to count events.

        Note: This class will maintain a list of length `max_timespan`; be reasonable about how long to make this.

        Args:
            max_timespan: The maximum amount of time, in seconds, for which we can query event counts.
        """
        self._max_timespan = max_timespan
        # Initialize a list of length `max_timespan`, where each element is a tuple that represents:
        # (an integer timestamp in seconds since Unix Epoch, the number of events that happened during that second)
        self._event_history = [(0, 0)] * max_timespan

    def record_event(self, timestamp=None, number_of_events=1):
        # type: (Optional[float], Optional[int]) -> None
        """Signal that an event (or multiple events) happened.

        Args:
            timestamp: The time, as seconds since Unix Epoch, that the event occurred. If no timestamp is provided,
                take the current time instead. Does not allow input times from the future.
            number_of_events: The number of events that you want to report during this call. All events will be labelled
                using the same timestamp.
        """
        now = time.time()
        if timestamp is None:
            timestamp = now
        if timestamp > now:
            raise ValueError(
                'record_event does not allow timestamps from the future. Current time: {}, Input time: {}'.format(
                    now, timestamp
                )
            )
        # truncate the timestamp to an integer. Note: this rounds down.
        timestamp_int = int(timestamp)
        index = timestamp_int % self._max_timespan
        existing_timestamp, existing_count = self._event_history[index]
        if existing_timestamp == timestamp_int:
            new_count = existing_count + number_of_events
        elif timestamp_int > existing_timestamp:
            new_count = number_of_events
        else:
            # If `timestamp_int` is less than the existing timestamp, it means that this event happened more than
            # `max_timespan` seconds before the existing timestamp. Don't count this event.
            new_count = existing_count
        self._event_history[index] = (timestamp_int, new_count)

    def request_event_count(self, timespan):
        # type: (int) -> int
        """Request a count of all recorded events that happened in the past `timespan` seconds.

        NOTE: because we round all event occurances down to the nearest second

        Args:
            timespan: The amount of time to look back when counting events. Must be less than or equal to max_timespan
                given during initialization.

        Returns:
            The number of events that have happened in the past `timespan` seconds.
        """
        if timespan > self._max_timespan:
            raise ValueError(
                'Timespan requested ({} seconds) was greater than the max timespan provided during EventCounter '
                'initialization ({} seconds)'.format(timespan, self._max_timespan)
            )
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
