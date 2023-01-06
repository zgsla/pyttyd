#!/usr/bin/env python

import asyncio
import json
import os

import paramiko
import websockets


ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys()

ssh_client.connect('127.0.0.1', 2222, 'root', 'root')


async def read_chan(websocket, chan):
    while True:
        print('chan status: ', chan.closed)
        data = chan.recv(1024)
        if data:
            await websocket.send(data.decode('utf8'))
        await asyncio.sleep(0.1)

async def handler(websocket):
    """
    Handle a connection and dispatch it according to who is connecting.

    """
    print('open')
    chan = ssh_client.invoke_shell(term='xterm')
    chan.setblocking(0)
    await read_chan(websocket, chan)
    print('opened')

    async for message in websocket:
        # Parse a "play" event from the UI.
        event = json.loads(message)
        print(event)
        data = event.get('input')
        if data:
            chan.send(data)
    print("closed")


async def main():
    # Set the stop condition when receiving SIGTERM.
    # loop = asyncio.get_running_loop()
    # stop = loop.create_future()
    # loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8001"))
    async with websockets.serve(handler, "", port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
