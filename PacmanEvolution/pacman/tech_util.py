"""
This file contains code that is only very weakly related to Pacman.
Most of the code adds some basic feature to the Python language
which is then used somewhere in the Pacman code.
"""

import contextlib
import signal
import sys
import time


# noinspection PyPep8Naming
class classproperty(object):
    """
    A decorator that converts a method into a class property.
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, _, owner_cls):
        return self.fget(owner_cls)


def map_2d(f, l):
    """
    2D version of Python's `map`.
    """
    return [[f(e) for e in r] for r in l]


def flatten_2d(l):
    """
    Flatten a 1D or fully 2D list into a 1D list.
    """
    if l and isinstance(l[0], list):
        return sum(l, [])
    else:
        return l


class timeit(object):
    """
    A context manager that times the execution of its body.
    """

    def __enter__(self):
        self.t = time.clock()
        return self

    def __exit__(self, typ, value, traceback):
        self.t = time.clock() - self.t


class TimeoutException(Exception):
    """
    An exception meant to be thrown when a timeout occurs.
    """
    pass


@contextlib.contextmanager
def windows_timeout(seconds):
    """
    A context manager that throws a TimeoutException when its body
    takes longer to execute than the given amount of seconds.
    Does not terminate the function.
    """
    t0 = time.time()
    yield
    if time.time() - t0 > seconds:
        raise TimeoutException

@contextlib.contextmanager
def linux_timeout(seconds):
    """
    A context manager that throws a TimeoutException when its body
    takes longer to execute than the given amount of seconds.
    """

    def signal_handler(*_):
        raise TimeoutException()

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

if hasattr(signal, 'SIGALRM'):
    timeout = linux_timeout
else:
    timeout = windows_timeout


# noinspection PyUnresolvedReferences
def _find_getch():
    """
    Determine which function to use to get keyboard input,
    depending on operating system.
    """
    try:
        # POSIX system. Create and return a getch that manipulates the tty.
        import termios
        import tty

        def _getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ord(ch)

        return _getch
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return lambda: ord(msvcrt.getch())


# set the keyboard input function
getch = _find_getch()


def getsym():
    """
    Get keyboard input.
    """
    c = getch()
    if c == 3:  # ctrl+c
        raise KeyboardInterrupt
    if c == 27:  # arrow key
        c = getch()
        if c == 91:  # arrow key
            c = getch()
            return {65: 'Up',
                    66: 'Down',
                    67: 'Right',
                    68: 'Left'}[c]
    return None
