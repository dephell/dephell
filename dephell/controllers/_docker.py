# built-in
from logging import getLogger
from pathlib import Path
from typing import List, Optional

# external
import attr
import docker
import dockerpty
import requests
from dephell_venvs import VEnvs

# app
from ..cached_property import cached_property


DOCKER_PREFIX = 'dephell-'


class DockerContainers:
    @cached_property
    def client(self) -> docker.DockerClient:
        return docker.from_env()

    def list(self):
        containers = self.client.containers.list(all=True)
        for container in containers:
            if container.name.startswith(DOCKER_PREFIX):
                yield container


@attr.s()
class DockerContainer:
    path = attr.ib(type=Path)
    env = attr.ib(type=str)

    repository = attr.ib(type=str, default='python')
    tag = attr.ib(type=str, default='latest')

    logger = getLogger('dephell.controllers.docker')

    # properties

    @cached_property
    def container_name(self) -> str:
        return '{prefix}{name}-{digest}-{env}'.format(
            prefix=DOCKER_PREFIX,
            name=self.path.name,
            digest=VEnvs._encode(str(self.path)),
            env=self.env,
        )

    @cached_property
    def network_name(self) -> str:
        return self.container_name + '-network'

    @property
    def image_name(self) -> str:
        return '{}:{}'.format(self.repository, self.tag)

    @property
    def tags(self):
        repository = self.repository
        if '/' not in repository:
            repository = 'library/' + repository
        url = 'https://hub.docker.com/v2/repositories/{}/tags/'.format(repository)
        tags = dict()
        while url is not None:
            response = requests.get(url)
            response.raise_for_status()
            content = response.json()
            url = content['next']
            for tag in content['results']:
                tags[tag['name']] = tag['last_updated'] or ''
        return sorted(tags, key=lambda tag: tags[tag], reverse=True)

    @cached_property
    def client(self) -> docker.DockerClient:
        return docker.from_env()

    @cached_property
    def container(self) -> Optional[docker.models.containers.Container]:
        try:
            return self.client.containers.get(self.container_name)
        except docker.errors.NotFound:
            return None

    @cached_property
    def network(self) -> Optional[docker.models.networks.Network]:
        return self.client.networks.get(self.network_name)

    # public methods

    def create(self, *, pull=True) -> None:
        if 'container' in self.__dict__:
            del self.__dict__['container']
        # get image
        try:
            image = self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            if not pull:
                raise
            self.logger.info('image not found, pulling...', extra=dict(
                repository=self.repository,
                tag=self.tag,
            ))
            image = self.client.images.pull(repository=self.repository, tag=self.tag)
            self.logger.info('pulled')

        # create network
        self.client.networks.create(self.network_name, check_duplicate=True)

        # mount the project
        # (but do not mount if it's obviously not a project)
        mounts = []
        if self.path not in (Path.home(), Path('/')):
            mounts.append(docker.types.Mount(
                target='/opt/project',
                source=str(self.path),
                type='bind',
            ))

        # create container
        self.client.containers.create(
            image=image,
            command='/bin/sh -c "bash || sh"',
            name=self.container_name,
            mounts=mounts,
            network=self.network_name,
            tty=True,
            stdin_open=True,
            working_dir='/opt/project',
        )

    def stop(self) -> None:
        self.container.stop()

    def remove(self) -> None:
        self.stop()
        self.container.remove(force=True)
        for container in self.network.containers:
            self.network.disconnect(container, force=True)
        self.network.remove()

    def exists(self) -> bool:
        if 'container' in self.__dict__:
            del self.__dict__['container']
        return self.container is not None

    def activate(self) -> None:
        return self.run(['sh', '-c', 'zsh || bash || sh'])

    def run(self, command: List[str]) -> None:
        self.container.start()
        dockerpty.exec_command(
            client=self.client.api,
            container=self.container.id,
            command=command,
        )
