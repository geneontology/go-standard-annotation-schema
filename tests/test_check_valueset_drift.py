"""Tests for scripts/check_valueset_drift.py."""

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
from linkml_runtime import SchemaView
from typer.testing import CliRunner, Result

import scripts.check_valueset_drift as drift

DATA_DIR = Path(__file__).parent / "fixtures" / "valueset_drift"
RO_FIXTURE = str(DATA_DIR / "ro.json")
ECO_FIXTURE = str(DATA_DIR / "eco.json")

RO = drift.Source("RO", RO_FIXTURE, ("RO", "BFO"))
ECO = drift.Source("ECO", ECO_FIXTURE, ("ECO",))

SCHEMA_HEADER = """\
id: https://example.org/drift-test
name: drift-test
prefixes:
  RO: http://purl.obolibrary.org/obo/RO_
  BFO: http://purl.obolibrary.org/obo/BFO_
  ECO: http://purl.obolibrary.org/obo/ECO_
  GO: http://purl.obolibrary.org/obo/GO_
default_prefix: drift-test
"""


def write_schema(tmp_path: Path, enums: str) -> str:
    path = tmp_path / "schema.yaml"
    path.write_text(SCHEMA_HEADER + "enums:\n" + enums, encoding="utf-8")
    return str(path)


def schema_view(tmp_path: Path, enums: str) -> SchemaView:
    return SchemaView(write_schema(tmp_path, enums))


CLEAN_ENUMS = """\
  Relation:
    permissible_values:
      "RO:0000001":
        title: enables
        meaning: RO:0000001
      "BFO:0000050":
        title: part of
        meaning: BFO:0000050
"""


# --- load_source ---


def test_iri_to_curie_converts_obo_purls():
    assert drift.iri_to_curie("http://purl.obolibrary.org/obo/RO_0002327") == (
        "RO:0002327"
    )
    assert drift.iri_to_curie("http://purl.obolibrary.org/obo/BFO_0000050") == (
        "BFO:0000050"
    )


def test_iri_to_curie_leaves_other_iris_alone():
    iri = "http://www.geneontology.org/formats/oboInOwl#consider"
    assert drift.iri_to_curie(iri) == iri
    assert drift.iri_to_curie("http://purl.obolibrary.org/obo/ro.json") == (
        "http://purl.obolibrary.org/obo/ro.json"
    )


def test_load_source_reads_version_labels_and_obsolete_terms():
    loaded = drift.load_source(RO_FIXTURE)

    assert loaded.version == (
        "http://purl.obolibrary.org/obo/ro/releases/2000-01-01/ro.json"
    )
    assert loaded.terms["RO:0000001"] == drift.Term("enables", False)
    assert loaded.terms["BFO:0000050"].label == "part of"
    assert loaded.terms["RO:0000003"] == drift.Term(
        "obsolete directly activates", True, ("RO:0000001", "RO:0000004")
    )
    assert loaded.terms["RO:0000005"].label is None


@pytest.mark.parametrize("name", ["missing.json", "malformed.json"])
def test_load_source_raises_source_load_error(name):
    with pytest.raises(drift.SourceLoadError):
        drift.load_source(str(DATA_DIR / name))


def test_load_source_wraps_network_errors(monkeypatch):
    def timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(drift.urllib.request, "urlopen", timeout)
    with pytest.raises(drift.SourceLoadError, match="timed out"):
        drift.load_source("http://example.org/ro.json")


# --- find_drift ---


def test_find_drift_clean(tmp_path):
    sv = schema_view(tmp_path, CLEAN_ENUMS)
    loaded = {"RO": drift.load_source(RO_FIXTURE)}

    report = drift.find_drift(sv, [RO], loaded)

    assert report.findings == {"RO": []}
    assert report.checked == 2
    assert not report.unchecked
    assert not report.has_drift


def test_find_drift_reports_each_finding_type(tmp_path):
    sv = schema_view(
        tmp_path,
        """\
  Relation:
    permissible_values:
      "RO:0000002":
        title: acts upstream of positive effect
        meaning: RO:0000002
      "RO:0000003":
        title: directly activates
        meaning: RO:0000003
      "RO:9999999":
        title: made up
        meaning: RO:9999999
""",
    )
    loaded = {"RO": drift.load_source(RO_FIXTURE)}

    report = drift.find_drift(sv, [RO], loaded)

    assert report.findings["RO"] == [
        drift.Finding(
            "Relation",
            "RO:0000002",
            drift.LABEL_MISMATCH,
            "title 'acts upstream of positive effect' != RO label "
            "'acts upstream of, positive effect'",
        ),
        drift.Finding(
            "Relation",
            "RO:0000003",
            drift.OBSOLETE_UPSTREAM,
            "RO:0000003; consider RO:0000001, RO:0000004",
        ),
        drift.Finding("Relation", "RO:9999999", drift.UNKNOWN_ID, "RO:9999999"),
    ]
    assert report.has_drift


def test_find_drift_missing_title_is_a_label_mismatch(tmp_path):
    sv = schema_view(
        tmp_path,
        """\
  Relation:
    permissible_values:
      "RO:0000001":
        meaning: RO:0000001
""",
    )
    report = drift.find_drift(sv, [RO], {"RO": drift.load_source(RO_FIXTURE)})

    assert [f.kind for f in report.findings["RO"]] == [drift.LABEL_MISMATCH]


def test_find_drift_reports_same_term_in_each_enum(tmp_path):
    sv = schema_view(
        tmp_path,
        """\
  First:
    permissible_values:
      "BFO:0000050":
        title: part_of
        meaning: BFO:0000050
  Second:
    permissible_values:
      "BFO:0000050":
        title: part_of
        meaning: BFO:0000050
""",
    )
    report = drift.find_drift(sv, [RO], {"RO": drift.load_source(RO_FIXTURE)})

    assert [f.enum for f in report.findings["RO"]] == ["First", "Second"]


def test_find_drift_routes_prefixes_and_counts_unchecked(tmp_path):
    sv = schema_view(
        tmp_path,
        CLEAN_ENUMS
        + """\
  Evidence:
    permissible_values:
      "ECO:0000001":
        title: inference from background scientific knowledge
        meaning: ECO:0000001
  Other:
    permissible_values:
      "GO:0003674":
        meaning: GO:0003674
      "GO:0008150":
        meaning: GO:0008150
      plain_value:
        title: no meaning here
""",
    )
    loaded = {
        "RO": drift.load_source(RO_FIXTURE),
        "ECO": drift.load_source(ECO_FIXTURE),
    }

    report = drift.find_drift(sv, [RO, ECO], loaded)

    assert report.findings == {"RO": [], "ECO": []}
    assert report.checked == 3
    assert report.unchecked == {"GO": 2, drift.NO_MEANING: 1}


def test_find_drift_skips_sources_that_failed_to_load(tmp_path):
    sv = schema_view(tmp_path, CLEAN_ENUMS)

    report = drift.find_drift(sv, [RO], {})

    assert report.findings == {}
    assert report.checked == 0
    assert not report.unchecked
    assert report.skipped == {"RO": 2}


def test_required_sources_only_returns_sources_in_use(tmp_path):
    sv = schema_view(tmp_path, CLEAN_ENUMS)

    assert drift.required_sources(sv, [RO, ECO]) == [RO]


# --- render_report ---


def test_render_report_groups_findings_and_summarizes():
    report = drift.DriftReport(
        findings={
            "RO": [drift.Finding("Relation", "RO:9999999", drift.UNKNOWN_ID, "x")],
        },
        checked=4,
        unchecked=Counter({"GO": 3, drift.NO_MEANING: 1}),
    )
    loaded = {"RO": drift.LoadedSource("ro-release-1", {})}
    failures = {"ECO": "eco.json: boom"}

    text = drift.render_report(report, loaded, failures)

    assert text == (
        "## RO (release ro-release-1)\n"
        "Relation RO:9999999: unknown ID (x)\n"
        "\n"
        "## ECO\n"
        "Could not load source: eco.json: boom\n"
        "\n"
        "Checked 4 values; 1 drift findings; 4 values unchecked "
        "(prefix GO: 3, no meaning: 1).\n"
    )


def test_render_report_counts_values_skipped_by_failed_sources():
    report = drift.DriftReport(skipped=Counter({"RO": 73}))
    failures = {"RO": "ro.json: boom"}

    text = drift.render_report(report, {}, failures)

    assert text.endswith(
        "Checked 0 values; 0 drift findings; "
        "73 values skipped because their source failed to load (RO: 73).\n"
    )


# --- command line ---


runner = CliRunner()


def invoke(*args: str) -> Result:
    return runner.invoke(drift.app, list(args))


@pytest.fixture
def ro_only(monkeypatch):
    monkeypatch.setattr(drift, "SOURCES", (RO,))


def test_cli_exits_0_when_clean(tmp_path, ro_only):
    schema = write_schema(tmp_path, CLEAN_ENUMS)

    result = invoke(schema)

    assert result.exit_code == drift.EXIT_OK, result.output
    assert "No drift." in result.stdout


def test_cli_exits_1_on_drift(tmp_path, ro_only):
    schema = write_schema(
        tmp_path,
        """\
  Relation:
    permissible_values:
      "RO:9999999":
        title: made up
        meaning: RO:9999999
""",
    )

    result = invoke(schema)

    assert result.exit_code == drift.EXIT_DRIFT, result.output
    assert "unknown ID" in result.stdout


def test_cli_source_override_replaces_location(tmp_path, ro_only):
    schema = write_schema(tmp_path, CLEAN_ENUMS)
    missing = str(tmp_path / "missing.json")

    result = invoke(schema, "--source", f"RO={missing}")

    assert result.exit_code == drift.EXIT_LOAD_ERROR, result.output
    assert "Could not load source" in result.stdout


def test_cli_load_error_wins_but_other_sources_still_report(tmp_path, monkeypatch):
    monkeypatch.setattr(
        drift,
        "SOURCES",
        (drift.Source("RO", str(tmp_path / "missing.json"), ("RO", "BFO")), ECO),
    )
    schema = write_schema(
        tmp_path,
        CLEAN_ENUMS
        + """\
  Evidence:
    permissible_values:
      "ECO:9999999":
        title: made up
        meaning: ECO:9999999
""",
    )

    result = invoke(schema)

    assert result.exit_code == drift.EXIT_LOAD_ERROR, result.output
    assert "## ECO (release" in result.stdout
    assert "unknown ID" in result.stdout
    assert "Could not load source" in result.stdout


@pytest.mark.parametrize(
    "bad", ["RO", "RO=", "NOPE=somewhere.json"], ids=["no-equals", "empty", "unknown"]
)
def test_cli_rejects_malformed_source_option(tmp_path, ro_only, bad):
    schema = write_schema(tmp_path, CLEAN_ENUMS)

    result = invoke(schema, "--source", bad)

    assert result.exit_code == drift.EXIT_LOAD_ERROR, result.output
    assert "--source" in result.stderr
    assert result.stdout == ""


def test_script_crash_exits_2_not_1(tmp_path):
    result = subprocess.run(
        [sys.executable, drift.__file__, str(tmp_path / "missing.yaml")],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == drift.EXIT_LOAD_ERROR
    assert "Traceback" in result.stderr


def test_script_import_failure_exits_2_not_1(tmp_path):
    broken = tmp_path / "linkml_runtime"
    broken.mkdir()
    (broken / "__init__.py").write_text(
        'raise ImportError("simulated linkml_runtime breakage")\n', encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, drift.__file__, str(tmp_path / "missing.yaml")],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
    )

    assert result.returncode == drift.EXIT_LOAD_ERROR
    assert "simulated linkml_runtime breakage" in result.stderr
