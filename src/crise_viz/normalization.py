from __future__ import annotations

import math
import re
import unicodedata
from typing import Any

import pandas as pd


def normalize_label(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("'", " ").replace("-", " ").replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.upper().strip()


def normalize_yes_no(value: Any) -> str:
    token = normalize_label(value)
    return "Oui" if token == "OUI" else "Non"


def ensure_numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
    return frame


def month_label(month: int) -> str:
    labels = {
        1: "Janvier",
        2: "Février",
        3: "Mars",
        4: "Avril",
        5: "Mai",
        6: "Juin",
        7: "Juillet",
        8: "Août",
        9: "Septembre",
        10: "Octobre",
        11: "Novembre",
        12: "Décembre",
    }
    return labels[int(month)]
