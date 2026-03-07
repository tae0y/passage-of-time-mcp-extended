# Use the Time Tools

This page describes the available tools and their response formats.

## Prerequisites

- A running passage-of-time-mcp server (see [Quick Start](../README.md#quick-start))

## `current_datetime(timezone="Asia/Seoul")`

Returns the current date and time. The foundation of temporal awareness.

```
Returns: "2024-01-15 14:30:45 KST"
```

## `time_difference(timestamp1, timestamp2, unit="auto")`

Calculates the duration between two timestamps with human-readable output.

```python
# Example response:
{
    "seconds": 11401,
    "formatted": "3 hours, 10 minutes, 1 second",
    "requested_unit": 3.17,  # if unit="hours"
    "is_negative": false
}
```

## `timestamp_context(timestamp)`

Provides human context about a timestamp — is it weekend? Business hours? Dinner time? Also detects Korean public holidays (including substitute holidays) using the `holidays` library.

```python
# Example response:
{
    "time_of_day": "evening",
    "day_of_week": "Saturday",
    "is_weekend": true,
    "is_holiday": false,
    "holiday_name": "",
    "is_business_hours": false,
    "typical_activity": "leisure_time",
    "relative_day": "today"
}
```

On weekends and Korean holidays, `typical_activity` returns `leisure_time` instead of `commute_time` or `work_time`. Activities like `lunch_time`, `dinner_time`, and `sleeping_time` remain unchanged regardless of day type.

## `time_since(timestamp)`

Calculates how long ago something happened with contextual descriptions.

```python
# Example response:
{
    "seconds": 7200,
    "formatted": "2 hours ago",
    "context": "earlier today"
}
```

## `parse_timestamp(timestamp)`

Converts timestamps between different formats for maximum compatibility.

```python
# Example response:
{
    "iso": "2024-01-15T14:30:45+09:00",
    "unix": "1705293045",
    "human": "January 15, 2024 at 2:30 PM KST",
    "day_of_week": "Monday"
}
```

## `add_time(timestamp, duration, unit)`

Adds or subtracts time with natural language descriptions.

```python
# Example response:
{
    "result": "2024-01-16 14:30:45",
    "iso": "2024-01-16T14:30:45+09:00",
    "description": "tomorrow at 2:30 PM"
}
```

## `format_duration(seconds, style="full")`

Formats durations in various styles for different contexts.

```python
# style="full": "2 hours, 30 minutes, 15 seconds"
# style="compact": "2h 30m 15s"
# style="minimal": "2:30:15"
```
