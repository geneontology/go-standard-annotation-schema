<a href="https://github.com/linkml/linkml-project-copier"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-teal.json" alt="Copier Badge" style="max-width:100%;"/></a>

# go-standard-annotation-schema

LinkML schema for GO Standard Annotations

## Documentation Website

[https://geneontology.github.io/go-standard-annotation-schema](https://geneontology.github.io/go-standard-annotation-schema)

## Repository Structure

* [docs/](docs/) - mkdocs-managed documentation
  * [elements/](docs/elements/) - generated schema documentation
* [examples/](examples/) - Examples of using the schema
* [project/](project/) - project files (these files are auto-generated, do not edit)
* [src/](src/) - source files (edit these)
  * [go_standard_annotation_schema](src/go_standard_annotation_schema)
    * [schema/](src/go_standard_annotation_schema/schema) -- LinkML schema (edit this)
    * [datamodel/](src/go_standard_annotation_schema/datamodel) -- generated Python
      datamodel
* [tests/](tests/) - Python tests
  * [data/](tests/data) - Example data

## Developer Tools

[uv](https://docs.astral.sh/uv/) is the only required development tool. It installs the
project dependencies and the locked copy of
[just](https://github.com/casey/just):

```shell
uv sync
uv run --locked just check
uv run --locked just test
```

Run `uv run --locked just` to see focused checks, generation commands, and documentation
recipes. See [CONTRIBUTING.md](CONTRIBUTING.md) for automatic fixes, optional Git hooks,
and editor integration.

If you have just installed globally, you can omit the `uv run --locked` prefix and run
`just` directly.

## Reading GPAD and GPI files

`GpadReader` and `GpiReader` stream validated annotations and entities without loading
the whole file into memory. Both readers support only version 2.0 of their respective
formats. A path ending in `.gz` is opened as a gzip-compressed text file; other paths
are opened as ordinary text files. For compatibility with producers that omit the GPI
object symbol, an empty column 2 is preserved as an empty `db_object_symbol`; other
mandatory GPI scalar columns remain required.

Use a reader as a context manager to inspect its header metadata and iterate over its
records:

```python
from go_standard_annotation_schema.io import GpadReader

with GpadReader("annotations.gpad.gz") as reader:
  print(reader.metadata.generated_by)
  for annotation in reader:
    print(annotation.db_object_id)
```

By default, an invalid data row raises `RowError`. Use `errors="skip"` to continue after
invalid rows, and `on_error` to inspect every skipped row:

```python
def report(issue):
  print(issue.source, issue.line_number, issue.code)


with GpadReader("annotations.gpad", errors="skip", on_error=report) as reader:
  for annotation in reader:
    consume(annotation)
  print(reader.stats.rows_skipped)
```

For an individual headerless GPI data row, use the class-level parser:

```python
from go_standard_annotation_schema.io import GpiReader

entity = GpiReader.parse_line(line)
print(entity.db_object_symbol)
```

For an individual headerless GPAD data row, the class-level parser returns every
annotation produced by that row:

```python
from go_standard_annotation_schema.io import GpadReader

(annotation,) = GpadReader.parse_line(line)
print(annotation.ontology_class_id)
```

For GPAD columns 7 and 11, pipes separate alternative annotations and commas
separate values within one annotation. When either field contains pipes, the reader
emits one `Annotation` for each Cartesian-product combination. Therefore
`GpadReader.parse_line()` returns a tuple, even when a row produces one annotation.

Interacting taxon identifiers are split only on pipes. Other content is passed
unchanged to `Annotation.model_validate()` for model-level validation.

See the
official [GPAD 2.0 format documentation](https://geneontology.org/docs/gene-product-association-data-gpad-format/)
and [GPI 2.0 format documentation](https://geneontology.org/docs/gene-product-information-gpi-format-2.0/).

## Credits

This project uses the
template [linkml-project-copier](https://github.com/linkml/linkml-project-copier).
