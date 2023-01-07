from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.endpoints import WebSocketEndpoint


import paramiko
import asyncio
import json


ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys()

ssh_client.connect('127.0.0.1', 2222, 'root', 'root')

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/webdevtool/static"), name="static")

templates = Jinja2Templates(directory="src/webdevtool/template")


class App(WebSocketEndpoint):
    encoding = 'bytes'
    chan = None 

    async def read_chan(self, websocket):
        while True:
            try:
                data = await asyncio.to_thread(self.chan.recv, 1024)
            except Exception as e:
                print(e)
                break
            if data:
                print(data)
                await websocket.send_bytes(data)

    async def on_connect(self, websocket):
        await websocket.accept()
        self.chan = ssh_client.invoke_shell(term='xterm')
        asyncio.create_task(self.read_chan(websocket))
        
        

    async def on_receive(self, websocket, data):
        event = json.loads(data)
        print('event: ', event)
        data = event.get('input')
        if data:
            await asyncio.to_thread(self.chan.send, data)
        await websocket.send_bytes(b"Message: " + data)

    async def on_disconnect(self, websocket, close_code):
        pass


async def read_chan(websocket, chan):
    while True:
        print('chan status: ', chan.closed)
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
        data = await websocket.receive_text()
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
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={'request': request})


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
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(f"Message text was: {data}")