# built-in
from textwrap import dedent

# project
from dephell.commands import GenerateTravisCommand
from dephell.config import Config


def test_make_travis_pytest(temp_path):
    (temp_path / 'pyproject.toml').write_text(dedent(
        """
        [tool.dephell.some_env]
        from = {format = "setuppy", path = "setup.py"}
        command = "pytest -x"
        """,
    ))

    config = Config()
    config.attach({'project': str(temp_path)})
    command = GenerateTravisCommand(argv=[], config=config)
    result = command()

    assert result is True
    assert (temp_path / '.travis.yml').exists()
    content = (temp_path / '.travis.yml').read_text()
    print(content)
    assert 'some_env' in content
