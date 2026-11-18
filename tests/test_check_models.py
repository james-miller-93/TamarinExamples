"""Test result validation without claiming that a prover was run."""

import subprocess
from pathlib import Path

import pytest

from check_models import main, run_model, validate_output


def test_accepts_expected_proof_and_attack() -> None:
    validate_output(
        "HonestRun (exists-trace): verified (6 steps)\n"
        "MITM (all-traces): falsified - found trace (7 steps)\n",
        {"HonestRun": "verified", "MITM": "falsified"},
    )


@pytest.mark.parametrize(
    "output",
    [
        "",
        "MITM (all-traces): verified (2 steps)",
        "MITM (all-traces): analysis incomplete (2 steps)",
        "MITM (all-traces): falsified\nWARNING: 1 wellformedness check failed!",
        "MITM (all-traces): falsified\nMITM (all-traces): falsified",
        "MITM (all-traces): falsified\nExtra (all-traces): verified",
    ],
)
def test_rejects_unsafe_or_incomplete_output(output: str) -> None:
    with pytest.raises(ValueError):
        validate_output(output, {"MITM": "falsified"})


def test_prover_failure_is_not_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=[], returncode=1)

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(RuntimeError, match="prover exited 1"):
        run_model("fake-prover", "Basic", {}, tmp_path)


def test_prover_timeout_is_not_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired("fake-prover", 600)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(RuntimeError, match="timed out"):
        run_model("fake-prover", "Basic", {}, tmp_path)


def test_missing_prover_is_actionable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("check_models.shutil.which", lambda name: None)
    assert main() == 2
    assert "Tamarin is missing" in capsys.readouterr().err


def test_wrong_version_is_rejected(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("check_models.shutil.which", lambda name: "fake-prover")

    def old_version(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="tamarin-prover 1.11.0")

    monkeypatch.setattr(subprocess, "run", old_version)
    assert main() == 1
    assert "Expected Tamarin 1.12.0" in capsys.readouterr().err


def test_version_command_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("check_models.shutil.which", lambda name: "fake-prover")

    def failed_version(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(1, "fake-prover")

    monkeypatch.setattr(subprocess, "run", failed_version)
    assert main() == 1
    assert "Model check failed" in capsys.readouterr().err
