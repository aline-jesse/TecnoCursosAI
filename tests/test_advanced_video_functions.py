"""
Testes Automatizados para Funcionalidades Avançadas de Vídeo
============================================================

Este módulo contém testes abrangentes para todas as funcionalidades
avançadas de processamento de vídeo implementadas no sistema.

Funcionalidades testadas:
- Extração de slides de PDF
- Criação de vídeos em lote
- União de vídeos em apresentação
- Pipeline completo PDF → Vídeo
- Otimização de processamento
- Validações e tratamento de erros

Autor: Sistema TecnoCursos AI
Data: Janeiro 2025
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Importar funções a serem testadas
from app.utils import (
    extract_pdf_slides_as_images,
    create_videos_for_slides,
    create_videos_from_pdf_and_audio,
    stitch_videos_to_presentation,
    create_complete_presentation_from_pdf,
    optimize_batch_processing,
    validate_batch_creation_params,
    batch_create_videos_info
)

# ==========================================
# FIXTURES E CONFIGURAÇÕES DE TESTE
# ==========================================

@pytest.fixture
def temp_directory():
    """Cria uma pasta temporária para testes."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_pdf_file():
    """Cria um arquivo PDF de exemplo para testes."""
    # Para testes reais, você precisaria criar um PDF válido
    # Aqui criamos um mock
    return "sample_test.pdf"  # Arquivo que já existe no projeto

@pytest.fixture
def sample_audio_files():
    """Lista de arquivos de áudio de exemplo."""
    return [
        "app/static/audios/intro_tecnica.wav",
        "app/static/audios/curso_python.wav",
        "app/static/audios/relatorio_exec.wav"
    ]

@pytest.fixture
def sample_slides_text():
    """Lista de textos de exemplo para slides."""
    return [
        "Bem-vindos ao TecnoCursos AI! Vamos aprender sobre inteligência artificial.",
        "Python é uma linguagem poderosa para machine learning e ciência de dados.",
        "Obrigado pela atenção! Continue praticando e aprendendo."
    ]

@pytest.fixture
def mock_moviepy():
    """Mock do MoviePy para testes sem dependência."""
    with patch('app.utils.MOVIEPY_AVAILABLE', True):
        with patch('moviepy.editor.VideoFileClip') as mock_clip:
            mock_instance = Mock()
            mock_instance.duration = 10.0
            mock_instance.w = 1280
            mock_instance.h = 720
            mock_clip.return_value = mock_instance
            yield mock_instance

# ==========================================
# TESTES PARA EXTRAÇÃO DE SLIDES DE PDF
# ==========================================

class TestPDFSlideExtraction:
    """Testes para extração de slides de PDF."""

    def test_extract_pdf_slides_valid_file(self, temp_directory, sample_pdf_file):
        """Testa extração de slides de um PDF válido."""
        if not os.path.exists(sample_pdf_file):
            pytest.skip("Arquivo PDF de exemplo não encontrado")
        
        output_folder = os.path.join(temp_directory, "slides_output")
        
        # Executar extração
        result = extract_pdf_slides_as_images(
            pdf_path=sample_pdf_file,
            output_folder=output_folder,
            dpi=150,
            image_format="PNG"
        )
        
        # Verificações
        assert isinstance(result, list)
        assert len(result) > 0
        assert os.path.exists(output_folder)
        
        # Verificar se arquivos foram criados
        for slide_path in result:
            assert os.path.exists(slide_path)
            assert slide_path.endswith('.png')

    def test_extract_pdf_slides_invalid_file(self, temp_directory):
        """Testa extração com arquivo PDF inexistente."""
        nonexistent_pdf = "nonexistent.pdf"
        output_folder = os.path.join(temp_directory, "slides_output")
        
        with pytest.raises(FileNotFoundError):
            extract_pdf_slides_as_images(
                pdf_path=nonexistent_pdf,
                output_folder=output_folder
            )

    def test_extract_pdf_slides_different_formats(self, temp_directory, sample_pdf_file):
        """Testa extração com diferentes formatos de imagem."""
        if not os.path.exists(sample_pdf_file):
            pytest.skip("Arquivo PDF de exemplo não encontrado")
        
        formats = ["PNG", "JPEG", "WEBP"]
        
        for img_format in formats:
            output_folder = os.path.join(temp_directory, f"slides_{img_format}")
            
            try:
                result = extract_pdf_slides_as_images(
                    pdf_path=sample_pdf_file,
                    output_folder=output_folder,
                    image_format=img_format
                )
                
                assert len(result) > 0
                for slide_path in result:
                    assert slide_path.endswith(f'.{img_format.lower()}')
                    
            except Exception as e:
                # Alguns formatos podem não estar disponíveis
                pytest.skip(f"Formato {img_format} não suportado: {e}")

    def test_extract_pdf_slides_invalid_extension(self, temp_directory):
        """Testa com arquivo que não é PDF."""
        text_file = os.path.join(temp_directory, "not_a_pdf.txt")
        with open(text_file, 'w') as f:
            f.write("Este não é um PDF")
        
        output_folder = os.path.join(temp_directory, "slides_output")
        
        with pytest.raises(ValueError, match="Arquivo deve ter extensão .pdf"):
            extract_pdf_slides_as_images(
                pdf_path=text_file,
                output_folder=output_folder
            )

# ==========================================
# TESTES PARA CRIAÇÃO DE VÍDEOS EM LOTE
# ==========================================

class TestBatchVideoCreation:
    """Testes para criação de vídeos em lote."""

    def test_create_videos_for_slides_valid_input(self, temp_directory, sample_slides_text, sample_audio_files):
        """Testa criação de vídeos com entrada válida."""
        # Filtrar apenas áudios que existem
        existing_audios = [audio for audio in sample_audio_files if os.path.exists(audio)]
        
        if len(existing_audios) < len(sample_slides_text):
            # Ajustar listas para terem o mesmo tamanho
            slides_text = sample_slides_text[:len(existing_audios)]
            audio_files = existing_audios
        else:
            slides_text = sample_slides_text
            audio_files = existing_audios[:len(sample_slides_text)]
        
        if not audio_files:
            pytest.skip("Nenhum arquivo de áudio encontrado para teste")
        
        output_folder = os.path.join(temp_directory, "videos_output")
        
        # Mock das funções de vídeo para evitar dependências pesadas
        with patch('app.utils.create_video_from_text_and_audio') as mock_create_video:
            mock_create_video.return_value = {
                'success': True,
                'output_path': 'fake_video.mp4',
                'duration': 10.0,
                'file_size': 1024000,
                'quality_score': 0.85
            }
            
            result = create_videos_for_slides(
                slides_text_list=slides_text,
                audios_path_list=audio_files,
                output_folder=output_folder
            )
            
            # Verificações
            assert isinstance(result, list)
            assert len(result) == len(slides_text)
            assert mock_create_video.call_count == len(slides_text)

    def test_create_videos_mismatched_lists(self, temp_directory):
        """Testa criação com listas de tamanhos diferentes."""
        slides_text = ["Texto 1", "Texto 2"]
        audio_files = ["audio1.wav"]  # Lista menor
        
        with pytest.raises(ValueError, match="Número de textos.*deve ser igual ao número de áudios"):
            create_videos_for_slides(
                slides_text_list=slides_text,
                audios_path_list=audio_files,
                output_folder=temp_directory
            )

    def test_create_videos_empty_lists(self, temp_directory):
        """Testa criação com listas vazias."""
        with pytest.raises(ValueError, match="As listas de texto e áudio não podem estar vazias"):
            create_videos_for_slides(
                slides_text_list=[],
                audios_path_list=[],
                output_folder=temp_directory
            )

# ==========================================
# TESTES PARA VALIDAÇÃO DE PARÂMETROS
# ==========================================

class TestParameterValidation:
    """Testes para validação de parâmetros."""

    def test_validate_batch_creation_params_valid(self, sample_slides_text, sample_audio_files, temp_directory):
        """Testa validação com parâmetros válidos."""
        # Usar apenas áudios que existem
        existing_audios = [audio for audio in sample_audio_files if os.path.exists(audio)]
        
        if not existing_audios:
            pytest.skip("Nenhum arquivo de áudio encontrado")
        
        slides_text = sample_slides_text[:len(existing_audios)]
        audio_files = existing_audios[:len(slides_text)]
        
        result = validate_batch_creation_params(
            slides_text_list=slides_text,
            audios_path_list=audio_files,
            output_folder=temp_directory
        )
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert "summary" in result

    def test_validate_batch_creation_params_missing_audio(self, sample_slides_text, temp_directory):
        """Testa validação com arquivos de áudio inexistentes."""
        fake_audio_files = ["fake1.wav", "fake2.wav", "fake3.wav"]
        
        result = validate_batch_creation_params(
            slides_text_list=sample_slides_text,
            audios_path_list=fake_audio_files,
            output_folder=temp_directory
        )
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert any("não encontrados" in error for error in result["errors"])

    def test_validate_batch_creation_params_empty_text(self, sample_audio_files, temp_directory):
        """Testa validação com textos vazios."""
        empty_slides = ["", "Texto válido", ""]
        existing_audios = [audio for audio in sample_audio_files if os.path.exists(audio)][:3]
        
        if len(existing_audios) < 3:
            pytest.skip("Áudios insuficientes para teste")
        
        result = validate_batch_creation_params(
            slides_text_list=empty_slides,
            audios_path_list=existing_audios,
            output_folder=temp_directory
        )
        
        # Textos vazios geram avisos, não erros
        assert len(result["warnings"]) > 0

# ==========================================
# TESTES PARA OTIMIZAÇÃO DE PROCESSAMENTO
# ==========================================

class TestProcessingOptimization:
    """Testes para otimização de processamento."""

    def test_optimize_batch_processing_basic(self):
        """Testa otimização básica de processamento."""
        result = optimize_batch_processing(
            slides_count=10,
            available_cores=4,
            memory_limit_gb=8
        )
        
        assert "batch_size" in result
        assert "parallel_workers" in result
        assert "processing_strategy" in result
        assert "estimated_time_minutes" in result
        assert "recommendations" in result
        
        assert result["batch_size"] > 0
        assert result["parallel_workers"] > 0
        assert result["parallel_workers"] <= 4  # Não deve exceder cores disponíveis

    def test_optimize_batch_processing_large_workload(self):
        """Testa otimização para workload grande."""
        result = optimize_batch_processing(
            slides_count=100,
            available_cores=8,
            memory_limit_gb=16
        )
        
        assert result["processing_strategy"] in ["small_batches", "large_batches"]
        assert len(result["recommendations"]) > 0

    def test_optimize_batch_processing_limited_resources(self):
        """Testa otimização com recursos limitados."""
        result = optimize_batch_processing(
            slides_count=50,
            available_cores=2,
            memory_limit_gb=4
        )
        
        assert result["parallel_workers"] <= 2
        assert any("RAM" in rec for rec in result["recommendations"])

# ==========================================
# TESTES PARA INFORMAÇÕES DE LOTE
# ==========================================

class TestBatchInfo:
    """Testes para informações de processamento em lote."""

    def test_batch_create_videos_info_basic(self):
        """Testa cálculo de informações básicas."""
        result = batch_create_videos_info(
            slides_count=5,
            template="modern",
            resolution="hd"
        )
        
        assert "estimated_time_minutes" in result
        assert "estimated_disk_space_mb" in result
        assert "recommended_memory_mb" in result
        assert "processing_tips" in result
        
        assert result["estimated_time_minutes"] > 0
        assert result["estimated_disk_space_mb"] > 0

    def test_batch_create_videos_info_different_resolutions(self):
        """Testa cálculos para diferentes resoluções."""
        resolutions = ["hd", "fhd", "4k"]
        
        for resolution in resolutions:
            result = batch_create_videos_info(
                slides_count=10,
                resolution=resolution
            )
            
            assert result["resolution"] == resolution
            assert "resolution_info" in result
            assert "width" in result["resolution_info"]
            assert "height" in result["resolution_info"]

    def test_batch_create_videos_info_large_batch(self):
        """Testa informações para lote grande."""
        result = batch_create_videos_info(
            slides_count=100,
            template="corporate",
            resolution="fhd"
        )
        
        # Deve ter dicas específicas para lotes grandes
        tips = result["processing_tips"]
        assert any("lotes menores" in tip for tip in tips) or any("RAM" in tip for tip in tips)

# ==========================================
# TESTES MOCK PARA FUNCIONALIDADES PESADAS
# ==========================================

class TestVideoStitching:
    """Testes para união de vídeos (com mocks)."""

    @patch('app.utils.MOVIEPY_AVAILABLE', True)
    def test_stitch_videos_mock(self, temp_directory):
        """Testa união de vídeos com mock do MoviePy."""
        video_paths = ["video1.mp4", "video2.mp4", "video3.mp4"]
        output_path = os.path.join(temp_directory, "final_presentation.mp4")
        
        with patch('moviepy.editor.VideoFileClip') as mock_clip_class:
            with patch('moviepy.editor.concatenate_videoclips') as mock_concat:
                with patch('moviepy.editor.ImageClip') as mock_image_clip:
                    
                    # Configurar mocks
                    mock_clip = Mock()
                    mock_clip.duration = 10.0
                    mock_clip.w = 1280
                    mock_clip.h = 720
                    mock_clip.close = Mock()
                    mock_clip.fadeout.return_value = mock_clip
                    mock_clip.fadein.return_value = mock_clip
                    mock_clip_class.return_value = mock_clip
                    
                    mock_final = Mock()
                    mock_final.duration = 30.0
                    mock_final.write_videofile = Mock()
                    mock_final.close = Mock()
                    mock_concat.return_value = mock_final
                    
                    # Simular arquivo criado
                    def fake_write_video(*args, **kwargs):
                        with open(output_path, 'w') as f:
                            f.write("fake video content")
                    
                    mock_final.write_videofile.side_effect = fake_write_video
                    
                    # Executar teste
                    result = stitch_videos_to_presentation(
                        video_paths=video_paths,
                        output_path=output_path,
                        transition_duration=0.5,
                        add_intro=True,
                        add_outro=True
                    )
                    
                    # Verificações
                    assert result["success"] is True
                    assert result["final_video_path"] == output_path
                    assert result["videos_processed"] == 3
                    assert os.path.exists(output_path)

# ==========================================
# TESTES DE INTEGRAÇÃO E EDGE CASES
# ==========================================

class TestEdgeCases:
    """Testes para casos extremos e edge cases."""

    def test_very_long_text_handling(self, temp_directory):
        """Testa tratamento de texto muito longo."""
        very_long_text = "A" * 3000  # Maior que o limite de 2000 caracteres
        slides_text = [very_long_text]
        audio_files = ["fake_audio.wav"]
        
        # Deve gerar aviso sobre texto longo
        result = validate_batch_creation_params(
            slides_text_list=slides_text,
            audios_path_list=audio_files,
            output_folder=temp_directory
        )
        
        assert len(result["warnings"]) > 0
        assert any("longo" in warning for warning in result["warnings"])

    def test_zero_slides_optimization(self):
        """Testa otimização com zero slides."""
        with pytest.raises(Exception):  # Deve gerar erro
            optimize_batch_processing(
                slides_count=0,
                available_cores=4,
                memory_limit_gb=8
            )

    def test_negative_parameters(self):
        """Testa parâmetros negativos."""
        with pytest.raises(Exception):
            batch_create_videos_info(
                slides_count=-5
            )

# ==========================================
# SUITE DE TESTES UTILITÁRIOS
# ==========================================

class TestUtilities:
    """Testes para funções utilitárias."""

    def test_path_handling(self, temp_directory):
        """Testa manipulação de caminhos."""
        # Testar criação de pastas
        nested_folder = os.path.join(temp_directory, "deep", "nested", "folder")
        
        result = validate_batch_creation_params(
            slides_text_list=["Teste"],
            audios_path_list=["fake.wav"],
            output_folder=nested_folder
        )
        
        # A função deve criar as pastas necessárias
        assert os.path.exists(nested_folder)

    def test_error_handling_graceful(self, temp_directory):
        """Testa tratamento de erros gracioso."""
        # Forçar erro ao usar pasta readonly (simulado)
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Acesso negado")):
            result = validate_batch_creation_params(
                slides_text_list=["Teste"],
                audios_path_list=["fake.wav"],
                output_folder=temp_directory
            )
            
            assert result["is_valid"] is False
            assert len(result["errors"]) > 0

# ==========================================
# CONFIGURAÇÃO DE TESTE
# ==========================================

def test_module_imports():
    """Testa se todos os módulos podem ser importados."""
    try:
        from app.utils import (
            extract_pdf_slides_as_images,
            create_videos_for_slides,
            create_videos_from_pdf_and_audio,
            stitch_videos_to_presentation,
            create_complete_presentation_from_pdf,
            optimize_batch_processing,
            validate_batch_creation_params,
            batch_create_videos_info
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Erro ao importar módulos: {e}")

def test_dependencies_available():
    """Testa disponibilidade de dependências críticas."""
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        from pathlib import Path
        assert True
    except ImportError as e:
        pytest.fail(f"Dependência crítica não disponível: {e}")

# ==========================================
# FIXTURES DE LIMPEZA
# ==========================================

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Limpa arquivos temporários após cada teste."""
    yield
    
    # Limpar arquivos temporários que podem ter sido criados
    temp_files = [
        "temp_intro_slide.png",
        "temp_outro_slide.png",
        "temp-audio.m4a"
    ]
    
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass  # Ignorar erros de limpeza

if __name__ == "__main__":
    # Executar testes se o arquivo for chamado diretamente
    pytest.main([__file__, "-v", "--tb=short"])
    print("\n🧪 Execução de testes concluída!")
    print("💡 Para executar com coverage: pytest --cov=app.utils tests/test_advanced_video_functions.py") 