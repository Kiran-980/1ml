"""Read-only loopback JSON fixture service with bounded request logging."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import time
from urllib.parse import urlparse

ap=argparse.ArgumentParser(); ap.add_argument('--trial',type=Path,required=True)
ap.add_argument('--resume',action='store_true',help='Serve the same immutable source at its recorded loopback port')
a=ap.parse_args()
trial=a.trial.resolve(); evaluator=trial/'evaluator'
payload=(evaluator/'http/region-context.json').read_bytes()
digest=hashlib.sha256(payload).hexdigest()
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status=200 if self.path=='/v1/region-context.json' else 404
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('ETag','"'+digest+'"')
        body=payload if status==200 else b'{"error":"unknown fixture route"}'
        self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        with (evaluator/'http-requests.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps({'utc_epoch':time.time(),'method':'GET','route':'region-context' if status==200 else 'other','status':status,'bytes':len(body)})+'\n')
    def log_message(self,*args): pass

source_path=trial/'materials/sources.json'
port=0
if a.resume:
    recorded=json.loads(source_path.read_text(encoding='utf-8'))
    parsed=urlparse(recorded['region_context']['url'])
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.path!='/v1/region-context.json' or not parsed.port:
        raise SystemExit('Invalid recorded loopback fixture URL')
    if digest!=recorded['region_context']['sha256']:
        raise SystemExit('HTTP fixture source identity changed')
    if hashlib.sha256(Path(recorded['database']['path']).read_bytes()).hexdigest()!=recorded['database']['sha256']:
        raise SystemExit('Database source identity changed')
    port=parsed.port
elif source_path.exists():
    raise SystemExit('Source settings already exist; use --resume to preserve their identity')
server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
url=f'http://127.0.0.1:{server.server_port}/v1/region-context.json'
db=trial/'materials/database/shipments.sqlite'
sources={'database':{'path':str(db),'engine':'sqlite','access':'read-only','sha256':hashlib.sha256(db.read_bytes()).hexdigest()},
         'region_context':{'url':url,'format':'JSON document with regions records array','snapshot_id':'shipment-context-v1','sha256':digest},
         'fixture_service':'Available during the evaluation; keep source settings configurable for later replay.'}
if not a.resume:
    source_path.write_text(json.dumps(sources,indent=2),encoding='utf-8')
    (evaluator/'server-info.json').write_text(json.dumps({'url':url,'port':server.server_port,'started_utc_epoch':time.time()},indent=2),encoding='utf-8')
print(json.dumps({'status':'ready','url':url}),flush=True)
try: server.serve_forever()
finally: server.server_close()
