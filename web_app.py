"""Local browser frontend for ReLoop. No third-party dependencies."""
import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import secrets
import webbrowser
from ai_assistant import Ollama, ModelError, Agent, rag_answer
from reloop import ROOT, load_state, save_state, read_json, match, confirm, summary


def serve(port=8765, state_path=None, open_browser=True, ai_mode="demo", model_name="qwen3:4b"):
    model = Ollama(model_name) if ai_mode == "ollama" else None
    state_path = Path(state_path or ROOT / 'local_state.json')
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def send(self, data, status=200, mime='application/json'):
            body = json.dumps(data, allow_nan=False).encode() if mime == 'application/json' else data
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            self.end_headers(); self.wfile.write(body)
        def trusted(self):
            hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
            if self.headers.get('Host') not in hosts:
                self.send({'error':'Invalid local host.'},403); return False
            origin = self.headers.get('Origin')
            if origin and origin not in {f'http://{h}' for h in hosts}:
                self.send({'error':'Request must come from this local app.'},403); return False
            return True
        def do_GET(self):
            if not self.trusted(): return
            try:
                route = self.path.split('?')[0]
                if route == '/api/bootstrap':
                    state = load_state(state_path)
                    self.send({'token':token, 'partners':read_json(ROOT/'partners.json'), 'inventory':state['inventory'], 'summary':summary(state), 'transfers':state['transfers'], 'ai': {'mode': ai_mode, 'model': model_name if model else None}}); return
                files = {'/':'index.html','/app.js':'app.js','/style.css':'style.css', '/assistant.js':'assistant.js'}
                if route not in files: self.send({'error':'Not found'},404); return
                file = ROOT/'web'/files[route]
                self.send(file.read_bytes(),mime=(mimetypes.guess_type(file.name)[0] or 'text/plain')+'; charset=utf-8')
            except (OSError,ValueError,KeyError): self.send({'error':'Could not read local project data. Check your data files.'},500)
        def do_POST(self):
            if not self.trusted(): return
            if not secrets.compare_digest(self.headers.get('X-ReLoop-Token',''),token):
                self.send({'error':'Reload the app before continuing.'},403); return
            try:
                size = int(self.headers.get('Content-Length',0))
                if size < 1 or size > 12000: raise ValueError('Invalid request size.')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data,dict): raise ValueError('Expected a JSON object.')
                quantity = data.get('quantity',1)
                if type(quantity) is not int: raise ValueError('Quantity must be a whole number.')
                state = load_state(state_path)
                if self.path == '/api/ask':
                    result = rag_answer(data.get('question'), model)
                elif self.path == '/api/agent':
                    result = Agent(state, data, model).run()
                elif self.path == '/api/match':
                    result = match(state,str(data.get('query','')),quantity,float(data.get('radius',10)),bool(data.get('repair',False)),str(data.get('recipient','SCHOOL01')))
                elif self.path == '/api/transfer':
                    result = confirm(state,str(data.get('item','')),quantity,float(data.get('price',0)),float(data.get('transport',0)),float(data.get('refurbishment',0)),data.get('inspected') is True,str(data.get('recipient','SCHOOL01')))
                    save_state(state_path,state)
                else: self.send({'error':'Not found'},404); return
                self.send(result)
            except ModelError as e: self.send({'error':str(e)},503)
            except (ValueError,TypeError,KeyError) as e: self.send({'error':str(e)},400)
            except OSError: self.send({'error':'Could not save local data. Check folder permissions.'},500)
        def log_message(self,*args): pass
    server = HTTPServer(('127.0.0.1',port),Handler)
    print(f'ReLoop AI is ready: http://127.0.0.1:{port}\nKeep this terminal open. Press Ctrl+C to stop.',flush=True)
    if open_browser: webbrowser.open(f'http://127.0.0.1:{port}')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--state',type=Path,default=ROOT/'local_state.json')
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--ai-mode', choices=['demo','ollama'], default='demo')
    parser.add_argument('--model', default='qwen3:4b')
    args=parser.parse_args()
    try: serve(args.port,args.state,not args.no_browser,args.ai_mode,args.model)
    except OSError as exc: parser.exit(1,f'Cannot start the local app: {exc}\nTry --port 8766 if the port is busy.\n')
