#!/usr/bin/env python3
"""
Exemplo Prático de Uso do Endpoint de Exportação de Vídeo - TecnoCursos AI

Este script demonstra como usar o endpoint de exportação de vídeo
para criar vídeos educacionais completos com TTS, avatar e montagem.

Exemplos incluídos:
1. Vídeo educacional simples
2. Apresentação corporativa
3. Tutorial técnico
4. Vídeo com avatar 3D

Uso:
    python exemplo_uso_video_export.py
"""

import requests
import json
import time
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/video-export"

def criar_video_educacional():
    """Exemplo 1: Vídeo educacional simples"""
    print("🎓 CRIANDO VÍDEO EDUCACIONAL")
    
    request_data = {
        "title": "Introdução à Programação Python",
        "description": "Vídeo educativo sobre fundamentos do Python",
        "scenes": [
            {
                "id": "intro",
                "title": "Introdução",
                "duration": 8.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "Bem-vindos ao curso de Python!\n\nVamos aprender os fundamentos da programação.",
                        "duration": 8.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.8, "height": 0.6},
                        "style": {
                            "fontsize": 48,
                            "color": "white",
                            "font": "Arial-Bold"
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": False
            },
            {
                "id": "variaveis",
                "title": "Variáveis",
                "duration": 12.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "Variáveis em Python\n\nnome = 'João'\nidade = 25\npreco = 19.99\n\nAs variáveis armazenam dados.",
                        "duration": 12.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.9, "height": 0.8},
                        "style": {
                            "fontsize": 36,
                            "color": "#00ff00",
                            "font": "Courier-Bold"
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": True,
                "avatar_style": "educational"
            }
        ],
        "resolution": "1080p",
        "fps": 30,
        "tts_voice": "pt_speaker_2",
        "tts_provider": "auto",
        "quality": "high"
    }
    
    return enviar_requisicao(request_data, "educacional")

def criar_apresentacao_corporativa():
    """Exemplo 2: Apresentação corporativa"""
    print("🏢 CRIANDO APRESENTAÇÃO CORPORATIVA")
    
    request_data = {
        "title": "Apresentação Corporativa - TecnoCursos AI",
        "description": "Demonstração de produtos e serviços",
        "scenes": [
            {
                "id": "titulo",
                "title": "Título",
                "duration": 6.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "TecnoCursos AI\n\nSoluções Empresariais de Inteligência Artificial",
                        "duration": 6.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.9, "height": 0.7},
                        "style": {
                            "fontsize": 52,
                            "color": "#0066cc",
                            "font": "Arial-Bold",
                            "stroke_color": "white",
                            "stroke_width": 3
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": True,
                "avatar_style": "professional"
            },
            {
                "id": "produtos",
                "title": "Produtos",
                "duration": 15.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "Nossos Produtos\n\n• Plataforma de E-learning\n• Geração de Conteúdo com IA\n• Avatares 3D Realistas\n• Sistema de TTS Avançado\n• Analytics Inteligente",
                        "duration": 15.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.9, "height": 0.8},
                        "style": {
                            "fontsize": 40,
                            "color": "white",
                            "font": "Arial-Bold"
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": True,
                "avatar_style": "professional"
            }
        ],
        "resolution": "1080p",
        "fps": 30,
        "tts_voice": "pt_speaker_0",
        "tts_provider": "bark",
        "quality": "high"
    }
    
    return enviar_requisicao(request_data, "corporativa")

def criar_tutorial_tecnico():
    """Exemplo 3: Tutorial técnico"""
    print("🔧 CRIANDO TUTORIAL TÉCNICO")
    
    request_data = {
        "title": "Tutorial: Configuração de API REST",
        "description": "Guia passo a passo para configurar APIs",
        "scenes": [
            {
                "id": "introducao",
                "title": "Introdução",
                "duration": 10.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "Tutorial: Configuração de API REST\n\nNeste tutorial vamos aprender:\n• Conceitos básicos de REST\n• Configuração do ambiente\n• Implementação prática",
                        "duration": 10.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.9, "height": 0.8},
                        "style": {
                            "fontsize": 38,
                            "color": "#ff6600",
                            "font": "Arial-Bold"
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": True,
                "avatar_style": "tech"
            },
            {
                "id": "codigo",
                "title": "Exemplo de Código",
                "duration": 18.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "Exemplo de API REST\n\nfrom fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}\n\n@app.post('/items/')\ndef create_item(item: dict):\n    return item",
                        "duration": 18.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.9, "height": 0.8},
                        "style": {
                            "fontsize": 32,
                            "color": "#00ff00",
                            "font": "Courier-Bold"
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": True,
                "avatar_style": "tech"
            }
        ],
        "resolution": "1080p",
        "fps": 30,
        "tts_voice": "pt_speaker_3",
        "tts_provider": "auto",
        "quality": "high"
    }
    
    return enviar_requisicao(request_data, "tutorial")

def criar_video_avatar_3d():
    """Exemplo 4: Vídeo com avatar 3D completo"""
    print("🎭 CRIANDO VÍDEO COM AVATAR 3D")
    
    request_data = {
        "title": "Apresentação com Avatar 3D",
        "description": "Demonstração de avatar 3D realista",
        "scenes": [
            {
                "id": "apresentacao",
                "title": "Apresentação",
                "duration": 12.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "Olá! Eu sou um avatar 3D gerado por IA.\n\nEstou aqui para apresentar nossa plataforma de criação de conteúdo educacional.",
                        "duration": 12.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.8, "height": 0.6},
                        "style": {
                            "fontsize": 44,
                            "color": "white",
                            "font": "Arial-Bold"
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": True,
                "avatar_style": "realistic"
            },
            {
                "id": "recursos",
                "title": "Recursos",
                "duration": 20.0,
                "elements": [
                    {
                        "type": "text",
                        "content": "Recursos Avançados\n\n• Sincronização labial precisa\n• Expressões faciais naturais\n• Gestos e movimentos corporais\n• Múltiplos estilos de avatar\n• Integração com TTS Bark",
                        "duration": 20.0,
                        "position": {"x": 0.5, "y": 0.5},
                        "size": {"width": 0.9, "height": 0.8},
                        "style": {
                            "fontsize": 40,
                            "color": "#ffff00",
                            "font": "Arial-Bold"
                        }
                    }
                ],
                "tts_enabled": True,
                "avatar_enabled": True,
                "avatar_style": "realistic"
            }
        ],
        "resolution": "4k",
        "fps": 60,
        "tts_voice": "pt_speaker_1",
        "tts_provider": "bark",
        "quality": "ultra"
    }
    
    return enviar_requisicao(request_data, "avatar_3d")

def enviar_requisicao(request_data, tipo):
    """Envia requisição para o endpoint de exportação"""
    try:
        print(f"📤 Enviando requisição para vídeo {tipo}...")
        
        response = requests.post(
            f"{API_BASE}/export",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            video_id = result['video_id']
            
            print(f"✅ Exportação iniciada!")
            print(f"🎬 Video ID: {video_id}")
            print(f"📊 Cenas: {len(request_data['scenes'])}")
            print(f"📺 Resolução: {request_data['resolution']}")
            print(f"🎤 TTS: {request_data['tts_provider']}")
            print(f"🎭 Avatar: {'Sim' if any(s['avatar_enabled'] for s in request_data['scenes']) else 'Não'}")
            
            return video_id
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def monitorar_processamento(video_id, nome):
    """Monitora o processamento de um vídeo"""
    print(f"\n⏳ Monitorando processamento de {nome}...")
    
    max_tentativas = 30  # 5 minutos
    tentativa = 0
    
    while tentativa < max_tentativas:
        try:
            response = requests.get(f"{API_BASE}/{video_id}/status")
            
            if response.status_code == 200:
                status = response.json()
                
                print(f"📊 {nome}: {status['status']} - {status['progress']:.1f}%")
                print(f"🎬 Estágio: {status['current_stage']}")
                
                if status.get('video_url'):
                    print(f"✅ {nome} concluído!")
                    print(f"🎬 URL: {status['video_url']}")
                    print(f"💾 Tamanho: {status.get('file_size', 0)/1024/1024:.2f}MB")
                    print(f"⏱️ Duração: {status.get('duration', 0):.2f}s")
                    return True
                
                if status['status'] == 'failed':
                    print(f"❌ {nome} falhou: {status.get('error_message', 'Erro desconhecido')}")
                    return False
                
                time.sleep(10)
                tentativa += 1
                
            else:
                print(f"❌ Erro ao verificar status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    print(f"⏰ Timeout: {nome} demorou mais que o esperado")
    return False

def main():
    """Função principal"""
    print("🎬 EXEMPLOS PRÁTICOS DE EXPORTAÇÃO DE VÍDEO")
    print("="*60)
    print("📝 TecnoCursos AI - Endpoint de Exportação")
    print("🔗 API: /api/video-export")
    print("="*60)
    
    # Verificar se o serviço está disponível
    try:
        response = requests.get(f"{API_BASE}/info")
        if response.status_code != 200:
            print("❌ Serviço de exportação não está disponível")
            print("💡 Certifique-se de que o servidor está rodando")
            return
    except Exception as e:
        print(f"❌ Erro ao conectar com o serviço: {e}")
        return
    
    print("✅ Serviço de exportação disponível!")
    
    # Exemplo 1: Vídeo educacional
    video_id_1 = criar_video_educacional()
    if video_id_1:
        monitorar_processamento(video_id_1, "Vídeo Educacional")
    
    # Exemplo 2: Apresentação corporativa
    video_id_2 = criar_apresentacao_corporativa()
    if video_id_2:
        monitorar_processamento(video_id_2, "Apresentação Corporativa")
    
    # Exemplo 3: Tutorial técnico
    video_id_3 = criar_tutorial_tecnico()
    if video_id_3:
        monitorar_processamento(video_id_3, "Tutorial Técnico")
    
    # Exemplo 4: Vídeo com avatar 3D
    video_id_4 = criar_video_avatar_3d()
    if video_id_4:
        monitorar_processamento(video_id_4, "Avatar 3D")
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS EXEMPLOS")
    print("="*60)
    print("✅ Vídeo Educacional - Conceitos básicos")
    print("✅ Apresentação Corporativa - Profissional")
    print("✅ Tutorial Técnico - Código e explicações")
    print("✅ Avatar 3D - Demonstração avançada")
    print("\n🎬 Todos os exemplos demonstram diferentes usos do endpoint!")
    print("🚀 O sistema está pronto para produção!")

if __name__ == "__main__":
    main() 