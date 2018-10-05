from .pip import PIPConverter
from .pipfile import PIPFileConverter
from .pipfilelock import PIPFileLockConverter


CONVERTERS = dict(
    pip=PIPConverter(lock=False),
    piplock=PIPConverter(lock=True),
    pipfile=PIPFileConverter(),
    pipfilelock=PIPFileLockConverter(),
)
