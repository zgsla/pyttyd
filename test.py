import asyncio
import time
import msvcrt
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

import paramiko

data = {
    'host': '127.0.0.1',
    'port': 2222,
    'user': 'root',
    'password': 'root'
}
data = {'password': '!@#blt*nix123', 'user': 'ubuntu', 'port': 22, 'host': '170.106.82.90', 'name': '爬虫',
        'id': 'ae687349d9ba41d78d9182d600605c79'}

commands = [
            '$SHELL -ilc "locale charmap"',
            '$SHELL -ic "locale charmap"'
        ]

print(data)

lock = asyncio.Lock()


async def read_chan(chan):
    # last = b''
    while not chan.closed:
        s = await asyncio.to_thread(chan.recv, 1024)
        # s = last + s
        # print('sss', s)
        # if b'\u' in s:
        #     if len(s) < 6:
        #         last = s
        #         continue
        #     else:
        #         sp = s.split(b'\u')
        #         if len(sp[-1]) < 4:
        #             sj = b'\u'.join(sp[:-1])
        #             last = b'\u' + sp[-1]
        #         else:
        #             sj = b'\u'.join(sp)
        #             last = b''
        #         s = sj.decode('unicode_escape')
        # else:
        #     s = s.decode('utf8')
        #     last = b''
        # print('sss2', s)
        s = s.decode('utf8')
        sys.stdout.write(s)
        sys.stdout.flush()


async def read_sock(chan):
    spec = 0
    while not chan.closed:
        # s = sys.stdin.readline()
        s = await asyncio.to_thread(msvcrt.getwch)
        # s = msvcrt.getwch()
        if s == '\x00':
            if spec != 1:
                spec = 1
        elif spec == 1:
            if s == 'H':  # 上
                chan.send('\x1b[A')
            elif s == 'K':  # 左
                chan.send('\x1b[D')
            elif s == 'M':  # 右
                chan.send('\x1b[C')
            elif s == 'P':  # 下
                chan.send('\x1b[B')
            else:
                chan.send(s)
            spec = 0
        else:
            # print(s, s.isascii(), end=' ')
            # if not s.isascii():
            #     s = s.encode('unicode_escape')
            # print(s)
            chan.send(s)


async def test11():
    with paramiko.SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=data['host'],
            port=data['port'],
            username=data['user'],
            password=data['password']
        )
        size = os.get_terminal_size()
        # with ssh_client.invoke_shell('xterm', cols, rows) as chan:
        with ssh_client.invoke_shell('xterm', size.columns, size.lines) as chan:
            # chan.setblocking(1)
            t1 = asyncio.create_task(read_chan(chan))
            t2 = asyncio.create_task(read_sock(chan))
            _, pending = await asyncio.wait(
                [t1, t2],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

    print(f'closed {data}')


if __name__ == '__main__':
    # print(os.openpty())
    asyncio.run(test11())
