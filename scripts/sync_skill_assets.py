# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Vlad Stirbu
# License text: ../skills/paper-to-dsr/LICENSE
"""Refresh the skill's bundled package and its LPPL license."""

from pathlib import Path
import shutil


def main():
    root = Path(__file__).resolve().parents[1]
    assets = root / "skills" / "paper-to-dsr" / "assets"
    for source, destination in (("dsrm.sty", "dsrm.sty"), ("LICENSE", "LICENSE-LPPL")):
        shutil.copyfile(root / source, assets / destination)
        print(f"Updated {assets.relative_to(root) / destination}")


if __name__ == "__main__":
    main()
