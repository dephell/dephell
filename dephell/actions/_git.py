# built-in
import subprocess
from logging import getLogger
from pathlib import Path
from typing import Iterable, Tuple

logger = getLogger('dephell.actions.git')


def _run(command, project: Path) -> Tuple[bool, str]:
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(project),
    )
    stdout = result.stdout.decode().strip()
    if result.returncode != 0:
        stderr = result.stderr.decode().strip()
        if stderr:
            logger.debug(stderr)
        if stdout:
            logger.debug(stdout)
        return False, stderr
    return True, stdout


def git_commit(message: str, paths: Iterable[Path], project: Path) -> bool:
    for path in paths:
        ok = _run(['git', 'add', '--update', str(path)], project=project)
        if not ok:
            return False
    result, _ = _run(['git', 'commit', '-m', message], project=project)
    return result


def git_tag(name: str, project: Path) -> bool:
    result, _ = _run(['git', 'tag', name], project=project)
    return result
