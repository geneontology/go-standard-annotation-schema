"""Check schema valueset enums for drift from their upstream ontologies.

The schema decides which terms belong in each enum. The upstream ontology
decides what each term is: its label and whether it is obsolete. This script
reports permissible values whose `meaning` no longer matches upstream.

Exit codes: 0 no drift, 1 drift found, 2 a source could not be loaded.
"""

from __future__ import annotations

import json
import sys
import traceback
import urllib.request
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, cast

import typer

if TYPE_CHECKING:
    # Imported at runtime inside main(), under the exit-2 crash guard.
    from linkml_runtime import SchemaView
    from linkml_runtime.linkml_model.meta import PermissibleValue

DEFAULT_SCHEMA = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "go_standard_annotation_schema"
    / "schema"
    / "go_standard_annotation_schema.yaml"
)

OBO_PURL = "http://purl.obolibrary.org/obo/"
TERM_REPLACED_BY = OBO_PURL + "IAO_0100001"
CONSIDER = "http://www.geneontology.org/formats/oboInOwl#consider"

UNKNOWN_ID = "unknown ID"
OBSOLETE_UPSTREAM = "obsolete upstream — remove this value"
LABEL_MISMATCH = "label mismatch"

NO_MEANING = "(no meaning)"

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_LOAD_ERROR = 2


@dataclass(frozen=True)
class Source:
    """An upstream ontology release and the CURIE prefixes it defines."""

    name: str
    location: str
    prefixes: tuple[str, ...]


SOURCES: tuple[Source, ...] = (Source("RO", OBO_PURL + "ro.json", ("RO", "BFO")),)


@dataclass(frozen=True)
class Term:
    """What a source says about one term."""

    label: str | None
    obsolete: bool
    replacements: tuple[str, ...] = ()


@dataclass(frozen=True)
class LoadedSource:
    """Terms read from one source release, keyed by CURIE."""

    version: str | None
    terms: dict[str, Term]


class SourceLoadError(Exception):
    """A source could not be fetched or parsed."""


@dataclass(frozen=True)
class Finding:
    """One drift problem for one permissible value."""

    enum: str
    value: str
    kind: str
    detail: str = ""


@dataclass
class DriftReport:
    """Result of comparing schema enums against loaded sources."""

    findings: dict[str, list[Finding]] = field(default_factory=dict)
    checked: int = 0
    unchecked: Counter[str] = field(default_factory=Counter)
    skipped: Counter[str] = field(default_factory=Counter)

    @property
    def has_drift(self) -> bool:
        return any(self.findings.values())


def iri_to_curie(iri: str) -> str:
    """Convert an OBO PURL like ``.../obo/RO_0002327`` to ``RO:0002327``."""
    if iri.startswith(OBO_PURL):
        prefix, sep, local = iri[len(OBO_PURL) :].partition("_")
        if sep and prefix and local:
            return f"{prefix}:{local}"
    return iri


def load_source(location: str) -> LoadedSource:
    """Read an OBO Graph JSON file from a URL or local path."""
    try:
        if "://" in location:
            with urllib.request.urlopen(location, timeout=120) as response:
                data = json.load(response)
        else:
            with open(location, encoding="utf-8") as handle:
                data = json.load(handle)
        graph = data["graphs"][0]
        nodes = graph.get("nodes", [])
        version = (graph.get("meta") or {}).get("version")
        terms: dict[str, Term] = {}
        for node in nodes:
            iri = node.get("id")
            if not iri:
                continue
            meta = node.get("meta") or {}
            replacements = tuple(
                iri_to_curie(prop["val"])
                for prop in meta.get("basicPropertyValues", [])
                if prop.get("pred") in (TERM_REPLACED_BY, CONSIDER)
            )
            terms[iri_to_curie(iri)] = Term(
                label=node.get("lbl"),
                obsolete=bool(meta.get("deprecated")),
                replacements=replacements,
            )
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as e:
        raise SourceLoadError(f"{location}: {e}") from e
    return LoadedSource(version=version, terms=terms)


def _meanings(
    schema_view: SchemaView,
) -> Iterable[tuple[str, str, str | None, str | None]]:
    """Yield (enum, value, meaning, title) for every permissible value."""
    for enum_name, enum in schema_view.all_enums().items():
        # SchemaView normalizes permissible_values to a name -> object mapping.
        values = cast("dict[str, PermissibleValue]", enum.permissible_values or {})
        for value_name, value in values.items():
            yield enum_name, value_name, value.meaning, value.title


def _prefix(curie: str) -> str:
    return curie.split(":", 1)[0]


def required_sources(
    schema_view: SchemaView, sources: Sequence[Source]
) -> list[Source]:
    """Return the sources that at least one permissible value needs."""
    prefixes = {_prefix(m) for _, _, m, _ in _meanings(schema_view) if m}
    return [s for s in sources if prefixes.intersection(s.prefixes)]


def find_drift(
    schema_view: SchemaView,
    sources: Sequence[Source],
    loaded: Mapping[str, LoadedSource],
) -> DriftReport:
    """Compare every permissible value against the source for its prefix.

    Values whose source is absent from ``loaded`` (it failed to load) are
    counted in ``skipped`` by source name; the caller reports the failure.
    """
    by_prefix = {prefix: s for s in sources for prefix in s.prefixes}
    report = DriftReport(findings={s.name: [] for s in sources if s.name in loaded})
    for enum_name, value_name, meaning, title in _meanings(schema_view):
        if not meaning:
            report.unchecked[NO_MEANING] += 1
            continue
        source = by_prefix.get(_prefix(meaning))
        if source is None:
            report.unchecked[_prefix(meaning)] += 1
            continue
        if source.name not in loaded:
            report.skipped[source.name] += 1
            continue
        report.checked += 1
        term = loaded[source.name].terms.get(meaning)
        findings = report.findings[source.name]
        if term is None:
            findings.append(Finding(enum_name, value_name, UNKNOWN_ID, meaning))
        elif term.obsolete:
            detail = meaning
            if term.replacements:
                detail += "; consider " + ", ".join(term.replacements)
            findings.append(Finding(enum_name, value_name, OBSOLETE_UPSTREAM, detail))
        elif title != term.label:
            findings.append(
                Finding(
                    enum_name,
                    value_name,
                    LABEL_MISMATCH,
                    f"title {title!r} != {source.name} label {term.label!r}",
                )
            )
    return report


def render_report(
    report: DriftReport,
    loaded: Mapping[str, LoadedSource],
    failures: Mapping[str, str],
) -> str:
    """Format the report as plain text, grouped by source."""
    lines: list[str] = []
    for name, findings in report.findings.items():
        lines.append(f"## {name} (release {loaded[name].version or 'unknown'})")
        if findings:
            lines.extend(
                f"{f.enum} {f.value}: {f.kind}" + (f" ({f.detail})" if f.detail else "")
                for f in findings
            )
        else:
            lines.append("No drift.")
        lines.append("")
    for name, error in failures.items():
        lines.append(f"## {name}")
        lines.append(f"Could not load source: {error}")
        lines.append("")
    total = sum(len(f) for f in report.findings.values())
    summary = f"Checked {report.checked} values; {total} drift findings"
    if report.unchecked:
        groups = ", ".join(
            f"no meaning: {count}" if key == NO_MEANING else f"prefix {key}: {count}"
            for key, count in sorted(
                report.unchecked.items(), key=lambda item: (item[0] == NO_MEANING, item)
            )
        )
        summary += f"; {sum(report.unchecked.values())} values unchecked ({groups})"
    if report.skipped:
        groups = ", ".join(f"{name}: {n}" for name, n in sorted(report.skipped.items()))
        summary += (
            f"; {sum(report.skipped.values())} values skipped because their source"
            f" failed to load ({groups})"
        )
    lines.append(summary + ".")
    return "\n".join(lines) + "\n"


app = typer.Typer()


def _parse_overrides(items: Sequence[str]) -> dict[str, str]:
    """Turn ``NAME=PATH_OR_URL`` options into a source name -> location map."""
    known = {s.name for s in SOURCES}
    overrides: dict[str, str] = {}
    for item in items:
        name, sep, location = item.partition("=")
        if not sep or not location:
            raise typer.BadParameter(
                f"must be NAME=PATH_OR_URL, got {item!r}", param_hint="'--source'"
            )
        if name not in known:
            raise typer.BadParameter(
                f"unknown source {name!r}; known: {', '.join(sorted(known))}",
                param_hint="'--source'",
            )
        overrides[name] = location
    return overrides


@app.command()
def main(
    schema: Annotated[
        str,
        typer.Argument(help="Schema to check.", show_default="the main schema"),
    ] = str(DEFAULT_SCHEMA),
    source: Annotated[
        list[str] | None,
        typer.Option(
            metavar="NAME=PATH_OR_URL",
            help="Replace a source's location; may be repeated.",
        ),
    ] = None,
) -> None:
    """Check schema valueset enums for drift from their upstream ontologies.

    Exit codes: 0 no drift, 1 drift found, 2 a source could not be loaded.
    """
    from linkml_runtime import SchemaView

    overrides = _parse_overrides(source or [])
    sources = [
        Source(s.name, overrides.get(s.name, s.location), s.prefixes) for s in SOURCES
    ]
    schema_view = SchemaView(schema)
    loaded: dict[str, LoadedSource] = {}
    failures: dict[str, str] = {}
    for src in required_sources(schema_view, sources):
        try:
            loaded[src.name] = load_source(src.location)
        except SourceLoadError as e:
            failures[src.name] = str(e)
    report = find_drift(schema_view, sources, loaded)
    typer.echo(render_report(report, loaded, failures), nl=False)
    if failures:
        raise typer.Exit(EXIT_LOAD_ERROR)
    raise typer.Exit(EXIT_DRIFT if report.has_drift else EXIT_OK)


if __name__ == "__main__":
    try:
        app()
    except Exception:  # Any crash must not look like "drift found" (exit 1).
        traceback.print_exc()
        sys.exit(EXIT_LOAD_ERROR)
