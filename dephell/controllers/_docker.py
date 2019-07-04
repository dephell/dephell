from logging import getLogger
from pathlib import Path
from typing import Optional

import attr
import docker
from dephell_venvs import VEnvs

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

        # create container
        mount = docker.types.Mount(
            target='/opt',
            source=str(self.path),
            type='bind',
        )
        self.client.containers.create(
            image=image,
            command='/bin/sh',
            name=self.container_name,
            mounts=[mount],
            network=self.network_name,
        )

    def remove(self) -> None:
        self.container.remove(force=True)
        for container in self.network.containers:
            self.network.disconnect(container, force=True)
        self.network.remove()

    def exists(self) -> bool:
        if 'container' in self.__dict__:
            del self.__dict__['container']
        return self.container is not None

    def activate(self) -> None:
        self.container.start()

    def deactivate(self) -> None:
        self.container.stop()
