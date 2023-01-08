from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocketDisconnect

import paramiko
import asyncio
import json


ssh_client = paramiko.SSHClient()
# ssh_client.load_system_host_keys()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect('127.0.0.1', 2222, 'root', 'root')

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/webdevtool/static"), name="static")

templates = Jinja2Templates(directory="src/webdevtool/template")


async def read_chan(websocket, chan):
    while not chan.closed:
        try:
            data = await asyncio.to_thread(chan.recv, 1024)
        except Exception as e:
            print(e)
            break
        if data:
            print(data)
            await websocket.send_text(data.decode('utf8'))


async def read_sock(websocket, chan):
    print("read sock")
    while True:
        try:
            data = await websocket.receive_text()
        except WebSocketDisconnect:
            break
        print('recv data: ', data)
        event = json.loads(data)
        data = event.get('input')
        if data:
            await asyncio.to_thread(chan.send, data)
        # await websocket.send_text(f"Message text was: {data}")
    # async for message in websocket:
    #     # Parse a "play" event from the UI.
    #     event = json.loads(message)
    #     print('event: ', event)
    #     data = event.get('input')
    #     if data:
    #         await asyncio.to_thread(chan.send, data)

@app.get("/", response_class=HTMLResponse)
async def ssh(request: Request):
    return templates.TemplateResponse("index.html", context={'request': request})


@app.get("/ssh", response_class=HTMLResponse)
async def ssh(request: Request):
    return templates.TemplateResponse("terminal.html", context={'request': request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('open')
    chan = ssh_client.invoke_shell(term='xterm')
    # chan.setblocking(1)
    # await read_chan(websocket, chan)
    print('opened')
    consumer_task = asyncio.create_task(read_chan(websocket, chan))
    producer_task = asyncio.create_task(read_sock(websocket, chan))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    print("closed")
    chan.close()
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(f"Message text was: {data}")