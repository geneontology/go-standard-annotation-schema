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
    * [schema/](src/go_standard_annotation_schema/schema) -- LinkML schema
      (edit this)
    * [datamodel/](src/go_standard_annotation_schema/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests
  * [data/](tests/data) - Example data

## Developer Tools

[uv](https://docs.astral.sh/uv/) is the only required development tool. It
installs the project dependencies and the locked copy of
[just](https://github.com/casey/just):

```shell
uv sync
uv run --locked just check
uv run --locked just test
```

Run `uv run --locked just` to see focused checks, generation commands,
and documentation recipes. See [CONTRIBUTING.md](CONTRIBUTING.md) for automatic
fixes, optional Git hooks, and editor integration.

If you have just installed globally, you can omit the `uv run --locked` prefix and run `just` directly.

## Credits

This project uses the template [linkml-project-copier](https://github.com/linkml/linkml-project-copier).
