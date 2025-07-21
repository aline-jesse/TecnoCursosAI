#!/usr/bin/env python3
"""
Servidor HTTP Simples - TecnoCursos AI
Versão nativa Python sem dependências externas
"""

import http.server
import socketserver
import json
import logging
import time
import os
import socket
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import urllib.parse
import io
import re # Added for multipart parsing

# Importar sistema de upload
try:
    from upload_handler import handle_upload_request, handle_list_request, handle_delete_request, handle_stats_request
    UPLOAD_AVAILABLE = True
except ImportError:
    UPLOAD_AVAILABLE = False
    logging.warning("Sistema de upload não disponível")

# Importar sistema de processamento em background
try:
    from background_processor import (
        start_background_processor, stop_background_processor,
        submit_background_task, get_task_status, get_all_tasks,
        cancel_task, get_processor_stats, TaskType
    )
    BACKGROUND_PROCESSOR_AVAILABLE = True
except ImportError:
    BACKGROUND_PROCESSOR_AVAILABLE = False
    logging.warning("Sistema de processamento em background não disponível")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
def get_config():
    """Carrega configuração do arquivo config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.warning(f"Erro ao carregar config.json: {e}, usando configurações padrão")
        return {
            "server": {"port": 8000, "host": "0.0.0.0"},
            "system": {"name": "TecnoCursos AI", "version": "2.0.0"}
        }

config = get_config()
DEFAULT_PORT = int(os.getenv("PORT", config.get("server", {}).get("port", 8000)))
HOST = os.getenv("HOST", config.get("server", {}).get("host", "0.0.0.0"))
DIRECTORY = Path(__file__).parent

def find_available_port(start_port=DEFAULT_PORT, max_attempts=20):
    """Encontra uma porta disponível"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                s.close()
                print(f"Porta {port} disponível")
                return port
        except OSError as e:
            print(f"Porta {port} em uso, tentando próxima...")
            continue
    return None

# Criar diretórios necessários
def create_directories():
    """Cria diretórios necessários para a aplicação"""
    directories = [
        "uploads",
        "uploads/videos",
        "uploads/audios",
        "uploads/images", 
        "uploads/documents",
        "static/videos",
        "static/audios",
        "static/thumbnails",
        "cache",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

class TecnoCursosHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado para o TecnoCursos AI"""
    
    def __init__(self, *args, **kwargs):
        self.start_time = time.time()
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def log_message(self, format, *args):
        """Log personalizado"""
        try:
            message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}"
            logger.info(message)
        except UnicodeEncodeError:
            # Fallback para codificação ASCII
            message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}"
            logger.info(message.encode('ascii', 'ignore').decode('ascii'))
    
    def do_GET(self):
        """Handler para requisições GET"""
        try:
            # Parse da URL
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            # Rotas da API
            if path.startswith('/api/'):
                return self.handle_api_request(path)
            
            # Rotas especiais
            if path == '/health':
                return self.handle_health()
            elif path == '/docs':
                return self.handle_docs()
            elif path == '/':
                return self.handle_home()
            elif path == '/favicon.ico':
                return self.handle_favicon()
            elif path.startswith('/static/'):
                return self.handle_static_file(path)
            elif path.startswith('/uploads/'):
                return self.handle_upload_file(path)
            else:
                # Tentar servir arquivo estático
                return self.handle_static_file(path)
                
        except (BrokenPipeError, ConnectionAbortedError) as e:
            logger.warning(f"Cliente desconectou: {e}")
            return
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            try:
                self.send_error(500, f"Internal Server Error: {str(e)}")
            except (BrokenPipeError, ConnectionAbortedError) as e:
                logger.warning(f"Cliente desconectou durante erro: {e}")
                return
    
    def do_POST(self):
        """Handler para requisições POST (upload)"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == '/api/upload':
                return self.handle_upload()
            elif path == '/api/background/task':
                return self.handle_submit_task()
            else:
                self.send_error(404, "Endpoint not found")
                
        except (BrokenPipeError, ConnectionAbortedError) as e:
            logger.warning(f"Cliente desconectou durante POST: {e}")
            return
        except Exception as e:
            logger.error(f"Erro no POST: {e}")
            try:
                self.send_error(500, f"Upload Error: {str(e)}")
            except (BrokenPipeError, ConnectionAbortedError) as e:
                logger.warning(f"Cliente desconectou durante erro de POST: {e}")
                return
    
    def do_DELETE(self):
        """Handler para requisições DELETE"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path.startswith('/api/upload/'):
                return self.handle_delete_upload(path)
            elif path.startswith('/api/background/task/'):
                return self.handle_cancel_task(path)
            else:
                self.send_error(404, "Endpoint not found")
                
        except (BrokenPipeError, ConnectionAbortedError) as e:
            logger.warning(f"Cliente desconectou durante DELETE: {e}")
            return
        except Exception as e:
            logger.error(f"Erro no DELETE: {e}")
            try:
                self.send_error(500, f"Delete Error: {str(e)}")
            except (BrokenPipeError, ConnectionAbortedError) as e:
                logger.warning(f"Cliente desconectou durante erro de DELETE: {e}")
                return
    
    def do_OPTIONS(self):
        """Handler para requisições OPTIONS (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def handle_upload(self):
        """Handler para upload de arquivos"""
        if not UPLOAD_AVAILABLE:
            self.send_error(503, "Upload system not available")
            return
        
        try:
            # Parse multipart form data manualmente
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Content-Type must be multipart/form-data")
                return
            
            # Extrair boundary
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if not boundary_match:
                self.send_error(400, "No boundary found in Content-Type")
                return
            
            boundary = boundary_match.group(1)
            
            # Ler dados do corpo
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "No content provided")
                return
            
            post_data = self.rfile.read(content_length)
            
            # Parse multipart data
            parts = self._parse_multipart(post_data, boundary)
            
            if 'file' not in parts:
                self.send_error(400, "No file provided")
                return
            
            file_data = parts['file']['data']
            filename = parts['file']['filename']
            
            if not filename:
                self.send_error(400, "No filename provided")
                return
            
            # Processar upload
            result = handle_upload_request(file_data, filename)
            
            # Enviar resposta
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            self.send_error(500, f"Upload Error: {str(e)}")
    
    def _parse_multipart(self, data: bytes, boundary: str) -> Dict:
        """Parse multipart form data manualmente"""
        parts = {}
        boundary_bytes = f'--{boundary}'.encode('utf-8')
        
        # Dividir por boundary
        sections = data.split(boundary_bytes)
        
        for section in sections[1:-1]:  # Ignorar primeiro e último
            if not section.strip():
                continue
            
            # Encontrar headers e body
            header_end = section.find(b'\r\n\r\n')
            if header_end == -1:
                continue
            
            headers_raw = section[:header_end]
            body = section[header_end + 4:]
            
            # Parse headers
            headers = {}
            for line in headers_raw.decode('utf-8').split('\r\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            # Extrair nome do campo
            content_disposition = headers.get('Content-Disposition', '')
            name_match = re.search(r'name="([^"]+)"', content_disposition)
            filename_match = re.search(r'filename="([^"]+)"', content_disposition)
            
            if name_match:
                field_name = name_match.group(1)
                filename = filename_match.group(1) if filename_match else None
                
                parts[field_name] = {
                    'data': body,
                    'filename': filename,
                    'headers': headers
                }
        
        return parts
    
    def handle_delete_upload(self, path):
        """Handler para deletar uploads"""
        if not UPLOAD_AVAILABLE:
            self.send_error(503, "Upload system not available")
            return
        
        try:
            # Extrair informações do path: /api/upload/videos/filename.mp4
            parts = path.split('/')
            if len(parts) != 5:
                self.send_error(400, "Invalid path format")
                return
            
            file_type = parts[3]
            filename = parts[4]
            
            result = handle_delete_request(filename, file_type)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erro ao deletar upload: {e}")
            self.send_error(500, f"Delete Error: {str(e)}")
    
    def handle_upload_file(self, path):
        """Handler para servir arquivos de upload"""
        try:
            # Remover /uploads/ do path
            file_path = path[9:]  # Remove '/uploads/'
            
            # Construir caminho completo
            full_path = DIRECTORY / "uploads" / file_path
            
            if full_path.exists() and full_path.is_file():
                # Determinar content-type
                content_type = 'application/octet-stream'
                if file_path.endswith('.mp4'):
                    content_type = 'video/mp4'
                elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif file_path.endswith('.png'):
                    content_type = 'image/png'
                elif file_path.endswith('.mp3'):
                    content_type = 'audio/mpeg'
                elif file_path.endswith('.pdf'):
                    content_type = 'application/pdf'
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
                
        except Exception as e:
            logger.error(f"Erro ao servir arquivo de upload: {e}")
            self.send_error(500, f"Error serving upload file: {str(e)}")
    
    def handle_api_request(self, path: str):
        """Handler para requisições da API"""
        try:
            if path == '/api/health':
                response = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": config.get("system", {}).get("version", "2.0.0"),
                    "uptime_seconds": time.time() - self.start_time,
                    "port": DEFAULT_PORT,
                    "host": HOST,
                    "upload_system": UPLOAD_AVAILABLE,
                    "background_processor": BACKGROUND_PROCESSOR_AVAILABLE
                }
            elif path == '/api/status':
                response = {
                    "total_users": 0,
                    "total_projects": 0,
                    "total_files": 0,
                    "total_videos": 0,
                    "system_metrics": {
                        "cpu_usage_percent": 0,
                        "memory_usage_percent": 0,
                        "disk_usage_percent": 0,
                        "available_memory_gb": 0,
                        "free_disk_gb": 0
                    },
                    "timestamp": datetime.now().isoformat(),
                    "port": DEFAULT_PORT,
                    "upload_system": UPLOAD_AVAILABLE
                }
            elif path == '/api/projects':
                response = {
                    "projects": [
                        {
                            "id": 1,
                            "name": "Projeto Demo",
                            "description": "Projeto de demonstração",
                            "status": "active",
                            "created_at": datetime.now().isoformat()
                        }
                    ],
                    "total": 1
                }
            elif path == '/api/videos':
                response = {
                    "videos": [
                        {
                            "id": 1,
                            "title": "Vídeo Demo",
                            "status": "completed",
                            "created_at": datetime.now().isoformat()
                        }
                    ],
                    "total": 1
                }
            elif path == '/api/audios':
                response = {
                    "audios": [
                        {
                            "id": 1,
                            "title": "Áudio Demo",
                            "status": "completed",
                            "created_at": datetime.now().isoformat()
                        }
                    ],
                    "total": 1
                }
            elif path == '/api/upload/files':
                if UPLOAD_AVAILABLE:
                    files = handle_list_request()
                    response = {"files": files, "total": len(files)}
                else:
                    response = {"error": "Upload system not available"}
            elif path == '/api/upload/stats':
                if UPLOAD_AVAILABLE:
                    response = handle_stats_request()
                else:
                    response = {"error": "Upload system not available"}
            elif path == '/api/background/tasks':
                if BACKGROUND_PROCESSOR_AVAILABLE:
                    tasks = get_all_tasks()
                    response = {
                        "tasks": [
                            {
                                "id": task.id,
                                "type": task.type.value,
                                "status": task.status.value,
                                "progress": task.progress,
                                "created_at": task.created_at.isoformat(),
                                "started_at": task.started_at.isoformat() if task.started_at else None,
                                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                                "result": task.result,
                                "error": task.error
                            }
                            for task in tasks
                        ],
                        "total": len(tasks)
                    }
                else:
                    response = {"error": "Background processor not available"}
            elif path == '/api/background/stats':
                if BACKGROUND_PROCESSOR_AVAILABLE:
                    response = get_processor_stats()
                else:
                    response = {"error": "Background processor not available"}
            elif path.startswith('/api/background/task/'):
                # Extrair task_id do path: /api/background/task/{task_id}
                task_id = path.split('/')[-1]
                if BACKGROUND_PROCESSOR_AVAILABLE:
                    task = get_task_status(task_id)
                    if task:
                        response = {
                            "id": task.id,
                            "type": task.type.value,
                            "status": task.status.value,
                            "progress": task.progress,
                            "created_at": task.created_at.isoformat(),
                            "started_at": task.started_at.isoformat() if task.started_at else None,
                            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                            "result": task.result,
                            "error": task.error,
                            "parameters": task.parameters
                        }
                    else:
                        response = {"error": "Task not found"}
                else:
                    response = {"error": "Background processor not available"}
            else:
                self.send_error(404, "API endpoint not found")
                return
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erro na API: {e}")
            self.send_error(500, f"API Error: {str(e)}")
    
    def handle_health(self):
        """Handler para health check"""
        try:
            # Verificar status do sistema
            system_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - self.start_time,
                "version": config.get("system", {}).get("version", "2.0.0"),
                "name": config.get("system", {}).get("name", "TecnoCursos AI"),
                "services": {
                    "upload": UPLOAD_AVAILABLE,
                    "background_processor": BACKGROUND_PROCESSOR_AVAILABLE,
                    "server": True
                },
                "memory": {
                    "available": True,
                    "directory": str(DIRECTORY)
                }
            }
            
            # Verificar se diretórios existem
            required_dirs = ["uploads", "static", "cache", "logs"]
            for dir_name in required_dirs:
                dir_path = DIRECTORY / dir_name
                system_status["memory"][dir_name] = dir_path.exists()
            
            response = {
                "success": True,
                "data": system_status
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                response_json = json.dumps(response, indent=2, ensure_ascii=False)
                self.wfile.write(response_json.encode('utf-8'))
            except UnicodeEncodeError:
                # Fallback para ASCII
                response_json = json.dumps(response, indent=2, ensure_ascii=True)
                self.wfile.write(response_json.encode('ascii'))
            except (BrokenPipeError, ConnectionAbortedError) as e:
                logger.warning(f"Cliente desconectou durante health check: {e}")
                return
                
        except Exception as e:
            logger.error(f"Erro no health check: {e}")
            try:
                self.send_error(500, f"Health Check Error: {str(e)}")
            except (BrokenPipeError, ConnectionAbortedError) as e:
                logger.warning(f"Cliente desconectou durante erro de health check: {e}")
                return
    
    def handle_docs(self):
        """Handler para documentação"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TecnoCursos AI - Documentação</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .endpoint {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .method {{ font-weight: bold; color: #007bff; }}
        .url {{ font-family: monospace; background: #e9ecef; padding: 2px 5px; }}
        .upload-section {{ background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>📚 TecnoCursos AI - Documentação da API</h1>
    
    <h2>🔗 Endpoints Disponíveis</h2>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/health</div>
        <p>Health check do sistema</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/health</div>
        <p>Health check da API</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/status</div>
        <p>Status do sistema</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/projects</div>
        <p>Lista de projetos</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/videos</div>
        <p>Lista de vídeos</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/audios</div>
        <p>Lista de áudios</p>
    </div>
    
    <h2>📤 Sistema de Upload</h2>
    
    <div class="upload-section">
        <div class="method">POST</div>
        <div class="url">/api/upload</div>
        <p>Upload de arquivos (multipart/form-data)</p>
        <p><strong>Tipos suportados:</strong> Vídeos, Áudios, Imagens, Documentos</p>
        <p><strong>Tamanho máximo:</strong> 100MB</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/upload/files</div>
        <p>Lista de arquivos enviados</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/upload/stats</div>
        <p>Estatísticas de uploads</p>
    </div>
    
    <div class="endpoint">
        <div class="method">DELETE</div>
        <div class="url">/api/upload/videos/{filename}</div>
        <p>Deletar arquivo específico</p>
    </div>
    
    <h2>⚡ Processamento em Background</h2>
    
    <div class="upload-section">
        <div class="method">POST</div>
        <div class="url">/api/background/task</div>
        <p>Submeter tarefa em background</p>
        <p><strong>Tipos:</strong> video_conversion, thumbnail_generation, audio_extraction, image_resize, document_processing, custom</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/background/tasks</div>
        <p>Lista de todas as tarefas</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/background/stats</div>
        <p>Estatísticas do processador</p>
    </div>
    
    <div class="endpoint">
        <div class="method">GET</div>
        <div class="url">/api/background/task/{task_id}</div>
        <p>Status de uma tarefa específica</p>
    </div>
    
    <div class="endpoint">
        <div class="method">DELETE</div>
        <div class="url">/api/background/task/{task_id}</div>
        <p>Cancelar uma tarefa</p>
    </div>
    
    <h2>🎬 Editor de Vídeo</h2>
    <p>Acesse <a href="/">http://localhost:8000/</a> para usar o editor de vídeo.</p>
    
    <h2>📊 Monitoramento</h2>
    <p>Health check: <a href="/health">http://localhost:8000/health</a></p>
</body>
</html>
            """
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erro na documentação: {e}")
            self.send_error(500, f"Documentation Error: {str(e)}")
    
    def handle_home(self):
        """Handler para página inicial"""
        try:
            # Verificar se existe index.html
            index_path = DIRECTORY / "index.html"
            if index_path.exists():
                return self.handle_static_file("/index.html")
            
            # HTML padrão se não existir index.html
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TecnoCursos AI - Editor de Vídeo</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 0; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 3em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card h3 {{
            color: #333;
            margin-top: 0;
        }}
        .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status.healthy {{ background: #d4edda; color: #155724; }}
        .status.warning {{ background: #fff3cd; color: #856404; }}
        .status.error {{ background: #f8d7da; color: #721c24; }}
        .api-links {{
            text-align: center;
            margin-top: 30px;
        }}
        .api-links a {{
            display: inline-block;
            margin: 10px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s ease;
        }}
        .api-links a:hover {{
            background: rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 TecnoCursos AI</h1>
            <p>Sistema Enterprise de Editor de Vídeo Inteligente</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 Status do Sistema</h3>
                <p><span class="status healthy">✅ Online</span></p>
                <p>Servidor rodando em <strong>http://localhost:{DEFAULT_PORT}</strong></p>
                <p>Versão: <strong>{config.get("system", {}).get("version", "2.0.0")}</strong></p>
            </div>
            
            <div class="card">
                <h3>🔧 Serviços</h3>
                <p><span class="status healthy">✅ API</span></p>
                <p><span class="status {'healthy' if UPLOAD_AVAILABLE else 'warning'}">{'✅' if UPLOAD_AVAILABLE else '⚠️'} Upload</span></p>
                <p><span class="status {'healthy' if BACKGROUND_PROCESSOR_AVAILABLE else 'warning'}">{'✅' if BACKGROUND_PROCESSOR_AVAILABLE else '⚠️'} Background Processor</span></p>
                <p><span class="status healthy">✅ Vídeo Generation</span></p>
            </div>
            
            <div class="card">
                <h3>📈 Estatísticas</h3>
                <p>Projetos: <strong>1</strong></p>
                <p>Vídeos: <strong>1</strong></p>
                <p>Áudios: <strong>1</strong></p>
            </div>
        </div>
        
        <div class="api-links">
            <a href="/health">🔍 Health Check</a>
            <a href="/docs">📚 Documentação</a>
            <a href="/api/health">🔧 API Health</a>
            <a href="/api/status">📊 Status</a>
            <a href="/api/upload/files">📤 Uploads</a>
        </div>
    </div>
</body>
</html>
            """
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erro na página inicial: {e}")
            self.send_error(500, f"Home Error: {str(e)}")
    
    def handle_favicon(self):
        """Handler para favicon"""
        try:
            favicon_path = DIRECTORY / "static" / "favicon.ico"
            if favicon_path.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'image/x-icon')
                self.end_headers()
                with open(favicon_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Favicon not found")
        except Exception as e:
            logger.error(f"Erro ao servir favicon: {e}")
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def handle_static_file(self, path: str):
        """Handler para arquivos estáticos"""
        try:
            # Remover leading slash
            if path.startswith('/'):
                path = path[1:]
            
            # Mapear caminhos
            if path == '':
                path = 'index.html'
            elif path == 'src/index.css':
                path = 'src/index.css'
            elif path == 'src/App.jsx':
                path = 'src/App.jsx'
            
            file_path = DIRECTORY / path
            
            if file_path.exists() and file_path.is_file():
                # Determinar content-type
                content_type = 'text/plain'
                if path.endswith('.html'):
                    content_type = 'text/html; charset=utf-8'
                elif path.endswith('.css'):
                    content_type = 'text/css'
                elif path.endswith('.js') or path.endswith('.jsx'):
                    content_type = 'application/javascript'
                elif path.endswith('.ico'):
                    content_type = 'image/x-icon'
                elif path.endswith('.png'):
                    content_type = 'image/png'
                elif path.endswith('.jpg') or path.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif path.endswith('.svg'):
                    content_type = 'image/svg+xml'
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
                
        except Exception as e:
            logger.error(f"Erro ao servir arquivo estático: {e}")
            self.send_error(500, f"Error serving file: {str(e)}")

    def handle_cancel_task(self, path):
        """Handler para cancelar tarefas"""
        if not BACKGROUND_PROCESSOR_AVAILABLE:
            self.send_error(503, "Background processor not available")
            return
        
        try:
            # Extrair task_id do path: /api/background/task/{task_id}
            task_id = path.split('/')[-1]
            
            success = cancel_task(task_id)
            
            if success:
                response = {"success": True, "message": f"Task {task_id} cancelled"}
            else:
                response = {"success": False, "error": "Task not found or cannot be cancelled"}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erro ao cancelar tarefa: {e}")
            self.send_error(500, f"Cancel Error: {str(e)}")
    
    def handle_submit_task(self):
        """Handler para submeter tarefas em background"""
        if not BACKGROUND_PROCESSOR_AVAILABLE:
            self.send_error(503, "Background processor not available")
            return
        
        try:
            # Ler dados do corpo da requisição
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            # Extrair parâmetros
            task_type_str = data.get('type', 'custom')
            parameters = data.get('parameters', {})
            
            # Converter string para TaskType
            try:
                task_type = TaskType(task_type_str)
            except ValueError:
                # Se não for um tipo válido, usar CUSTOM
                task_type = TaskType.CUSTOM
                parameters['custom_type'] = task_type_str
            
            # Submeter tarefa
            task_id = submit_background_task(task_type, parameters)
            
            response = {
                "success": True,
                "task_id": task_id,
                "type": task_type.value,
                "message": "Task submitted successfully"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erro ao submeter tarefa: {e}")
            self.send_error(500, f"Submit Error: {str(e)}")

def main():
    """Função principal"""
    try:
        # Criar diretórios
        create_directories()
        
        # Iniciar processador em background
        if BACKGROUND_PROCESSOR_AVAILABLE:
            start_background_processor()
            logger.info("Processador em background iniciado")
        
        # Encontrar porta disponível
        PORT = find_available_port(DEFAULT_PORT, 10)
        if PORT is None:
            print(f"❌ Não foi possível encontrar uma porta disponível entre {DEFAULT_PORT} e {DEFAULT_PORT + 9}")
            return
        
        print(f"🚀 Iniciando servidor na porta {PORT}...")
        
        # Configurar servidor
        with socketserver.TCPServer((HOST, PORT), TecnoCursosHandler) as httpd:
            print(f"Servidor TecnoCursos AI rodando em http://localhost:{PORT}")
            print(f"Servindo arquivos do diretório: {DIRECTORY}")
            print(f"Health check: http://localhost:{PORT}/health")
            print(f"Documentacao: http://localhost:{PORT}/docs")
            print(f"Editor: http://localhost:{PORT}/")
            print(f"API: http://localhost:{PORT}/api/health")
            print(f"Upload: {'Disponivel' if UPLOAD_AVAILABLE else 'Indisponivel'}")
            print(f"Background Processor: {'Disponivel' if BACKGROUND_PROCESSOR_AVAILABLE else 'Indisponivel'}")
            print("Pressione Ctrl+C para parar o servidor...")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuario")
        if BACKGROUND_PROCESSOR_AVAILABLE:
            stop_background_processor()
            print("Processador em background parado")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        if BACKGROUND_PROCESSOR_AVAILABLE:
            stop_background_processor()

if __name__ == "__main__":
    main() 