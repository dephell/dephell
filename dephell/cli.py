from cleo import Application
from .commands import ConvertCommand


def run():
    application = Application()
    application.add(ConvertCommand())
    application.run()


if __name__ == '__main__':
    run()
