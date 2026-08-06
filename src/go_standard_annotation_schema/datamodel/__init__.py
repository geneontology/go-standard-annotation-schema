"""Data model package for go-standard-annotation-schema."""

from pathlib import Path

from .go_standard_annotation_schema import (
    Annotation,
    AnnotationExtension,
    AnnotationProperty,
    Entity,
    EntityProperty,
    Property,
)

THIS_PATH = Path(__file__).parent

SCHEMA_DIRECTORY = THIS_PATH.parent / "schema"
MAIN_SCHEMA_PATH = SCHEMA_DIRECTORY / "go_standard_annotation_schema.yaml"

__all__ = [
    "Annotation",
    "AnnotationExtension",
    "AnnotationProperty",
    "Entity",
    "EntityProperty",
    "Property",
]
