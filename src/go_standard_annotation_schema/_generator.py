"""Define a custom Pydantic generator that folds type patterns into slot patterns

This generator uses the before_generate_slot lifecycle hook to check if a slot's range
is a type with a pattern. If so, and if the slot does not already have a pattern, it
copies the type's pattern into the slot's pattern.

TODO: consider how to contribute this back into the core LinkML Pydantic generator.

References:
    - https://linkml.io/linkml/generators/common/lifecycle.html
"""

import copy

import typer
from linkml.generators import PydanticGenerator
from linkml.generators.pydanticgen import MetadataMode
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SlotDefinition

app = typer.Typer()


class _CustomPydanticGenerator(PydanticGenerator):
    def before_generate_slot(
        self, slot: SlotDefinition, sv: SchemaView
    ) -> SlotDefinition:
        if slot.range in sv.all_types():
            induced_type = sv.induced_type(slot.range)
            if induced_type.pattern and not slot.pattern:
                updated_slot = copy.deepcopy(slot)
                updated_slot.pattern = induced_type.pattern
                return updated_slot
        return slot


@app.command()
def main(schema_path: str):
    """Generate Pydantic models with type patterns folded into slot patterns."""
    gen = _CustomPydanticGenerator(
        schema_path,
        metadata_mode=MetadataMode.NONE,
    )
    print(gen.serialize(), end="")  # noqa: T201


if __name__ == "__main__":
    app()
