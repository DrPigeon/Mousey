# -*- coding: utf-8 -*-
import datetime
import re
import time
from typing import Union, Tuple

from mousey import commands


SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = DAY * 365

TIME_RE = re.compile(
    r"^(me )?(in )?"
    r"(?:(?P<months>\d+)( ?months?| ?mo))? ?"
    r"(?:(?P<weeks>\d+)( ?weeks?| ?w))? ?"
    r"(?:(?P<days>\d+)( ?days?|d))? ?"
    r"(?:(?P<hours>\d+)( ?hours?| ?hrs?| ?h))? ?"
    r"(?:(?P<minutes>\d+)( ?minutes?| ?mins?| ?m))? ?"
    r"((?P<seconds>\d+)( ?seconds?| ?secs?| ?s))? ?"
    r"(about |to )?"
    r"(?P<rest>.*)",
    re.IGNORECASE
)


def _from_human_time(argument: str) -> Tuple[int, commands.RecalledArgument]:
    """
    Convert an string argument into a number of seconds and the remaining text.

    Times below 0 seconds are not supported, if no time is found 0 seconds is returned.
    """
    match = TIME_RE.search(argument)
    total_seconds = 0

    months = match.group("months")
    if months:
        total_seconds += int(months) * MONTH

    weeks = match.group("weeks")
    if weeks:
        total_seconds += int(weeks) * WEEK

    days = match.group("days")
    if days:
        total_seconds += int(days) * DAY

    hours = match.group("hours")
    if hours:
        total_seconds += int(hours) * HOUR

    minutes = match.group("minutes")
    if minutes:
        total_seconds += int(minutes) * MINUTE

    seconds = match.group("seconds")
    if seconds:
        total_seconds += int(seconds) * SECOND

    if total_seconds < 0:
        raise commands.BadArgument("Could not determine amount of time.")

    rest = match.group("rest")
    return total_seconds, commands.RecalledArgument(rest)


class Time:
    """Represents a time in the future, mostly acts as a converter for commands."""

    def __init__(self, seconds: int):
        self.seconds = seconds

        now = datetime.datetime.utcnow()
        self.date = now + datetime.timedelta(seconds=seconds)

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> tuple:
        """Converts to a time, spaces are allowed in the argument."""
        seconds, remaining = _from_human_time(argument)
        if seconds == 0:
            raise commands.BadArgument('Can\'t locate time argument or argument is below 0 seconds.')
        return cls(seconds), remaining


def human_delta(delta, *, short=True):
    """
    Converts to a human readable time delta.

    Parameters
    ----------
    delta : Union[int, float, datetime.datetime, datetime.timedelta]
        The amount of time to convert
    short : bool
        Controls whether only the three biggest units of time end up in the result or all. Defaults to True.

    Returns
    -------
    str
        A human readable version of the time.
    """
    if isinstance(delta, datetime.datetime):
        delta = datetime.datetime.utcnow() - delta

    if isinstance(delta, datetime.timedelta):
        delta = delta.total_seconds()

    if isinstance(delta, float):
        delta = int(delta)

    if delta <= 0:
        return "0s"

    years, rest = divmod(delta, YEAR)
    months, rest = divmod(rest, MONTH)
    days, rest = divmod(rest, DAY)
    hours, rest = divmod(rest, HOUR)
    minutes, seconds = divmod(rest, MINUTE)

    periods = [("y", years), ("mo", months), ("d", days), ("h", hours), ("m", minutes), ("s", seconds)]
    periods = [f"{value}{name}" for name, value in periods if value > 0]

    if len(periods) > 2:
        if short:
            # only the biggest three
            return f'{periods[0]}, {periods[1]} and {periods[2]}'

        return f'{", ".join(periods[:-1])} and {periods[-1]}'
    return " and ".join(periods)


class Timer:
    """Context manager to measure how long the indented block takes to run."""

    def __init__(self):
        self.start: int = None
        self.end: int = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()

    @property
    def duration(self):
        """Duration in ms."""
        return (self.end - self.start) * 1000
