import json
import asyncio
import logging

import paramiko

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect

from webdevtool.schema import SSHConnectModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/webdevtool/static"), name="static")

templates = Jinja2Templates(directory="src/webdevtool/template")


@app.get("/", response_class=HTMLResponse)
async def ssh(request: Request):
    return templates.TemplateResponse("index.html", context={'request': request})


@app.get("/ssh/connect", response_class=HTMLResponse)
async def ssh(request: Request, name: str, host: str, port: int, user: str, password: str):
    return templates.TemplateResponse("terminal.html", context={'request': request, 'name': name})


@app.post("/ssh")
async def ssh(body: SSHConnectModel):
    print(body)
    return {
        "code": 0
    }


@app.websocket("/ssh/connect")
async def websocket_endpoint(websocket: WebSocket, name: str, host: str, port: int, user: str, password: str):
    await websocket.accept()
    logging.info(f'accepted host:{host}, port:{port}, user:{user}, password：{password}')
    with paramiko.SSHClient() as ssh_client:
        # ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(host, port, user, password)
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            await websocket.close(reason=str(e))
            return
        with ssh_client.invoke_shell(term='xterm') as chan:
            # chan.setblocking(1)
            # await read_chan(websocket, chan)
            consumer_task = asyncio.create_task(read_chan(websocket, chan))
            producer_task = asyncio.create_task(read_sock(websocket, chan))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            chan.close()
    logging.info(f'closed host:{host}, port:{port}, user:{user}, password：{password}')


async def read_chan(websocket, chan):
    while not chan.closed:
        try:
            data = await asyncio.to_thread(chan.recv, 1024)
        except Exception as e:
            logging.error('chan.recv error', exc_info=e)
            break
        if data:
            await websocket.send_text(data.decode('utf8'))


async def read_sock(websocket, chan):
    while True:
        try:
            data = await websocket.receive_text()
        except WebSocketDisconnect:
            break
        event = json.loads(data)
        data = event.get('input')
        if data:
            await asyncio.to_thread(chan.send, data)
