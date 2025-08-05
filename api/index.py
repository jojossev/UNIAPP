from http.server import BaseHTTPRequestHandler
from django.http import HttpResponse

def handler(request):
    return HttpResponse("Bienvenue sur mon application Django sur Vercel!", content_type="text/plain")
