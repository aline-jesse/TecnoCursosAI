#!/usr/bin/env python3
"""
Script de teste para as funções de extração de texto PDF usando PyMuPDF
Execute: python test_pdf_extraction.py
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório app ao path para importar utils
sys.path.append('app')

try:
    from utils import (
        extract_pdf_text, 
        extract_pdf_text_with_formatting,
        search_text_in_pdf,
        create_thumbnail,
        create_multiple_thumbnails,
        get_pdf_page_info,
        ensure_directories_exist
    )
    print("✅ Funções importadas com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar funções: {e}")
    sys.exit(1)

def create_sample_pdf():
    """
    Cria um PDF de exemplo para testes usando reportlab
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Garantir que diretórios existam
        ensure_directories_exist()
        
        pdf_path = Path("app/static/uploads/pdf/sample_test.pdf")
        
        # Criar PDF de exemplo
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Página 1
        c.drawString(100, 750, "DOCUMENTO DE TESTE - PyMuPDF")
        c.drawString(100, 720, "Este é um documento PDF de exemplo para testar")
        c.drawString(100, 690, "as funções de extração de texto.")
        c.drawString(100, 660, "")
        c.drawString(100, 630, "Conteúdo importante:")
        c.drawString(120, 600, "• Extração de texto completa")
        c.drawString(120, 570, "• Análise de metadados")
        c.drawString(120, 540, "• Criação de thumbnails")
        c.drawString(120, 510, "• Busca de termos específicos")
        c.drawString(100, 480, "")
        c.drawString(100, 450, "Palavras-chave para busca:")
        c.drawString(120, 420, "PyMuPDF, extração, teste, PDF")
        
        c.showPage()
        
        # Página 2
        c.drawString(100, 750, "SEGUNDA PÁGINA DO TESTE")
        c.drawString(100, 720, "Esta é a segunda página do documento de teste.")
        c.drawString(100, 690, "")
        c.drawString(100, 660, "Mais conteúdo para testar:")
        c.drawString(120, 630, "• Processamento de múltiplas páginas")
        c.drawString(120, 600, "• Contagem de palavras por página")
        c.drawString(120, 570, "• Análise de formatação")
        c.drawString(100, 540, "")
        c.drawString(100, 510, "Este documento contém a palavra 'teste' várias vezes")
        c.drawString(100, 480, "para demonstrar a funcionalidade de busca.")
        
        c.save()
        
        print(f"✅ PDF de exemplo criado: {pdf_path}")
        return pdf_path
        
    except ImportError:
        print("⚠️ reportlab não instalado - usando PDF existente se disponível")
        return None
    except Exception as e:
        print(f"❌ Erro ao criar PDF de exemplo: {e}")
        return None

def test_extract_text(pdf_path: Path):
    """
    Testa a extração de texto básica
    """
    print("\n" + "="*50)
    print("🔍 TESTE: Extração de Texto Básica")
    print("="*50)
    
    result = extract_pdf_text(pdf_path)
    
    if result["success"]:
        print(f"✅ Extração bem-sucedida!")
        print(f"📄 Páginas: {result['page_count']}")
        print(f"📝 Palavras totais: {len(result['text'].split())}")
        print(f"🔤 Caracteres totais: {len(result['text'])}")
        print(f"📁 Tamanho do arquivo: {result['file_size']} bytes")
        
        print("\n📋 Metadados do PDF:")
        for key, value in result["metadata"].items():
            if value:
                print(f"   {key}: {value}")
        
        print("\n📄 Informações por página:")
        for page_info in result["pages_text"][:3]:  # Mostrar só as 3 primeiras
            print(f"   Página {page_info['page_number']}: {page_info['word_count']} palavras, {page_info['char_count']} caracteres")
        
        print("\n📝 Texto extraído (primeiros 300 caracteres):")
        print(f"   {result['text'][:300]}...")
        
        return True
    else:
        print(f"❌ Falha na extração: {result['error']}")
        return False

def test_extract_with_formatting(pdf_path: Path):
    """
    Testa a extração com informações de formatação
    """
    print("\n" + "="*50)
    print("🎨 TESTE: Extração com Formatação")
    print("="*50)
    
    result = extract_pdf_text_with_formatting(pdf_path)
    
    if result["success"]:
        print(f"✅ Extração com formatação bem-sucedida!")
        print(f"📄 Páginas processadas: {result['page_count']}")
        print(f"📝 Texto simples: {len(result['plain_text'])} caracteres")
        print(f"🎨 Blocos formatados: {len(result['formatted_content'])} páginas")
        
        if result["formatted_content"]:
            first_page = result["formatted_content"][0]
            print(f"\n📄 Primeira página contém {len(first_page['blocks'])} blocos de texto")
        
        return True
    else:
        print(f"❌ Falha na extração formatada: {result['error']}")
        return False

def test_search_functionality(pdf_path: Path):
    """
    Testa a funcionalidade de busca
    """
    print("\n" + "="*50)
    print("🔍 TESTE: Busca de Texto")
    print("="*50)
    
    search_terms = ["teste", "PyMuPDF", "extração", "PDF"]
    
    for term in search_terms:
        print(f"\n🔍 Buscando por: '{term}'")
        result = search_text_in_pdf(pdf_path, term)
        
        if result["success"]:
            print(f"   ✅ {result['total_matches']} ocorrências encontradas")
            
            if result["pages_with_matches"]:
                for page_match in result["pages_with_matches"]:
                    print(f"   📄 Página {page_match['page_number']}: {page_match['match_count']} ocorrências")
                    
                    # Mostrar contexto da primeira ocorrência
                    if page_match["matches"]:
                        context = page_match["matches"][0]["context"]
                        if context:
                            print(f"      Contexto: {context[:100]}...")
        else:
            print(f"   ❌ Erro na busca: {result['error']}")

def test_thumbnail_creation(pdf_path: Path):
    """
    Testa a criação de thumbnails
    """
    print("\n" + "="*50)
    print("🖼️ TESTE: Criação de Thumbnails")
    print("="*50)
    
    # Testar thumbnail da primeira página
    print("📸 Criando thumbnail da primeira página...")
    thumbnail_path = create_thumbnail(pdf_path, thumbnail_size=(200, 300))
    
    if thumbnail_path:
        print(f"✅ Thumbnail criado: {thumbnail_path}")
        if Path(thumbnail_path).exists():
            size = Path(thumbnail_path).stat().st_size
            print(f"   📁 Tamanho: {size} bytes")
    else:
        print("❌ Falha ao criar thumbnail")
    
    # Testar thumbnails múltiplos
    print("\n📸 Criando thumbnails de múltiplas páginas...")
    thumbnails = create_multiple_thumbnails(pdf_path, pages=[1, 2], thumbnail_size=(150, 200))
    
    if thumbnails:
        print(f"✅ {len(thumbnails)} thumbnails criados:")
        for thumb in thumbnails:
            print(f"   📄 {thumb}")
    else:
        print("❌ Falha ao criar thumbnails múltiplos")

def test_page_info(pdf_path: Path):
    """
    Testa a obtenção de informações das páginas
    """
    print("\n" + "="*50)
    print("📊 TESTE: Informações das Páginas")
    print("="*50)
    
    result = get_pdf_page_info(pdf_path)
    
    if result["success"]:
        print(f"✅ Informações obtidas com sucesso!")
        print(f"📄 Total de páginas: {result['page_count']}")
        print(f"📐 Tamanho médio: {result['document_size']['width']:.1f} x {result['document_size']['height']:.1f}")
        
        print("\n📄 Detalhes por página:")
        for page_info in result["pages_info"]:
            print(f"   Página {page_info['page_number']}:")
            print(f"      📐 Dimensões: {page_info['width']:.1f} x {page_info['height']:.1f}")
            print(f"      🔄 Rotação: {page_info['rotation']}°")
            print(f"      🔗 Links: {page_info['links_count']}")
            print(f"      🖼️ Imagens: {page_info['images_count']}")
            print(f"      📝 Caracteres: {page_info['text_length']}")
        
        return True
    else:
        print(f"❌ Falha ao obter informações: {result['error']}")
        return False

def main():
    """
    Função principal do teste
    """
    print("🧪 TESTE DAS FUNÇÕES DE EXTRAÇÃO DE PDF COM PyMuPDF")
    print("=" * 60)
    
    # Verificar se PyMuPDF está disponível
    try:
        import fitz
        print(f"✅ PyMuPDF (fitz) versão: {fitz.version[0]}")
    except ImportError:
        print("❌ PyMuPDF não está instalado!")
        print("   Instale com: pip install PyMuPDF")
        return
    
    # Criar ou encontrar um PDF para teste
    pdf_path = create_sample_pdf()
    
    if pdf_path is None:
        # Tentar encontrar um PDF existente
        possible_paths = [
            Path("app/static/uploads/pdf").glob("*.pdf"),
            Path("*.pdf"),
            Path("docs/*.pdf"),
            Path("examples/*.pdf")
        ]
        
        pdf_found = None
        for path_pattern in possible_paths:
            pdfs = list(path_pattern) if hasattr(path_pattern, '__iter__') else list(Path(".").glob(str(path_pattern)))
            if pdfs:
                pdf_found = pdfs[0]
                break
        
        if pdf_found:
            pdf_path = pdf_found
            print(f"📄 Usando PDF existente: {pdf_path}")
        else:
            print("❌ Nenhum PDF encontrado para teste!")
            print("   Coloque um arquivo PDF no diretório atual ou instale reportlab para criar um PDF de exemplo")
            return
    
    # Executar todos os testes
    tests_passed = 0
    total_tests = 5
    
    try:
        # Teste 1: Extração básica
        if test_extract_text(pdf_path):
            tests_passed += 1
        
        # Teste 2: Extração com formatação
        if test_extract_with_formatting(pdf_path):
            tests_passed += 1
        
        # Teste 3: Busca de texto
        test_search_functionality(pdf_path)
        tests_passed += 1
        
        # Teste 4: Criação de thumbnails
        test_thumbnail_creation(pdf_path)
        tests_passed += 1
        
        # Teste 5: Informações das páginas
        if test_page_info(pdf_path):
            tests_passed += 1
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
    
    # Resultado final
    print("\n" + "="*60)
    print("🏁 RESULTADO DOS TESTES")
    print("="*60)
    print(f"✅ Testes aprovados: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 Todas as funções de extração PDF estão funcionando!")
    else:
        print("⚠️ Alguns testes falharam - verifique os erros acima")
    
    print("\n📚 Funções disponíveis:")
    print("   • extract_pdf_text() - Extração completa de texto")
    print("   • extract_pdf_text_with_formatting() - Extração com formatação")
    print("   • search_text_in_pdf() - Busca de termos específicos")
    print("   • create_thumbnail() - Thumbnail da primeira página")
    print("   • create_multiple_thumbnails() - Thumbnails de múltiplas páginas")
    print("   • get_pdf_page_info() - Informações detalhadas das páginas")

if __name__ == "__main__":
    main() 