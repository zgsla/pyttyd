import os
import json
import uuid
import asyncio
import logging
import datetime

import paramiko

from fastapi import FastAPI, Request, WebSocket, Header, Depends, Body, Cookie, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import insert, update, select, delete

from pyttyd import __basepath__
from pyttyd.crypto import rsa_key
from pyttyd.depends import CryptoDepend
from pyttyd.schema import CreateSSHConnectModel, UpdateSSHConnectModel, DeleteSSHConnectModel, WdtModel
from pyttyd.model import engine, tb_ssh_connect

app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{os.path.join(__basepath__, 'static')}"), name="static")

templates = Jinja2Templates(directory=f"{os.path.join(__basepath__, 'template')}")


@app.get("/", response_class=HTMLResponse)
async def ssh(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            'request': request,
            'publickey': rsa_key.pb_text.decode('utf8').replace('\n', '\\\n')
        }
    )


@app.get("/ssh/connect", response_class=HTMLResponse)
async def ssh(request: Request):
    return templates.TemplateResponse(
        "terminal.html",
        context={
            'request': request,
            'publickey': rsa_key.pb_text.decode('utf8').replace('\n', '\\\n')
        },
        headers={
            'Cookie': 'session=aaa'
        }
    )


@app.get("/ssh")
async def ssh(token: str = None, cryptor: CryptoDepend = Depends(CryptoDepend)):
    stmt = select(tb_ssh_connect)
    if token is not None:
        ssh_id = cryptor.decrypt(token)
        stmt = stmt.where(
            tb_ssh_connect.c.id == ssh_id
        )

    with engine.connect() as conn:
        res = conn.execute(stmt)
        data = res.fetchall() if token is None else res.fetchone()

    def to_dict(row):
        dct = {}
        for k, v in row.items():
            if isinstance(v, datetime.datetime):
                dct[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            else:
                dct[k] = v
        return dct

    return cryptor.encrypt(
        json.dumps(
            {
                "code": 0,
                "data": [to_dict(row) for row in data] if isinstance(data, list) else to_dict(data)
            }
        ).encode('utf8')
    )


@app.post("/ssh")
async def ssh(*, cryptor: CryptoDepend = Depends(CryptoDepend), body: WdtModel):
    print('insert ssh', body)
    data = cryptor.decrypt(body.token)
    item = json.loads(data)
    with engine.connect() as conn:
        result = conn.execute(
            insert(tb_ssh_connect).values(
                id=uuid.uuid4().hex,
                name=item['name'],
                host=item['host'],
                port=item['port'],
                user=item['user'],
                password=item['password']
            )
        )
        lastrowid = result.lastrowid
    return cryptor.encrypt(
        json.dumps(
            {
                "code": 0,
                "id": lastrowid
            }
        ).encode('utf8')
    )


@app.put("/ssh")
async def ssh(*, cryptor: CryptoDepend = Depends(CryptoDepend), body: WdtModel):
    print('update ssh', body)
    data = cryptor.decrypt(body.token)
    item = json.loads(data)

    with engine.connect() as conn:
        result = conn.execute(update(tb_ssh_connect).where(tb_ssh_connect.c.id == item['id']).values(
            name=item['name'],
            host=item['host'],
            port=item['port'],
            user=item['user'],
            password=item['password']
        ))
        rowcount = result.rowcount

    return cryptor.encrypt(
        json.dumps(
            {
                "code": 0 if rowcount == 1 else 1
            }
        ).encode('utf8')
    )


@app.delete("/ssh")
async def ssh(body: DeleteSSHConnectModel):
    print('delete ssh', body.ssh_id)
    with engine.connect() as conn:
        conn.execute(delete(tb_ssh_connect).where(tb_ssh_connect.c.id == body.ssh_id))
    return {
        "code": 0
    }


@app.websocket("/ssh/connect")
async def websocket_endpoint(
        websocket: WebSocket,

        rows: int,
        cols: int,
        token: str,
        cryptor: CryptoDepend = Depends(CryptoDepend),
):
    await websocket.accept()
    # print('token: ', token)
    data = json.loads(cryptor.decrypt(token))
    print(f'accepted {data}')
    with paramiko.SSHClient() as ssh_client:
        # ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(data['host'], data['port'], data['user'], data['password'])
        except Exception as e:
            await websocket.close(reason=str(e))
            return
        with ssh_client.invoke_shell('xterm', cols, rows) as chan:
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
            # chan.close()
    print(f'closed {data}')


async def read_chan(websocket, chan):
    while not chan.closed:
        try:
            data = await asyncio.to_thread(chan.recv, 1024)
        except Exception as e:
            logging.error('chan.recv error', exc_info=e)
            await websocket.close(reason=str(e))
            break
        if data:
            await websocket.send_text(data.decode('utf8'))


async def read_sock(websocket, chan):
    while True:
        try:
            data = await websocket.receive_text()
        except WebSocketDisconnect:
            break
        except Exception as e:
            logging.error('websocket.receive_text error', exc_info=e)
            # await websocket.close(reason=str(e))
            break
        event = json.loads(data)
        data = event.get('input')
        if data:
            await asyncio.to_thread(chan.send, data)
        size = event.get('resize')
        if size:
            await asyncio.to_thread(chan.resize_pty, *size)
