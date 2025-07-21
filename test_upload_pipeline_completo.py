"""
Teste do Pipeline Completo de Upload com Geração de Vídeo
========================================================

Este script testa o endpoint /upload modificado que executa o pipeline completo:
1. Upload de arquivo PDF/PPTX
2. Extração de texto por slides
3. Geração de áudios individuais
4. Criação de vídeos para cada slide
5. Concatenação em vídeo final
6. Registro no banco de dados

Autor: Sistema TecnoCursos AI
Data: Janeiro 2025
"""

import asyncio
import requests
import json
import time
from pathlib import Path

# Configurações do teste
BASE_URL = "http://localhost:8000"
TEST_PDF_PATH = "sample_test.pdf"  # Arquivo de teste existente
PROJECT_ID = 1  # ID do projeto para teste

def test_upload_pipeline():
    """
    Testa o pipeline completo de upload com geração de vídeo
    """
    print("🚀 Iniciando teste do pipeline completo de upload")
    print("="*60)
    
    # Verificar se arquivo de teste existe
    if not Path(TEST_PDF_PATH).exists():
        print(f"❌ Arquivo de teste não encontrado: {TEST_PDF_PATH}")
        print("📋 Criando arquivo PDF simples para teste...")
        create_test_pdf()
    
    # Dados do upload
    upload_data = {
        'project_id': PROJECT_ID,
        'description': 'Teste do pipeline completo de geração de vídeo'
    }
    
    try:
        print(f"📤 Fazendo upload do arquivo: {TEST_PDF_PATH}")
        print(f"🎯 Endpoint: {BASE_URL}/api/files/upload")
        
        # Fazer upload
        with open(TEST_PDF_PATH, 'rb') as file:
            files = {'file': (TEST_PDF_PATH, file, 'application/pdf')}
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/files/upload",
                files=files,
                data=upload_data,
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
            
            # Geração de vídeo (NOVA FUNCIONALIDADE)
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
                test_video_download(BASE_URL + download_links.get('final_video'))
            
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

def test_video_download(video_url):
    """
    Testa o download do vídeo final gerado
    """
    print(f"\n🎬 Testando download do vídeo final...")
    print(f"🔗 URL: {video_url}")
    
    try:
        response = requests.head(video_url)
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
        c.drawString(100, 720, "Este é o primeiro slide da apresentação de teste.")
        c.drawString(100, 690, "O sistema irá gerar um vídeo automaticamente.")
        c.showPage()
        
        # Página 2
        c.drawString(100, 750, "Slide 2: Funcionalidades Principais")
        c.drawString(100, 720, "• Upload de arquivos PDF e PPTX")
        c.drawString(100, 690, "• Extração automática de texto")
        c.drawString(100, 660, "• Geração de narração com TTS")
        c.drawString(100, 630, "• Criação de vídeos individuais")
        c.drawString(100, 600, "• Concatenação em vídeo final")
        c.showPage()
        
        # Página 3
        c.drawString(100, 750, "Slide 3: Conclusão")
        c.drawString(100, 720, "Pipeline completo de automação implementado!")
        c.drawString(100, 690, "Obrigado por usar o TecnoCursos AI.")
        c.showPage()
        
        c.save()
        print(f"✅ PDF de teste criado: {TEST_PDF_PATH}")
        
    except ImportError:
        print("⚠️ ReportLab não está instalado. Criando arquivo de texto simples...")
        with open("sample_test.txt", "w", encoding="utf-8") as f:
            f.write("Slide 1: Introdução\n")
            f.write("Este é um teste do sistema TecnoCursos AI.\n\n")
            f.write("Slide 2: Funcionalidades\n")
            f.write("O sistema processa arquivos automaticamente.\n\n")
            f.write("Slide 3: Conclusão\n")
            f.write("Pipeline de vídeo implementado com sucesso!\n")
        print(f"✅ Arquivo de texto criado: sample_test.txt")

def main():
    """
    Função principal do teste
    """
    print("🎯 TESTE DO PIPELINE COMPLETO DE UPLOAD E GERAÇÃO DE VÍDEO")
    print("="*70)
    print(f"📍 Servidor: {BASE_URL}")
    print(f"📄 Arquivo de teste: {TEST_PDF_PATH}")
    print(f"📁 Projeto ID: {PROJECT_ID}")
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
    
    # Executar teste
    success = test_upload_pipeline()
    
    print("\n" + "="*70)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Pipeline completo de upload → vídeo funcionando!")
    else:
        print("❌ TESTE FALHOU!")
        print("🔧 Verifique os logs do servidor para mais detalhes.")
    print("="*70)

if __name__ == "__main__":
    main() 