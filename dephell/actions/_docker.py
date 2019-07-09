from pathlib import Path
from ..controllers import DockerContainer


def get_docker_container(config):
    return DockerContainer(
        path=Path(config['project']),
        env=config.env,
        repository=config['docker']['repo'],
        tag=config['docker']['tag'],
    )
