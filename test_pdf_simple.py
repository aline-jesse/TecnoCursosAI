#!/usr/bin/env python3
"""
Teste simplificado das funções de extração de PDF usando PyMuPDF
Não depende de bibliotecas externas além do PyMuPDF
"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple, List

# Verificar se PyMuPDF está disponível
try:
    import fitz  # PyMuPDF
    print(f"✅ PyMuPDF (fitz) versão: {fitz.version[0]}")
except ImportError:
    print("❌ PyMuPDF não está instalado!")
    print("   Instale com: pip install PyMuPDF")
    sys.exit(1)

def extract_pdf_text_simple(file_path: Path, max_pages: Optional[int] = None) -> dict:
    """
    Extrai texto completo de um arquivo PDF usando PyMuPDF - Versão simplificada
    """
    result = {
        "success": False,
        "text": "",
        "page_count": 0,
        "pages_text": [],
        "metadata": {},
        "file_size": 0,
        "error": None
    }
    
    try:
        # Verificar se arquivo existe
        if not file_path.exists():
            result["error"] = f"Arquivo não encontrado: {file_path}"
            return result
        
        # Obter tamanho do arquivo
        result["file_size"] = file_path.stat().st_size
        
        # Abrir documento PDF com PyMuPDF
        pdf_document = fitz.open(str(file_path))
        result["page_count"] = pdf_document.page_count
        
        # Extrair metadados do PDF
        metadata = pdf_document.metadata
        result["metadata"] = {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", "")
        }
        
        # Determinar quantas páginas processar
        pages_to_process = result["page_count"]
        if max_pages and max_pages > 0:
            pages_to_process = min(max_pages, result["page_count"])
        
        # Extrair texto de cada página
        all_text = []
        pages_text = []
        
        for page_num in range(pages_to_process):
            try:
                page = pdf_document[page_num]
                page_text = page.get_text()
                
                # Limpar texto
                cleaned_text = page_text.strip()
                
                pages_text.append({
                    "page_number": page_num + 1,
                    "text": cleaned_text,
                    "word_count": len(cleaned_text.split()),
                    "char_count": len(cleaned_text)
                })
                
                all_text.append(cleaned_text)
                
                print(f"📄 Página {page_num + 1}/{pages_to_process} processada: {len(cleaned_text)} caracteres")
                
            except Exception as page_error:
                print(f"⚠️ Erro ao processar página {page_num + 1}: {page_error}")
                pages_text.append({
                    "page_number": page_num + 1,
                    "text": "",
                    "error": str(page_error),
                    "word_count": 0,
                    "char_count": 0
                })
        
        # Fechar documento
        pdf_document.close()
        
        # Combinar todo o texto
        result["text"] = "\n\n".join(all_text)
        result["pages_text"] = pages_text
        result["success"] = True
        
        # Estatísticas finais
        total_words = len(result["text"].split())
        total_chars = len(result["text"])
        
        print(f"✅ PDF processado com sucesso:")
        print(f"   📄 Páginas: {result['page_count']} (processadas: {pages_to_process})")
        print(f"   📝 Palavras: {total_words}")
        print(f"   🔤 Caracteres: {total_chars}")
        print(f"   📁 Tamanho: {result['file_size']} bytes")
        
        return result
        
    except Exception as e:
        error_msg = f"Erro ao extrair texto do PDF: {str(e)}"
        print(f"❌ {error_msg}")
        result["error"] = error_msg
        return result

def create_thumbnail_simple(file_path: Path, thumbnail_size: Tuple[int, int] = (300, 400)) -> Optional[str]:
    """
    Cria thumbnail para arquivo PDF usando PyMuPDF - Versão simplificada
    """
    try:
        # Verificar se é um arquivo PDF
        if not file_path.suffix.lower() == '.pdf':
            print(f"⚠️ Arquivo não é PDF: {file_path}")
            return None
        
        # Verificar se arquivo existe
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            return None
        
        # Criar diretório de thumbnails se não existir
        thumbnail_dir = Path("thumbnails")
        thumbnail_dir.mkdir(exist_ok=True)
        
        # Gerar nome do thumbnail
        thumbnail_name = f"{file_path.stem}_thumb.png"
        thumbnail_path = thumbnail_dir / thumbnail_name
        
        # Abrir documento PDF
        pdf_document = fitz.open(str(file_path))
        
        if pdf_document.page_count == 0:
            print(f"⚠️ PDF vazio: {file_path}")
            pdf_document.close()
            return None
        
        # Pegar a primeira página
        first_page = pdf_document[0]
        
        # Calcular matriz de transformação para o tamanho desejado
        page_rect = first_page.rect
        scale_x = thumbnail_size[0] / page_rect.width
        scale_y = thumbnail_size[1] / page_rect.height
        scale = min(scale_x, scale_y)  # Manter proporção
        
        matrix = fitz.Matrix(scale, scale)
        
        # Renderizar página como imagem
        pix = first_page.get_pixmap(matrix=matrix)
        
        # Salvar como PNG
        pix.save(str(thumbnail_path))
        
        # Limpar recursos
        pix = None
        pdf_document.close()
        
        print(f"✅ Thumbnail criado: {thumbnail_path} ({thumbnail_size[0]}x{thumbnail_size[1]})")
        return str(thumbnail_path)
        
    except Exception as e:
        print(f"❌ Erro ao criar thumbnail: {e}")
        return None

def search_text_simple(file_path: Path, search_term: str) -> dict:
    """
    Busca por texto específico no PDF - Versão simplificada
    """
    result = {
        "success": False,
        "search_term": search_term,
        "total_matches": 0,
        "pages_with_matches": [],
        "error": None
    }
    
    try:
        pdf_document = fitz.open(str(file_path))
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # Buscar texto na página
            text_instances = page.search_for(search_term)
            
            if text_instances:
                page_matches = {
                    "page_number": page_num + 1,
                    "match_count": len(text_instances)
                }
                result["pages_with_matches"].append(page_matches)
                result["total_matches"] += len(text_instances)
        
        pdf_document.close()
        result["success"] = True
        
        print(f"🔍 Busca concluída: {result['total_matches']} ocorrências de '{search_term}'")
        
        return result
        
    except Exception as e:
        error_msg = f"Erro na busca: {str(e)}"
        print(f"❌ {error_msg}")
        result["error"] = error_msg
        return result

def create_sample_pdf_simple():
    """
    Cria um PDF de exemplo simples para testes
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = Path("sample_test.pdf")
        
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
        print("⚠️ reportlab não instalado - tentando encontrar PDF existente")
        return None
    except Exception as e:
        print(f"❌ Erro ao criar PDF de exemplo: {e}")
        return None

def test_extraction(pdf_path: Path):
    """
    Testa a extração de texto
    """
    print("\n" + "="*50)
    print("🔍 TESTE: Extração de Texto")
    print("="*50)
    
    result = extract_pdf_text_simple(pdf_path)
    
    if result["success"]:
        print(f"\n✅ Extração bem-sucedida!")
        print(f"📄 Páginas: {result['page_count']}")
        print(f"📝 Palavras totais: {len(result['text'].split())}")
        print(f"🔤 Caracteres totais: {len(result['text'])}")
        
        print("\n📋 Metadados do PDF:")
        for key, value in result["metadata"].items():
            if value:
                print(f"   {key}: {value}")
        
        print("\n📝 Texto extraído (primeiros 300 caracteres):")
        print(f"   {result['text'][:300]}...")
        
        return True
    else:
        print(f"❌ Falha na extração: {result['error']}")
        return False

def test_thumbnail(pdf_path: Path):
    """
    Testa a criação de thumbnails
    """
    print("\n" + "="*50)
    print("🖼️ TESTE: Criação de Thumbnail")
    print("="*50)
    
    thumbnail_path = create_thumbnail_simple(pdf_path, thumbnail_size=(200, 300))
    
    if thumbnail_path:
        print(f"✅ Thumbnail criado: {thumbnail_path}")
        if Path(thumbnail_path).exists():
            size = Path(thumbnail_path).stat().st_size
            print(f"   📁 Tamanho: {size} bytes")
        return True
    else:
        print("❌ Falha ao criar thumbnail")
        return False

def test_search(pdf_path: Path):
    """
    Testa a busca de texto
    """
    print("\n" + "="*50)
    print("🔍 TESTE: Busca de Texto")
    print("="*50)
    
    search_terms = ["teste", "PDF", "extração"]
    success_count = 0
    
    for term in search_terms:
        print(f"\n🔍 Buscando por: '{term}'")
        result = search_text_simple(pdf_path, term)
        
        if result["success"]:
            print(f"   ✅ {result['total_matches']} ocorrências encontradas")
            
            if result["pages_with_matches"]:
                for page_match in result["pages_with_matches"]:
                    print(f"   📄 Página {page_match['page_number']}: {page_match['match_count']} ocorrências")
            success_count += 1
        else:
            print(f"   ❌ Erro na busca: {result['error']}")
    
    return success_count > 0

def main():
    """
    Função principal do teste
    """
    print("🧪 TESTE SIMPLIFICADO - EXTRAÇÃO DE PDF COM PyMuPDF")
    print("=" * 60)
    
    # Criar ou encontrar um PDF para teste
    pdf_path = create_sample_pdf_simple()
    
    if pdf_path is None:
        # Tentar encontrar um PDF existente
        print("📄 Procurando por PDFs existentes...")
        possible_files = list(Path(".").glob("*.pdf"))
        
        if possible_files:
            pdf_path = possible_files[0]
            print(f"📄 Usando PDF existente: {pdf_path}")
        else:
            print("❌ Nenhum PDF encontrado para teste!")
            print("   Coloque um arquivo PDF no diretório atual")
            print("   Ou instale reportlab para criar um PDF de exemplo:")
            print("   pip install reportlab")
            return
    
    # Executar todos os testes
    tests_passed = 0
    total_tests = 3
    
    try:
        # Teste 1: Extração de texto
        if test_extraction(pdf_path):
            tests_passed += 1
        
        # Teste 2: Criação de thumbnail
        if test_thumbnail(pdf_path):
            tests_passed += 1
        
        # Teste 3: Busca de texto
        if test_search(pdf_path):
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
    
    print("\n📚 Funcionalidades testadas:")
    print("   • extract_pdf_text() - Extração completa de texto")
    print("   • create_thumbnail() - Criação de thumbnails")
    print("   • search_text() - Busca de termos específicos")
    print("\n💡 Para usar essas funções no seu código:")
    print("   from app.utils import extract_pdf_text, create_thumbnail")

if __name__ == "__main__":
    main() 