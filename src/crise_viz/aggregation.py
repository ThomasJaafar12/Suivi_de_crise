from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .config import (
    BILAN_SUBTABS,
    CONTRIBUTION_DIMENSIONS,
    METRIC_LABELS,
    METRIC_TABS,
    REGION_SOURCES,
    SPECIAL_GEOGRAPHIES,
)
from .normalization import month_label


@dataclass(frozen=True)
class DashboardPayload:
    payload: dict[str, Any]


def build_payload(
    accord: pd.DataFrame,
    geo: pd.DataFrame,
    geo_meta: dict[str, Any],
    title: str,
    source_name: str,
) -> DashboardPayload:
    years = sorted(accord["PerAnnee"].unique().tolist())
    latest_year = max(years)
    latest_month = int(accord.loc[accord["PerAnnee"] == latest_year, "PerMois"].max())
    partial_latest_year = latest_month < 12
    comparison_year = max([year for year in years if year != latest_year], default=latest_year)
    month_cutoff = latest_month if partial_latest_year else 12

    latest_slice = accord[(accord["PerAnnee"] == latest_year) & (accord["PerMois"] <= month_cutoff)]
    previous_slice = accord[(accord["PerAnnee"] == comparison_year) & (accord["PerMois"] <= month_cutoff)]

    payload = {
        "meta": {
            "title": title,
            "source": source_name,
            "available_years": years,
            "latest_year": latest_year,
            "latest_month": latest_month,
            "month_cutoff": month_cutoff,
            "month_cutoff_label": month_label(month_cutoff),
            "partial_latest_year": partial_latest_year,
            "comparison_year": comparison_year,
            "default_tab": "bilan",
            "default_bilan_subtab": "overview",
            "default_metric": "amount",
            "metric_labels": METRIC_LABELS,
            "metric_tabs": METRIC_TABS,
            "bilan_subtabs": BILAN_SUBTABS,
            "contribution_dimensions": CONTRIBUTION_DIMENSIONS,
            "region_sources": REGION_SOURCES,
            "geo_quality": geo_meta["quality"],
            "source_limitations": {
                "ape_on_geo": False,
                "map_scope": "France métropolitaine + Corse",
            },
            "filters": _build_filter_catalog(accord, geo),
        },
        "facts": {
            "management": _compact_management_fact_table(accord),
            "geography": _compact_geo_fact_table(geo),
        },
        "highlights": {
            "latest_ytd": _summarize_totals(latest_slice),
            "comparison_ytd": _summarize_totals(previous_slice),
        },
        "notes": _build_notes(accord, geo, latest_slice, month_cutoff, latest_year, comparison_year),
        "geojson": geo_meta["geojson"],
    }
    return DashboardPayload(payload)


def _build_filter_catalog(accord: pd.DataFrame, geo: pd.DataFrame) -> dict[str, Any]:
    nace_options = (
        accord[["nace88", "lib88"]]
        .drop_duplicates()
        .sort_values(["nace88", "lib88"])
        .rename(columns={"nace88": "code", "lib88": "label"})
        .to_dict(orient="records")
    )
    ape_options = (
        accord[["ape", "libape"]]
        .drop_duplicates()
        .sort_values(["ape", "libape"])
        .rename(columns={"ape": "code", "libape": "label"})
        .to_dict(orient="records")
    )
    return {
        "period_modes": [
            {"key": "ytd", "label": "YTD auto"},
            {"key": "full", "label": "Année complète"},
        ],
        "geo_levels": [
            {"key": "region", "label": "Région"},
            {"key": "department", "label": "Département"},
        ],
        "categories": sorted(accord["Categ"].dropna().unique().tolist()),
        "plans": sorted(accord["TopPlan"].dropna().unique().tolist()),
        "code_cnrj": sorted(accord["CodeCNRJ"].dropna().unique().tolist()),
        "sectors": sorted(accord["Sect"].dropna().unique().tolist()),
        "management_regions": sorted(accord["libregion"].dropna().unique().tolist()),
        "geographic_regions": sorted(geo["libregionGEO"].dropna().unique().tolist()),
        "departments": sorted(geo["libdpt"].dropna().unique().tolist()),
        "nace_options": nace_options,
        "ape_options": ape_options,
        "default_category": "Toutes catégories",
        "default_plan": "Tous",
        "default_code_cnrj": "Tous",
        "default_sector": "Tous les secteurs",
        "default_nace": "Tous les Nace 88",
        "default_ape": "",
        "default_include_other": True,
    }


def _compact_management_fact_table(frame: pd.DataFrame) -> dict[str, Any]:
    columns = {
        "PerAnnee": "y",
        "PerMois": "m",
        "libregion": "rgm",
        "Categ": "cat",
        "TopPlan": "plan",
        "CodeCNRJ": "cnrj",
        "Sect": "sect",
        "nace88": "n88",
        "lib88": "n88l",
        "ape": "ape",
        "libape": "apel",
        "NbAccord": "nb",
        "MttAccord": "amt",
        "DureeAccord": "dur",
    }
    compact = frame[list(columns.keys())].rename(columns=columns).copy()
    ordered_columns = list(columns.values())
    return {
        "columns": ordered_columns,
        "rows": compact[ordered_columns].values.tolist(),
    }


def _compact_geo_fact_table(frame: pd.DataFrame) -> dict[str, Any]:
    columns = {
        "PerAnnee": "y",
        "PerMois": "m",
        "libregionGEO": "rgg",
        "libdpt": "dpt",
        "Categ": "cat",
        "TopPlan": "plan",
        "CodeCNRJ": "cnrj",
        "Sect": "sect",
        "nace88": "n88",
        "lib88": "n88l",
        "NbAccord": "nb",
        "MttAccord": "amt",
        "DureeAccord": "dur",
    }
    compact = frame[list(columns.keys())].rename(columns=columns).copy()
    ordered_columns = list(columns.values())
    return {
        "columns": ordered_columns,
        "rows": compact[ordered_columns].values.tolist(),
    }


def _summarize_totals(frame: pd.DataFrame) -> dict[str, float]:
    nb = float(frame["NbAccord"].sum())
    amount = float(frame["MttAccord"].sum())
    duration_total = float(frame["DureeAccord"].sum())
    return {
        "nb": nb,
        "amount": amount,
        "avg_duration": (duration_total / nb) if nb else 0.0,
        "avg_ticket": (amount / nb) if nb else 0.0,
    }


def _build_notes(
    accord: pd.DataFrame,
    geo: pd.DataFrame,
    latest_slice: pd.DataFrame,
    month_cutoff: int,
    latest_year: int,
    comparison_year: int,
) -> list[dict[str, Any]]:
    total_nb = float(accord["NbAccord"].sum())
    code_yes = float(accord.loc[accord["CodeCNRJ"] == "Oui", "NbAccord"].sum())
    share_yes = (code_yes / total_nb) * 100.0 if total_nb else 0.0
    geo_filtered = geo[(geo["PerAnnee"] == latest_year) & (geo["PerMois"] <= month_cutoff)]
    geo_region = (
        geo_filtered.loc[~geo_filtered["libregionGEO"].isin(SPECIAL_GEOGRAPHIES)]
        .groupby("libregionGEO", as_index=False)["NbAccord"]
        .sum()
        .sort_values("NbAccord", ascending=False)
    )
    top_geo_region = geo_region.iloc[0]["libregionGEO"] if not geo_region.empty else "N/A"
    top_sector = (
        latest_slice.groupby("Sect", as_index=False)["NbAccord"]
        .sum()
        .sort_values("NbAccord", ascending=False)
        .iloc[0]["Sect"]
    )
    return [
        {
            "title": "Périmètre de lecture",
            "body": (
                f"Le tableau compare {latest_year} à {comparison_year} sur la même fenêtre temporelle, "
                f"avec une lecture YTD arrêtée à fin {month_label(month_cutoff).lower()} pour l’année la plus récente."
            ),
        },
        {
            "title": "CodeCNRJ=Oui quasi absent",
            "body": (
                f"Le marqueur explicite CodeCNRJ=Oui représente {share_yes:.3f} % des délais. "
                "Le récit visuel repose surtout sur le périmètre sectoriel."
            ),
        },
        {
            "title": "Signaux dominants",
            "body": (
                f"{top_sector} reste le principal contributeur en volume dans la coupe courante. "
                f"Côté géographie, {top_geo_region} domine la lecture régionale."
            ),
        },
        {
            "title": "Limites de source",
            "body": (
                "Le filtre APE est disponible sur les vues de gestion, mais la source géographique ne porte pas cette dimension. "
                "Les cartes et rankings géographiques l’ignorent donc lorsqu’un APE est sélectionné."
            ),
        },
    ]
