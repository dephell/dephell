from ..config import Config, parser


class BaseCommand:
    parser = parser

    def __init__(self, argv):
        parser = self.get_parser()
        self.args = parser.parse_args(argv)
        self.config = self.get_config(self.args)

    @classmethod
    def get_parser(cls):
        return cls.parser

    @classmethod
    def get_config(cls, args):
        config = Config()
        config.attach_file(path=args.config, env=args.env)
        config.attach_cli(args)
        return config

    def validate(self):
        is_valid = self.config.validate()
        if not is_valid:
            print(self.config.format_errors())
        return is_valid
