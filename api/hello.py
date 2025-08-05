from http.server import BaseHTTPRequestHandler
from http import HTTPStatus

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bonjour depuis Vercel!')

def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'Bonjour depuis Vercel!'
    }
