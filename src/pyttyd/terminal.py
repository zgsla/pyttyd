import json
import asyncio
import logging
import paramiko

from fastapi import WebSocketDisconnect

from pyttyd.common import encodingmap, default_encoding


class Terminal(paramiko.SSHClient):

    def __init__(self, websocket, conn, rows, cols):

        super(Terminal, self).__init__()

        self._rows = rows
        self._cols = cols
        self._ws = websocket

        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(conn['host'], conn['port'], conn['user'], conn['password'])
        _, stdout, _ = self.exec_command('$SHELL -ilc "locale charmap"')
        charmap = stdout.read().decode().strip()
        stdout.close()
        self._encoding = encodingmap.get(charmap, default_encoding)

    async def join(self):
        with self.invoke_shell('xterm', self._cols, self._rows) as chan:
            # chan.setblocking(1)
            # await read_chan(websocket, chan)
            consumer_task = asyncio.create_task(self.read_chan(chan))
            producer_task = asyncio.create_task(self.read_sock(chan))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

    async def read_chan(self, chan):
        while not chan.closed:
            try:
                data = await asyncio.to_thread(chan.recv, 1024)
                # print('chan.recv: ', data)
            except Exception as e:
                logging.error('chan.recv error', exc_info=e)
                await self._ws.close(reason=str(e))
                break
            if data:
                await self._ws.send_text(data.decode(self._encoding))

    async def read_sock(self, chan):
        while True:
            try:
                data = await self._ws.receive_text()
                # print(data)
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
                chan.send(data.encode(self._encoding))
            size = event.get('resize')
            if size:
                chan.resize_pty(*size)