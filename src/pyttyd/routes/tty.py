import os
import json
import logging
import asyncio
import subprocess
import time

from fastapi import WebSocket, Depends, WebSocketDisconnect
from fastapi.routing import APIWebSocketRoute


async def read_sock(ws, ppty):
    while True:
        try:
            data = await ws.receive_text()
            print(data)
        except WebSocketDisconnect:
            break
        except Exception as e:
            logging.error('websocket.receive_text error', exc_info=e)
            # await websocket.close(reason=str(e))
            break
        event = json.loads(data)
        data = event.get('input')
        if data:
            # print(data.encode('gbk'))
            # chan.send(data.encode('utf8'))
            os.write(ppty, data.encode('utf8'))
        # size = event.get('resize')
        # if size:
        #     os.putenv('COLUMNS', str(size[1]))
        #     os.putenv('ROWS', str(size[0]))
            # chan.resize_pty(*size)


async def win_read(ws, popen: subprocess.Popen):
    while True:
        try:
            data = await ws.receive_text()
            print(data)
        except WebSocketDisconnect:
            break
        except Exception as e:
            logging.error('websocket.receive_text error', exc_info=e)
            # await websocket.close(reason=str(e))
            break
        event = json.loads(data)
        data = event.get('input')
        if data:
            # print(data.encode('gbk'))
            # chan.send(data.encode('utf8'))
            # os.write(ppty, data.encode('utf8'))
            data = data.replace('\r', '\n')
            data = data.replace('\u001b[A', chr(0x21))
            popen.stdin.write(data.encode('utf8'))
            popen.stdin.flush()
            print('写入', data)
        # size = event.get('resize')
        # if size:
        #     os.putenv('COLUMNS', str(size[1]))
        #     os.putenv('ROWS', str(size[0]))
            # chan.resize_pty(*size)


async def read_chan(ws, ppty):
    while True:
        try:
            if hasattr(asyncio, 'to_thread'):
                data = await asyncio.to_thread(os.read, ppty, 1024)
            else:
                data = await asyncio.get_running_loop().run_in_executor(None, os.read, ppty, 1024)
            # print('chan.recv: ', data)
        except Exception as e:
            logging.error('chan.recv error', exc_info=e)
            await ws.close(reason=str(e))
            break
        if data:
            await ws.send_text(data.decode('utf8'))


async def win_chan(ws, fd):
    print('win-read')
    while True:
        try:
            if hasattr(asyncio, 'to_thread'):
                await asyncio.to_thread(fd.flush)
                data = await asyncio.to_thread(os.read, fd.fileno(), 1024)
            else:
                await asyncio.get_running_loop().run_in_executor(None, fd.flush)
                data = await asyncio.get_running_loop().run_in_executor(None, os.read, fd.fileno(), 1024)

        except Exception as e:
            logging.error('chan.recv error', exc_info=e)
            await ws.close(reason=str(e))
            break
        if data:
            await ws.send_bytes(data.decode('gbk'))


async def websocket_endpoint(
        websocket: WebSocket,
        rows: int,
        cols: int,
        # cryptor: CryptoDepend = Depends(CryptoDepend),
):
    await websocket.accept()
    print('accepted')
    print('openpty')
    if os.name == 'nt':
        file1 = open("ttt.txt", 'w+')
        file2 = open("ttt.txt", 'r')
        process = subprocess.Popen(
            'cmd.exe',
            stdin=subprocess.PIPE,
            stdout=file1,
            stderr=subprocess.STDOUT,
            shell=True
        )
        producer_task = asyncio.create_task(win_read(websocket, process))
        consumer_task = asyncio.create_task(win_chan(websocket, file2))
        done, pending = await asyncio.wait(
            [producer_task, consumer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
    else:
        master, slave = os.openpty()
        process = subprocess.Popen('bash', stdin=slave, stdout=slave, stderr=slave, shell=True)
        consumer_task = asyncio.create_task(read_chan(websocket, master))
        producer_task = asyncio.create_task(read_sock(websocket, master))

        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


router = APIWebSocketRoute("/tty", websocket_endpoint)
