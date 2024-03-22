from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from pyttyd import __static__, __html__
from pyttyd.pty import PTY

app = FastAPI()

app.mount("/static", StaticFiles(directory=__static__), name="static")


@app.get("/", response_class=HTMLResponse)
async def v_index():
    return __html__


@app.websocket("/tty")
async def websocket_endpoint(
        websocket: WebSocket,
        rows: int,
        cols: int,
):
    await websocket.accept()
    print('accepted')
    async with PTY(websocket) as pty:
        await pty.run()
