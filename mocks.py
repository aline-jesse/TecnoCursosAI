#!/usr/bin/env python3
"""
Sistema de Mocks Completo - TecnoCursos AI
Mocks para todas as integrações externas
"""

import json
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import base64
import uuid

class MockOpenAI:
    """Mock da API OpenAI para geração de conteúdo"""
    
    def __init__(self, api_key: str = "mock-key"):
        self.api_key = api_key
        
    def generate_course_content(self, topic: str, duration: int = 30) -> Dict[str, Any]:
        """Gera conteúdo de curso mockado"""
        time.sleep(1)  # Simular latência
        
        mock_content = {
            "title": f"Curso Completo de {topic}",
            "description": f"Aprenda {topic} do básico ao avançado com exemplos práticos e exercícios.",
            "duration_minutes": duration,
            "difficulty": random.choice(["Iniciante", "Intermediário", "Avançado"]),
            "modules": [
                {
                    "title": f"Introdução ao {topic}",
                    "content": f"Neste módulo você aprenderá os conceitos fundamentais de {topic}.",
                    "duration": 5,
                    "order": 1
                },
                {
                    "title": f"{topic} na Prática", 
                    "content": f"Aplicações práticas e exemplos reais de {topic}.",
                    "duration": 15,
                    "order": 2
                },
                {
                    "title": f"{topic} Avançado",
                    "content": f"Técnicas avançadas e melhores práticas em {topic}.",
                    "duration": 10,
                    "order": 3
                }
            ],
            "script": f"Olá! Bem-vindos ao curso de {topic}. Hoje vamos aprender sobre os conceitos fundamentais...",
            "keywords": [topic.lower(), "curso", "tutorial", "aprendizado"],
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": mock_content,
            "tokens_used": random.randint(500, 1500),
            "cost": round(random.uniform(0.01, 0.05), 4)
        }

class MockElevenLabs:
    """Mock da API ElevenLabs para Text-to-Speech"""
    
    def __init__(self, api_key: str = "mock-key"):
        self.api_key = api_key
        
    def text_to_speech(self, text: str, voice_id: str = "default") -> Dict[str, Any]:
        """Converte texto em áudio mockado"""
        time.sleep(2)  # Simular processamento
        
        # Simular arquivo de áudio
        audio_data = base64.b64encode(b"mock-audio-data").decode()
        
        return {
            "success": True,
            "audio_data": audio_data,
            "audio_url": f"https://mock-tts.com/audio/{uuid.uuid4()}.mp3",
            "duration_seconds": len(text) * 0.1,  # ~10 chars per second
            "voice_used": voice_id,
            "text_length": len(text),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """Retorna lista de vozes mockadas"""
        return [
            {"id": "voice_1", "name": "Maria", "language": "pt-BR", "gender": "female"},
            {"id": "voice_2", "name": "João", "language": "pt-BR", "gender": "male"},
            {"id": "voice_3", "name": "Ana", "language": "pt-BR", "gender": "female"},
            {"id": "voice_4", "name": "Carlos", "language": "pt-BR", "gender": "male"}
        ]

class MockDID:
    """Mock da API D-ID para geração de avatar"""
    
    def __init__(self, api_key: str = "mock-key"):
        self.api_key = api_key
        
    def create_video(self, script: str, avatar_id: str = "default") -> Dict[str, Any]:
        """Cria vídeo com avatar mockado"""
        time.sleep(5)  # Simular processamento
        
        video_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "video_id": video_id,
            "video_url": f"https://mock-avatar.com/videos/{video_id}.mp4",
            "thumbnail_url": f"https://mock-avatar.com/thumbs/{video_id}.jpg",
            "duration_seconds": len(script) * 0.08,  # ~12.5 chars per second
            "avatar_used": avatar_id,
            "script_length": len(script),
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
    
    def get_avatars(self) -> List[Dict[str, Any]]:
        """Retorna lista de avatares mockados"""
        return [
            {"id": "avatar_1", "name": "Professora Clara", "type": "female", "style": "professional"},
            {"id": "avatar_2", "name": "Professor Roberto", "type": "male", "style": "casual"},
            {"id": "avatar_3", "name": "Dra. Sofia", "type": "female", "style": "academic"},
            {"id": "avatar_4", "name": "Prof. Miguel", "type": "male", "style": "friendly"}
        ]

class MockEmailService:
    """Mock do serviço de email"""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.config = smtp_config
        self.sent_emails = []
        
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        """Envia email mockado"""
        time.sleep(0.5)  # Simular envio
        
        email_data = {
            "id": str(uuid.uuid4()),
            "to": to,
            "subject": subject,
            "body": body,
            "html": html,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        
        self.sent_emails.append(email_data)
        
        return {
            "success": True,
            "message_id": email_data["id"],
            "status": "sent"
        }
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Retorna emails enviados"""
        return self.sent_emails

class MockDatabase:
    """Mock do banco de dados"""
    
    def __init__(self):
        self.data = {
            "users": {},
            "courses": {},
            "videos": {},
            "analytics": []
        }
        
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria usuário mockado"""
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "created_at": datetime.now().isoformat(),
            **user_data
        }
        self.data["users"][user_id] = user
        return user
    
    def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria curso mockado"""
        course_id = str(uuid.uuid4())
        course = {
            "id": course_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            **course_data
        }
        self.data["courses"][course_id] = course
        return course
    
    def create_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria vídeo mockado"""
        video_id = str(uuid.uuid4())
        video = {
            "id": video_id,
            "created_at": datetime.now().isoformat(),
            "status": "processing",
            **video_data
        }
        self.data["videos"][video_id] = video
        return video
    
    def log_analytics(self, event: str, data: Dict[str, Any]):
        """Log de analytics mockado"""
        analytics_entry = {
            "id": str(uuid.uuid4()),
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.data["analytics"].append(analytics_entry)

class MockRedis:
    """Mock do Redis para cache"""
    
    def __init__(self):
        self.cache = {}
        
    def get(self, key: str) -> Optional[str]:
        """Obtém valor do cache"""
        item = self.cache.get(key)
        if item and item["expires"] > datetime.now():
            return item["value"]
        elif item:
            del self.cache[key]
        return None
    
    def set(self, key: str, value: str, ttl: int = 3600):
        """Define valor no cache"""
        self.cache[key] = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=ttl)
        }
    
    def delete(self, key: str):
        """Remove valor do cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()

class MockPaymentService:
    """Mock do serviço de pagamento"""
    
    def __init__(self):
        self.transactions = []
        
    def create_payment(self, amount: float, currency: str = "BRL", description: str = "") -> Dict[str, Any]:
        """Cria pagamento mockado"""
        time.sleep(1)  # Simular processamento
        
        transaction = {
            "id": str(uuid.uuid4()),
            "amount": amount,
            "currency": currency,
            "description": description,
            "status": random.choice(["approved", "pending", "declined"]),
            "created_at": datetime.now().isoformat()
        }
        
        self.transactions.append(transaction)
        
        return {
            "success": transaction["status"] != "declined",
            "transaction": transaction,
            "payment_url": f"https://mock-payment.com/pay/{transaction['id']}"
        }

class MockCloudStorage:
    """Mock do armazenamento em nuvem"""
    
    def __init__(self):
        self.files = {}
        
    def upload_file(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Upload de arquivo mockado"""
        time.sleep(0.5)  # Simular upload
        
        file_id = str(uuid.uuid4())
        file_info = {
            "id": file_id,
            "path": file_path,
            "size": len(content),
            "url": f"https://mock-storage.com/files/{file_id}",
            "uploaded_at": datetime.now().isoformat()
        }
        
        self.files[file_id] = file_info
        
        return {
            "success": True,
            "file": file_info
        }
    
    def delete_file(self, file_id: str) -> bool:
        """Deletar arquivo mockado"""
        if file_id in self.files:
            del self.files[file_id]
            return True
        return False

# Instâncias globais dos mocks
mock_openai = MockOpenAI()
mock_tts = MockElevenLabs()
mock_avatar = MockDID()
mock_email = MockEmailService({})
mock_db = MockDatabase()
mock_redis = MockRedis()
mock_payment = MockPaymentService()
mock_storage = MockCloudStorage()

def get_mock_service(service_name: str):
    """Retorna serviço mock pelo nome"""
    services = {
        "openai": mock_openai,
        "tts": mock_tts,
        "avatar": mock_avatar,
        "email": mock_email,
        "database": mock_db,
        "redis": mock_redis,
        "payment": mock_payment,
        "storage": mock_storage
    }
    return services.get(service_name)

if __name__ == "__main__":
    print("🎭 TecnoCursos AI - Sistema de Mocks")
    print("="*40)
    
    # Testar mocks
    print("🤖 Testando OpenAI...")
    result = mock_openai.generate_course_content("Python")
    print(f"✅ Curso gerado: {result['data']['title']}")
    
    print("\n🔊 Testando TTS...")
    audio = mock_tts.text_to_speech("Olá, mundo!")
    print(f"✅ Áudio gerado: {audio['duration_seconds']}s")
    
    print("\n🎬 Testando Avatar...")
    video = mock_avatar.create_video("Bem-vindos ao curso!")
    print(f"✅ Vídeo gerado: {video['video_id']}")
    
    print("\n📧 Testando Email...")
    email_result = mock_email.send_email("test@test.com", "Teste", "Conteúdo")
    print(f"✅ Email enviado: {email_result['message_id']}")
    
    print("\n🗃️ Testando Database...")
    user = mock_db.create_user({"name": "João", "email": "joao@test.com"})
    print(f"✅ Usuário criado: {user['id']}")
    
    print("\n🚀 Todos os mocks funcionando!")
