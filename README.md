# Event Counter
Instrumental take home challenge.

**Note: Works only in Python 3, not compatible with Python 2.**

## Setup

When in the "instrumental_take_home" directory:
- install requirements using `pip install -r requirements.txt`
- run tests using `pytest`

## Notes:
The time resolution of this module is 1 second. Because of this, when requesting event counts, we may report extra events, or miss events, at the beginning of the requested time window. See `EventCounter.request_event_count` docstring for more details and examples.

Because the resolution was allowed to be course (1 second), and because the max_timespan was allowed to be relatively short (5 minutes, but configurable in my solution), I was able to make an optimization, namely storing counts of events in a list, where each element contains the number of events that happened within that second. This allows us to record events in constant time, though it uses O(N) space and requesting an event count takes O(N) time, N being the maximum timespan in seconds. I felt this is an acceptable balance because I was told that we will be making potentially millions of record_event calls per second, and will be requesting a count of past events much less often and in a less time-constrained environment.

## Example Usage:
```
import time

import event_counter

# initialize an event counter with a maximum lookback timespan of 5 minutes.
counter = event_counter.EventCounter(300)

# record an event using the current timestamp
counter.record_event()

# record multiple events at once (all of which will be treated as having the same timestamp)
counter.record_event(number_of_events=45)

# whoops, we forgot to record an event that happened 20s ago, so we should record this event using a custom timestamp
counter.record_event(timestamp=time.time() - 20)

# request all events that happened in the past x seconds (must be no larger than the maximum timespan entered during initialization).
print('Total events that happened in the past 5 minutes: {}'.format(counter.request_event_count(300)))

```
