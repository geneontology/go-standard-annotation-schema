from __future__ import annotations

import gzip
import os
from collections import deque
from collections.abc import Callable, Iterator
from datetime import date, datetime
from io import TextIOBase
from typing import ClassVar, Generic, TextIO, TypeVar

from pydantic import ValidationError

from go_standard_annotation_schema.datamodel import (
    Property,
)

from .types import (
    ErrorMode,
    FileMetadata,
    FormatName,
    HeaderError,
    MetadataEntry,
    ReaderState,
    ReaderStateError,
    ReaderStats,
    RowError,
    RowIssue,
)

ModelT = TypeVar("ModelT")
PropertyT = TypeVar("PropertyT", bound=Property)
Source = str | os.PathLike[str] | TextIO
ErrorCallback = Callable[[RowIssue], None]


class _FieldCountError(ValueError):
    pass


def _empty_as_none(value: str) -> str | None:
    """Convert an empty string to None, otherwise return the original value."""
    return value or None


def _split_values(value: str, separator: str) -> list[str]:
    """Split a required value and reject empty members."""
    values = value.split(separator)
    if any(item == "" for item in values):
        raise ValueError("empty item in multi-value field")
    return values


def _split_optional(value: str | None, separator: str = "|") -> list[str] | None:
    """
    Split a string into a list of values using the specified separator, returning
    None if the input is None or empty. Raises ValueError if any item is empty.
    """
    if not value:
        return None
    return _split_values(value, separator)


def _parse_properties(
    value: str | None, property_type: type[PropertyT]
) -> list[PropertyT] | None:
    """Parse a string of property expressions into a list of Property instances.

    The input string is expected to be a series of expressions separated by '|', where
    each expression is of the form 'key=value'. This function will create instances of
    the specified property_type for each valid expression. If the input is None or
    empty, it returns None. Raises ValueError for any invalid expressions.
    """
    if not value:
        return None
    result = []
    for expression in value.split("|"):
        key, separator, property_value = expression.partition("=")
        if not separator or not key or not property_value:
            raise ValueError(f"invalid property expression: {expression!r}")
        result.append(property_type(property_key=key, property_value=property_value))
    return result


def _open_source(source: Source) -> tuple[TextIO, bool, str | None]:
    """
    Open a source for reading, returning a readable text stream, a boolean indicating
    whether the stream should be closed by the caller, and the source name if available.
    """
    if isinstance(source, (str, os.PathLike)):
        path = os.fspath(source)
        if path.endswith(".gz"):
            return gzip.open(path, mode="rt", encoding="utf-8", newline=""), True, path
        return open(path, encoding="utf-8", newline=""), True, path
    if not isinstance(source, TextIOBase):
        raise TypeError("source must be a path or text stream")
    return source, False, getattr(source, "name", None)


def _without_line_terminator(line: str) -> str:
    """Remove the line terminator from a line, handling both LF and CRLF endings."""
    if line.endswith("\r\n"):
        return line[:-2]
    if line.endswith("\n"):
        return line[:-1]
    return line


class _Reader(Generic[ModelT], Iterator[ModelT]):
    """Private base class for readers of structured annotation files.

    This class provides common functionality for reading and parsing structured
    annotation files, including handling headers, metadata, and data rows. Subclasses
    must implement the `_convert_fields` method to convert a list of fields into a
    specific model instance.
    """

    format_name: ClassVar[FormatName]
    version_header: ClassVar[str]
    expected_columns: ClassVar[int]

    def __init__(
        self,
        source: Source,
        *,
        errors: ErrorMode = "strict",
        on_error: ErrorCallback | None = None,
    ) -> None:
        if errors not in ("strict", "skip"):
            raise ValueError("errors must be 'strict' or 'skip'")
        self._source = source
        self._errors = errors
        self._on_error = on_error
        self._state: ReaderState = "new"
        self._stream: TextIO | None = None
        self._owns_stream = False
        self._source_name: str | None = None
        self._metadata: FileMetadata | None = None
        self._buffered_line: tuple[int, str] | None = None
        self._pending_models: deque[ModelT] = deque()
        self._counters = {
            "lines_read": 0,
            "metadata_entries": 0,
            "data_rows": 0,
            "records_yielded": 0,
            "rows_skipped": 0,
            "blank_lines": 0,
            "comments_ignored": 0,
        }

    @property
    def metadata(self) -> FileMetadata:
        if self._state == "new" or self._metadata is None:
            raise ReaderStateError(
                "metadata is available only after entering the reader"
            )
        return self._metadata

    @property
    def stats(self) -> ReaderStats:
        return ReaderStats(**self._counters)

    def __enter__(self) -> _Reader[ModelT]:
        if self._state != "new":
            raise ReaderStateError("reader cannot be entered more than once")

        try:
            self._stream, self._owns_stream, self._source_name = _open_source(
                self._source
            )
            self._read_header_block()
            self._state = "open"
        except Exception:
            if self._owns_stream and self._stream is not None:
                self._stream.close()
            self._state = "closed"
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._owns_stream and self._stream is not None:
            self._stream.close()
        self._state = "closed"

    def __iter__(self) -> _Reader[ModelT]:
        if self._state != "open":
            raise ReaderStateError("reader can only be iterated while open")
        return self

    def __next__(self) -> ModelT:
        if self._state != "open":
            raise ReaderStateError("reader can only be iterated while open")

        while True:
            if self._pending_models:
                self._counters["records_yielded"] += 1
                return self._pending_models.popleft()

            line_info = self._next_line()
            if line_info is None:
                self._state = "exhausted"
                raise StopIteration
            line_number, raw_line = line_info
            line = _without_line_terminator(raw_line)
            if line == "":
                self._counters["blank_lines"] += 1
                continue
            if line.startswith("!"):
                self._counters["comments_ignored"] += 1
                continue

            self._counters["data_rows"] += 1
            try:
                models = self._parse_data_line(raw_line, line_number)
            except RowError as error:
                if self._errors == "strict":
                    raise error from error.issue.cause
                self._counters["rows_skipped"] += 1
                if self._on_error is not None:
                    self._on_error(error.issue)
                continue
            self._pending_models.extend(models)

    @classmethod
    def _parse_models(
        cls,
        line: str,
        *,
        line_number: int | None,
        source: str | None,
    ) -> tuple[ModelT, ...]:
        """Parse a single line of text into one or more model instances."""
        raw_line = _without_line_terminator(line)

        try:
            if raw_line == "" or raw_line.startswith("!"):
                raise ValueError("line must contain a data row")
            fields = list(map(_empty_as_none, raw_line.split("\t")))
            if len(fields) != cls.expected_columns:
                raise _FieldCountError(
                    f"expected {cls.expected_columns} fields, found {len(fields)}"
                )
            return cls._convert_fields(fields)
        except RowError:
            raise
        except Exception as cause:
            code = "validation" if isinstance(cause, ValidationError) else "syntax"
            if isinstance(cause, _FieldCountError):
                code = "field-count"
            issue = RowIssue(
                source=source,
                line_number=line_number,
                format=cls.format_name,
                code=code,
                raw_line=raw_line,
                cause=cause,
            )
            raise RowError(issue) from cause

    def _parse_data_line(self, line: str, line_number: int) -> tuple[ModelT, ...]:
        """Parse a data line into one or more model instances."""
        return self._parse_models(
            line,
            line_number=line_number,
            source=self._source_name,
        )

    @classmethod
    def _convert_fields(
        cls,
        fields: list[str | None],
    ) -> tuple[ModelT, ...]:
        """Convert a list of fields into one or more model instances.

        This method must be implemented by subclasses to handle format-specific field
        conversion.
        """
        raise NotImplementedError

    def _next_line(self) -> tuple[int, str] | None:
        """
        Read the next line from the stream, returning a tuple of (line_number, line).

        If a line has been buffered (e.g., after reading the header), it will return
        that line first. If the end of the stream is reached, it returns None.
        """
        if self._buffered_line is not None:
            line_info = self._buffered_line
            self._buffered_line = None
            return line_info
        assert self._stream is not None
        raw_line = self._stream.readline()
        if raw_line == "":
            return None
        self._counters["lines_read"] += 1
        return self._counters["lines_read"], raw_line

    def _read_header_block(self) -> None:
        """Read the header block from the stream and populate the file metadata."""
        entries: list[MetadataEntry] = []
        while True:
            line_info = self._next_line()
            if line_info is None:
                break
            line_number, raw_line = line_info
            line = _without_line_terminator(raw_line)
            if line == "":
                self._counters["blank_lines"] += 1
                continue
            if not line.startswith("!"):
                # We seem to have reached the first data line; buffer it for the next
                # read and exit the header parsing loop.
                self._buffered_line = (line_number, raw_line)
                break

            key, separator, value = line[1:].partition(":")
            key = key.strip()
            # We are intentionally not handling unstructured header values for now.
            if not separator or not key:
                self._counters["comments_ignored"] += 1
                continue
            entries.append(MetadataEntry(key, value.removeprefix(" ")))
            self._counters["metadata_entries"] += 1

        # Collect the values for the required keys, validate that each one appears
        # exactly once, and validate their contents.
        required_keys = (
            self.version_header,
            "generated-by",
            "date-generated",
        )
        values = {
            key: tuple(entry.value for entry in entries if entry.key == key)
            for key in required_keys
        }
        for key, header_values in values.items():
            if len(header_values) != 1:
                self._header_error(key, "must appear exactly once")

        version = values[self.version_header][0]
        if version != "2.0":
            self._header_error(self.version_header, "must be 2.0")
        generated_by = values["generated-by"][0]
        if generated_by == "":
            self._header_error("generated-by", "must not be empty")
        date_value = values["date-generated"][0]
        try:
            date_generated = (
                datetime.fromisoformat(date_value)
                if "T" in date_value or " " in date_value
                else date.fromisoformat(date_value)
            )
        except ValueError as error:
            self._header_error("date-generated", "is not a valid ISO date", error)

        # Populate the file metadata field with the collected and validated values.
        self._metadata = FileMetadata(
            format=self.format_name,
            version=version,
            generated_by=generated_by,
            date_generated=date_generated,
            entries=tuple(entries),
        )

    def _header_error(
        self, key: str, message: str, cause: Exception | None = None
    ) -> None:
        """
        Raise a HeaderError with a formatted message, optionally chaining from a cause.
        """
        source = f"{self._source_name}: " if self._source_name else ""
        error = HeaderError(f"{source}invalid header {key}: {message}")
        if cause is None:
            raise error
        raise error from cause
