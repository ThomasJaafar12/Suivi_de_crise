from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from .config import MAPPABLE_DEPARTMENTS_EXCLUDED, SPECIAL_GEOGRAPHIES
from .normalization import normalize_label


def load_geo_assets(geo_frame: pd.DataFrame, asset_dir: Path) -> dict[str, Any]:
    department_geojson = _read_json(asset_dir / "france_departments_source.geojson")
    region_geojson = _read_json(asset_dir / "france_regions_source.geojson")
    department_region_lookup = _department_region_lookup(geo_frame)
    department_name_map = _map_department_features(department_geojson, department_region_lookup)
    quality = _quality_report(geo_frame, department_name_map, department_region_lookup)

    enriched_departments = {"type": "FeatureCollection", "features": []}
    for feature in department_geojson["features"]:
        properties = dict(feature["properties"])
        normalized = normalize_label(properties["nom"])
        mapped_name = department_name_map.get(normalized)
        excel_region = department_region_lookup.get(mapped_name) if mapped_name else None
        properties["name"] = mapped_name or properties["nom"]
        properties["excel_department"] = mapped_name
        properties["excel_region"] = excel_region
        enriched_departments["features"].append(
            {
                "type": feature["type"],
                "geometry": feature["geometry"],
                "properties": properties,
            }
        )

    display_departments = {
        "type": "FeatureCollection",
        "features": [
            feature
            for feature in enriched_departments["features"]
            if _is_metropolitan_department_code(feature["properties"]["code"])
        ],
    }

    return {
        "quality": quality,
        "geojson": {
            "departments": enriched_departments,
            "departments_display": display_departments,
            "regions_source": region_geojson,
        },
    }


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _department_region_lookup(geo_frame: pd.DataFrame) -> dict[str, str]:
    filtered = geo_frame[~geo_frame["libdpt"].isin(MAPPABLE_DEPARTMENTS_EXCLUDED)].copy()
    output: dict[str, str] = {}
    for department, rows in filtered.groupby("libdpt"):
        output[str(department)] = Counter(rows["libregionGEO"]).most_common(1)[0][0]
    return output


def _map_department_features(
    department_geojson: dict[str, Any], department_region_lookup: dict[str, str]
) -> dict[str, str]:
    excel_candidates = {normalize_label(name): name for name in department_region_lookup}
    feature_map: dict[str, str] = {}
    for feature in department_geojson["features"]:
        normalized = normalize_label(feature["properties"]["nom"])
        if normalized in excel_candidates:
            feature_map[normalized] = excel_candidates[normalized]

    aliases = {
        "COTES D ARMOR": "Côtes-d'Armor",
        "ARDECHE": "Ardèche",
        "DROME": "Drôme",
        "COTE D OR": "Côte-d'Or",
        "REUNION": "Réunion",
    }
    for normalized, excel_name in aliases.items():
        if normalized not in feature_map and excel_name in department_region_lookup:
            feature_map[normalized] = excel_name
    return feature_map


def _quality_report(
    geo_frame: pd.DataFrame,
    department_name_map: dict[str, str],
    department_region_lookup: dict[str, str],
) -> dict[str, Any]:
    dataset_departments = sorted(set(department_region_lookup))
    mapped_departments = sorted(set(department_name_map.values()))
    unmatched_departments = sorted(set(dataset_departments) - set(mapped_departments))
    mappable_region_count = len(
        set(geo_frame.loc[~geo_frame["libregionGEO"].isin(SPECIAL_GEOGRAPHIES), "libregionGEO"])
    )
    coverage = len(mapped_departments) / len(dataset_departments) if dataset_departments else 1.0
    if coverage < 0.95:
        raise ValueError(
            f"Couverture cartographique insuffisante: {coverage:.1%}. "
            f"Départements non appariés: {unmatched_departments}"
        )
    return {
        "department_coverage_ratio": coverage,
        "mapped_departments": len(mapped_departments),
        "total_mappable_departments": len(dataset_departments),
        "unmatched_departments": unmatched_departments,
        "mappable_regions_in_dataset": mappable_region_count,
    }


def _is_metropolitan_department_code(code: str) -> bool:
    token = str(code).upper()
    if token in {"2A", "2B"}:
        return True
    if token.startswith("97") or token.startswith("98"):
        return False
    return True
