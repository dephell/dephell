# built-in
import subprocess
from logging import getLogger
from pathlib import Path
from typing import Iterable


logger = getLogger('dephell.actions.git')


def _run(command, project: Path) -> bool:
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(project),
    )
    if result.returncode != 0:
        stderr = result.stderr.decode().strip()
        if stderr:
            logger.debug(stderr)
        stdout = result.stdout.decode().strip()
        if stdout:
            logger.debug(stdout)
        return False
    return True


def git_commit(message: str, paths: Iterable[Path], project: Path) -> bool:
    for path in paths:
        ok = _run(['git', 'add', '--update', str(path)], project=project)
        if not ok:
            return False
    return _run(['git', 'commit', '-m', message], project=project)


def git_tag(name: str, project: Path) -> bool:
    return _run(['git', 'tag', name], project=project)
