from datetime import datetime

import pytest

from go_standard_annotation_schema.io.types import (
    FileMetadata,
    MetadataEntry,
    ReaderStats,
    RowError,
    RowIssue,
)


def test_metadata_preserves_order_and_repeated_values():
    entries = (
        MetadataEntry("gpad-version", "2.0"),
        MetadataEntry("funding", "grant-a"),
        MetadataEntry("funding", "grant-b"),
    )
    metadata = FileMetadata(
        format="gpad",
        version="2.0",
        generated_by="WB",
        date_generated=datetime(2026, 8, 4, 12, 30),
        entries=entries,
    )

    assert metadata.entries == entries
    assert metadata.getall("funding") == ("grant-a", "grant-b")
    assert metadata.getall("missing") == ()


def test_reader_stats_is_immutable():
    stats = ReaderStats(records_yielded=3)

    with pytest.raises((AttributeError, TypeError)):
        setattr(stats, "records_yielded", 4)  # noqa: B010


def test_row_error_exposes_structured_issue():
    cause = ValueError("bad field")
    issue = RowIssue("sample.gpad", 17, "gpad", "field-count", "a\tb", cause)

    error = RowError(issue)

    assert error.issue is issue
    assert "sample.gpad:17" in str(error)
    assert "field-count" in str(error)
