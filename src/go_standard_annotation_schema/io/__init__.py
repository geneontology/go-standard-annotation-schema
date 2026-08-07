"""Streaming readers and diagnostics for GO annotation exchange formats."""

from .gpad import GpadReader
from .gpi import GpiReader
from .types import (
    ErrorMode,
    FileMetadata,
    FormatName,
    HeaderError,
    MetadataEntry,
    ReaderError,
    ReaderStateError,
    ReaderStats,
    RowError,
    RowIssue,
)

__all__ = [
    "ErrorMode",
    "FileMetadata",
    "FormatName",
    "GpadReader",
    "GpiReader",
    "HeaderError",
    "MetadataEntry",
    "ReaderError",
    "ReaderStateError",
    "ReaderStats",
    "RowError",
    "RowIssue",
]
