#!/usr/bin/env python3
"""
Servidor simples para servir a aplicação React
TecnoCursos AI - Editor de Vídeo
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configurações do servidor
PORT = 8000
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler customizado para servir arquivos estáticos e SPA"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def guess_type(self, path):
        """Sobrescreve o método para configurar MIME types corretos"""
        # Mapeamento de extensões para MIME types
        mime_types = {
            '.js': 'application/javascript',
            '.jsx': 'application/javascript',
            '.ts': 'application/javascript',
            '.tsx': 'application/javascript',
            '.css': 'text/css',
            '.html': 'text/html',
            '.json': 'application/json',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject'
        }
        
        # Obtém a extensão do arquivo
        ext = Path(path).suffix.lower()
        
        # Retorna o MIME type apropriado
        if ext in mime_types:
            return mime_types[ext]
        
        # Fallback para o método padrão
        return super().guess_type(path)
    
    def do_GET(self):
        """Manipula requisições GET"""
        # Mapeia rotas para arquivos
        route_mappings = {
            '/': '/index.html',
            '/health': '/health.json',
            '/api/status': '/api/status.json',
            '/api/health': '/api/health.json',
            '/api/files/upload': '/api/files/upload.json',
            '/api/projects': '/api/projects.json',
            '/api/videos': '/api/videos.json',
            '/api/audios': '/api/audios.json',
            '/ws': '/ws.json',
            '/manifest.json': '/manifest.json',
        }
        
        # Verifica se é uma rota mapeada
        if self.path in route_mappings:
            self.path = route_mappings[self.path]
        
        # Para rotas que não existem, serve index.html (SPA)
        if not os.path.exists(DIRECTORY / self.path.lstrip('/')):
            if not self.path.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot')):
                self.path = '/index.html'
        
        return super().do_GET()
    
    def do_POST(self):
        """Manipula requisições POST"""
        if self.path == '/api/files/upload':
            # Simula upload de arquivo
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = {
                "success": True,
                "message": "Arquivo enviado com sucesso",
                "file_id": "file_" + str(int(os.urandom(4).hex(), 16)),
                "url": "/uploads/sample_file.jpg"
            }
            
            self.wfile.write(str(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Manipula requisições OPTIONS (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def create_api_files():
    """Cria arquivos de API de exemplo"""
    api_dir = DIRECTORY / 'api'
    api_dir.mkdir(exist_ok=True)
    
    # Arquivo de status
    status_file = api_dir / 'status.json'
    if not status_file.exists():
        status_file.write_text('{"status": "online", "version": "1.0.0", "timestamp": "2025-07-19T12:00:00Z"}')
    
    # Arquivo de health
    health_file = api_dir / 'health.json'
    if not health_file.exists():
        health_file.write_text('{"healthy": true, "uptime": 3600, "memory": "128MB"}')
    
    # Arquivo de upload
    upload_file = api_dir / 'files' / 'upload.json'
    upload_file.parent.mkdir(exist_ok=True)
    if not upload_file.exists():
        upload_file.write_text('{"success": true, "message": "Upload endpoint ready"}')
    
    # Arquivo de projetos
    projects_file = api_dir / 'projects.json'
    if not projects_file.exists():
        projects_file.write_text('{"projects": [], "total": 0}')
    
    # Arquivo de vídeos
    videos_file = api_dir / 'videos.json'
    if not videos_file.exists():
        videos_file.write_text('{"videos": [], "total": 0}')
    
    # Arquivo de áudios
    audios_file = api_dir / 'audios.json'
    if not audios_file.exists():
        audios_file.write_text('{"audios": [], "total": 0}')

def create_manifest():
    """Cria arquivo manifest.json"""
    manifest_file = DIRECTORY / 'manifest.json'
    if not manifest_file.exists():
        manifest_content = {
            "name": "TecnoCursos AI - Editor de Vídeo",
            "short_name": "TecnoCursos AI",
            "description": "Editor de vídeo com IA",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#1a1a1a",
            "theme_color": "#667eea",
            "icons": [
                {
                    "src": "/static/favicon.ico",
                    "sizes": "64x64",
                    "type": "image/x-icon"
                }
            ]
        }
        import json
        manifest_file.write_text(json.dumps(manifest_content, indent=2))

def main():
    """Função principal"""
    print(f"🚀 Iniciando servidor TecnoCursos AI...")
    print(f"📁 Diretório: {DIRECTORY}")
    print(f"🌐 Porta: {PORT}")
    print(f"🔗 URL: http://localhost:{PORT}")
    print(f"📱 PWA: http://localhost:{PORT}/manifest.json")
    print(f"🏥 Health: http://localhost:{PORT}/health")
    print(f"📊 Status: http://localhost:{PORT}/api/status")
    print()
    
    # Cria arquivos necessários
    create_api_files()
    create_manifest()
    
    # Configura o servidor
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"✅ Servidor rodando em http://localhost:{PORT}")
        print("⏹️  Pressione Ctrl+C para parar")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor parado pelo usuário")
            httpd.shutdown()

if __name__ == "__main__":
    main() 