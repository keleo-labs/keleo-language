"""Make the validators run on a stock interpreter, without touching it.

The validators need `jsonschema`, and the obvious instruction — `pip install
jsonschema` — fails on most current machines. Debian, Ubuntu, Fedora and
Homebrew all mark their Python externally managed (PEP 668), so pip refuses
with `externally-managed-environment`. The usual escapes (`--break-system-packages`,
`--user`, `sudo pip`) work by damaging the interpreter other software depends on.

So each validator calls `ensure_dependencies()` before importing jsonschema. If
the package is missing, this builds a virtualenv keyed to the tool, installs
into it, and re-execs. Callers keep running `python3 validate/validate-practice.py
<args>` with no changed invocation and no interpreter path to remember.

The venv lives outside the repository, so a clean checkout does not destroy it
and a redeploy does not rebuild it.
"""

import os
import subprocess
import sys
from pathlib import Path

TOOL_NAME = "keleo-validate"
REQUIREMENTS = ["jsonschema"]
# Set by the bootstrap before re-exec, so a child that still cannot import the
# package reports the real problem instead of re-execing forever.
_REENTRY_FLAG = "KELEO_VALIDATE_BOOTSTRAPPED"


def venv_dir():
    """Where this tool's virtualenv lives. Honours XDG_DATA_HOME where set."""
    data_home = os.environ.get("XDG_DATA_HOME")
    base = Path(data_home) if data_home else Path.home() / ".local" / "share"
    return base / "agent-skills" / TOOL_NAME / "venv"


def venv_python(venv=None):
    """Path to the venv's interpreter, on POSIX and Windows."""
    venv = venv or venv_dir()
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def running_inside(venv=None):
    """Is the current interpreter the one inside this venv?

    Compares sys.prefix, NOT sys.executable. venv/bin/python is a symlink back
    to the base interpreter, so resolving sys.executable makes an outside call
    compare equal to an inside one — the bootstrap then never fires and the
    validator reports a misleading "missing from the virtualenv" error.
    sys.prefix is the value venv actually redirects.
    """
    venv = venv or venv_dir()
    try:
        return Path(sys.prefix).resolve() == venv.resolve()
    except OSError:
        return False


def _missing():
    """Requirements that cannot be imported in the current interpreter."""
    missing = []
    for requirement in REQUIREMENTS:
        module = requirement.split("[")[0].replace("-", "_")
        try:
            __import__(module)
        except ImportError:
            missing.append(requirement)
    return missing


def _venv_satisfies(python):
    """Can the venv's interpreter import everything we need?"""
    probe = "import " + ", ".join(r.split("[")[0].replace("-", "_") for r in REQUIREMENTS)
    try:
        return subprocess.run(
            [str(python), "-c", probe], capture_output=True, timeout=30
        ).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _reexec(python):
    """Hand the current command over to the venv's interpreter."""
    env = dict(os.environ, **{_REENTRY_FLAG: "1"})
    os.execve(str(python), [str(python), *sys.argv], env)


def ensure_dependencies():
    """Import-guard replacement: guarantee the requirements are importable.

    Returns normally when they already are. Otherwise creates the venv, installs
    into it, and re-execs the current command there — so this call does not
    return in that case.
    """
    missing = _missing()
    if not missing:
        return

    venv = venv_dir()

    # Already re-execed and still short: installing did not take. Say so plainly
    # rather than looping.
    if os.environ.get(_REENTRY_FLAG) or running_inside(venv):
        print(
            f"ERROR: {', '.join(missing)} still missing from {venv} after bootstrap.\n"
            f"Remove the directory and retry, or install manually:\n"
            f"  {venv_python(venv)} -m pip install {' '.join(REQUIREMENTS)}",
            file=sys.stderr,
        )
        sys.exit(2)

    python = venv_python(venv)

    # A venv that already satisfies the requirements just needs re-execing into.
    # Without this check, every call from an interpreter lacking the package
    # pays for a pip subprocess before getting to the work.
    if python.exists() and _venv_satisfies(python):
        _reexec(python)

    if not python.exists():
        print(f"Creating virtualenv for {TOOL_NAME} at {venv} ...", file=sys.stderr)
        try:
            venv.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            print(
                f"ERROR: could not create a virtualenv at {venv}.\n{exc.stderr or exc}\n"
                "On Debian and Ubuntu the venv module ships separately — "
                "install it with: sudo apt install python3-venv",
                file=sys.stderr,
            )
            sys.exit(2)
        except OSError as exc:
            print(f"ERROR: could not create a virtualenv at {venv}: {exc}", file=sys.stderr)
            sys.exit(2)

    print(f"Installing {', '.join(missing)} into {venv} ...", file=sys.stderr)
    try:
        subprocess.run(
            [str(python), "-m", "pip", "install", "-q", *REQUIREMENTS],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(
            f"ERROR: could not install {', '.join(REQUIREMENTS)} into {venv}.\n"
            f"{exc.stderr or exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    _reexec(python)
