from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from go_standard_annotation_schema.datamodel import Annotation

VALID_ANNOTATION = Path(__file__).parent / "data" / "valid" / "Annotation-0001.yaml"

# Default ECO terms for each GO evidence code, from
# http://purl.obolibrary.org/obo/eco/gaf-eco-mapping.txt
DEFAULT_ECO_TERMS = [
    "ECO:0000269",  # EXP
    "ECO:0007005",  # HDA
    "ECO:0007007",  # HEP
    "ECO:0007003",  # HGI
    "ECO:0007001",  # HMP
    "ECO:0006056",  # HTP
    "ECO:0000318",  # IBA
    "ECO:0000319",  # IBD
    "ECO:0000305",  # IC
    "ECO:0000314",  # IDA
    "ECO:0000501",  # IEA
    "ECO:0000270",  # IEP
    "ECO:0000317",  # IGC
    "ECO:0000316",  # IGI
    "ECO:0000320",  # IKR
    "ECO:0000315",  # IMP
    "ECO:0000353",  # IPI
    "ECO:0000321",  # IRD
    "ECO:0000247",  # ISA
    "ECO:0000255",  # ISM
    "ECO:0000266",  # ISO
    "ECO:0000250",  # ISS
    "ECO:0000303",  # NAS
    "ECO:0000307",  # ND
    "ECO:0000245",  # RCA
    "ECO:0000304",  # TAS
]


def annotation_values(evidence_type: str) -> dict:
    values = yaml.safe_load(VALID_ANNOTATION.read_text())
    values["evidence_type"] = evidence_type
    return values


@pytest.mark.parametrize("evidence_type", DEFAULT_ECO_TERMS)
def test_annotation_accepts_default_eco_terms(evidence_type):
    annotation = Annotation.model_validate(annotation_values(evidence_type))

    assert annotation.evidence_type == evidence_type


@pytest.mark.parametrize(
    "evidence_type",
    [
        # More specific than the IDA default; has GO evidence code IDA in ECO
        "ECO:0007719",
        # Used for GO_REF:0000114 in GO's eco-usage-constraints.yaml
        "ECO:0005546",
        "not-an-eco-id",
    ],
)
def test_annotation_rejects_non_default_eco_terms(evidence_type):
    with pytest.raises(ValidationError):
        Annotation.model_validate(annotation_values(evidence_type))
