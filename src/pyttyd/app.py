import pty
import asyncio
import subprocess

from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from pyttyd import __static__, __html__
from terminal import read_sock, read_chan

app = FastAPI()

app.mount("/static", StaticFiles(directory=__static__), name="static")


@app.get("/", response_class=HTMLResponse)
async def v_index():
    return __html__


@app.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        rows: int,
        cols: int,
):
    await websocket.accept()
    print('accepted')
    master, slave = pty.openpty()
    process = subprocess.Popen('bash', stdin=slave, stdout=slave, stderr=slave, shell=True)
    consumer_task = asyncio.create_task(read_chan(websocket, master))
    producer_task = asyncio.create_task(read_sock(websocket, master))

    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
