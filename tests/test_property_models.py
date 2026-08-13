from datetime import date

import pytest
from pydantic import ValidationError

from go_standard_annotation_schema.datamodel import (
    AnnotationProperties,
    GeneProductProperties,
)


def test_annotation_properties_have_typed_specification_slots():
    properties = AnnotationProperties.model_validate(
        {
            "id": "GOA:1",
            "model_state": "production",
            "noctua_model_id": "gomodel:123",
            "contributor_id": ["orcid:0000-0001", "goc:abc"],
            "reviewer_id": ["orcid:0000-0002"],
            "creation_date": "2026-08-13",
            "modification_date": ["2026-08-14"],
            "reviewed_date": ["2026-08-15"],
            "comment": ["first", "second"],
        }
    )

    assert properties.id == "GOA:1"
    assert properties.contributor_id == ["orcid:0000-0001", "goc:abc"]
    assert properties.creation_date == date(2026, 8, 13)
    assert properties.modification_date == [date(2026, 8, 14)]
    assert properties.reviewed_date == [date(2026, 8, 15)]
    assert properties.comment == ["first", "second"]


@pytest.mark.parametrize(
    "values,skip_reason",
    [
        ({"id": "not-an-id"}, "https://github.com/linkml/linkml/pull/3832"),
        ({"model_state": "not alphabetic"}, None),
        (
            {"noctua_model_id": "not-an-id"},
            "https://github.com/linkml/linkml/pull/3832",
        ),
        (
            {"contributor_id": ["https://orcid.org/0000-0001"]},
            "https://github.com/linkml/linkml/pull/3832",
        ),
        (
            {"reviewer_id": ["example:0000-0001"]},
            "https://github.com/linkml/linkml/pull/3832",
        ),
        ({"creation_date": "not-a-date"}, None),
        ({"modification_date": ["not-a-date"]}, None),
        ({"reviewed_date": ["not-a-date"]}, None),
        ({"unsupported": "value"}, None),
    ],
)
def test_annotation_properties_reject_invalid_values(values, skip_reason):
    if skip_reason:
        pytest.skip(skip_reason)
    with pytest.raises(ValidationError):
        AnnotationProperties.model_validate(values)


def test_gene_product_properties_have_typed_specification_slots():
    properties = GeneProductProperties.model_validate(
        {
            "db_subset": "Swiss-Prot",
            "uniprot_proteome": "UP000001940",
            "go_annotation_complete": "2026-08-13",
            "go_annotation_summary": "Curated summary",
        }
    )

    assert properties.db_subset == "Swiss-Prot"
    assert properties.uniprot_proteome == "UP000001940"
    assert properties.go_annotation_complete == date(2026, 8, 13)
    assert properties.go_annotation_summary == "Curated summary"


@pytest.mark.parametrize(
    "values",
    [
        {"db_subset": "reviewed"},
        {"uniprot_proteome": "UPABC"},
        {"go_annotation_complete": "not-a-date"},
        {"unsupported": "value"},
    ],
)
def test_gene_product_properties_reject_invalid_values(values):
    with pytest.raises(ValidationError):
        GeneProductProperties.model_validate(values)
