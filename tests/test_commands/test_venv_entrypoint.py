# built-in
from pathlib import Path
from textwrap import dedent

# project
from dephell.commands import VenvEntrypointCommand
from dephell.config import Config


def test_make_script(temp_path: Path):
    dotenv = temp_path / '.env'
    dotenv.touch()
    exe = temp_path / 'flake8'
    exe.touch()

    config = Config()
    config.attach({
        'project': str(temp_path),
        'dotenv': str(temp_path),
        'vars': {'KEY': 'value'},
    })

    command = VenvEntrypointCommand(argv=[], config=config)
    script = command._make_script(command=['flake8', '--help'], executable=exe)

    expected = """
        #!/usr/bin/env bash
        export KEY="value"
        . {dotenv}
        cd {path}
        {exe} --help $@
    """
    expected = expected.format(
        dotenv=str(dotenv.absolute()),
        path=str(temp_path.absolute()),
        exe=str(exe.absolute()),
    )
    assert script.strip() == dedent(expected).strip()
