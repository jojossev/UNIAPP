from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Bienvenue sur Vercel! La configuration fonctionne maintenant!')
        return

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'success',
            'message': 'Requête reçue avec succès!',
            'method': self.command,
            'path': self.path,
            'body': body.decode('utf-8')
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

def handler(request, context):
    return Handler(request, context, None)
