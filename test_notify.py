import io
import json
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import notify


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


class NotifyTests(unittest.TestCase):
    @patch.dict(os.environ, {"REMINDER_URL": "https://example.com/", "REMINDER_KEY": "test-key"})
    @patch("notify.urllib.request.urlopen")
    def test_dispatch(self, open_url):
        open_url.return_value = Response({"ok": True, "sent": 2, "failed": 0})
        with redirect_stdout(io.StringIO()) as output:
            notify.main()
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.com/api/cron")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("X-reminder-key"), "test-key")
        self.assertEqual(json.loads(output.getvalue())["sent"], 2)

    @patch.dict(os.environ, {"REMINDER_URL": "https://example.com", "REMINDER_KEY": "test-key"})
    @patch("notify.urllib.request.urlopen", return_value=Response({"ok": False}))
    def test_rejected_dispatch_fails(self, _):
        with self.assertRaises(RuntimeError):
            notify.main()


if __name__ == "__main__":
    unittest.main()

