#!/usr/bin/env python3
"""Lay out wheels as a PEP 503 simple index: one folder per project + index.html."""
from __future__ import annotations

import html
import shutil
from collections import defaultdict
from pathlib import Path

from packaging.utils import canonicalize_name, parse_wheel_filename

ROOT = Path(__file__).resolve().parent / "wheels_linux_py310_torch2.6.0_cu126"


def move_root_wheels(wheels_dir: Path) -> None:
    for whl in sorted(wheels_dir.glob("*.whl")):
        if whl.parent != wheels_dir:
            continue
        proj, _v, _b, _t = parse_wheel_filename(whl.name)
        dest_dir = wheels_dir / canonicalize_name(proj)
        dest_dir.mkdir(parents=True, exist_ok=True)
        target = dest_dir / whl.name
        if whl.resolve() == target.resolve():
            continue
        if target.exists():
            raise FileExistsError(target)
        shutil.move(str(whl), str(target))


def package_dirs(wheels_dir: Path) -> dict[str, list[Path]]:
    by_name: dict[str, list[Path]] = defaultdict(list)
    for sub in sorted(wheels_dir.iterdir()):
        if not sub.is_dir():
            continue
        for whl in sorted(sub.glob("*.whl")):
            proj, _v, _b, _t = parse_wheel_filename(whl.name)
            key = canonicalize_name(proj)
            if key != sub.name:
                raise ValueError(
                    f"Wheel {whl.name} belongs under {key}/ but is in {sub.name}/"
                )
            by_name[key].append(whl)
    return by_name


def write_package_index(pkg_dir: Path, wheels: list[Path]) -> None:
    lines = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head><meta charset=\"utf-8\"/><title>Links for "
        + html.escape(pkg_dir.name)
        + "</title></head>",
        "<body>",
        "<h1>Links for "
        + html.escape(pkg_dir.name)
        + "</h1>",
    ]
    for whl in sorted(wheels, key=lambda p: p.name):
        name = whl.name
        lines.append(
            f'<a href="{html.escape(name)}">{html.escape(name)}</a><br/>'
        )
    lines.append("</body></html>")
    (pkg_dir / "index.html").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_root_index(wheels_dir: Path, package_names: list[str]) -> None:
    lines = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head><meta charset=\"utf-8\"/><title>Simple index</title></head>",
        "<body>",
        "<h1>Package index</h1>",
    ]
    for name in sorted(package_names):
        lines.append(
            f'<a href="{html.escape(name + "/")}">{html.escape(name)}</a><br/>'
        )
    lines.append("</body></html>")
    (wheels_dir / "index.html").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    wheels_dir = ROOT
    if not wheels_dir.is_dir():
        raise SystemExit(f"Missing wheels directory: {wheels_dir}")

    move_root_wheels(wheels_dir)
    by_name = package_dirs(wheels_dir)
    if not by_name:
        raise SystemExit(f"No package subfolders with .whl under {wheels_dir}")

    for canon, paths in by_name.items():
        write_package_index(wheels_dir / canon, paths)

    write_root_index(wheels_dir, list(by_name.keys()))
    print(f"Indexed {len(by_name)} packages under {wheels_dir}")


if __name__ == "__main__":
    main()
