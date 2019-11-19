# built-in
from pathlib import Path

# app
from ..controllers import DockerContainer


def get_docker_container(config) -> DockerContainer:
    container = DockerContainer(
        path=Path(config['project']),
        env=config.env,
        repository=config['docker']['repo'],
        tag=config['docker']['tag'],
    )
    container_name = config['docker'].get('container')
    if container_name:
        container.container_name = container_name
    return container
