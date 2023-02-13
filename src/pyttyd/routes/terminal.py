from fastapi import WebSocket, Depends
from fastapi.routing import APIWebSocketRoute
from pyttyd.depends import CryptoDepend
from pyttyd.terminal import Terminal


async def websocket_endpoint(
        websocket: WebSocket,
        rows: int,
        cols: int,
        cryptor: CryptoDepend = Depends(CryptoDepend),
):
    await websocket.accept()
    data = cryptor.json()
    print(f'accepted {data}')
    with Terminal(websocket=websocket, conn=data, rows=rows, cols=cols) as term:
        await term.join()


router = APIWebSocketRoute("/ssh/connect", websocket_endpoint)
