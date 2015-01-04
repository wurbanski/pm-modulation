import sys

from cli import menu, rename
from system import *


__author__ = 'Wojciech Urbański'
config = None


@rename("Configure system")
def create_system():
    print("Creating system configuration with parameters time = %d, sample_rate = %d" % (1, 200))
    SystemConfiguration(time=1, sample_rate=200)


@rename("Quit")
def quit_app():
    raise SystemExit


def main():
    options = [quit_app, create_system]
    menu("Main Menu", options)()


if __name__ == '__main__':
    sys.exit(main())