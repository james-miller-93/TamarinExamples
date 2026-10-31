"""Run the teaching models; fail closed on incomplete or unexpected results."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "Basic": {"HonestRun": "verified", "MITM": "falsified"},
    "EasyFixMITM": {
        "HonestRun": "verified",
        "OriginalMITM": "falsified",
        "FixedMITM": "verified",
        "MITMAlternate": "verified",
    },
}


def validate_output(output: str, expected: dict[str, str]) -> None:
    """Reject warnings and missing, duplicate, incomplete, or unexpected results.

    Raises:
        ValueError: If the output does not match the complete expected lemma set.
    """
    if re.search(r"\bwarning\b|wellformedness check.*failed", output, re.IGNORECASE):
        raise ValueError("Tamarin reported a warning; inspect the saved log")
    matches = re.findall(
        r"^\s*(\w+)\s+\((?:all-traces|exists-trace)\):\s*(\w+)", output, re.MULTILINE
    )
    if len(matches) != len(expected) or dict(matches) != expected:
        raise ValueError(f"unexpected lemma results: {matches!r}; expected {expected!r}")


def run_model(prover: str, name: str, expected: dict[str, str], log_dir: Path) -> None:
    """Run a model with a time limit, retain output, and validate the results.

    Raises:
        RuntimeError: If the prover times out or exits unsuccessfully.
        ValueError: If the returned lemma results differ from expectations.
    """
    log = log_dir / f"{name}.log"
    command = [prover, "--prove", str(ROOT / "Diffie-Hellman" / f"{name}.spthy")]
    with log.open("w") as output:
        try:
            result = subprocess.run(
                command, stdout=output, stderr=subprocess.STDOUT, timeout=600, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"{name}: timed out after 600s; see {log}") from exc
    if result.returncode != 0:
        raise RuntimeError(f"{name}: prover exited {result.returncode}; see {log}")
    validate_output(log.read_text(), expected)


def main() -> int:
    """Check tool availability/version, then run all model checks."""
    prover = shutil.which("tamarin-prover")
    if prover is None:
        print(
            "Tamarin is missing. Install the official 1.12.0 toolchain; see README.md.",
            file=sys.stderr,
        )
        return 2
    try:
        version = subprocess.run(
            [prover, "--version"], capture_output=True, text=True, timeout=30, check=True
        ).stdout
        if not re.search(r"\b1\.12\.0\b", version):
            raise ValueError(f"Expected Tamarin 1.12.0; got {version.strip()!r}")
        log_dir = ROOT / "results"
        log_dir.mkdir(exist_ok=True)
        (log_dir / "version.txt").write_text(version)
        for name, expected in EXPECTED.items():
            run_model(prover, name, expected, log_dir)
            print(f"{name}: all {len(expected)} expected results confirmed")
    except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        print(f"Model check failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
