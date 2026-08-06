# ============ Justfile settings ===========

# List recipes instead of running the default recipe when no recipe is specified.
set default-list := true

# ============ Variables used in recipes ============

schema_name := "go_standard_annotation_schema"
source_schema_dir := "src" / schema_name / "schema"
source_schema_path := source_schema_dir / schema_name + ".yaml"
materialized_schema_path := "tmp" / schema_name + "_materialized.yaml"
python_dir := "src" / schema_name / "datamodel"
project_dir := "project"
doc_dir := "docs/elements"

# ============== Project recipes ==============

# Install project dependencies
[group('project management')]
install:
  uv sync

# Clean all generated files
[group('project management')]
clean:
  rm -rf tmp
  find {{python_dir}} -type f -name "*.py" -not -name "__init__.py" -delete
  find {{python_dir}} -type d -delete
  find {{project_dir}} -not -name "README.md" -delete
  rm -rf {{doc_dir}}/*.md

# Run all tests
[group('model development')]
test: gen-python
  uv run python -m pytest
  -mkdir -p examples/output
  -rm -rf examples/output/*.*
  uv run linkml-run-examples \
    --input-formats yaml \
    --output-formats json \
    --output-formats yaml \
    --counter-example-input-directory tests/data/invalid \
    --input-directory tests/data/valid \
    --output-directory examples/output \
    --schema {{materialized_schema_path}} > examples/output/README.md

# Run all non-mutating code quality checks
[group('code quality')]
check: lock-check format-check lint-python lint-yaml spellcheck lint-schema type-check

# Apply safe Python lint fixes and formatting
[group('code quality')]
fix:
  uv run --locked ruff check --fix .
  uv run --locked ruff format .

# Check that the dependency lockfile is current
[group('code quality')]
lock-check:
  uv lock --check

# Check Python formatting
[group('code quality')]
format-check:
  uv run --locked ruff format --check .

# Lint Python source and tests
[group('code quality')]
lint-python:
  uv run --locked ruff check .

# Type-check Python source and tests
[group('code quality')]
type-check:
  uv run --locked ty check

# Lint YAML files
[group('code quality')]
lint-yaml:
  uv run --locked yamllint .

# Check spelling
[group('code quality')]
spellcheck:
  uv run --locked codespell

# Lint the LinkML source schema
[group('code quality')]
lint-schema:
  uv run --locked linkml lint {{source_schema_dir}}

# Generate all artifacts from the schema
[group('model development')]
all: gen-doc gen-json-schema gen-python

# Generate md documentation for the schema and add artifacts
[group('model development')]
gen-doc: _gen-materialized-schema
  uv run linkml generate doc \
    --stacktrace \
    --directory {{doc_dir}} \
    {{materialized_schema_path}}

# Build docs and run test server
[group('model development')]
serve-doc: gen-doc
  uv run mkdocs serve

# Generate JSON Schema from the schema
[group('model development')]
gen-json-schema: _gen-materialized-schema
  mkdir -p {{project_dir}}/jsonschema
  uv run linkml generate json-schema \
    --top-class Annotation \
    {{materialized_schema_path}} > {{project_dir}}/jsonschema/{{schema_name}}.schema.json

# Generate Pydantic models from the schema
[group('model development')]
gen-python: _gen-materialized-schema
  uv run linkml generate pydantic \
    {{materialized_schema_path}} > {{python_dir}}/{{schema_name}}.py

# ============== Internal recipes ==============

# Generate a copy of the schema with materialized structured patterns to be
# used as the basis for generating other artifacts.
# TODO: This can be removed once LinkML supports pattern materialization directly in
#       more generators. See: https://github.com/linkml/linkml/pull/3832
_gen-materialized-schema:
  mkdir -p tmp
  uv run linkml generate linkml \
    --format yaml \
    --materialize-patterns \
    --no-materialize-attributes \
    {{source_schema_path}} > {{materialized_schema_path}}
