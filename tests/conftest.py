# built-in
import shutil
import socket
from pathlib import Path

# external
import pytest


true_socket = socket.socket
true_connect = socket.socket.connect


class SocketBlockedError(RuntimeError):
    pass


class SocketConnectBlockedError(RuntimeError):
    pass


@pytest.fixture()
def socket_disabled():
    disable_socket()
    yield
    socket.socket = true_socket


def pytest_runtest_setup(item):
    """
    + socket disabled by default
    + @pytest.mark.allow_hosts() -- allow all connections
    + @pytest.mark.allow_hosts(['pypi,org']) -- allow pypi.org connections
    """
    marker = item.get_closest_marker('allow_hosts')
    hosts = None
    # if test marked with allow_hosts and hosts specified
    if marker and marker.args:
        hosts = marker.args[0]

    if marker:  # if test marked with allow_hosts
        if hosts is not None:  # if hosts are specified, allow only them
            socket_allow_hosts(hosts)
    else:  # if test not marked, disable socket at all
        disable_socket()


def pytest_runtest_teardown():
    socket.socket.connect = true_connect
    socket.socket = true_socket


def disable_socket():
    def guarded(*args, **kwargs):
        raise SocketBlockedError('use @pytest.mark.allow_hosts to unblock some hosts')

    socket.socket = guarded


def socket_allow_hosts(allowed=None):
    def guarded_connect(inst, *args):
        host = args[0][0]
        if host and host in allowed:
            return true_connect(inst, *args)
        raise SocketConnectBlockedError(allowed, host)

    socket.socket.connect = guarded_connect


@pytest.fixture()
def temp_path(tmp_path: Path):
    for path in tmp_path.iterdir():
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(str(path))
    yield tmp_path


@pytest.fixture()
def temp_cache(temp_path):
    from dephell.config import config

    config.attach({'cache': {'path': str(temp_path)}})
