
class GitSpecifier:
    def __contains__(self, release):
        # check that this is GitRelease without imports
        return hasattr(release, 'commit')

    def __iadd__(self, other):
        if hasattr(other, '_attach'):
            attached = other._attach(self)
            if attached:
                return other
        return NotImplemented
