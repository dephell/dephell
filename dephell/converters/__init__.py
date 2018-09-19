from .pip import PIPConverter
from .pipfile import PIPFileConverter


CONVERTERS = dict(
    pip=PIPConverter(lock=False),
    piplock=PIPConverter(lock=True),
    pipfile=PIPFileConverter(),
)
