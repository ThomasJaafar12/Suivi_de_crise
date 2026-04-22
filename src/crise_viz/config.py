from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_TITLE = "Délais accordés aux secteurs impactés par la crise énergétique"
DEFAULT_OUTPUT = "dist/crise_dashboard.html"
DEFAULT_VARIANT = "premium_moderne"
SPECIAL_GEOGRAPHIES = {"ETRANGER", "TOM", "NON_IDENTIFIABLE"}
MAPPABLE_DEPARTMENTS_EXCLUDED = {"Etranger", "Tom", "NON_IDENTIFIABLE"}
METRIC_LABELS = {
    "nb": "Nombre de délais",
    "amount": "Montant accordé",
    "avg_duration": "Durée moyenne",
    "avg_ticket": "Ticket moyen",
}
METRIC_TABS = [
    {"key": "nb", "label": "Nombre de délais"},
    {"key": "amount", "label": "Montant accordé"},
    {"key": "avg_duration", "label": "Durée moyenne"},
    {"key": "avg_ticket", "label": "Ticket moyen"},
]
BILAN_SUBTABS = [
    {"key": "overview", "label": "Vue d’ensemble"},
    {"key": "contribution", "label": "Contribution"},
    {"key": "geography", "label": "Géographie"},
    {"key": "method", "label": "Méthode"},
]
CONTRIBUTION_DIMENSIONS = [
    {"key": "sector", "label": "Secteur"},
    {"key": "region", "label": "Région"},
    {"key": "nace", "label": "Nace 88"},
]
REGION_SOURCES = [
    {"key": "geographic", "label": "Région géographique"},
    {"key": "management", "label": "Région de gestion"},
]


@dataclass(frozen=True)
class BuildConfig:
    input_path: Path
    output_path: Path
    title: str = DEFAULT_TITLE
    default_variant: str = DEFAULT_VARIANT
    verbose: bool = False

    def ensure_parent(self) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
