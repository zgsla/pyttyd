import unittest
from websockets.sync.client import connect


class TestTTY(unittest.TestCase):

    def setUp(self) -> None:
        self.websocket = connect('127.0.0.1:8221')

    def test_send(self):
        self.websocket.send('echo "hello world"\n')
        data = self.websocket.recv(10)
        assert data == 'hello world'

    def tearDown(self) -> None:
        self.websocket.close()


if __name__ == '__main__':
    unittest.main()