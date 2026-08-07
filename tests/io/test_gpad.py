from datetime import date
from io import StringIO

import pytest

import go_standard_annotation_schema.io as go_io
from go_standard_annotation_schema.datamodel import Annotation
from go_standard_annotation_schema.io import (
    FileMetadata,
    GpadReader,
    GpiReader,
    HeaderError,
    ReaderStats,
    RowError,
)

GPAD_LINE = (
    "WB:WBGene00000001\tNOT\tRO:0002331\tGO:0008286\t"
    "PMID:12393910|WB_REF:WBPaper1\tECO:0000316\t"
    "WB:WBGene00000090,WB:WBGene00000898\tNCBITaxon:9606\t"
    "2020-11-30\tWB\t"
    "BFO:0000066(WBbt:0005753),RO:0002092(WBls:0000038)\t"
    "id=GOA:1|comment=value=with=equals"
)
GPAD_HEADER = """!gpad-version: 2.0
!generated-by: tests
!date-generated: 2026-08-04 12:30
"""


def _with_field(line: str, column: int, value: str) -> str:
    fields = line.split("\t")
    fields[column - 1] = value
    return "\t".join(fields)


def _parse_one(line: str) -> Annotation:
    (annotation,) = GpadReader.parse_line(line)
    return annotation


def test_parse_gpad_line_returns_annotation_tuple():
    annotation = _parse_one(GPAD_LINE)

    assert annotation.negation is True
    assert annotation.references == ["PMID:12393910", "WB_REF:WBPaper1"]
    assert annotation.with_or_from == [
        "WB:WBGene00000090",
        "WB:WBGene00000898",
    ]
    assert annotation.annotation_extensions is not None
    assert [item.extension_relation for item in annotation.annotation_extensions] == [
        "BFO:0000066",
        "RO:0002092",
    ]
    assert annotation.annotation_properties is not None
    assert annotation.annotation_properties[1].property_value == "value=with=equals"


def test_io_package_exports_gpad_reader_with_supported_reader_namespace():
    """The public facade must support all documented readers and row diagnostics."""
    assert (
        FileMetadata,
        GpadReader,
        GpiReader,
        HeaderError,
        ReaderStats,
        RowError,
    ) == (
        go_io.FileMetadata,
        go_io.GpadReader,
        go_io.GpiReader,
        go_io.HeaderError,
        go_io.ReaderStats,
        go_io.RowError,
    )
    assert "GpadReader" in go_io.__all__


@pytest.mark.parametrize(("raw_value", "expected"), [("", None), ("NOT", True)])
def test_gpad_negation_maps_only_empty_and_not(raw_value, expected):
    """The GPAD negation token must map to the datamodel's optional Boolean."""
    annotation = _parse_one(_with_field(GPAD_LINE, 2, raw_value))

    assert annotation.negation is expected


def test_gpad_rejects_unknown_negation_token():
    """A negation token other than empty or NOT is malformed GPAD."""
    with pytest.raises(RowError):
        GpadReader.parse_line(_with_field(GPAD_LINE, 2, "NO"))


@pytest.mark.parametrize(
    "line",
    [
        "\t".join(GPAD_LINE.split("\t")[:-1]),
        GPAD_LINE + "\textra",
    ],
)
def test_gpad_requires_exactly_twelve_fields(line):
    """Both missing and additional GPAD columns must be field-count errors."""
    with pytest.raises(RowError) as caught:
        GpadReader.parse_line(line)

    assert caught.value.issue.code == "field-count"


def test_gpad_preserves_trailing_empty_twelfth_field():
    """An empty properties column remains a twelfth field rather than disappearing."""
    annotation = _parse_one(_with_field(GPAD_LINE, 12, "") + "\n")

    assert annotation.annotation_properties is None


def test_gpad_requires_at_least_one_reference():
    """The required references collection cannot be represented by an empty column."""
    with pytest.raises(RowError):
        GpadReader.parse_line(_with_field(GPAD_LINE, 5, ""))


@pytest.mark.parametrize("column", [1, 3, 4, 6, 9, 10])
def test_gpad_rejects_empty_required_scalar_fields(column):
    """Every mandatory scalar GPAD column must contain a value."""
    with pytest.raises(RowError) as caught:
        GpadReader.parse_line(_with_field(GPAD_LINE, column, ""))

    assert caught.value.issue.code in {"syntax", "validation"}


def test_gpad_splits_pipes_into_annotations_and_commas_into_lists():
    line = _with_field(GPAD_LINE, 7, "A:1,B:2|C:3,D:4")

    annotations = GpadReader.parse_line(line)

    assert [item.with_or_from for item in annotations] == [
        ["A:1", "B:2"],
        ["C:3", "D:4"],
    ]


def test_gpad_expands_both_grouped_fields_as_a_cartesian_product():
    line = _with_field(GPAD_LINE, 7, "A:1,B:2|C:3")
    line = _with_field(
        line,
        11,
        "RO:0000001(X:1),RO:0000002(X:2)|RO:0000003(X:3)",
    )

    annotations = GpadReader.parse_line(line)

    assert [item.with_or_from for item in annotations] == [
        ["A:1", "B:2"],
        ["A:1", "B:2"],
        ["C:3"],
        ["C:3"],
    ]
    extension_groups = []
    for item in annotations:
        assert item.annotation_extensions is not None
        extension_groups.append(
            [extension.extension_relation for extension in item.annotation_extensions]
        )
    assert extension_groups == [
        ["RO:0000001", "RO:0000002"],
        ["RO:0000003"],
        ["RO:0000001", "RO:0000002"],
        ["RO:0000003"],
    ]


@pytest.mark.parametrize(
    ("column", "value"),
    [
        (11, "RO:0002233(X:1"),
        (11, "RO:0002233(X:1))"),
        (11, "(X:1)"),
        (11, "RO:0002233()"),
        (11, "RO:2(X:1)BFO:3(Y:2)"),
        (11, "RO:2(X:1)(Y:2)"),
        (7, "A:1||B:2"),
        (7, "A:1,"),
        (11, "RO:0002233(X:1,Y:2)"),
        (11, "RO:0002233(X:1)|"),
        (11, "RO:0002233(X:1),"),
    ],
)
def test_gpad_rejects_malformed_logical_groups_and_extensions(column, value):
    """Unbalanced, structurally empty, and empty-member expressions are malformed."""
    with pytest.raises(RowError):
        GpadReader.parse_line(_with_field(GPAD_LINE, column, value))


def test_streaming_counts_physical_rows_and_expanded_annotations():
    expanded = _with_field(GPAD_LINE, 7, "A:1|B:2")
    source = StringIO(GPAD_HEADER + expanded + "\n" + GPAD_LINE + "\n")

    with GpadReader(source) as reader:
        annotations = list(reader)

    assert len(annotations) == 3
    assert reader.stats.data_rows == 2
    assert reader.stats.records_yielded == 3


def test_direct_parsing_rejects_an_entire_invalid_expansion(monkeypatch):
    calls = 0
    original = Annotation.model_validate

    def reject_second(values):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValueError("invalid expanded combination")
        return original(values)

    monkeypatch.setattr(
        Annotation,
        "model_validate",
        staticmethod(reject_second),
    )
    expanded = _with_field(GPAD_LINE, 7, "A:1|B:2")

    with pytest.raises(RowError):
        GpadReader.parse_line(expanded)

    assert calls == 2


def test_skip_mode_discards_an_entire_invalid_expanded_row(monkeypatch):
    calls = 0
    original = Annotation.model_validate

    def reject_second(values):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValueError("invalid expanded combination")
        return original(values)

    monkeypatch.setattr(
        Annotation,
        "model_validate",
        staticmethod(reject_second),
    )
    expanded = _with_field(GPAD_LINE, 7, "A:1|B:2")
    source = StringIO(GPAD_HEADER + expanded + "\n" + GPAD_LINE + "\n")

    with GpadReader(source, errors="skip") as reader:
        annotations = list(reader)

    assert len(annotations) == 1
    assert reader.stats.data_rows == 2
    assert reader.stats.records_yielded == 1
    assert reader.stats.rows_skipped == 1


def test_skip_mode_continues_after_malformed_extensions():
    """A malformed extension row in skip mode must not block later annotations."""
    malformed = _with_field(GPAD_LINE, 11, "RO:0002233(X:1")
    source = StringIO(GPAD_HEADER + malformed + "\n" + GPAD_LINE + "\n")

    with GpadReader(source, errors="skip") as reader:
        annotations = list(reader)

    assert [annotation.db_object_id for annotation in annotations] == [
        "WB:WBGene00000001"
    ]
    assert reader.stats.rows_skipped == 1


def test_interacting_taxa_are_split_only_on_pipes():
    pipe_line = _with_field(
        GPAD_LINE,
        8,
        "NCBITaxon:9606|NCBITaxon:10090",
    )
    comma_line = _with_field(
        GPAD_LINE,
        8,
        "NCBITaxon:9606,NCBITaxon:10090",
    )

    assert _parse_one(pipe_line).interacting_taxon_id == [
        "NCBITaxon:9606",
        "NCBITaxon:10090",
    ]
    assert _parse_one(comma_line).interacting_taxon_id == [
        "NCBITaxon:9606,NCBITaxon:10090"
    ]


def test_gpad_annotation_date_is_parsed_as_a_date():
    """The GPAD timestamp column must reach the model date unchanged in meaning."""
    annotation = _parse_one(GPAD_LINE)

    assert annotation.annotation_date == date(2020, 11, 30)
    assert isinstance(annotation.annotation_date, date)


def test_gpad_property_continuations_repeat_the_preceding_key():
    """Keyless property segments repeat the immediately preceding GPAD key."""
    line = _with_field(
        GPAD_LINE,
        12,
        "contributor-id=https://one|https://two|https://three",
    )

    annotation = _parse_one(line)

    assert annotation.annotation_properties is not None
    assert [
        (item.property_key, item.property_value)
        for item in annotation.annotation_properties
    ] == [
        ("contributor-id", "https://one"),
        ("contributor-id", "https://two"),
        ("contributor-id", "https://three"),
    ]


def test_gpad_rejects_a_keyless_first_property_segment():
    """A GPAD property continuation must follow an explicit property key."""
    line = _with_field(GPAD_LINE, 12, "https://one|id=GOA:1")

    with pytest.raises(RowError):
        GpadReader.parse_line(line)
