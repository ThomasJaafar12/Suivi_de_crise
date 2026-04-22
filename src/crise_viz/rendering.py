from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .aggregation import DashboardPayload
from .config import DEFAULT_TITLE


def render_dashboard(config: object, payload: DashboardPayload) -> str:
    env = Environment(
        loader=FileSystemLoader(str(Path(__file__).resolve().parent / "templates")),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("dashboard.html.j2")
    return template.render(
        page_title=getattr(config, "title", DEFAULT_TITLE) or DEFAULT_TITLE,
        payload_json=json.dumps(payload.payload, ensure_ascii=False, separators=(",", ":")),
    )
