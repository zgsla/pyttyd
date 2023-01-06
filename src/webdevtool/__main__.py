import os
import sys
import asyncio

from .webapp import app
from .websocket import main as wmain


def debug():
    app.run(debug=True)


def _websocket():
    asyncio.run(wmain())


def main():
    if len(sys.argv) <= 1:
        debug()
    else:
        _websocket()
    print("1222")


if __name__ == '__main__':
    main()
