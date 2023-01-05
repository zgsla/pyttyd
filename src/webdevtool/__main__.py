import os


def debug():
    from .webapp import app
    app.run(debug=True)


def main():
    debug()
    print("1222")


if __name__ == '__main__':
    main()
