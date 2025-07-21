#!/usr/bin/env python3
"""
TESTE COMPLETO DO PIPELINE DE EXTRAÇÃO E NARRAÇÃO
=================================================

Este arquivo testa o pipeline completo do TecnoCursos AI:
1. Upload/processamento de arquivo PDF ou PPTX
2. Extração de texto usando as funções implementadas
3. Geração de narração usando TTS (Text-to-Speech)
4. Exibição dos resultados

Arquivo: test_pipeline.py
Autor: TecnoCursos AI System
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional

# Configurações do teste
ARQUIVO_TESTE_PDF = "sample_test.pdf"  # Arquivo PDF de exemplo
ARQUIVO_TESTE_PPTX = "slide_test.png"  # Se existir um arquivo PPTX
DIRETORIO_SAIDA_AUDIO = "temp"  # Diretório onde salvar os áudios gerados

def imprimir_cabecalho():
    """Imprime o cabeçalho do teste com informações do sistema"""
    print("\n" + "="*80)
    print("🎯 TESTE COMPLETO DO PIPELINE TECNOCURSOS AI")
    print("="*80)
    print("📋 Funcionalidades testadas:")
    print("   ✅ Extração de texto de PDF/PPTX")
    print("   ✅ Geração de narração (TTS)")
    print("   ✅ Validação de arquivos gerados")
    print("   ✅ Exibição de estatísticas")
    print("="*80)

def verificar_dependencias():
    """Verifica se todas as dependências necessárias estão disponíveis"""
    print("\n🔍 VERIFICANDO DEPENDÊNCIAS...")
    
    # Lista de módulos necessários
    dependencias = {
        'fitz': 'PyMuPDF (para PDF)',
        'pptx': 'python-pptx (para PPTX)', 
        'gtts': 'gTTS (para TTS)',
        'pydub': 'pydub (para conversão de áudio)'
    }
    
    dependencias_ok = True
    
    for modulo, descricao in dependencias.items():
        try:
            if modulo == 'fitz':
                import fitz
                print(f"   ✅ {descricao}: v{fitz.version[0]}")
            elif modulo == 'pptx':
                from pptx import Presentation
                print(f"   ✅ {descricao}: Disponível")
            elif modulo == 'gtts':
                from gtts import gTTS
                print(f"   ✅ {descricao}: Disponível")
            elif modulo == 'pydub':
                from pydub import AudioSegment
                print(f"   ✅ {descricao}: Disponível")
        except ImportError:
            print(f"   ⚠️  {descricao}: Não disponível (opcional)")
            if modulo in ['fitz', 'gtts']:  # Dependências críticas
                dependencias_ok = False
    
    if not dependencias_ok:
        print("\n❌ Algumas dependências críticas estão faltando!")
        print("   Execute: pip install PyMuPDF gtts pydub python-pptx")
        return False
    
    print("✅ Todas as dependências críticas estão disponíveis!")
    return True

def verificar_arquivos_teste():
    """Verifica se os arquivos de teste existem"""
    print("\n📁 VERIFICANDO ARQUIVOS DE TESTE...")
    
    arquivos_encontrados = []
    
    # Verificar PDF de exemplo
    if os.path.exists(ARQUIVO_TESTE_PDF):
        tamanho = os.path.getsize(ARQUIVO_TESTE_PDF)
        print(f"   ✅ PDF encontrado: {ARQUIVO_TESTE_PDF} ({tamanho:,} bytes)")
        arquivos_encontrados.append(('pdf', ARQUIVO_TESTE_PDF))
    else:
        print(f"   ⚠️  PDF não encontrado: {ARQUIVO_TESTE_PDF}")
    
    # Procurar por arquivos PPTX na pasta
    arquivos_pptx = list(Path('.').glob('*.pptx'))
    if arquivos_pptx:
        arquivo_pptx = str(arquivos_pptx[0])
        tamanho = os.path.getsize(arquivo_pptx)
        print(f"   ✅ PPTX encontrado: {arquivo_pptx} ({tamanho:,} bytes)")
        arquivos_encontrados.append(('pptx', arquivo_pptx))
    else:
        print(f"   ⚠️  Nenhum arquivo PPTX encontrado")
    
    if not arquivos_encontrados:
        print("\n❌ Nenhum arquivo de teste encontrado!")
        print("   Coloque um arquivo PDF ou PPTX na pasta do projeto para testar.")
        return None
    
    return arquivos_encontrados

def extrair_texto_pdf(caminho_arquivo: str) -> List[str]:
    """
    Extrai texto de um arquivo PDF usando a função implementada
    
    Args:
        caminho_arquivo: Caminho para o arquivo PDF
        
    Returns:
        Lista com o texto de cada página
    """
    print(f"\n📄 EXTRAINDO TEXTO DO PDF: {caminho_arquivo}")
    
    try:
        # Importar função de extração de texto do sistema
        from app.utils import extract_text_from_pdf
        
        # Extrair texto usando a função implementada
        print("   🔄 Processando páginas do PDF...")
        texto_paginas = extract_text_from_pdf(caminho_arquivo)
        
        # Exibir estatísticas
        total_paginas = len(texto_paginas)
        total_caracteres = sum(len(pagina) for pagina in texto_paginas)
        total_palavras = sum(len(pagina.split()) for pagina in texto_paginas)
        
        print(f"   ✅ Extração concluída:")
        print(f"      📄 Páginas processadas: {total_paginas}")
        print(f"      🔤 Total de caracteres: {total_caracteres:,}")
        print(f"      📝 Total de palavras: {total_palavras:,}")
        
        return texto_paginas
        
    except Exception as e:
        print(f"   ❌ Erro na extração de PDF: {str(e)}")
        return []

def extrair_texto_pptx(caminho_arquivo: str) -> List[str]:
    """
    Extrai texto de um arquivo PPTX usando a função implementada
    
    Args:
        caminho_arquivo: Caminho para o arquivo PPTX
        
    Returns:
        Lista com o texto de cada slide
    """
    print(f"\n🎨 EXTRAINDO TEXTO DO PPTX: {caminho_arquivo}")
    
    try:
        # Importar função de extração de texto do sistema
        from app.utils import extract_text_from_pptx
        
        # Extrair texto usando a função implementada
        print("   🔄 Processando slides do PPTX...")
        texto_slides = extract_text_from_pptx(caminho_arquivo)
        
        # Exibir estatísticas
        total_slides = len(texto_slides)
        total_caracteres = sum(len(slide) for slide in texto_slides)
        total_palavras = sum(len(slide.split()) for slide in texto_slides)
        
        print(f"   ✅ Extração concluída:")
        print(f"      🎨 Slides processados: {total_slides}")
        print(f"      🔤 Total de caracteres: {total_caracteres:,}")
        print(f"      📝 Total de palavras: {total_palavras:,}")
        
        return texto_slides
        
    except Exception as e:
        print(f"   ❌ Erro na extração de PPTX: {str(e)}")
        return []

def preparar_texto_para_narracao(textos: List[str], max_caracteres: int = 1500) -> str:
    """
    Prepara o texto extraído para geração de narração
    
    Args:
        textos: Lista de textos extraídos
        max_caracteres: Máximo de caracteres para a narração
        
    Returns:
        Texto combinado e otimizado para TTS
    """
    print(f"\n📝 PREPARANDO TEXTO PARA NARRAÇÃO...")
    
    # Filtrar textos vazios e combinar
    textos_validos = [texto.strip() for texto in textos if texto.strip()]
    
    if not textos_validos:
        print("   ⚠️  Nenhum texto válido encontrado!")
        return ""
    
    # Combinar textos com separadores
    texto_combinado = " ".join(textos_validos)
    
    # Limitar tamanho para TTS (evitar textos muito longos)
    if len(texto_combinado) > max_caracteres:
        texto_combinado = texto_combinado[:max_caracteres]
        # Tentar cortar em uma frase completa
        ultimo_ponto = texto_combinado.rfind('.')
        if ultimo_ponto > max_caracteres * 0.8:  # Se encontrou um ponto após 80% do texto
            texto_combinado = texto_combinado[:ultimo_ponto + 1]
        texto_combinado += " [Texto truncado para demonstração]"
    
    print(f"   ✅ Texto preparado:")
    print(f"      🔤 Caracteres: {len(texto_combinado):,}")
    print(f"      📝 Palavras: {len(texto_combinado.split()):,}")
    print(f"      📋 Preview: {texto_combinado[:150]}...")
    
    return texto_combinado

def gerar_narracao_fallback(texto: str, nome_arquivo: str) -> Dict:
    """
    Gera narração usando gTTS diretamente como fallback
    
    Args:
        texto: Texto para converter em áudio
        nome_arquivo: Nome do arquivo de saída (sem extensão)
        
    Returns:
        Dicionário com resultado da geração
    """
    print(f"\n🎤 GERANDO NARRAÇÃO COM gTTS (FALLBACK)...")
    
    # Criar diretório de saída se não existir
    Path(DIRETORIO_SAIDA_AUDIO).mkdir(exist_ok=True)
    
    # Caminho completo do arquivo de saída
    caminho_audio = os.path.join(DIRETORIO_SAIDA_AUDIO, f"{nome_arquivo}.mp3")
    
    try:
        from gtts import gTTS
        
        print("   🔄 Iniciando geração com gTTS (Google TTS)...")
        print(f"   📁 Arquivo de saída: {caminho_audio}")
        
        # Marcar tempo de início
        inicio = time.time()
        
        # Gerar narração usando gTTS
        tts = gTTS(text=texto, lang='pt', slow=False)
        tts.save(caminho_audio)
        
        # Calcular tempo de processamento
        tempo_processamento = time.time() - inicio
        
        # Obter informações do arquivo gerado
        if os.path.exists(caminho_audio):
            tamanho_arquivo = os.path.getsize(caminho_audio)
            
            # Estimar duração (aproximadamente 150 palavras por minuto)
            num_palavras = len(texto.split())
            duracao_estimada = (num_palavras / 150) * 60  # em segundos
            
            print(f"   ✅ Narração gerada com sucesso!")
            print(f"      📁 Arquivo: {caminho_audio}")
            print(f"      ⏱️  Duração estimada: {duracao_estimada:.2f} segundos")
            print(f"      🎵 Provedor usado: gTTS (Google)")
            print(f"      📦 Tamanho: {tamanho_arquivo:,} bytes")
            print(f"      ⚡ Tempo de processamento: {tempo_processamento:.2f} segundos")
            
            return {
                'success': True,
                'audio_path': caminho_audio,
                'duration': duracao_estimada,
                'provider': 'gTTS (Google)',
                'file_size': tamanho_arquivo,
                'processing_time': tempo_processamento
            }
        else:
            return {
                'success': False,
                'error': 'Arquivo de áudio não foi criado',
                'processing_time': tempo_processamento
            }
            
    except Exception as e:
        print(f"   ❌ Erro na geração com gTTS: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def gerar_narracao(texto: str, nome_arquivo: str) -> Dict:
    """
    Gera narração em áudio a partir do texto usando TTS
    
    Args:
        texto: Texto para converter em áudio
        nome_arquivo: Nome do arquivo de saída (sem extensão)
        
    Returns:
        Dicionário com resultado da geração
    """
    print(f"\n🎤 GERANDO NARRAÇÃO EM ÁUDIO...")
    
    # Criar diretório de saída se não existir
    Path(DIRETORIO_SAIDA_AUDIO).mkdir(exist_ok=True)
    
    # Caminho completo do arquivo de saída
    caminho_audio = os.path.join(DIRETORIO_SAIDA_AUDIO, f"{nome_arquivo}.mp3")
    
    try:
        # Tentar primeiro o sistema TTS completo
        print("   🔄 Tentando usar sistema TTS avançado...")
        
        try:
            # Importar função de geração de narração do sistema
            from app.utils import generate_narration_sync
            
            print("   📁 Arquivo de saída: {caminho_audio}")
            
            # Marcar tempo de início
            inicio = time.time()
            
            # Gerar narração usando a função síncrona
            resultado = generate_narration_sync(
                text=texto,
                output_path=caminho_audio,
                voice="v2/pt_speaker_0",  # Voz padrão em português
                provider="auto",  # Detectar automaticamente o melhor provedor (gTTS ou Bark)
                language="pt"  # Português
            )
            
            # Calcular tempo de processamento
            tempo_processamento = time.time() - inicio
            
            if resultado.get('success', False):
                # Obter informações do arquivo gerado
                tamanho_arquivo = os.path.getsize(resultado['audio_path']) if os.path.exists(resultado['audio_path']) else 0
                
                print(f"   ✅ Narração gerada com sistema avançado!")
                print(f"      📁 Arquivo: {resultado['audio_path']}")
                print(f"      ⏱️  Duração: {resultado.get('duration', 0):.2f} segundos")
                print(f"      🎵 Provedor usado: {resultado.get('provider_used', 'N/A')}")
                print(f"      📦 Tamanho: {tamanho_arquivo:,} bytes")
                print(f"      ⚡ Tempo de processamento: {tempo_processamento:.2f} segundos")
                
                return {
                    'success': True,
                    'audio_path': resultado['audio_path'],
                    'duration': resultado.get('duration', 0),
                    'provider': resultado.get('provider_used', 'N/A'),
                    'file_size': tamanho_arquivo,
                    'processing_time': tempo_processamento
                }
            else:
                print(f"   ⚠️  Sistema avançado falhou: {resultado.get('error', 'Erro desconhecido')}")
                raise Exception("Sistema TTS avançado não disponível")
                
        except Exception as e:
            print(f"   ⚠️  Sistema TTS avançado não disponível: {str(e)}")
            print("   🔄 Tentando fallback com gTTS...")
            
            # Usar fallback com gTTS
            return gerar_narracao_fallback(texto, nome_arquivo)
            
    except Exception as e:
        print(f"   ❌ Erro geral na geração de narração: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def exibir_resultados_finais(resultados: Dict):
    """Exibe o resumo final dos resultados do teste"""
    print("\n" + "="*80)
    print("📊 RESUMO FINAL DO TESTE")
    print("="*80)
    
    if resultados.get('success', False):
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"\n📋 Resultados:")
        print(f"   📄 Arquivo processado: {resultados.get('arquivo_original', 'N/A')}")
        print(f"   📝 Texto extraído: {resultados.get('total_caracteres', 0):,} caracteres")
        print(f"   🎤 Áudio gerado: {resultados.get('audio_path', 'N/A')}")
        print(f"   ⏱️  Duração do áudio: {resultados.get('duration', 0):.2f} segundos")
        print(f"   🔊 Provedor TTS: {resultados.get('provider', 'N/A')}")
        print(f"   📦 Tamanho do áudio: {resultados.get('file_size', 0):,} bytes")
        print(f"   ⚡ Tempo total: {resultados.get('tempo_total', 0):.2f} segundos")
        
        print(f"\n🎯 COMO TESTAR O RESULTADO:")
        print(f"   1. Abra o arquivo: {resultados.get('audio_path', 'N/A')}")
        print(f"   2. Reproduza o áudio para verificar a narração")
        print(f"   3. O áudio deve conter o texto extraído do arquivo original")
        
    else:
        print("❌ TESTE FALHOU!")
        print(f"   Erro: {resultados.get('error', 'Erro desconhecido')}")
    
    print("="*80)

def main():
    """Função principal que executa todo o pipeline de teste"""
    
    # Marcar tempo de início do teste completo
    inicio_teste = time.time()
    
    # 1. Exibir cabeçalho
    imprimir_cabecalho()
    
    # 2. Verificar dependências
    if not verificar_dependencias():
        return
    
    # 3. Verificar arquivos de teste
    arquivos_teste = verificar_arquivos_teste()
    if not arquivos_teste:
        return
    
    # 4. Processar o primeiro arquivo encontrado
    tipo_arquivo, caminho_arquivo = arquivos_teste[0]
    
    # 5. Extrair texto baseado no tipo de arquivo
    if tipo_arquivo == 'pdf':
        textos_extraidos = extrair_texto_pdf(caminho_arquivo)
    elif tipo_arquivo == 'pptx':
        textos_extraidos = extrair_texto_pptx(caminho_arquivo)
    else:
        print(f"❌ Tipo de arquivo não suportado: {tipo_arquivo}")
        return
    
    if not textos_extraidos:
        print("❌ Nenhum texto foi extraído do arquivo!")
        return
    
    # 6. Preparar texto para narração
    texto_para_narracao = preparar_texto_para_narracao(textos_extraidos)
    
    if not texto_para_narracao:
        print("❌ Não foi possível preparar texto para narração!")
        return
    
    # 7. Gerar narração
    nome_arquivo_saida = f"narracao_teste_{int(time.time())}"
    resultado_narracao = gerar_narracao(texto_para_narracao, nome_arquivo_saida)
    
    # 8. Calcular tempo total
    tempo_total = time.time() - inicio_teste
    
    # 9. Preparar resultados finais
    resultados_finais = {
        'success': resultado_narracao.get('success', False),
        'arquivo_original': caminho_arquivo,
        'total_caracteres': len(texto_para_narracao),
        'audio_path': resultado_narracao.get('audio_path'),
        'duration': resultado_narracao.get('duration', 0),
        'provider': resultado_narracao.get('provider', 'N/A'),
        'file_size': resultado_narracao.get('file_size', 0),
        'tempo_total': tempo_total,
        'error': resultado_narracao.get('error')
    }
    
    # 10. Exibir resultados finais
    exibir_resultados_finais(resultados_finais)

if __name__ == "__main__":
    """
    INSTRUÇÕES PARA EXECUTAR O TESTE:
    
    1. REQUISITOS:
       - Python 3.8+
       - Dependências instaladas: pip install PyMuPDF gtts pydub python-pptx
       - Arquivo PDF ou PPTX na pasta do projeto (ex: sample_test.pdf)
    
    2. EXECUTAR:
       python test_pipeline.py
    
    3. O QUE O TESTE FAZ:
       - Verifica dependências e arquivos
       - Extrai texto do arquivo encontrado
       - Gera narração MP3 do texto
       - Salva o áudio na pasta 'temp/'
       - Exibe estatísticas completas
    
    4. RESULTADOS:
       - Console: Logs detalhados de cada etapa
       - Arquivo: narracao_teste_[timestamp].mp3 na pasta temp/
    
    5. PROBLEMAS COMUNS:
       - Se não encontrar arquivo: coloque um PDF/PPTX na pasta
       - Se TTS falhar: verifique conexão internet (gTTS)
       - Se dependências: pip install PyMuPDF gtts pydub
    """
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário!")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc() 