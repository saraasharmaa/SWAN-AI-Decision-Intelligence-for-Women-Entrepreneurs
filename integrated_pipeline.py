"""
Master pipeline for the Women's Economic Empowerment project.

Runs:
    main.py                  -> Phases 1-4
    phase_5_prescriptive.py  -> Phase 5
    phase_6_operational.py   -> Phase 6

Usage:
    python integrated_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_script(filename):
    script = ROOT / filename

    if not script.exists():
        raise FileNotFoundError(f"Missing required file: {script}")

    print("\n" + "=" * 65)
    print(f"RUNNING: {filename}")
    print("=" * 65)

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
    )

    if result.returncode != 0:
        print(f"\nERROR: {filename} failed.")
        raise SystemExit(result.returncode)

    print(f"\n✓ {filename} completed successfully.")


def main():
    print("\n" + "=" * 65)
    print("WOMEN'S ECONOMIC EMPOWERMENT")
    print("FULL INTEGRATED PIPELINE")
    print("=" * 65)

    run_script("main.py")
    run_script("phase_5_prescriptive.py")
    run_script("phase_6_operational.py")

    print("\n" + "=" * 65)
    print("FULL PIPELINE COMPLETE")
    print("=" * 65)

    print("\nAll results are saved in:")
    print(ROOT / "outputs")


if __name__ == "__main__":
    main()
