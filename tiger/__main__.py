import sys

from tiger.dl import main as run


def _no_traceback_excepthook(exc_type, exc_val, traceback):
    pass

def main():
    try:
        run()
    except KeyboardInterrupt:
        # whatever cleanup code you need here...
        if sys.excepthook is sys.__excepthook__:
            sys.excepthook = _no_traceback_excepthook
        raise

if __name__ == "__main__":
    main()