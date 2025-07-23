"""
Demonstração das APIs do TecnoCursosAI
Este script testa as principais funcionalidades do sistema
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprime um separador de seção"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health_check():
    """Testa o endpoint de health check"""
    print_section("1. HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Sistema está funcionando!")
            print(f"   - Status: {data['status']}")
            print(f"   - Versão: {data['version']}")
            print(f"   - Uptime: {data['uptime_seconds']:.2f} segundos")
            print(f"   - Banco de dados: {data['database_status']}")
            
            # Mostra serviços disponíveis
            print("\n   Serviços disponíveis:")
            for service, status in data['services'].items():
                emoji = "✅" if status == "available" else "❌"
                print(f"   {emoji} {service}: {status}")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

def test_tts_generation():
    """Testa a geração de áudio TTS"""
    print_section("2. GERAÇÃO DE ÁUDIO (TTS)")
    
    texto = "Olá! Bem-vindo ao TecnoCursosAI. Este é um teste de conversão de texto em fala."
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/tts/generate",
            json={
                "text": texto,
                "voice": "pt-BR-AntonioNeural",
                "speed": 1.0,
                "format": "mp3"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Áudio gerado com sucesso!")
            print(f"   - Arquivo: {data.get('filename', 'N/A')}")
            print(f"   - URL: {data.get('url', 'N/A')}")
            print(f"   - Duração: {data.get('duration', 'N/A')} segundos")
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_scene_management():
    """Testa o gerenciamento de cenas"""
    print_section("3. GERENCIAMENTO DE CENAS")
    
    # Criar uma nova cena
    print("📝 Criando nova cena...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/scenes",
            json={
                "title": f"Cena de Teste - {datetime.now().strftime('%H:%M:%S')}",
                "duration": 10,
                "description": "Cena criada automaticamente para teste",
                "elements": []
            }
        )
        
        if response.status_code in [200, 201]:
            scene_data = response.json()
            scene_id = scene_data.get('id')
            print(f"✅ Cena criada com ID: {scene_id}")
            
            # Listar cenas
            print("\n📋 Listando cenas...")
            list_response = requests.get(f"{BASE_URL}/api/scenes")
            if list_response.status_code == 200:
                scenes = list_response.json()
                print(f"✅ Total de cenas: {len(scenes)}")
                for i, scene in enumerate(scenes[:3]):  # Mostra até 3 cenas
                    print(f"   {i+1}. {scene.get('title', 'Sem título')} (ID: {scene.get('id')})")
        else:
            print(f"❌ Erro ao criar cena: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_analytics():
    """Testa o endpoint de analytics"""
    print_section("4. ANALYTICS")
    
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/overview")
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics obtido com sucesso!")
            print(f"   - Total de usuários: {data.get('total_users', 0)}")
            print(f"   - Total de projetos: {data.get('total_projects', 0)}")
            print(f"   - Total de vídeos: {data.get('total_videos', 0)}")
            print(f"   - Uso de armazenamento: {data.get('storage_used_mb', 0):.2f} MB")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_modern_ai():
    """Testa as funcionalidades de IA moderna"""
    print_section("5. IA MODERNA")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/modern-ai/prompt",
            json={
                "prompt": "Crie um roteiro curto para um vídeo educacional sobre Python",
                "max_tokens": 150,
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ IA processou com sucesso!")
            print(f"   - Resposta: {data.get('response', 'N/A')[:100]}...")
            print(f"   - Tokens usados: {data.get('tokens_used', 'N/A')}")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("  🚀 DEMONSTRAÇÃO DAS APIs DO TECNOCURSOSAI")
    print("="*60)
    print(f"\n  Base URL: {BASE_URL}")
    print(f"  Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executa os testes
    test_health_check()
    time.sleep(1)
    
    test_tts_generation()
    time.sleep(1)
    
    test_scene_management()
    time.sleep(1)
    
    test_analytics()
    time.sleep(1)
    
    test_modern_ai()
    
    print("\n" + "="*60)
    print("  ✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print("="*60)
    print("\n💡 Dica: Acesse http://localhost:8000/docs para ver toda a documentação da API")
    print("📚 Para mais exemplos, consulte a pasta 'docs/examples'")

if __name__ == "__main__":
    main() 