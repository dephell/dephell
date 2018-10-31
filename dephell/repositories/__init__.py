from .release import ReleaseRepo
from .warehouse import WareHouseRepo


__all__ = ['ReleaseRepo', 'WareHouseRepo']


def get_repo(link=None):
    if link is None:
        return WareHouseRepo()
    return ReleaseRepo(link=link)
