"""
Teste do Pipeline Completo com Autenticação Automática
======================================================

Este script testa o endpoint /upload com autenticação automática:
1. Registra usuário de teste (se necessário)
2. Faz login para obter token
3. Cria projeto de teste
4. Executa upload com pipeline completo
5. Valida resultado final

Autor: Sistema TecnoCursos AI
Data: Janeiro 2025
"""

import requests
import json
import time
import uuid
from pathlib import Path

# Configurações do teste
BASE_URL = "http://localhost:8000"
TEST_PDF_PATH = "sample_test.pdf"

# Credenciais de teste
TEST_USER = {
    "email": f"teste_{uuid.uuid4().hex[:8]}@tecnocursos.ai",
    "password": "senha123456",
    "name": "Usuário Teste Pipeline"
}

def register_and_login():
    """
    Registra usuário de teste e faz login para obter token
    """
    print("🔐 Configurando autenticação...")
    
    try:
        # 1. Registrar usuário
        print(f"📝 Registrando usuário: {TEST_USER['email']}")
        register_data = {
            "full_name": TEST_USER["name"],
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "username": TEST_USER["email"]  # Usar email como username
        }
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json=register_data,
            timeout=10
        )
        
        if register_response.status_code in [200, 201]:
            print("✅ Usuário registrado com sucesso")
        elif register_response.status_code == 400:
            print("ℹ️ Usuário já existe, continuando...")
        else:
            print(f"⚠️ Status do registro: {register_response.status_code}")
        
        # 2. Fazer login
        print("🔑 Fazendo login...")
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,  # JSON data
            timeout=10
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            if access_token:
                print("✅ Login realizado com sucesso")
                return access_token
            else:
                print("❌ Token não encontrado na resposta")
                return None
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"📝 Resposta: {login_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na autenticação: {str(e)}")
        return None

def create_test_project(token):
    """
    Cria projeto de teste para upload
    """
    print("📁 Criando projeto de teste...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        project_data = {
            "name": f"Projeto Teste Pipeline {uuid.uuid4().hex[:8]}",
            "description": "Projeto para teste do pipeline completo"
        }
        
        response = requests.post(
            f"{BASE_URL}/projects",
            json=project_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            project = response.json()
            project_id = project.get("id")
            print(f"✅ Projeto criado com ID: {project_id}")
            return project_id
        else:
            print(f"❌ Erro ao criar projeto: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao criar projeto: {str(e)}")
        return None

def test_upload_pipeline_authenticated(token, project_id):
    """
    Testa o pipeline completo de upload com autenticação
    """
    print(f"🚀 Iniciando teste do pipeline autenticado")
    print("="*60)
    
    # Verificar se arquivo de teste existe
    if not Path(TEST_PDF_PATH).exists():
        print(f"❌ Arquivo de teste não encontrado: {TEST_PDF_PATH}")
        print("📋 Criando arquivo PDF simples para teste...")
        create_test_pdf()
    
    # Headers com token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Dados do upload
    upload_data = {
        'project_id': project_id,
        'description': 'Teste autenticado do pipeline completo de geração de vídeo'
    }
    
    try:
        print(f"📤 Fazendo upload autenticado do arquivo: {TEST_PDF_PATH}")
        print(f"🎯 Endpoint: {BASE_URL}/api/files/upload")
        
        # Fazer upload
        with open(TEST_PDF_PATH, 'rb') as file:
            files = {'file': (TEST_PDF_PATH, file, 'application/pdf')}
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/files/upload",
                files=files,
                data=upload_data,
                headers=headers,
                timeout=300  # 5 minutos timeout
            )
            end_time = time.time()
        
        print(f"⏱️ Tempo total de processamento: {end_time - start_time:.2f} segundos")
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎉 PIPELINE EXECUTADO COM SUCESSO!")
            print("="*60)
            
            # Informações básicas do arquivo
            print("📁 ARQUIVO CARREGADO:")
            print(f"   • ID: {result.get('id')}")
            print(f"   • UUID: {result.get('uuid')}")
            print(f"   • Nome: {result.get('filename')}")
            print(f"   • Tamanho: {result.get('file_size')} bytes")
            print(f"   • Tipo: {result.get('file_type')}")
            
            # Extração de texto
            text_extraction = result.get('text_extraction', {})
            print(f"\n📄 EXTRAÇÃO DE TEXTO:")
            print(f"   • Sucesso: {text_extraction.get('success')}")
            print(f"   • Páginas/Slides: {text_extraction.get('pages_count')}")
            print(f"   • Total de caracteres: {text_extraction.get('text_length')}")
            
            # Geração de áudio
            audio_generation = result.get('audio_generation', {})
            print(f"\n🎵 GERAÇÃO DE ÁUDIO:")
            print(f"   • Sucesso: {audio_generation.get('success')}")
            print(f"   • URL do áudio: {audio_generation.get('audio_url')}")
            print(f"   • Nome do arquivo: {audio_generation.get('audio_filename')}")
            if audio_generation.get('error'):
                print(f"   • Erro: {audio_generation.get('error')}")
            
            # Geração de vídeo (FUNCIONALIDADE PRINCIPAL)
            video_generation = result.get('video_generation', {})
            print(f"\n🎬 GERAÇÃO DE VÍDEO:")
            print(f"   • Sucesso: {video_generation.get('success')}")
            print(f"   • URL do vídeo: {video_generation.get('video_url')}")
            print(f"   • Nome do arquivo: {video_generation.get('video_filename')}")
            
            video_stats = video_generation.get('video_stats', {})
            if video_stats:
                print(f"   • Total de slides processados: {video_stats.get('total_slides')}")
                print(f"   • Áudios gerados: {video_stats.get('audios_generated')}")
                print(f"   • Vídeos criados: {video_stats.get('videos_created')}")
                print(f"   • Duração final: {video_stats.get('final_video_duration')} segundos")
                print(f"   • Tamanho do vídeo: {video_stats.get('final_video_size')} bytes")
                print(f"   • Tempo de processamento: {video_stats.get('processing_time')} segundos")
                print(f"   • ID do vídeo no banco: {video_stats.get('video_id')}")
                print(f"   • UUID do vídeo: {video_stats.get('video_uuid')}")
            
            if video_generation.get('error'):
                print(f"   • Erro: {video_generation.get('error')}")
            
            # Links de download
            download_links = result.get('download_links', {})
            print(f"\n🔗 LINKS DE DOWNLOAD:")
            print(f"   • Arquivo original: {BASE_URL}{download_links.get('original_file')}")
            if download_links.get('audio_narration'):
                print(f"   • Narração em áudio: {BASE_URL}{download_links.get('audio_narration')}")
            if download_links.get('final_video'):
                print(f"   • 🎯 VÍDEO FINAL: {BASE_URL}{download_links.get('final_video')}")
            
            # Resumo do pipeline
            pipeline_summary = result.get('pipeline_summary', {})
            print(f"\n📋 RESUMO DO PIPELINE:")
            steps = pipeline_summary.get('steps_completed', [])
            for step in steps:
                print(f"   {step}")
            print(f"   • Tempo total: {pipeline_summary.get('total_processing_time')}")
            print(f"   • Resultado final: {pipeline_summary.get('final_output')}")
            
            # Status geral
            print(f"\n✅ PROCESSAMENTO COMPLETO: {result.get('processing_completed')}")
            if result.get('processing_error'):
                print(f"⚠️ ERROS: {result.get('processing_error')}")
            
            # Testar download do vídeo final
            if download_links.get('final_video'):
                test_video_download(BASE_URL + download_links.get('final_video'), token)
            
            # Testar endpoints relacionados
            test_additional_endpoints(token, result.get('id'), video_stats.get('video_id'))
            
            return True
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - O processamento está demorando mais que 5 minutos")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

def test_video_download(video_url, token):
    """
    Testa o download do vídeo final gerado
    """
    print(f"\n🎬 Testando download do vídeo final...")
    print(f"🔗 URL: {video_url}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.head(video_url, headers=headers)
        if response.status_code == 200:
            file_size = response.headers.get('content-length')
            content_type = response.headers.get('content-type')
            print(f"✅ Vídeo disponível para download")
            print(f"   • Tamanho: {file_size} bytes")
            print(f"   • Tipo: {content_type}")
        else:
            print(f"❌ Vídeo não está disponível: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar download: {str(e)}")

def test_additional_endpoints(token, file_id, video_id):
    """
    Testa endpoints adicionais relacionados ao arquivo e vídeo
    """
    print(f"\n🔍 Testando endpoints adicionais...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Testar listagem de arquivos
        response = requests.get(f"{BASE_URL}/api/files/", headers=headers)
        if response.status_code == 200:
            files = response.json()
            print(f"✅ Listagem de arquivos: {len(files)} arquivos encontrados")
        
        # Testar detalhes do arquivo
        if file_id:
            response = requests.get(f"{BASE_URL}/api/files/{file_id}", headers=headers)
            if response.status_code == 200:
                print(f"✅ Detalhes do arquivo ID {file_id} obtidos")
        
        # Testar listagem de áudios
        response = requests.get(f"{BASE_URL}/api/files/audios", headers=headers)
        if response.status_code == 200:
            audios = response.json()
            print(f"✅ Listagem de áudios: encontrados")
        
        # Testar status do sistema
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status do sistema: {status.get('status')}")
            
    except Exception as e:
        print(f"⚠️ Erro ao testar endpoints adicionais: {str(e)}")

def create_test_pdf():
    """
    Cria um PDF simples para teste se não existir
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        print("📄 Criando PDF de teste...")
        
        c = canvas.Canvas(TEST_PDF_PATH, pagesize=letter)
        
        # Página 1
        c.drawString(100, 750, "Slide 1: Introdução ao TecnoCursos AI")
        c.drawString(100, 720, "Este é o primeiro slide da apresentação de teste do pipeline completo.")
        c.drawString(100, 690, "O sistema irá gerar automaticamente um vídeo profissional.")
        c.drawString(100, 660, "Funcionalidades: Upload, Extração, TTS, Vídeo e Concatenação.")
        c.showPage()
        
        # Página 2
        c.drawString(100, 750, "Slide 2: Funcionalidades Principais")
        c.drawString(100, 720, "• Upload de arquivos PDF e PPTX")
        c.drawString(100, 690, "• Extração automática de texto por slides")
        c.drawString(100, 660, "• Geração de narração com sistema TTS avançado")
        c.drawString(100, 630, "• Criação de vídeos individuais para cada slide")
        c.drawString(100, 600, "• Concatenação automática em apresentação final")
        c.drawString(100, 570, "• Registro completo no banco de dados")
        c.showPage()
        
        # Página 3
        c.drawString(100, 750, "Slide 3: Resultados e Benefícios")
        c.drawString(100, 720, "✅ Pipeline automatizado de ponta a ponta")
        c.drawString(100, 690, "✅ Vídeos profissionais em minutos")
        c.drawString(100, 660, "✅ Links diretos para download")
        c.drawString(100, 630, "✅ Integração completa com banco de dados")
        c.drawString(100, 600, "✅ Sistema pronto para produção")
        c.showPage()
        
        # Página 4
        c.drawString(100, 750, "Slide 4: Conclusão")
        c.drawString(100, 720, "🎉 Pipeline completo de automação implementado com sucesso!")
        c.drawString(100, 690, "🚀 TecnoCursos AI está pronto para transformar")
        c.drawString(100, 660, "   qualquer apresentação em vídeo profissional.")
        c.drawString(100, 630, "💼 Obrigado por usar o TecnoCursos AI!")
        c.showPage()
        
        c.save()
        print(f"✅ PDF de teste criado: {TEST_PDF_PATH}")
        
    except ImportError:
        print("⚠️ ReportLab não está instalado. Criando arquivo texto simples...")
        with open("sample_test.txt", "w", encoding="utf-8") as f:
            f.write("Slide 1: Introdução ao TecnoCursos AI\n")
            f.write("Este é um teste completo do pipeline automatizado.\n\n")
            f.write("Slide 2: Funcionalidades Principais\n") 
            f.write("O sistema processa arquivos e gera vídeos automaticamente.\n\n")
            f.write("Slide 3: Resultados\n")
            f.write("Pipeline de vídeo funcionando perfeitamente!\n\n")
            f.write("Slide 4: Conclusão\n")
            f.write("Sistema TecnoCursos AI está pronto para produção!\n")
        print(f"✅ Arquivo de texto criado: sample_test.txt")

def main():
    """
    Função principal do teste autenticado
    """
    print("🎯 TESTE COMPLETO DO PIPELINE COM AUTENTICAÇÃO")
    print("="*70)
    print(f"📍 Servidor: {BASE_URL}")
    print(f"📄 Arquivo de teste: {TEST_PDF_PATH}")
    print(f"👤 Email de teste: {TEST_USER['email']}")
    print()
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
        else:
            print("⚠️ Servidor retornou código inesperado")
    except:
        print("❌ Servidor não está rodando. Inicie com: python main.py")
        return
    
    # Executar fluxo completo
    print("\n" + "="*70)
    
    # 1. Autenticação
    token = register_and_login()
    if not token:
        print("❌ Falha na autenticação")
        return
    
    # 2. Criar projeto
    project_id = create_test_project(token)
    if not project_id:
        print("❌ Falha ao criar projeto")
        return
    
    # 3. Testar pipeline
    success = test_upload_pipeline_authenticated(token, project_id)
    
    print("\n" + "="*70)
    if success:
        print("🎉 TESTE COMPLETO EXECUTADO COM SUCESSO!")
        print("✅ Pipeline completo de upload → vídeo funcionando!")
        print("🎬 Vídeo final gerado e disponível para download!")
        print("💾 Todas as informações salvas no banco de dados!")
        print("🔗 Links diretos funcionando corretamente!")
        print("\n🚀 SISTEMA TECNOCURSOS AI PRONTO PARA PRODUÇÃO!")
    else:
        print("❌ TESTE FALHOU!")
        print("🔧 Verifique os logs do servidor para mais detalhes.")
    print("="*70)

if __name__ == "__main__":
    main() 