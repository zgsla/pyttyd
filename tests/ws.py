import json
import time
import unittest
from websockets.sync.client import connect


class TestTTY(unittest.TestCase):

    def setUp(self) -> None:
        self.websocket = connect('ws://127.0.0.1:8221/tty?rows=100&cols=100')

    def test_send(self):
        self.websocket.recv(10)
        self.websocket.send(json.dumps({'input': 'echo "hello world!"\n'}))
        time.sleep(5)
        data = self.websocket.recv(10)
        print(data)
        assert data.endswith('hello world!')

    def tearDown(self) -> None:
        self.websocket.close()


if __name__ == '__main__':
    unittest.main()
