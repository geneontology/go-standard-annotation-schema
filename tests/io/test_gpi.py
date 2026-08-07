import gzip
from io import StringIO

import pytest

import go_standard_annotation_schema.io as go_io
from go_standard_annotation_schema.datamodel.go_standard_annotation_schema import Entity
from go_standard_annotation_schema.io import GpiReader, RowError

GPI_LINE = (
    "WB:WBGene00000019\tabt-1\tABC transporter domain-containing protein\t"
    "C24F3.5|CELE_C24F3.5|abt-1\tPR:000000001\tNCBITaxon:6239\t\t"
    "WB:WBGene00000019\t\tUniProtKB:S6EZS3\tdb-subset=Swiss-Prot"
)
GPI_HEADER = """!gpi-version: 2.0
!generated-by: tests
!date-generated: 2026-08-04 12:30
"""


def _with_field(line: str, column: int, value: str) -> str:
    fields = line.split("\t")
    fields[column - 1] = value
    return "\t".join(fields)


def test_io_package_exports_gpi_reader_and_public_diagnostics():
    """The package facade must expose readers and diagnostics, not private helpers."""
    assert go_io.GpiReader is GpiReader
    assert {"ErrorMode", "FileMetadata", "RowError", "ReaderStats"} <= set(
        go_io.__all__
    )
    assert "_Reader" not in go_io.__all__


def test_parse_gpi_line_returns_entity():
    """An 11-column GPI row must convert into the corresponding entity."""
    entity = GpiReader.parse_line(GPI_LINE)

    assert entity.db_object_id == "WB:WBGene00000019"
    assert entity.db_object_synonyms == ["C24F3.5", "CELE_C24F3.5", "abt-1"]
    assert entity.encoded_by is None
    assert entity.canonical_object_id == "WB:WBGene00000019"
    assert entity.db_xrefs == ["UniProtKB:S6EZS3"]
    assert entity.gene_product_properties is not None
    assert entity.gene_product_properties[0].property_value == "Swiss-Prot"


def test_reader_exposes_gpi_metadata_and_streams_entities():
    """A GPI stream must expose its header and yield validated entity models."""
    with GpiReader(StringIO(GPI_HEADER + GPI_LINE + "\n")) as reader:
        assert reader.metadata.format == "gpi"
        assert reader.metadata.version == "2.0"
        entities = list(reader)

    assert len(entities) == 1
    assert isinstance(entities[0], Entity)


def test_gpi_optional_and_pipe_delimited_fields_map_to_expected_values():
    """Empty scalar names and each pipe-delimited GPI field need their native shape."""
    fields = GPI_LINE.split("\t")
    fields[2] = ""
    fields[3] = "one|two"
    fields[6] = "gene:one|gene:two"
    fields[8] = "complex:one|complex:two"
    fields[9] = "xref:one|xref:two"

    entity = GpiReader.parse_line("\t".join(fields))

    assert entity.db_object_name is None
    assert entity.db_object_synonyms == ["one", "two"]
    assert entity.encoded_by == ["gene:one", "gene:two"]
    assert entity.protein_containing_complex_members == ["complex:one", "complex:two"]
    assert entity.db_xrefs == ["xref:one", "xref:two"]


@pytest.mark.parametrize("column", [1, 5, 6, 8])
def test_gpi_rejects_empty_required_scalar_fields(column):
    """Every mandatory scalar GPI column must contain a value."""
    with pytest.raises(RowError) as caught:
        GpiReader.parse_line(_with_field(GPI_LINE, column, ""))

    assert caught.value.issue.code == "validation"


def test_gpi_property_values_preserve_equals_after_the_delimiter():
    """An equals sign in a property value must remain part of that value."""
    fields = GPI_LINE.split("\t")
    fields[10] = "go-annotation-summary=a=b"

    entity = GpiReader.parse_line("\t".join(fields))

    assert entity.gene_product_properties is not None
    assert entity.gene_product_properties[0].property_value == "a=b"


def test_gpi_accepts_an_ncrna_sequence_ontology_descendant():
    """GPI permits any Sequence Ontology child of the ncRNA entity type."""
    fields = GPI_LINE.split("\t")
    fields[4] = "SO:0001035"

    entity = GpiReader.parse_line("\t".join(fields))

    assert entity.db_object_type == "SO:0001035"


def test_skip_mode_omits_invalid_gpi_rows_and_continues():
    """Skip mode must discard an invalid GPI row and yield the following valid row."""
    fields = GPI_LINE.split("\t")
    fields[10] = "unsupported-property=value"
    source = StringIO(GPI_HEADER + "\t".join(fields) + "\n" + GPI_LINE + "\n")

    with GpiReader(source, errors="skip") as reader:
        entities = list(reader)

    assert [entity.db_object_id for entity in entities] == ["WB:WBGene00000019"]
    assert reader.stats.rows_skipped == 1


def test_gzip_gpi_path_is_read_as_text(tmp_path):
    """A .gpi.gz path must be decompressed before parsing GPI records."""
    path = tmp_path / "sample.gpi.gz"
    with gzip.open(path, "wt") as stream:
        stream.write(GPI_HEADER + GPI_LINE + "\n")

    with GpiReader(path) as reader:
        assert [entity.db_object_symbol for entity in reader] == ["abt-1"]


def test_gpi_reader_leaves_caller_owned_stream_open():
    """Closing a GPI reader must not close a text stream it did not open."""
    source = StringIO(GPI_HEADER + GPI_LINE + "\n")

    with GpiReader(source) as reader:
        assert next(reader).db_object_id == "WB:WBGene00000019"

    assert not source.closed
