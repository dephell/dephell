# built-in
import shutil
import socket
from pathlib import Path

# external
import pytest
from aioresponses import aioresponses


true_socket = socket.socket
true_connect = socket.socket.connect


class SocketBlockedError(RuntimeError):
    pass


class SocketConnectBlockedError(RuntimeError):
    pass


def fake_socket(*args, **kwargs):
    raise SocketBlockedError('use @pytest.mark.allow_hosts to unblock some hosts')


def pytest_addoption(parser):
    group = parser.getgroup('socket')
    group.addoption(
        '--no-network',
        action='store_true',
        help='skip tests with network interactions',
    )


@pytest.fixture(autouse=True)
def no_network(request):
    _setup(request)
    yield
    socket.socket.connect = true_connect
    socket.socket = true_socket


def _setup(request):
    """
    + socket disabled by default
    + @pytest.mark.allow_hosts() -- allow all connections
    + @pytest.mark.allow_hosts(['pypi,org']) -- allow pypi.org connections
    """
    marker = request.node.get_closest_marker('allow_hosts')

    # block network if no marker
    if not marker:
        socket.socket = fake_socket
        return

    # skip marked tests if no network connection
    if request.config.getoption('--no-network'):
        pytest.skip('test requires network connection')

    # if test marked with allow_hosts and hosts specified
    # allow only these hosts. Otherwise allow all hosts
    if marker.args:
        hosts = marker.args[0]
        socket_allow_hosts(hosts)
        return


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


@pytest.fixture
def requirements_dir() -> Path:
    """ Return the absolute Path to 'tests/requirements' """
    return Path(__file__).parent / Path('requirements')


@pytest.fixture
def fixtures_path() -> Path:
    return Path(__file__).parent / Path('fixtures')


class PatchedAIOResponses(aioresponses):
    async def _request_mock(self, orig_self, method, url, *args, **kwargs):
        # add `orig_self` (original `ClientSession`) into `args`
        return await super()._request_mock(orig_self, method, url, orig_self, *args, **kwargs)


@pytest.fixture
def asyncio_mock() -> PatchedAIOResponses:
    with PatchedAIOResponses() as mock:
        yield mock
