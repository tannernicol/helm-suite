import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _bash_syntax_check(path: Path) -> None:
    result = subprocess.run(
        ["bash", "-n", str(path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"{path} failed bash -n: {result.stderr}"


def test_setup_script_syntax() -> None:
    _bash_syntax_check(REPO_ROOT / "setup.sh")


def test_all_scripts_syntax() -> None:
    scripts_dir = REPO_ROOT / "scripts"
    for script in sorted(scripts_dir.iterdir()):
        if script.is_file() and script.suffix != ".py":
            _bash_syntax_check(script)
