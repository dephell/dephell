from .warehouse import WareHouseRepo


__all__ = ['WareHouseRepo', 'get_repo']


def get_repo(url=None):
    if url is None:
        return WareHouseRepo()
    raise NotImplementedError
