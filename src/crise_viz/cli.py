from __future__ import annotations

import argparse
from pathlib import Path

from .aggregation import build_payload
from .config import BuildConfig, DEFAULT_OUTPUT, DEFAULT_TITLE, DEFAULT_VARIANT
from .geo import load_geo_assets
from .ingestion import load_workbook_frames
from .rendering import render_dashboard


def build_command(config: BuildConfig) -> Path:
    config.ensure_parent()
    accord, geo = load_workbook_frames(config.input_path)
    geo_assets = load_geo_assets(geo, Path(__file__).resolve().parent / "assets" / "geo")
    payload = build_payload(accord, geo, geo_assets, config.title, config.input_path.name)
    html = render_dashboard(config, payload)
    config.output_path.write_text(html, encoding="utf-8")
    return config.output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="crise_viz", description="Build a standalone HTML crisis dashboard.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="Generate the standalone HTML dashboard.")
    build.add_argument("--input", required=True, type=Path, help="Path to the Excel workbook.")
    build.add_argument("--output", type=Path, default=Path(DEFAULT_OUTPUT), help="Output HTML path.")
    build.add_argument("--title", default=DEFAULT_TITLE, help="Dashboard title.")
    build.add_argument("--default-variant", default=DEFAULT_VARIANT, help="Default visual variant.")
    build.add_argument("--verbose", action="store_true", help="Print basic progress information.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command != "build":
        raise SystemExit(f"Unknown command: {args.command}")
    config = BuildConfig(
        input_path=args.input,
        output_path=args.output,
        title=args.title,
        default_variant=args.default_variant,
        verbose=args.verbose,
    )
    output_path = build_command(config)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
