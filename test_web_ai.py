"""HTTP integration tests using a temporary state file; no real model required."""
import json
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
import urllib.error
from pathlib import Path

class WebAssistantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); cls.port = sock.getsockname()[1]
        cls.base = f'http://127.0.0.1:{cls.port}'
        cls.state = Path(cls.temp.name)/'state.json'
        cls.process = subprocess.Popen([sys.executable, 'web_app.py', '--no-browser', '--port', str(cls.port), '--state', str(cls.state)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for _ in range(100):
            try:
                cls.bootstrap = json.load(urllib.request.urlopen(cls.base+'/api/bootstrap', timeout=1)); break
            except (OSError, urllib.error.URLError): time.sleep(.05)
        else:
            cls.process.terminate(); cls.process.wait(timeout=5)
            raise RuntimeError('Test server did not start.')
    @classmethod
    def tearDownClass(cls):
        cls.process.terminate(); cls.process.wait(timeout=5)
        cls.process.stderr.close(); cls.temp.cleanup()
    def post(self, route, data, token=None):
        request=urllib.request.Request(self.base+route, data=json.dumps(data).encode(), headers={'Content-Type':'application/json','X-ReLoop-Token':token if token is not None else self.bootstrap['token']})
        return json.load(urllib.request.urlopen(request,timeout=10))
    def test_assets_and_mode(self):
        self.assertEqual(self.bootstrap['ai']['mode'], 'demo')
        page=urllib.request.urlopen(self.base).read().decode()
        self.assertIn('ask-form',page)
        self.assertIn('agent-form',page)
        self.assertIn('sourceMarkup',urllib.request.urlopen(self.base+'/assistant.js').read().decode())
    def test_retrieval_endpoint(self):
        r=self.post('/api/ask',{'question':'What inspection is required for a school monitor transfer?'})
        self.assertEqual(r['mode'],'retrieval_preview')
        self.assertTrue(r['sources'])
    def test_agent_proposes_without_writing(self):
        r=self.post('/api/agent',{'query':'display for computer lab','quantity':2,'recipient':'SCHOOL01','radius':10,'repair':False})
        self.assertEqual(r['status'],'awaiting_human_inspection')
        self.assertFalse(r['transfer_recorded'])
        self.assertFalse(self.state.exists())
    def test_invalid_partner_and_quantity(self):
        for request in [{'query':'monitor','recipient':'SCHOOL02'},{'query':'monitor','quantity':1.5}]:
            with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/agent',request)
            self.assertEqual(e.exception.code,400)
    def test_token_required(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/ask',{'question':'inspection'},'invalid')
        self.assertEqual(e.exception.code,403)

if __name__=='__main__':unittest.main()
