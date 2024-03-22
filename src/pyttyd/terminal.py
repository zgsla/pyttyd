import os
import json
import logging
import asyncio
import subprocess
import time

from fastapi import WebSocketDisconnect


async def read_sock(ws, ppty):
    while True:
        try:
            data = await ws.receive_text()
            print(data)
        except WebSocketDisconnect:
            break
        except Exception as e:
            logging.error('websocket.receive_text error', exc_info=e)
            await ws.close(reason=str(e))
            break
        event = json.loads(data)
        data = event.get('input')
        if data:
            os.write(ppty, data.encode('utf8'))


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

