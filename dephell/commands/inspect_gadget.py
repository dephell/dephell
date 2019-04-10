# built-in
from argparse import ArgumentParser

# app
from ..config import builders
from .base import BaseCommand


# Source: https://www.asciiart.eu/cartoons/inspector-gadget
# Author: https://en.wikipedia.org/wiki/Joan_Stark
GADGET = r"""
           ___
     _..--"\  `|`""--.._
  .-'       \  |        `'-.
 /           \_|___...----'`\
|__,,..--""``(_)--..__      |
'\     _.--'`.I._     ''--..'
  `''"`,#JGS/_|_\###,---'`
    ,#'  _.:`___`:-._ '#,
   #'  ,~'-;(oIo);-'~, '#
   #   `~-(  |    )=~`  #
   #       | |_  |      #
   #       ; ._. ;      #
   #  _..-;|\ - /|;-._  #
   #-'   /_ \\_// _\  '-#
 /`#    ; /__\-'__\;    #`\
;  #\.--|  |O  O   |'-./#  ;
|__#/   \ _;O__O___/   \#__|
 | #\    [I_[_]__I]    /# |
 \_(#   /  |O  O   \   #)_/
       /   |        \
      /    |         \
     /    /\          \
    /     | `\         ;
   ;      \   '.       |
    \-._.__\     \_..-'/
     '.\  \-.._.-/  /'`
        \_.\    /._/
         \_.;  ;._/
       .-'-./  \.-'-.
      (___.'    '.___)
"""


class InspectGadgetCommand(BaseCommand):
    """Show Inspector Gadget.

    This command shouldn't be documented.
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell inspect config',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        return parser

    def __call__(self) -> bool:
        print(GADGET)
        return True
