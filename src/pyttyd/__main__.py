import socket
import uvicorn


try:
    host = socket.gethostbyname(socket.gethostname())
except:
    host = '127.0.0.1'


def main():
    uvicorn.run(
        'pyttyd.app:app',
        host=host,
        port=8221
    )
