import json
import asyncio
import logging
import urllib.parse
import paramiko

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import insert, update, select, delete

from webdevtool.crypto import rsa_key
from webdevtool.schema import CreateSSHConnectModel, UpdateSSHConnectModel, DeleteSSHConnectModel
from webdevtool.model import engine, tb_ssh_connect

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/webdevtool/static"), name="static")

templates = Jinja2Templates(directory="src/webdevtool/template")


@app.get("/", response_class=HTMLResponse)
async def ssh(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            'request': request,
            'publickey': rsa_key.pb_text().decode('utf8').replace('\n', '\\\n')
        }
    )


@app.get("/ssh/connect", response_class=HTMLResponse)
async def ssh(request: Request, name: str, ssh_id: int):
    return templates.TemplateResponse("terminal.html", context={'request': request, 'name': name})


@app.get("/ssh")
async def ssh(ssh_id: int = None):
    with engine.connect() as conn:
        stmt = select(tb_ssh_connect)
        if ssh_id is not None:
            stmt = stmt.where(
                tb_ssh_connect.c.id == ssh_id
            )
        res = conn.execute(stmt)
        if ssh_id is None:
            data = res.fetchall()
        else:
            data = res.fetchone()
    return {
        "code": 0,
        "data": data
    }


@app.post("/ssh")
async def ssh(body: CreateSSHConnectModel):
    print('insert ssh', body)
    with engine.connect() as conn:
        result = conn.execute(
            insert(tb_ssh_connect).values(
                name=body.name,
                host=body.host,
                port=body.port,
                user=body.user,
                password=body.password
            )
        )
        lastrowid = result.lastrowid
    return {
        "code": 0,
        "id": lastrowid
    }


@app.put("/ssh")
async def ssh(body: UpdateSSHConnectModel):
    print('update ssh', body)
    password = rsa_key.pv_key.decrypt()
    with engine.connect() as conn:
        result = conn.execute(update(tb_ssh_connect).where(tb_ssh_connect.c.id == body.id).values(
            name=body.name,
            host=body.host,
            port=body.port,
            user=body.user,
            password=body.password
        ))
        rowcount = result.rowcount
    if rowcount == 1:
        return {"code": 0, "id": body.id}
    else:
        return {"code": 1}


@app.delete("/ssh")
async def ssh(body: DeleteSSHConnectModel):
    print('delete ssh', body.id)
    with engine.connect() as conn:
        conn.execute(delete(tb_ssh_connect).where(tb_ssh_connect.c.id == body.id))
    return {
        "code": 0
    }


@app.websocket("/ssh/connect")
async def websocket_endpoint(
        websocket: WebSocket,
        name: str,
        host: str,
        port: int,
        user: str,
        password: str,
        rows: int,
        cols: int
):
    await websocket.accept()
    password = urllib.parse.unquote(password)
    logging.info(f'accepted host:{host}, port:{port}, user:{user}, password：{password}')
    with paramiko.SSHClient() as ssh_client:
        # ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(host, port, user, password)
        except Exception as e:
            await websocket.close(reason=str(e))
            return
        with ssh_client.invoke_shell(term='xterm') as chan:
            chan.resize_pty(cols, rows)
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
            await websocket.close(reason=str(e))
            break
        if data:
            await websocket.send_text(data.decode('utf8'))


async def read_sock(websocket, chan):
    while True:
        try:
            data = await websocket.receive_text()
        except Exception as e:
            logging.error('websocket.receive_text error', exc_info=e)
            await websocket.close(reason=str(e))
            break
        event = json.loads(data)
        data = event.get('input')
        if data:
            await asyncio.to_thread(chan.send, data)
        size = event.get('resize')
        if size:
            await asyncio.to_thread(chan.resize_pty, *size)
