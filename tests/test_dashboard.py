from __future__ import annotations

from pathlib import Path

from src.crise_viz.aggregation import build_payload
from src.crise_viz.config import BuildConfig
from src.crise_viz.geo import load_geo_assets
from src.crise_viz.ingestion import load_workbook_frames
from src.crise_viz.rendering import render_dashboard


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "Data_source" / "Crise_Secteur_NRJ_Delais_Version interne_260413.xlsx"
ASSET_DIR = ROOT / "src" / "crise_viz" / "assets" / "geo"


def build_test_payload():
    accord, geo = load_workbook_frames(WORKBOOK)
    geo_assets = load_geo_assets(geo, ASSET_DIR)
    return build_payload(accord, geo, geo_assets, "Test dashboard", WORKBOOK.name)


def test_payload_detects_partial_latest_year_and_new_dimensions():
    payload = build_test_payload().payload
    assert payload["meta"]["latest_year"] == 2026
    assert payload["meta"]["latest_month"] == 4
    assert payload["meta"]["partial_latest_year"] is True
    assert payload["meta"]["month_cutoff"] == 4
    assert payload["meta"]["geo_quality"]["department_coverage_ratio"] >= 0.95
    assert payload["meta"]["default_tab"] == "bilan"
    assert payload["meta"]["default_metric"] == "amount"
    assert payload["meta"]["filters"]["plans"] == ["Non", "Oui"]
    assert payload["meta"]["filters"]["code_cnrj"] == ["Non", "Oui"]
    assert len(payload["meta"]["filters"]["nace_options"]) >= 80
    assert len(payload["meta"]["filters"]["ape_options"]) >= 600
    assert "management" in payload["facts"]
    assert "geography" in payload["facts"]


def test_rendered_html_contains_shell_navigation_and_bilan_runtime():
    payload = build_test_payload()
    output_path = ROOT / "dist" / "test_dashboard_render.html"
    config = BuildConfig(
        input_path=WORKBOOK,
        output_path=output_path,
        title="Test dashboard",
        default_variant="premium_moderne",
        verbose=False,
    )
    html = render_dashboard(config, payload)
    assert "payload-data" in html
    assert "Windows-like navigator" in html
    assert "Bilan premium moderne" in html
    assert "Vue d’ensemble" in html
    assert "Contribution" in html
    assert "Géographie" in html
    assert "Méthode" in html
    assert "Treemap de contribution à l’évolution" in html
    assert "Le filtre APE n’est pas disponible sur la source géographique" in html
