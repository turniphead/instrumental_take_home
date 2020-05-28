import time
from typing import Optional


class EventCounter:

    def __init__(self, max_timespan=300):
        # type: (Optional[int]) -> None
        """Create an object to count events with a resolution of one second.

        Note: This class will maintain a list of length `max_timespan` + 1; be reasonable about how long to make this.

        Args:
            max_timespan: The maximum amount of time, in seconds, for which we can query event counts.
        """
        self._max_timespan = max_timespan
        # Initialize a list of length `max_timespan` + 1, where each element is a tuple that represents:
        # (an integer timestamp in seconds since Unix Epoch, the number of events that happened during that second)
        self._event_history = [(0, 0)] * (max_timespan + 1)

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
        index = timestamp_int % len(self._event_history)
        existing_timestamp, existing_count = self._event_history[index]

        # If `timestamp_int` is less than the existing timestamp, it means that this event happened more than
        # `max_timespan` seconds before the existing timestamp. We don't count this current event and don't change the
        # event history.
        if existing_timestamp == timestamp_int:
            # If its the same timestamp, just add to the existing event count.
            new_count = existing_count + number_of_events
            self._event_history[index] = (timestamp_int, new_count)
        elif timestamp_int > existing_timestamp:
            # If the timestamp is larger than the existing timestamp, erase the count in this bucket and start a new one
            # with the current event(s).
            new_count = number_of_events
            self._event_history[index] = (timestamp_int, new_count)

    def request_event_count(self, timespan):
        # type: (float) -> int
        """Request a count of all recorded events that happened in the past `timespan` seconds.

        Note: Because this class has a resolution of one second, we may end up tallying extra events that occurred N
        seconds before (now - timespan), or missing some events that happened N seconds after (now - timespan), where
        the maximum value of N is 0.5.
        Example 1: If the current time is 15.49, and we request events for the past 2 seconds, we will tally all events
            that took place during "13.x", "14.x", and "15.x". Events that happened 13 <= x < 13.49 are "extra" events
            that would not be tallied with a finer resolution.
        Example 2: If the current time is 16, and we request events for the past 2.5 seconds, we will tally all events
            that took place during "14.x", "15.x", and "16.x". Events that happened 13.5 <= x < 14 are "missed" events
            that would be tallied with a finer resolution.

        Args:
            timespan: The amount of time to look back when counting events. Must be less than or equal to max_timespan
                given during EventCounter instantiation.

        Returns:
            The number of events that have happened in the past `timespan` seconds.
        """
        if timespan > self._max_timespan:
            raise ValueError(
                'Timespan requested ({} seconds) was greater than the max timespan provided during EventCounter '
                'instantiation ({} seconds)'.format(timespan, self._max_timespan)
            )
        elif timespan <= 0:
            return 0

        now = time.time()
        start_time = int(round(now - timespan))
        total_count = 0
        for t in range(start_time, int(now + 1)):
            index = t % len(self._event_history)
            timestamp, count = self._event_history[index]
            if timestamp >= start_time:
                total_count += count
        return total_count
