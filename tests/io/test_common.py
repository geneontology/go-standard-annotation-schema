from __future__ import annotations

from io import StringIO
from typing import cast

import pytest

from go_standard_annotation_schema.datamodel.go_standard_annotation_schema import (
    Property,
)
from go_standard_annotation_schema.io._common import (
    _empty_as_none,
    _parse_properties,
    _Reader,
    _split_optional,
)
from go_standard_annotation_schema.io.types import (
    ErrorMode,
    HeaderError,
    ReaderStateError,
    RowError,
)


class StringReader(_Reader[str]):
    format_name = "gpad"
    version_header = "gpad-version"
    expected_columns = 2

    @classmethod
    def _convert_fields(cls, fields):
        return (":".join(fields),)


class ExpandingStringReader(StringReader):
    @classmethod
    def _convert_fields(cls, fields):
        del cls
        value = ":".join(fields)
        return (f"{value}:1", f"{value}:2")


class FieldsValueErrorReader(StringReader):
    @classmethod
    def _convert_fields(cls, fields):
        raise ValueError("converter rejected fields after inspection")


VALID = """!gpad-version: 2.0
!generated-by: tests
!date-generated: 2026-08-04 12:30
!funding: grant-a
!funding: grant-b
a\tb
c\td
"""


def test_context_parses_metadata_and_streams_records():
    """A reader must expose parsed headers and yield each valid row in order."""
    source = StringIO(VALID)
    reader = StringReader(source)

    with pytest.raises(ReaderStateError):
        _ = reader.metadata

    with reader:
        assert reader.metadata.version == "2.0"
        assert reader.metadata.generated_by == "tests"
        assert reader.metadata.getall("funding") == ("grant-a", "grant-b")
        assert list(reader) == ["a:b", "c:d"]

    assert not source.closed
    assert reader.stats.records_yielded == 2


def test_reader_streams_every_model_from_each_physical_row():
    with ExpandingStringReader(StringIO(VALID)) as reader:
        assert list(reader) == ["a:b:1", "a:b:2", "c:d:1", "c:d:2"]

    assert reader.stats.data_rows == 2
    assert reader.stats.records_yielded == 4


def test_reader_rejects_a_second_iteration_after_exhaustion():
    """A fully consumed single-pass reader must not silently iterate again."""
    reader = StringReader(StringIO(VALID))

    with reader:
        assert list(reader) == ["a:b", "c:d"]
        with pytest.raises(ReaderStateError):
            list(reader)

    assert reader.metadata.version == "2.0"
    assert reader.stats.records_yielded == 2


@pytest.mark.parametrize(
    "text",
    [
        "!generated-by: tests\n!date-generated: 2026-08-04\na\tb\n",
        (
            "!gpad-version: 1.2\n!generated-by: tests\n"
            "!date-generated: 2026-08-04\na\tb\n"
        ),
        (
            "!gpad-version: 2.0\n!gpad-version: 2.0\n!generated-by: tests\n"
            "!date-generated: 2026-08-04\na\tb\n"
        ),
    ],
)
def test_invalid_required_headers_are_always_fatal(text):
    """Missing, duplicate, and incompatible versions must fail even in skip mode."""
    with pytest.raises(HeaderError), StringReader(StringIO(text), errors="skip"):
        pass


def test_empty_generated_by_header_is_fatal():
    """The required generated-by header must contain a producer name."""
    text = VALID.replace("!generated-by: tests", "!generated-by: ")

    with pytest.raises(HeaderError, match="generated-by"), StringReader(StringIO(text)):
        pass


def test_strict_mode_wraps_row_error_with_physical_line_number():
    """Malformed data rows must retain their physical line number and cause."""
    text = VALID.replace("a\tb", "too\tmany\tfields")
    with StringReader(StringIO(text)) as reader, pytest.raises(RowError) as caught:
        next(reader)
    assert caught.value.issue.line_number == 6
    assert isinstance(caught.value.__cause__, ValueError)


def test_skip_mode_calls_callback_and_continues():
    """Skip mode must report a bad row and continue at the next valid record."""
    issues = []
    text = VALID.replace("a\tb", "too\tmany\tfields")
    with StringReader(StringIO(text), errors="skip", on_error=issues.append) as reader:
        assert list(reader) == ["c:d"]
    assert len(issues) == 1
    assert reader.stats.rows_skipped == 1


def test_tab_only_row_is_a_strict_field_count_error():
    """Tabs are row delimiters, so a tab-only physical line is not blank."""
    text = VALID.replace("a\tb", "\t\t")

    with StringReader(StringIO(text)) as reader, pytest.raises(RowError) as caught:
        next(reader)

    assert caught.value.issue.code == "field-count"
    assert reader.stats.blank_lines == 0
    assert reader.stats.data_rows == 1


def test_skip_mode_reports_tab_only_row_and_preserves_real_blank_line():
    """Skip mode must diagnose tab-delimited rows while ignoring only empty lines."""
    issues = []
    text = VALID.replace("a\tb\n", "\n\t\t\n")

    with StringReader(StringIO(text), errors="skip", on_error=issues.append) as reader:
        assert list(reader) == ["c:d"]

    assert [issue.code for issue in issues] == ["field-count"]
    assert reader.stats.blank_lines == 1
    assert reader.stats.data_rows == 2
    assert reader.stats.rows_skipped == 1


def test_parse_line_treats_tab_only_input_as_a_data_row():
    """Direct parsing must classify a malformed tab-delimited row by field count."""
    with pytest.raises(RowError) as caught:
        StringReader._parse_models("\t\t", line_number=None, source=None)

    assert caught.value.issue.code == "field-count"


def test_converter_value_error_mentioning_fields_remains_a_syntax_error():
    """Only the exact column-count branch may produce a field-count issue."""
    with pytest.raises(RowError) as caught:
        FieldsValueErrorReader._parse_models("a\tb", line_number=None, source=None)

    assert caught.value.issue.code == "syntax"


def test_callback_failure_propagates():
    """Errors raised by the user's row callback must not be swallowed."""

    def fail(_issue):
        raise RuntimeError("callback failed")

    text = VALID.replace("a\tb", "bad")
    with (
        StringReader(StringIO(text), errors="skip", on_error=fail) as reader,
        pytest.raises(RuntimeError, match="callback failed"),
    ):
        next(reader)


class CountingStringIO(StringIO):
    def __init__(self, value: str):
        super().__init__(value)
        self.readline_calls = 0

    def readline(self, *args, **kwargs):
        self.readline_calls += 1
        return super().readline(*args, **kwargs)


def test_context_entry_reads_only_through_first_data_row():
    """Entering a reader must not eagerly consume records beyond its buffer."""
    source = CountingStringIO(VALID)

    with StringReader(source):
        assert source.readline_calls == 6


def test_path_source_is_closed_but_caller_stream_is_not(tmp_path):
    """The reader owns and closes path sources but leaves supplied streams usable."""
    path = tmp_path / "sample.gpad"
    path.write_text(VALID)
    reader = StringReader(path)
    with reader:
        assert next(reader) == "a:b"
    assert reader._stream is not None
    assert reader._stream.closed

    source = StringIO(VALID)
    with StringReader(source):
        pass
    assert not source.closed


def test_reader_rejects_invalid_state_and_error_mode():
    """Readers must only iterate once open and reject unsupported error modes."""
    reader = StringReader(StringIO(VALID))
    with pytest.raises(ReaderStateError):
        next(reader)
    with reader:
        pass
    with pytest.raises(ReaderStateError):
        next(reader)
    with pytest.raises(ReaderStateError):
        reader.__enter__()
    with pytest.raises(ValueError, match="errors"):
        StringReader(StringIO(VALID), errors=cast(ErrorMode, "ignore"))


@pytest.mark.parametrize(
    ("value", "expected"),
    [("", None), ("one|two", ["one", "two"]), ("one,two", ["one,two"])],
)
def test_split_optional_converts_empty_and_nonempty_values(value, expected):
    """Optional fields must return None only for empty values."""
    assert _split_optional(value) == expected


def test_split_optional_rejects_empty_items():
    """A multi-value field with an empty member is malformed."""
    with pytest.raises(ValueError, match="empty item"):
        _split_optional("one||two")


def test_empty_as_none_converts_only_the_empty_string():
    """Only a zero-length scalar value represents a missing optional field."""
    assert _empty_as_none("") is None
    assert _empty_as_none(" ") == " "


def test_parse_properties_preserves_equals_after_the_key():
    """Property values may contain equals signs after their delimiter."""
    assert _parse_properties("key=value=with=equals", Property) == [
        Property(property_key="key", property_value="value=with=equals")
    ]


@pytest.mark.parametrize("value", ["=value", "key=", "key", "key=value|"])
def test_parse_properties_rejects_malformed_expressions(value):
    """Each property expression must have a nonempty key and value."""
    with pytest.raises(ValueError, match="invalid property expression"):
        _parse_properties(value, Property)
