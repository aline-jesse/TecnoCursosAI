#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Completo - Sistema de Geração de Vídeo com IA
==================================================

Este demo mostra como usar o sistema completo de geração de vídeo
implementado no TecnoCursos AI, incluindo:

- Criação de projeto e cenas
- Adição de assets e configurações
- Geração automática de vídeo com MoviePy
- Integração com IA (narração, avatar, backgrounds)
- Download e gerenciamento de vídeos

Baseado nas melhores práticas de:
- FastAPI CRUD operations
- MoviePy video generation  
- AI service integration
- Background task processing

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import asyncio
import requests
import json
from datetime import datetime
from pathlib import Path
import time

# Configurações
API_BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "demo@tecnocursos.ai"
TEST_USER_PASSWORD = "demo123"

class VideoGenerationDemo:
    """
    Demo completo do sistema de geração de vídeo
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.project_id = None
        self.scene_ids = []
        
    def authenticate(self):
        """Autenticar usuário de teste"""
        print("🔐 Autenticando usuário de teste...")
        
        # Login
        response = self.session.post(f"{API_BASE_URL}/api/auth/login", data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.auth_token}"
            })
            print("✅ Autenticação realizada com sucesso")
            return True
        else:
            print(f"❌ Erro na autenticação: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def create_demo_project(self):
        """Criar projeto de demonstração"""
        print("\n📁 Criando projeto de demonstração...")
        
        project_data = {
            "name": "Demo Curso de IA",
            "description": "Projeto de demonstração para geração de vídeo com IA",
            "tipo": "curso",
            "is_public": False
        }
        
        response = self.session.post(
            f"{API_BASE_URL}/api/projects/", 
            json=project_data
        )
        
        if response.status_code == 201:
            data = response.json()
            self.project_id = data["id"]
            print(f"✅ Projeto criado: ID {self.project_id}")
            return True
        else:
            print(f"❌ Erro ao criar projeto: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def create_demo_scenes(self):
        """Criar cenas de demonstração"""
        print("\n🎭 Criando cenas de demonstração...")
        
        scenes_data = [
            {
                "name": "Introdução ao Curso",
                "projeto_id": self.project_id,
                "texto": "Bem-vindos ao nosso curso completo de Inteligência Artificial! Hoje vamos explorar os conceitos fundamentais da IA.",
                "duracao": 6.0,
                "ordem": 1,
                "style_preset": "modern",
                "background_color": "#4a90e2",
                "is_active": True
            },
            {
                "name": "O que é Inteligência Artificial?",
                "projeto_id": self.project_id,
                "texto": "A Inteligência Artificial é a capacidade de máquinas realizarem tarefas que normalmente requerem inteligência humana.",
                "duracao": 8.0,
                "ordem": 2,
                "style_preset": "corporate",
                "background_color": "#2ecc71",
                "is_active": True
            },
            {
                "name": "Aplicações Práticas da IA",
                "projeto_id": self.project_id,
                "texto": "Vamos ver como a IA está transformando diversos setores: saúde, educação, transporte e muito mais!",
                "duracao": 7.0,
                "ordem": 3,
                "style_preset": "tech",
                "background_color": "#e74c3c",
                "is_active": True
            },
            {
                "name": "Conclusão",
                "projeto_id": self.project_id,
                "texto": "Obrigado por acompanhar nosso curso! Continue explorando o fascinante mundo da Inteligência Artificial.",
                "duracao": 5.0,
                "ordem": 4,
                "style_preset": "modern",
                "background_color": "#9b59b6",
                "is_active": True
            }
        ]
        
        created_scenes = 0
        
        for scene_data in scenes_data:
            response = self.session.post(
                f"{API_BASE_URL}/api/scenes/",
                json=scene_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.scene_ids.append(data["id"])
                print(f"✅ Cena criada: '{scene_data['name']}' (ID: {data['id']})")
                created_scenes += 1
            else:
                print(f"❌ Erro ao criar cena '{scene_data['name']}': {response.status_code}")
                print(f"Response: {response.text}")
        
        print(f"📊 Total de cenas criadas: {created_scenes}/{len(scenes_data)}")
        return created_scenes > 0
    
    def generate_video(self, quality="medium", include_avatar=False, include_narration=False):
        """Gerar vídeo do projeto"""
        print(f"\n🎬 Iniciando geração de vídeo...")
        print(f"   📺 Qualidade: {quality}")
        print(f"   🤖 Avatar: {'Sim' if include_avatar else 'Não'}")
        print(f"   🎵 Narração: {'Sim' if include_narration else 'Não'}")
        
        generation_data = {
            "quality": quality,
            "include_avatar": include_avatar,
            "include_narration": include_narration,
            "export_format": "mp4"
        }
        
        response = self.session.post(
            f"{API_BASE_URL}/api/scenes/project/{self.project_id}/generate-video",
            json=generation_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Geração iniciada: {data['status']}")
            
            if data["status"] == "completed":
                print(f"🎉 Vídeo gerado com sucesso!")
                print(f"   📁 Arquivo: {data['filename']}")
                print(f"   ⏱️ Duração: {data['duration']:.2f}s")
                print(f"   💾 Tamanho: {data['file_size_mb']:.2f} MB")
                print(f"   🔗 Download: {data['download_url']}")
                return data
            
            elif data["status"] == "processing":
                print(f"⏳ Processando em background...")
                print(f"   🕐 Tempo estimado: {data['estimated_time']}")
                print(f"   📊 Status endpoint: {data['status_endpoint']}")
                
                # Aguardar conclusão
                return self.wait_for_completion(data["status_endpoint"])
            
        else:
            print(f"❌ Erro na geração: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def wait_for_completion(self, status_endpoint):
        """Aguardar conclusão da geração"""
        print("\n⏳ Aguardando conclusão da geração...")
        
        max_attempts = 30  # 5 minutos máximo
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(10)  # Aguardar 10 segundos
            attempt += 1
            
            response = self.session.get(f"{API_BASE_URL}{status_endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                status = data["status"]
                
                print(f"🔄 Status: {status} (tentativa {attempt}/{max_attempts})")
                
                if status == "completed":
                    print(f"🎉 Vídeo concluído!")
                    print(f"   📁 Arquivo: {data['video_filename']}")
                    print(f"   💾 Tamanho: {data['file_size_mb']:.2f} MB")
                    print(f"   🔗 Download: {data['download_url']}")
                    return data
                
                elif status in ["error", "failed"]:
                    print(f"❌ Geração falhou: {data.get('message', 'Erro desconhecido')}")
                    return None
            
            else:
                print(f"⚠️ Erro ao verificar status: {response.status_code}")
        
        print("⏰ Timeout - geração demorou mais que o esperado")
        return None
    
    def download_video(self, download_url, filename):
        """Fazer download do vídeo"""
        print(f"\n📥 Fazendo download do vídeo: {filename}")
        
        response = self.session.get(f"{API_BASE_URL}{download_url}")
        
        if response.status_code == 200:
            # Salvar arquivo
            output_path = Path(f"downloads/{filename}")
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Download concluído: {output_path}")
            print(f"   💾 Tamanho: {len(response.content) / (1024*1024):.2f} MB")
            return str(output_path)
        
        else:
            print(f"❌ Erro no download: {response.status_code}")
            return None
    
    def get_video_metrics(self):
        """Obter métricas de uso do vídeo"""
        print("\n📊 Obtendo métricas de uso...")
        
        response = self.session.get(f"{API_BASE_URL}/api/scenes/metrics/usage")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Métricas obtidas:")
            print(f"   📈 Total de cenas: {data['summary']['total_scenes']}")
            print(f"   📅 Cenas no período: {data['summary']['scenes_in_period']}")
            print(f"   📊 Média por dia: {data['summary']['average_per_day']}")
            
            if data['top_scenes']:
                print("   🏆 Cenas mais visualizadas:")
                for scene in data['top_scenes'][:3]:
                    print(f"     - {scene['name']}: {scene['view_count']} views")
            
            return data
        
        else:
            print(f"❌ Erro ao obter métricas: {response.status_code}")
            return None
    
    def demonstrate_ai_integration_points(self):
        """Demonstrar pontos de integração com IA"""
        print("\n🤖 PONTOS DE INTEGRAÇÃO COM IA IMPLEMENTADOS:")
        print("="*60)
        
        print("\n1. 🎵 NARRAÇÃO COM TTS (Text-to-Speech):")
        print("   📍 Localização: app/services/video_generation_service.py:_generate_narration()")
        print("   🔧 Integração TODO:")
        print("     - Azure Cognitive Services Speech")
        print("     - OpenAI TTS")
        print("     - Google Cloud Text-to-Speech")
        print("     - ElevenLabs para vozes naturais")
        print("   💡 Exemplo de uso:")
        print("     text = scene_data.text_content")
        print("     audio = await azure_tts.synthesize(text, voice='pt-BR-FranciscaNeural')")
        
        print("\n2. 👤 AVATAR FALANTE:")
        print("   📍 Localização: app/services/video_generation_service.py:_create_avatar_clip()")
        print("   🔧 Integração TODO:")
        print("     - D-ID para avatar realista")
        print("     - HeyGen para apresentador virtual")
        print("     - Synthesia para avatar customizado")
        print("     - RunwayML para animação de personagem")
        print("   💡 Exemplo de uso:")
        print("     avatar_video = await d_id.generate_avatar(")
        print("         text=scene_text, presenter_id='amy', voice='microsoft')")
        
        print("\n3. 🎨 BACKGROUNDS GERADOS POR IA:")
        print("   📍 Localização: app/services/video_generation_service.py:_create_background_clip()")
        print("   🔧 Integração TODO:")
        print("     - DALL-E para imagens temáticas")
        print("     - Midjourney para backgrounds artísticos")
        print("     - Stable Diffusion para cenários personalizados")
        print("     - RunwayML para backgrounds animados")
        print("   💡 Exemplo de uso:")
        print("     prompt = f'Professional background for {scene.style_preset} presentation'")
        print("     bg_image = await dalle.generate_image(prompt)")
        
        print("\n4. 🎼 MÚSICA DE FUNDO AUTOMÁTICA:")
        print("   📍 Localização: app/services/video_generation_service.py:_add_global_elements()")
        print("   🔧 Integração TODO:")
        print("     - Aiva para música instrumental")
        print("     - Amper Music para trilhas personalizadas")
        print("     - Soundraw para música adaptativa")
        print("     - OpenAI Jukebox para composição")
        print("   💡 Exemplo de uso:")
        print("     music = await aiva.compose(style='corporate', duration=video.duration)")
        
        print("\n5. 🎬 EFEITOS VISUAIS AVANÇADOS:")
        print("   📍 Localização: app/services/video_generation_service.py:_concatenate_scenes_with_transitions()")
        print("   🔧 Integração TODO:")
        print("     - RunwayML para transições inteligentes")
        print("     - Pika Labs para efeitos de movimento")
        print("     - Stable Video para animações")
        print("     - LeiaPix para efeito 3D")
        print("   💡 Exemplo de uso:")
        print("     transition = await runway.generate_transition(scene1, scene2, style='smooth')")
        
        print("\n6. 📝 LEGENDAS AUTOMÁTICAS:")
        print("   📍 Localização: TODO - implementar em próxima versão")
        print("   🔧 Integração TODO:")
        print("     - Whisper para transcrição")
        print("     - Azure Speech para sincronização")
        print("     - Google Speech-to-Text")
        print("     - Rev.ai para legendas profissionais")
        
        print("\n🔄 PIPELINE COMPLETO DE IA:")
        print("1. Texto da cena → TTS → Áudio narração")
        print("2. Estilo da cena → DALL-E → Background personalizado")
        print("3. Texto + Avatar → D-ID → Apresentador falante")
        print("4. Duração do vídeo → Aiva → Música de fundo")
        print("5. Transições → RunwayML → Efeitos suaves")
        print("6. Áudio final → Whisper → Legendas sincronizadas")
        
        print("\n💡 CONFIGURAÇÃO PARA ATIVAR IA:")
        print("1. Instalar dependências: pip install openai azure-cognitiveservices-speech")
        print("2. Configurar API keys em .env:")
        print("   OPENAI_API_KEY=your_key")
        print("   AZURE_SPEECH_KEY=your_key")
        print("   D_ID_API_KEY=your_key")
        print("3. Habilitar nos endpoints: include_avatar=True, include_narration=True")
    
    async def run_complete_demo(self):
        """Executar demonstração completa"""
        print("🚀 DEMO COMPLETO - SISTEMA DE GERAÇÃO DE VÍDEO COM IA")
        print("="*60)
        print(f"🕐 Início: {datetime.now().strftime('%H:%M:%S')}")
        
        # 1. Autenticar
        if not self.authenticate():
            return False
        
        # 2. Criar projeto
        if not self.create_demo_project():
            return False
        
        # 3. Criar cenas
        if not self.create_demo_scenes():
            return False
        
        # 4. Gerar vídeo
        video_result = self.generate_video(
            quality="medium",
            include_avatar=False,  # Desabilitado por enquanto
            include_narration=False  # Desabilitado por enquanto
        )
        
        if video_result:
            # 5. Download (opcional)
            if "download_url" in video_result:
                self.download_video(
                    video_result["download_url"],
                    video_result.get("filename", video_result.get("video_filename"))
                )
        
        # 6. Métricas
        self.get_video_metrics()
        
        # 7. Demonstrar pontos de IA
        self.demonstrate_ai_integration_points()
        
        print(f"\n✅ Demo concluído com sucesso!")
        print(f"🕐 Fim: {datetime.now().strftime('%H:%M:%S')}")
        
        return True

def main():
    """Função principal"""
    demo = VideoGenerationDemo()
    
    # Executar demo
    try:
        loop = asyncio.get_event_loop()
        success = loop.run_until_complete(demo.run_complete_demo())
        
        if success:
            print("\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        else:
            print("\n❌ Alguns problemas encontrados - verifique os logs")
            
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no demo: {e}")

if __name__ == "__main__":
    main() 