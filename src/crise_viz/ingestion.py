from __future__ import annotations

from pathlib import Path

import pandas as pd

from .normalization import ensure_numeric, normalize_yes_no


ACCORD_COLUMNS = [
    "per",
    "libregion",
    "Categ",
    "Sect",
    "nace88",
    "lib88",
    "ape",
    "libape",
    "TopPlan",
    "CodeCNRJ",
    "NbAccord",
    "MttAccord",
    "DureeAccord",
    "PerAnnee",
    "PerMois",
]
ACCORD_GEO_COLUMNS = [
    "per",
    "libregionGEO",
    "libdpt",
    "Categ",
    "Sect",
    "nace88",
    "lib88",
    "TopPlan",
    "CodeCNRJ",
    "NbAccord",
    "MttAccord",
    "DureeAccord",
    "PerAnnee",
    "PerMois",
]


def load_workbook_frames(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    accord = pd.read_excel(path, sheet_name="Accord", usecols=ACCORD_COLUMNS, engine="openpyxl")
    geo = pd.read_excel(path, sheet_name="AccordGeo", usecols=ACCORD_GEO_COLUMNS, engine="openpyxl")
    return prepare_accord(accord), prepare_geo(geo)


def prepare_accord(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["PerAnnee"] = data["PerAnnee"].astype(int)
    data["PerMois"] = data["PerMois"].astype(int)
    data["TopPlan"] = data["TopPlan"].map(normalize_yes_no)
    data["CodeCNRJ"] = data["CodeCNRJ"].map(normalize_yes_no)
    data["nace88"] = data["nace88"].fillna("").astype(str)
    data["lib88"] = data["lib88"].fillna("").astype(str)
    data["ape"] = data["ape"].fillna("").astype(str)
    data["libape"] = data["libape"].fillna("").astype(str)
    data["libregion"] = data["libregion"].fillna("").astype(str)
    data["Categ"] = data["Categ"].fillna("").astype(str)
    data["Sect"] = data["Sect"].fillna("").astype(str)
    ensure_numeric(data, ["NbAccord", "MttAccord", "DureeAccord"])
    return data


def prepare_geo(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["PerAnnee"] = data["PerAnnee"].astype(int)
    data["PerMois"] = data["PerMois"].astype(int)
    data["TopPlan"] = data["TopPlan"].map(normalize_yes_no)
    data["CodeCNRJ"] = data["CodeCNRJ"].map(normalize_yes_no)
    data["nace88"] = data["nace88"].fillna("").astype(str)
    data["lib88"] = data["lib88"].fillna("").astype(str)
    data["libregionGEO"] = data["libregionGEO"].fillna("").astype(str)
    data["libdpt"] = data["libdpt"].fillna("").astype(str)
    data["Categ"] = data["Categ"].fillna("").astype(str)
    data["Sect"] = data["Sect"].fillna("").astype(str)
    ensure_numeric(data, ["NbAccord", "MttAccord", "DureeAccord"])
    return data
