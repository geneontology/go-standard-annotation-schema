from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal, TextIO

ErrorMode = Literal["strict", "skip"]
"""The error handling mode for a reader."""

FormatName = Literal["gpad", "gpi"]
ReaderState = Literal["new", "open", "exhausted", "closed"]


@dataclass(frozen=True)
class MetadataEntry:
    """A single key-value pair from a file's header."""

    key: str
    value: str


@dataclass(frozen=True)
class FileMetadata:
    """Representation of a file's header, including required and custom fields."""

    format: FormatName
    version: str
    generated_by: str
    date_generated: date | datetime
    entries: tuple[MetadataEntry, ...]

    def getall(self, key: str) -> tuple[str, ...]:
        return tuple(entry.value for entry in self.entries if entry.key == key)


@dataclass(frozen=True)
class RowIssue:
    """Information about a problem with a data row."""

    source: str | None
    line_number: int | None
    format: FormatName
    code: str
    raw_line: str
    cause: Exception


@dataclass(frozen=True)
class ReaderStats:
    """Statistics about the reader's progress and results."""

    lines_read: int = 0
    metadata_entries: int = 0
    data_rows: int = 0
    records_yielded: int = 0
    rows_skipped: int = 0
    blank_lines: int = 0
    comments_ignored: int = 0


class ReaderError(Exception):
    """Base class for GPAD/GPI reader failures."""


class ReaderStateError(ReaderError):
    """Raised when a reader is used outside its valid lifecycle."""


class HeaderError(ReaderError):
    """Raised when required file metadata is invalid."""


class RowError(ReaderError):
    """Raised when a data row is invalid."""

    def __init__(self, issue: RowIssue):
        self.issue = issue
        if issue.source and issue.line_number is not None:
            location = f"{issue.source}:{issue.line_number}"
        elif issue.source:
            location = issue.source
        elif issue.line_number is not None:
            location = f"line {issue.line_number}"
        else:
            location = "row"
        message = f"{location}: invalid {issue.format.upper()} row ({issue.code})"
        super().__init__(message)


Source = str | os.PathLike[str] | TextIO
"""A source of data for the reader."""

ErrorCallback = Callable[[RowIssue], None]
"""A callback function for handling row issues."""
