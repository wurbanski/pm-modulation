import sys
from blocks import *
from signals import *
from system import *
from pprint import pprint


__author__ = 'Wojciech Urbański'
config = None


def menu(prompt, options):
    def menu_screen():
        while True:
            print_options(options)
            option = selection(prompt)
            options[option]()

    return menu_screen


def rename(newname):
    def decorator(f):
        f.__name__ = newname
        return f

    return decorator


def selection(title=""):
    print(title)
    choice = None
    while choice is None:
        try:
            choice = int(input('>>>'))
        except ValueError:
            print("Not a valid option.")
    return choice


def print_options(options):
    for i, option in enumerate(options):
        print("%2d) %s" % (i, option.__name__))


@rename("Configure system")
def create_system():
    SystemConfiguration(time=1, sample_rate=200)


@rename("Quit")
def quit_app():
    raise SystemExit


def main():
    options = [quit_app, create_system]
    menu("Main Menu", options)()


if __name__ == '__main__':
    sys.exit(main())