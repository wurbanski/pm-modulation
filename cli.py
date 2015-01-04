__author__ = 'Wojciech Urbański'


def menu(prompt, options):
    def menu_screen():
        while True:
            print_options(options)
            option = selection(prompt)
            options[option]()

    return menu_screen


def back():
    return 0


def rename(newname):
    def decorator(f):
        f.__name__ = newname
        return f

    return decorator


def selection(prompt=""):
    print(prompt)
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