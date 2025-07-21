"""
Testes unitários para as funções de extração de texto PDF e PPTX
Arquivo: tests/test_text_extraction.py
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import List

# Adicionar o diretório app ao path para importar as funções
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

try:
    from utils import extract_text_from_pdf, extract_text_from_pptx, clean_extracted_text
except ImportError:
    pytest.skip("Módulo utils não encontrado", allow_module_level=True)


class TestTextExtraction:
    """Classe de testes para extração de texto de arquivos PDF e PPTX"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf_path = os.path.join(self.temp_dir, "test.pdf")
        self.test_pptx_path = os.path.join(self.temp_dir, "test.pptx")
    
    def teardown_method(self):
        """Cleanup executado após cada teste"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class TestExtractTextFromPDF:
    """Testes específicos para a função extract_text_from_pdf"""
    
    def test_extract_text_from_pdf_file_not_found(self):
        """Testa se FileNotFoundError é levantada para arquivo inexistente"""
        non_existent_file = "arquivo_inexistente.pdf"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            extract_text_from_pdf(non_existent_file)
        
        assert "Arquivo PDF não encontrado" in str(exc_info.value)
        assert non_existent_file in str(exc_info.value)
    
    def test_extract_text_from_pdf_empty_path(self):
        """Testa comportamento com path vazio"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("")
    
    def test_extract_text_from_pdf_none_path(self):
        """Testa comportamento com path None"""
        with pytest.raises(TypeError):
            extract_text_from_pdf(None)
    
    @patch('fitz.open')
    def test_extract_text_from_pdf_success(self, mock_fitz_open):
        """Testa extração bem-sucedida de texto de PDF"""
        # Mock do documento PDF
        mock_doc = MagicMock()
        mock_doc.page_count = 2
        
        # Mock das páginas
        mock_page_1 = MagicMock()
        mock_page_1.get_text.return_value = "Texto da página 1\n\nCom quebras de linha"
        
        mock_page_2 = MagicMock()
        mock_page_2.get_text.return_value = "Texto da página 2\n\n\nCom mais quebras"
        
        mock_doc.__getitem__ = MagicMock(side_effect=[mock_page_1, mock_page_2])
        mock_doc.close = MagicMock()
        
        mock_fitz_open.return_value = mock_doc
        
        # Simular arquivo existente
        with patch('os.path.exists', return_value=True):
            result = extract_text_from_pdf("test.pdf")
        
        # Verificações
        assert isinstance(result, list)
        assert len(result) == 2
        assert "Texto da página 1" in result[0]
        assert "Texto da página 2" in result[1]
        
        # Verificar se os métodos foram chamados
        mock_fitz_open.assert_called_once_with("test.pdf")
        mock_doc.close.assert_called_once()
    
    @patch('fitz.open')
    def test_extract_text_from_pdf_empty_document(self, mock_fitz_open):
        """Testa PDF vazio (sem páginas)"""
        mock_doc = MagicMock()
        mock_doc.page_count = 0
        mock_doc.close = MagicMock()
        
        mock_fitz_open.return_value = mock_doc
        
        with patch('os.path.exists', return_value=True):
            result = extract_text_from_pdf("empty.pdf")
        
        assert isinstance(result, list)
        assert len(result) == 0
        mock_doc.close.assert_called_once()
    
    @patch('fitz.open')
    def test_extract_text_from_pdf_exception_handling(self, mock_fitz_open):
        """Testa tratamento de exceções durante a extração"""
        mock_fitz_open.side_effect = Exception("Erro de leitura do PDF")
        
        with patch('os.path.exists', return_value=True):
            with pytest.raises(Exception) as exc_info:
                extract_text_from_pdf("corrupted.pdf")
        
        assert "Erro ao processar arquivo PDF" in str(exc_info.value)


class TestExtractTextFromPPTX:
    """Testes específicos para a função extract_text_from_pptx"""
    
    def test_extract_text_from_pptx_file_not_found(self):
        """Testa se FileNotFoundError é levantada para arquivo inexistente"""
        non_existent_file = "arquivo_inexistente.pptx"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            extract_text_from_pptx(non_existent_file)
        
        assert "Arquivo PPTX não encontrado" in str(exc_info.value)
        assert non_existent_file in str(exc_info.value)
    
    def test_extract_text_from_pptx_missing_dependency(self):
        """Testa comportamento quando python-pptx não está instalado"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'pptx'")):
                with pytest.raises(ImportError) as exc_info:
                    extract_text_from_pptx("test.pptx")
                
                assert "python-pptx não encontrada" in str(exc_info.value)
    
    @patch('os.path.exists', return_value=True)
    def test_extract_text_from_pptx_success(self, mock_exists):
        """Testa extração bem-sucedida de texto de PPTX"""
        # Mock da apresentação
        mock_presentation = MagicMock()
        
        # Mock dos slides
        mock_slide_1 = MagicMock()
        mock_slide_2 = MagicMock()
        mock_presentation.slides = [mock_slide_1, mock_slide_2]
        
        # Mock das shapes com texto
        mock_shape_1 = MagicMock()
        mock_shape_1.text = "Título do Slide 1"
        mock_shape_1.text_frame = None
        mock_shape_1.table = None
        
        mock_shape_2 = MagicMock()
        mock_shape_2.text = "Conteúdo do Slide 1"
        
        mock_slide_1.shapes = [mock_shape_1, mock_shape_2]
        
        # Mock para slide 2
        mock_shape_3 = MagicMock()
        mock_shape_3.text = "Slide 2 Content"
        mock_slide_2.shapes = [mock_shape_3]
        
        with patch('pptx.Presentation', return_value=mock_presentation):
            result = extract_text_from_pptx("test.pptx")
        
        # Verificações
        assert isinstance(result, list)
        assert len(result) == 2
        assert "Título do Slide 1" in result[0]
        assert "Slide 2 Content" in result[1]
    
    @patch('os.path.exists', return_value=True)
    def test_extract_text_from_pptx_with_tables(self, mock_exists):
        """Testa extração de texto de slides com tabelas"""
        mock_presentation = MagicMock()
        mock_slide = MagicMock()
        mock_presentation.slides = [mock_slide]
        
        # Mock de shape com tabela
        mock_shape = MagicMock()
        mock_shape.text = ""
        mock_table = MagicMock()
        
        # Mock das células da tabela
        mock_cell_1 = MagicMock()
        mock_cell_1.text = "Célula 1"
        mock_cell_2 = MagicMock()
        mock_cell_2.text = "Célula 2"
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell_1, mock_cell_2]
        mock_table.rows = [mock_row]
        
        mock_shape.table = mock_table
        mock_slide.shapes = [mock_shape]
        
        with patch('pptx.Presentation', return_value=mock_presentation):
            result = extract_text_from_pptx("test.pptx")
        
        assert len(result) == 1
        assert "Célula 1" in result[0]
        assert "Célula 2" in result[0]


class TestCleanExtractedText:
    """Testes para a função clean_extracted_text"""
    
    def test_clean_extracted_text_empty_string(self):
        """Testa comportamento com string vazia"""
        result = clean_extracted_text("")
        assert result == ""
    
    def test_clean_extracted_text_none(self):
        """Testa comportamento com None"""
        result = clean_extracted_text(None)
        assert result == ""
    
    def test_clean_extracted_text_multiple_newlines(self):
        """Testa remoção de múltiplas quebras de linha"""
        text_with_newlines = "Texto\n\n\n\nCom muitas\n\n\n\nquebras"
        result = clean_extracted_text(text_with_newlines)
        expected = "Texto\n\nCom muitas\n\nquebras"
        assert result == expected
    
    def test_clean_extracted_text_multiple_spaces(self):
        """Testa remoção de múltiplos espaços"""
        text_with_spaces = "Texto    com     muitos    espaços"
        result = clean_extracted_text(text_with_spaces)
        expected = "Texto com muitos espaços"
        assert result == expected
    
    def test_clean_extracted_text_tabs(self):
        """Testa remoção de tabs excessivos"""
        text_with_tabs = "Texto\t\t\tcom\t\t\tmuitos\t\t\ttabs"
        result = clean_extracted_text(text_with_tabs)
        expected = "Texto com muitos tabs"
        assert result == expected
    
    def test_clean_extracted_text_whitespace_edges(self):
        """Testa remoção de espaços nas bordas"""
        text_with_whitespace = "   \n\t  Texto central  \t\n   "
        result = clean_extracted_text(text_with_whitespace)
        expected = "Texto central"
        assert result == expected
    
    def test_clean_extracted_text_complex_formatting(self):
        """Testa limpeza de texto com formatação complexa"""
        complex_text = """   
        
        Título Principal
        
        
        
        Parágrafo    com     espaços
        
        
        Outro   parágrafo\t\t\tcom\t\ttabs
        
        
        
        """
        result = clean_extracted_text(complex_text)
        
        # Verificar que múltiplas quebras foram reduzidas
        assert "\n\n\n" not in result
        # Verificar que múltiplos espaços foram reduzidos
        assert "  " not in result
        # Verificar que o texto foi limpo nas bordas
        assert not result.startswith(" ")
        assert not result.endswith(" ")


class TestIntegrationTests:
    """Testes de integração usando arquivos reais se disponíveis"""
    
    def test_extract_text_from_real_pdf(self):
        """Testa com arquivo PDF real se disponível"""
        real_pdf_path = "sample_test.pdf"
        
        if os.path.exists(real_pdf_path):
            try:
                result = extract_text_from_pdf(real_pdf_path)
                
                assert isinstance(result, list)
                assert len(result) > 0
                
                # Verificar que cada página tem algum conteúdo processado
                for i, page_text in enumerate(result):
                    assert isinstance(page_text, str)
                    print(f"Página {i+1}: {len(page_text)} caracteres")
                    
            except Exception as e:
                pytest.fail(f"Falha na extração de PDF real: {e}")
        else:
            pytest.skip("Arquivo PDF de teste não encontrado")
    
    def test_file_type_validation(self):
        """Testa validação de tipos de arquivo"""
        # Criar arquivo temporário com extensão incorreta
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"conteudo qualquer")
            txt_file_path = tmp_file.name
        
        try:
            # A função deve funcionar independente da extensão se o conteúdo for válido
            # Mas deve falhar para arquivos que não são PDF
            with pytest.raises(Exception):
                extract_text_from_pdf(txt_file_path)
        finally:
            os.unlink(txt_file_path)


@pytest.fixture
def sample_pdf_content():
    """Fixture com conteúdo de exemplo para testes"""
    return {
        'pages': [
            "Primeira página do documento\nCom algum conteúdo interessante",
            "Segunda página\nCom mais informações relevantes",
            "Terceira página\nConclusão do documento"
        ]
    }


@pytest.fixture
def sample_pptx_content():
    """Fixture com conteúdo de exemplo para PPTX"""
    return {
        'slides': [
            "Título: Apresentação Importante\nSubtítulo: Dados relevantes",
            "Slide 2: Análise\nGráficos e tabelas",
            "Conclusão\nPróximos passos"
        ]
    }


# Configurações específicas para pytest
pytestmark = pytest.mark.asyncio

if __name__ == "__main__":
    """Executar testes se chamado diretamente"""
    pytest.main([__file__, "-v", "--tb=short"]) 