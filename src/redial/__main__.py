import sys


def main():
    try:
        from .ssh_using_tree import run
        sys.exit(run())
    except KeyboardInterrupt:
        from . import ExitStatus
        sys.exit(ExitStatus.ERROR_CTRL_C)


if __name__ == '__main__':
    main()