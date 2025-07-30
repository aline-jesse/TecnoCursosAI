#!/usr/bin/env python3
"""
Frontend Simples - TecnoCursos AI
Servidor HTTP simples para o frontend
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)

def start_frontend_server():
    """Inicia servidor do frontend"""
    PORT = 3000
    
    try:
        with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
            print(f"🎨 Frontend servindo na porta {PORT}")
            print(f"🌐 Acesse: http://localhost:{PORT}")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"⚠️ Porta {PORT} já está em uso!")
            print("Tentando porta 3001...")
            try:
                with socketserver.TCPServer(("", 3001), SimpleHTTPRequestHandler) as httpd:
                    print(f"🎨 Frontend servindo na porta 3001")
                    print(f"🌐 Acesse: http://localhost:3001")
                    httpd.serve_forever()
            except:
                print("❌ Erro ao iniciar frontend")
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando Frontend TecnoCursos AI...")
    start_frontend_server()
