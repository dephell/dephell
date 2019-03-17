# built-in
from sys import argv

# app
from .cli import main


exit(main(argv[1:]))
