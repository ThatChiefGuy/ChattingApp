import json
import unittest
from unittest.mock import MagicMock
import server

class TestBroadcast(unittest.TestCase):
    def test_broadcast(self):
        client1 = MagicMock()
        client2 = MagicMock()

        clients = {client1:"Jopa",
                  client2:"pero"}


        server.broadcast_message("chat"," ", clients)
        self.assertEqual(client1.send.call_count, 1)
        self.assertEqual(client2.send.call_count, 1)

class TestDecode(unittest.TestCase):
    def test_decode(self):
        json_bytes = b'{"type":"chat", "message":"hello"}'

        result = server.decode(json_bytes)

        expected = {"type":"chat", "message":"hello"}

        self.assertEqual(expected, result)

    def test_decode_invalid_json_bytes(self):
        invalid_json_bytes = b'{"type":"chat", "message":"hello"'
        with self.assertRaises(json.JSONDecodeError):
            server.decode(invalid_json_bytes)


if __name__ == "__main__":
    unittest.main()