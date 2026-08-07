from __future__ import annotations

from typing import ClassVar

from go_standard_annotation_schema.datamodel import (
    Entity,
    EntityProperty,
)

from ._common import (
    _parse_properties,
    _Reader,
    _split_optional,
)


class GpiReader(_Reader[Entity]):
    """Stream GPI 2.0 rows as validated Entity models."""

    format_name: ClassVar[str] = "gpi"
    version_header: ClassVar[str] = "gpi-version"
    expected_columns: ClassVar[int] = 11

    @classmethod
    def _convert_fields(
        cls,
        fields: list[str | None],
    ) -> tuple[Entity, ...]:
        del cls
        return (
            Entity.model_validate(
                {
                    "db_object_id": fields[0],
                    "db_object_symbol": fields[1],
                    "db_object_name": fields[2],
                    "db_object_synonyms": _split_optional(fields[3]),
                    "db_object_type": fields[4],
                    "db_object_taxon_id": fields[5],
                    "encoded_by": _split_optional(fields[6]),
                    "canonical_object_id": fields[7],
                    "protein_containing_complex_members": _split_optional(fields[8]),
                    "db_xrefs": _split_optional(fields[9]),
                    "gene_product_properties": _parse_properties(
                        fields[10], EntityProperty
                    ),
                }
            ),
        )

    @classmethod
    def parse_line(
        cls,
        line: str,
        *,
        line_number: int | None = None,
        source: str | None = None,
    ) -> Entity:
        (entity,) = cls._parse_models(
            line,
            line_number=line_number,
            source=source,
        )
        return entity
