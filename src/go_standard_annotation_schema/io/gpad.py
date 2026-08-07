from __future__ import annotations

from itertools import product
from typing import ClassVar

from go_standard_annotation_schema.datamodel import (
    Annotation,
    AnnotationExtension,
    AnnotationProperty,
)

from ._common import _Reader, _split_optional, _split_values


def _split_alternatives(value: str | None) -> tuple[list[str] | None, ...]:
    """Split pipe alternatives, then split each alternative into comma members."""
    if value is None:
        return (None,)
    return tuple(
        _split_values(alternative, ",") for alternative in _split_values(value, "|")
    )


def _parse_extension_alternatives(
    value: str | None,
) -> tuple[list[AnnotationExtension] | None, ...]:
    result: list[list[AnnotationExtension] | None] = []
    for expressions in _split_alternatives(value):
        if expressions is None:
            result.append(None)
            continue
        extensions = []
        for expression in expressions:
            relation, separator, remainder = expression.partition("(")
            if (
                not separator
                or not relation
                or not remainder.endswith(")")
                or "(" in remainder
                or ")" in remainder[:-1]
            ):
                raise ValueError(f"invalid annotation extension: {expression!r}")
            term = remainder[:-1]
            if not term:
                raise ValueError(f"invalid annotation extension: {expression!r}")
            extensions.append(
                AnnotationExtension(
                    extension_relation=relation,
                    extension_term=term,
                )
            )
        result.append(extensions)
    return tuple(result)


def _parse_properties(value: str | None) -> list[AnnotationProperty] | None:
    if not value:
        return None

    result = []
    preceding_key: str | None = None
    for expression in value.split("|"):
        key, separator, property_value = expression.partition("=")
        if separator:
            if not key or not property_value:
                raise ValueError(f"invalid property expression: {expression!r}")
            preceding_key = key
        elif preceding_key is None or not expression:
            raise ValueError(f"invalid property expression: {expression!r}")
        else:
            property_value = expression
        result.append(
            AnnotationProperty(
                property_key=preceding_key,
                property_value=property_value,
            )
        )
    return result


class GpadReader(_Reader[Annotation]):
    """Stream GPAD 2.0 rows as validated `Annotation` models.

    Use the reader as a context manager. Iteration is valid only while the
    context is open. A GPAD row can expand into multiple annotations when its
    with/from or annotation-extension column contains pipe alternatives.

    Examples:
        Read annotations from a plain-text or gzip-compressed path:

        ```python
        from go_standard_annotation_schema.io import GpadReader

        with GpadReader("annotations.gpad.gz") as reader:
            for annotation in reader:
                print(annotation.ontology_class_id)
            print(reader.stats.records_yielded)
        ```

        Skip invalid rows and inspect their issues:

        ```python
        from go_standard_annotation_schema.io import GpadReader, RowIssue

        def report(issue):
            print(issue.source, issue.line_number, issue.code)

        with GpadReader("annotations.gpad", errors="skip", on_error=report) as reader:
            for annotation in reader:
                pass
        ```
    """

    format_name: ClassVar[str] = "gpad"
    version_header: ClassVar[str] = "gpad-version"
    expected_columns: ClassVar[int] = 12

    @classmethod
    def parse_line(
        cls,
        line: str,
        *,
        line_number: int | None = None,
        source: str | None = None,
    ) -> tuple[Annotation, ...]:
        """Parse one GPAD 2.0 data row into one or more annotations.

        Args:
            line: A tab-delimited GPAD data row, with or without a line ending.
            line_number: Optional source line number included in error details.
            source: Optional source name included in error details.

        Returns:
            One or more validated annotations. The tuple contains multiple
                annotations when pipe alternatives expand the row.

        Raises:
            RowError: If the row has the wrong field count, invalid GPAD syntax,
                or values rejected by model validation.

        Examples:
            ```python
            from go_standard_annotation_schema.io import GpadReader

            annotations = GpadReader.parse_line(line)
            ```
        """
        return cls._parse_models(
            line,
            line_number=line_number,
            source=source,
        )

    @classmethod
    def _convert_fields(
        cls,
        fields: list[str | None],
    ) -> tuple[Annotation, ...]:
        del cls
        if fields[1] is None:
            negation = None
        elif fields[1] == "NOT":
            negation = True
        else:
            raise ValueError(f"invalid negation: {fields[1]!r}")

        shared_values = {
            "db_object_id": fields[0],
            "negation": negation,
            "relation": fields[2],
            "ontology_class_id": fields[3],
            "references": _split_optional(fields[4]),
            "evidence_type": fields[5],
            "interacting_taxon_id": _split_optional(fields[7]),
            "annotation_date": fields[8],
            "assigned_by": fields[9],
            "annotation_properties": _parse_properties(fields[11]),
        }
        # Column 7 (with/from) and column 11 (annotation extensions) can both have
        # multiple pipe-delimited alternatives. Each alternative represents a separate
        # annotation; the pipe-separation is just a compact serialization format. Here
        # we expand the alternatives into separate Annotation models, producing a
        # Cartesian product of the two sets of alternatives.
        return tuple(
            Annotation.model_validate(
                {
                    **shared_values,
                    "with_or_from": with_or_from,
                    "annotation_extensions": annotation_extensions,
                }
            )
            for with_or_from, annotation_extensions in product(
                _split_alternatives(fields[6]),
                _parse_extension_alternatives(fields[10]),
            )
        )
