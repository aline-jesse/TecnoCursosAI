#!/usr/bin/env python3
"""
Teste do Endpoint de Upload com Geração Automática de Narração
============================================================

Este script testa o endpoint /upload modificado que:
1. Detecta o tipo do arquivo (PDF ou PPTX)
2. Extrai texto automaticamente
3. Gera narração MP3
4. Salva o áudio em /static/audios
5. Registra no banco de dados na tabela 'audios'
6. Retorna informações completas

Uso:
    python test_upload_with_narration.py
"""

import requests
import json
import os
import sys
from pathlib import Path

# Configurações do teste
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
UPLOAD_URL = f"{BASE_URL}/api/files/upload"
AUDIOS_URL = f"{BASE_URL}/api/files/audios"

# Credenciais de teste (ajustar conforme necessário)
TEST_USER = {
    "username": "admin",  # ou "testuser"
    "password": "admin123"  # ou senha do usuário de teste
}

def login() -> str:
    """
    Fazer login e obter token de acesso
    """
    print("🔐 Fazendo login...")
    
    response = requests.post(
        LOGIN_URL,
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Login realizado com sucesso!")
        return access_token
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def test_upload_pdf(token: str, project_id: int = 1):
    """
    Testar upload de arquivo PDF com geração automática de narração
    """
    print("\n📄 Testando upload de PDF...")
    
    # Procurar um arquivo PDF de exemplo no projeto
    pdf_files = list(Path(".").glob("*.pdf"))
    if not pdf_files:
        print("❌ Nenhum arquivo PDF encontrado no diretório atual")
        return None
    
    pdf_file = pdf_files[0]
    print(f"📁 Usando arquivo: {pdf_file}")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(pdf_file, "rb") as f:
        files = {
            "file": (pdf_file.name, f, "application/pdf")
        }
        data = {
            "project_id": project_id,
            "description": "Teste de upload com geração automática de narração"
        }
        
        print("⏳ Enviando arquivo e aguardando processamento...")
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Upload realizado com sucesso!")
        print_upload_result(result)
        return result
    else:
        print(f"❌ Erro no upload: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def test_upload_pptx(token: str, project_id: int = 1):
    """
    Testar upload de arquivo PPTX com geração automática de narração
    """
    print("\n📊 Testando upload de PPTX...")
    
    # Procurar um arquivo PPTX de exemplo no projeto
    pptx_files = list(Path(".").glob("*.pptx"))
    if not pptx_files:
        print("❌ Nenhum arquivo PPTX encontrado no diretório atual")
        return None
    
    pptx_file = pptx_files[0]
    print(f"📁 Usando arquivo: {pptx_file}")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(pptx_file, "rb") as f:
        files = {
            "file": (pptx_file.name, f, "application/vnd.openxmlformats-officedocument.presentationml.presentation")
        }
        data = {
            "project_id": project_id,
            "description": "Teste de upload PPTX com geração automática de narração"
        }
        
        print("⏳ Enviando arquivo e aguardando processamento...")
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Upload realizado com sucesso!")
        print_upload_result(result)
        return result
    else:
        print(f"❌ Erro no upload: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def print_upload_result(result: dict):
    """
    Imprimir resultado detalhado do upload
    """
    print("\n📋 RESULTADO DO UPLOAD:")
    print(f"   ID: {result.get('id')}")
    print(f"   Nome: {result.get('filename')}")
    print(f"   Tipo: {result.get('file_type')}")
    print(f"   Tamanho: {result.get('file_size')} bytes")
    print(f"   Status: {result.get('status')}")
    
    # Informações de extração de texto
    text_info = result.get('text_extraction', {})
    print(f"\n📝 EXTRAÇÃO DE TEXTO:")
    print(f"   Sucesso: {text_info.get('success')}")
    print(f"   Páginas/Slides: {text_info.get('pages_count')}")
    print(f"   Tamanho do texto: {text_info.get('text_length')} caracteres")
    
    if text_info.get('combined_text'):
        preview = text_info['combined_text'][:200] + "..." if len(text_info['combined_text']) > 200 else text_info['combined_text']
        print(f"   Preview: {preview}")
    
    # Informações de geração de áudio
    audio_info = result.get('audio_generation', {})
    print(f"\n🔊 GERAÇÃO DE ÁUDIO:")
    print(f"   Sucesso: {audio_info.get('success')}")
    print(f"   URL do áudio: {audio_info.get('audio_url')}")
    print(f"   Nome do arquivo: {audio_info.get('audio_filename')}")
    
    if audio_info.get('error'):
        print(f"   Erro: {audio_info['error']}")
    
    # Status geral
    print(f"\n✅ PROCESSAMENTO COMPLETO: {result.get('processing_completed')}")
    if result.get('processing_error'):
        print(f"❌ ERRO: {result['processing_error']}")

def test_list_audios(token: str):
    """
    Testar listagem de áudios gerados
    """
    print("\n🎵 Testando listagem de áudios...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(AUDIOS_URL, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Listagem de áudios realizada com sucesso!")
        
        audios = result.get('audios', [])
        print(f"📊 Total de áudios: {result.get('pagination', {}).get('total', 0)}")
        
        for i, audio in enumerate(audios, 1):
            print(f"\n🎵 Áudio {i}:")
            print(f"   ID: {audio.get('id')}")
            print(f"   Título: {audio.get('title')}")
            print(f"   Arquivo: {audio.get('filename')}")
            print(f"   Duração: {audio.get('duration')}s")
            print(f"   Provider: {audio.get('tts_provider')}")
            print(f"   Voz: {audio.get('voice_type')}")
            print(f"   URL: {audio.get('audio_url')}")
            print(f"   Criado: {audio.get('created_at')}")
        
        return result
    else:
        print(f"❌ Erro ao listar áudios: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def test_audio_access(token: str, audio_url: str):
    """
    Testar acesso ao arquivo de áudio gerado
    """
    print(f"\n🎧 Testando acesso ao áudio: {audio_url}")
    
    full_url = f"{BASE_URL}{audio_url}"
    
    response = requests.head(full_url)
    
    if response.status_code == 200:
        print("✅ Áudio acessível!")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Content-Length: {response.headers.get('content-length')} bytes")
        return True
    else:
        print(f"❌ Erro ao acessar áudio: {response.status_code}")
        return False

def main():
    """
    Função principal de teste
    """
    print("🧪 INICIANDO TESTES DO ENDPOINT DE UPLOAD COM NARRAÇÃO")
    print("=" * 60)
    
    # 1. Fazer login
    token = login()
    if not token:
        print("❌ Não foi possível fazer login. Verifique as credenciais.")
        sys.exit(1)
    
    # 2. Testar upload de PDF
    pdf_result = test_upload_pdf(token)
    
    # 3. Testar upload de PPTX (se disponível)
    pptx_result = test_upload_pptx(token)
    
    # 4. Listar áudios gerados
    audios_result = test_list_audios(token)
    
    # 5. Testar acesso aos áudios gerados
    if audios_result and audios_result.get('audios'):
        for audio in audios_result['audios'][:2]:  # Testar os 2 primeiros
            test_audio_access(token, audio.get('audio_url'))
    
    print("\n" + "=" * 60)
    print("🎉 TESTES CONCLUÍDOS!")
    
    # Resumo dos resultados
    print("\n📊 RESUMO:")
    print(f"   ✅ PDF processado: {'Sim' if pdf_result else 'Não'}")
    print(f"   ✅ PPTX processado: {'Sim' if pptx_result else 'Não'}")
    print(f"   ✅ Áudios listados: {'Sim' if audios_result else 'Não'}")
    
    if pdf_result and pdf_result.get('processing_completed'):
        print(f"   🎵 Narração PDF gerada: {pdf_result.get('audio_generation', {}).get('audio_url')}")
    
    if pptx_result and pptx_result.get('processing_completed'):
        print(f"   🎵 Narração PPTX gerada: {pptx_result.get('audio_generation', {}).get('audio_url')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        sys.exit(1) 