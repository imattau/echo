import sys
from .application import EchoApplication


def main():
    app = EchoApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
