import os


__version__ = '1.1.1'

__basepath__ = os.path.dirname(os.path.abspath(__file__))

__static__ = os.path.join(__basepath__, 'static')
__template__ = os.path.join(__basepath__, 'template')

__html__ = '''
    <!DOCTYPE html>
        <html translate="no">
        <head>
            <title>Pyttyd Terminal</title>
            <meta charset="UTF-8">
            <link rel="stylesheet" href="/static/css/xterm.css">
            <link rel="icon" href="/static/img/favicon.ico">
        </head>
        <body style="margin:0">
          <div id="terminal"></div>
        </body>
        <script src="static/js/xterm.js"></script>
        <script src="static/js/xterm-addon-fit.js"></script>
        <script src="static/js/tty.js"></script>
    </html>
'''
