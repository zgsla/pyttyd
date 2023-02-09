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

from pyttyd import __basepath__, crud
from pyttyd.crypto import rsa_key
from pyttyd.depends import CryptoDepend, to_dict
from pyttyd.model import engine, tb_ssh_connect
from pyttyd.terminal import Terminal

app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{os.path.join(__basepath__, 'static')}"), name="static")

templates = Jinja2Templates(directory=f"{os.path.join(__basepath__, 'template')}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            'request': request,
            'conns': crud.get_conns(),
            'publickey': rsa_key.pb_text.decode('utf8')
        }
    )


@app.get("/ssh/connect", response_class=HTMLResponse)
async def ssh(request: Request):
    return templates.TemplateResponse(
        "terminal.html",
        context={
            'request': request,
            'publickey': rsa_key.pb_text.decode('utf8')
        }
    )


@app.get("/ssh")
async def ssh(cryptor: CryptoDepend = Depends(CryptoDepend)):
    stmt = select(tb_ssh_connect)
    if cryptor.token:
        ssh_id = cryptor.decrypt(cryptor.token)
        stmt = stmt.where(
            tb_ssh_connect.c.id == ssh_id
        )

    with engine.connect() as conn:
        res = conn.execute(stmt)
        data = res.fetchall() if cryptor.token is None else res.fetchone()

    return cryptor.encrypt(
        json.dumps(
            {
                "code": 0,
                "data": [to_dict(row) for row in data] if isinstance(data, list) else to_dict(data)
            }
        ).encode('utf8')
    )


@app.post("/ssh")
async def ssh(*, cryptor: CryptoDepend = Depends(CryptoDepend)):

    data = cryptor.decrypt(cryptor.token)
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
async def ssh(cryptor: CryptoDepend = Depends(CryptoDepend)):
    data = cryptor.decrypt(cryptor.token)
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
async def ssh(cryptor=Depends(CryptoDepend)):
    # print('delete ssh', cryptor.token)
    data = cryptor.decrypt(cryptor.token)
    item = json.loads(data)
    with engine.connect() as conn:
        conn.execute(delete(tb_ssh_connect).where(tb_ssh_connect.c.id == item['id']))
    return {
        "code": 0
    }


@app.websocket("/ssh/connect")
async def websocket_endpoint(
        websocket: WebSocket,

        rows: int,
        cols: int,
        cryptor: CryptoDepend = Depends(CryptoDepend),
):
    await websocket.accept()
    # print('token: ', token)
    data = cryptor.json()
    print(f'accepted {data}')
    with Terminal(websocket=websocket, conn=data, rows=rows, cols=cols) as term:
        await term.join()
