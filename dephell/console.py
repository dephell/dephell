import sys
from cleo import ProgressIndicator
from contextlib import contextmanager
from time import time
from cleo.outputs.stream_output import StreamOutput


# https://github.com/sdispater/cleo/blob/2c3e73a34f3008ba7f4733c9565adc8548181d54/tests/helpers/test_progress_indicator.py#L76
output = StreamOutput(sys.stdout)


# https://github.com/sdispater/poetry/blob/master/poetry/puzzle/provider.py
class Progress(ProgressIndicator):
    def __init__(self, output=output):
        super().__init__(output)
        self.format = "%message% <fg=black;options=bold>(%elapsed:2s%)</>"

    @contextmanager
    def auto(self, message='<info>Resolving dependencies</info>...'):
        with super().auto(message, message):
            yield

    def _formatter_elapsed(self):
        elapsed = time() - self.start_time
        return "{:.1f}s".format(elapsed)
