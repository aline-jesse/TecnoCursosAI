#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários para Sistema TTS - generate_narration
=====================================================

Testes abrangentes para validar funcionalidades de conversão texto-para-áudio
usando mocks para evitar dependências externas durante testes.
"""

import unittest
import asyncio
import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import sys

# Adicionar diretório raiz para importações
sys.path.append(str(Path(__file__).parent.parent))

class TestGenerateNarration(unittest.TestCase):
    """Testes para funções de narração TTS"""
    
    def setUp(self):
        """Setup executado antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_text = "Este é um teste de narração em português."
        self.test_output_path = os.path.join(self.temp_dir, "test_audio.mp3")
        
    def tearDown(self):
        """Cleanup executado após cada teste"""
        # Limpar arquivos temporários
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('app.utils.TTS_AVAILABLE', True)
    @patch('app.utils.TTSService')
    def test_generate_narration_sync_success(self, mock_tts_service):
        """Testa geração síncrona bem-sucedida"""
        from app.utils import generate_narration_sync
        
        # Mock do resultado TTS
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.audio_path = self.test_output_path
        mock_result.duration = 5.2
        mock_result.provider_used = "gtts"
        mock_result.metadata = {"voice": "pt_speaker_0"}
        
        mock_service_instance = MagicMock()
        mock_service_instance.generate_audio = AsyncMock(return_value=mock_result)
        mock_tts_service.return_value = mock_service_instance
        
        # Executar teste
        result = generate_narration_sync(
            text=self.test_text,
            output_path=self.test_output_path,
            provider="gtts"
        )
        
        # Validações
        self.assertTrue(result['success'])
        self.assertEqual(result['audio_path'], self.test_output_path)
        self.assertEqual(result['duration'], 5.2)
        self.assertEqual(result['provider_used'], "gtts")
        self.assertIsNone(result['error'])
        
    @patch('app.utils.TTS_AVAILABLE', True)
    @patch('app.utils.TTSService')
    async def test_generate_narration_async_success(self, mock_tts_service):
        """Testa geração assíncrona bem-sucedida"""
        from app.utils import generate_narration
        
        # Mock do resultado TTS
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.audio_path = self.test_output_path
        mock_result.duration = 8.7
        mock_result.provider_used = "bark"
        mock_result.metadata = {"voice": "v2/pt_speaker_2"}
        
        mock_service_instance = MagicMock()
        mock_service_instance.generate_audio = AsyncMock(return_value=mock_result)
        mock_tts_service.return_value = mock_service_instance
        
        # Executar teste
        result = await generate_narration(
            text=self.test_text,
            output_path=self.test_output_path,
            provider="bark",
            voice="v2/pt_speaker_2"
        )
        
        # Validações
        self.assertTrue(result['success'])
        self.assertEqual(result['audio_path'], self.test_output_path)
        self.assertEqual(result['duration'], 8.7)
        self.assertEqual(result['provider_used'], "bark")
        
    @patch('app.utils.TTS_AVAILABLE', False)
    def test_tts_not_available(self):
        """Testa comportamento quando TTS não está disponível"""
        from app.utils import generate_narration_sync
        
        result = generate_narration_sync(
            text=self.test_text,
            output_path=self.test_output_path
        )
        
        self.assertFalse(result['success'])
        self.assertIn("TTS não disponível", result['error'])
        self.assertIsNone(result['audio_path'])
        
    def test_empty_text_validation(self):
        """Testa validação de texto vazio"""
        from app.utils import generate_narration_sync
        
        with patch('app.utils.TTS_AVAILABLE', True):
            # Texto vazio
            result = generate_narration_sync(text="", output_path=self.test_output_path)
            self.assertFalse(result['success'])
            self.assertIn("vazio", result['error'])
            
            # Texto apenas espaços
            result = generate_narration_sync(text="   ", output_path=self.test_output_path)
            self.assertFalse(result['success'])
            self.assertIn("vazio", result['error'])
            
    def test_text_length_validation(self):
        """Testa validação de comprimento do texto"""
        from app.utils import generate_narration_sync
        
        with patch('app.utils.TTS_AVAILABLE', True):
            # Texto muito longo
            long_text = "x" * 3000
            result = generate_narration_sync(text=long_text, output_path=self.test_output_path)
            
            self.assertFalse(result['success'])
            self.assertIn("muito longo", result['error'])
            self.assertIn("3000 caracteres", result['error'])
            
    @patch('app.utils.TTS_AVAILABLE', True)
    @patch('app.utils.TTSService')
    def test_tts_service_failure(self, mock_tts_service):
        """Testa tratamento de falha no serviço TTS"""
        from app.utils import generate_narration_sync
        
        # Mock de falha no TTS
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Erro no modelo TTS"
        mock_result.audio_path = None
        mock_result.duration = 0.0
        mock_result.provider_used = "bark"
        
        mock_service_instance = MagicMock()
        mock_service_instance.generate_audio = AsyncMock(return_value=mock_result)
        mock_tts_service.return_value = mock_service_instance
        
        result = generate_narration_sync(
            text=self.test_text,
            output_path=self.test_output_path
        )
        
        self.assertFalse(result['success'])
        self.assertIn("Erro no modelo TTS", result['error'])
        self.assertIsNone(result['audio_path'])
        
    @patch('app.utils.TTS_AVAILABLE', True)
    @patch('app.utils.TTSService')
    def test_exception_handling(self, mock_tts_service):
        """Testa tratamento de exceções"""
        from app.utils import generate_narration_sync
        
        # Mock que levanta exceção
        mock_service_instance = MagicMock()
        mock_service_instance.generate_audio = AsyncMock(side_effect=Exception("Erro de conexão"))
        mock_tts_service.return_value = mock_service_instance
        
        result = generate_narration_sync(
            text=self.test_text,
            output_path=self.test_output_path
        )
        
        self.assertFalse(result['success'])
        self.assertIn("Erro na geração de narração", result['error'])
        self.assertIn("Erro de conexão", result['error'])
        
    @patch('app.utils.TTS_AVAILABLE', True)
    def test_provider_configuration(self):
        """Testa configuração de diferentes provedores"""
        from app.utils import TTSProvider
        
        with patch('app.utils.TTSService') as mock_tts_service:
            from app.utils import generate_narration_sync
            
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.audio_path = self.test_output_path
            mock_result.duration = 3.0
            mock_result.provider_used = "gtts"
            
            mock_service_instance = MagicMock()
            mock_service_instance.generate_audio = AsyncMock(return_value=mock_result)
            mock_tts_service.return_value = mock_service_instance
            
            # Testar provider "bark"
            result = generate_narration_sync(
                text=self.test_text,
                output_path=self.test_output_path,
                provider="bark"
            )
            
            # Verificar se TTSConfig foi chamado com BARK
            call_args = mock_service_instance.generate_audio.call_args
            config = call_args[1]['config']  # config é passado como keyword arg
            self.assertEqual(config.provider, TTSProvider.BARK)
            
    def test_audio_file_creation(self):
        """Testa criação do diretório de saída"""
        from app.utils import generate_narration_sync
        
        # Diretório que não existe
        non_existent_dir = os.path.join(self.temp_dir, "subdir", "audio")
        output_path = os.path.join(non_existent_dir, "test.mp3")
        
        with patch('app.utils.TTS_AVAILABLE', True), \
             patch('app.utils.TTSService') as mock_tts_service:
            
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.audio_path = output_path
            mock_result.duration = 1.0
            mock_result.provider_used = "gtts"
            
            mock_service_instance = MagicMock()
            mock_service_instance.generate_audio = AsyncMock(return_value=mock_result)
            mock_tts_service.return_value = mock_service_instance
            
            result = generate_narration_sync(
                text=self.test_text,
                output_path=output_path
            )
            
            # Verificar que o diretório foi criado
            self.assertTrue(os.path.exists(non_existent_dir))
            self.assertTrue(result['success'])


class TestTTSIntegration(unittest.TestCase):
    """Testes de integração com serviços TTS reais (quando disponíveis)"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipUnless(
        os.getenv('TTS_INTEGRATION_TESTS') == 'true',
        "Testes de integração TTS desabilitados. Use TTS_INTEGRATION_TESTS=true para habilitar"
    )
    def test_real_gtts_integration(self):
        """Teste de integração real com gTTS (apenas se habilitado)"""
        from app.utils import generate_narration_sync
        
        output_path = os.path.join(self.temp_dir, "integration_test.mp3")
        
        result = generate_narration_sync(
            text="Teste de integração real com gTTS.",
            output_path=output_path,
            provider="gtts"
        )
        
        if result['success']:
            self.assertTrue(os.path.exists(result['audio_path']))
            self.assertGreater(result['duration'], 0)
            self.assertEqual(result['provider_used'], "gtts")
        else:
            # Se falhar, verificar se é por dependências ausentes
            self.assertIn("disponível", result['error'].lower())


class TestTTSPerformance(unittest.TestCase):
    """Testes de performance e stress"""
    
    @patch('app.utils.TTS_AVAILABLE', True)
    @patch('app.utils.TTSService')
    def test_concurrent_requests(self, mock_tts_service):
        """Testa múltiplas requisições concorrentes"""
        from app.utils import generate_narration
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.audio_path = "test.mp3"
        mock_result.duration = 2.0
        mock_result.provider_used = "gtts"
        
        mock_service_instance = MagicMock()
        mock_service_instance.generate_audio = AsyncMock(return_value=mock_result)
        mock_tts_service.return_value = mock_service_instance
        
        async def test_concurrent():
            tasks = []
            for i in range(5):
                task = generate_narration(
                    text=f"Teste concorrente {i}",
                    output_path=f"test_{i}.mp3"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
        
        results = asyncio.run(test_concurrent())
        
        # Verificar que todas as 5 requisições foram bem-sucedidas
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertTrue(result['success'])
    
    @patch('app.utils.TTS_AVAILABLE', True)
    def test_large_text_chunking(self):
        """Testa comportamento com texto grande"""
        from app.utils import generate_narration_sync
        
        # Texto no limite (2000 caracteres)
        limit_text = "A" * 2000
        
        with patch('app.utils.TTSService') as mock_tts_service:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.audio_path = "large_test.mp3"
            mock_result.duration = 15.0
            mock_result.provider_used = "gtts"
            
            mock_service_instance = MagicMock()
            mock_service_instance.generate_audio = AsyncMock(return_value=mock_result)
            mock_tts_service.return_value = mock_service_instance
            
            result = generate_narration_sync(
                text=limit_text,
                output_path="large_test.mp3"
            )
            
            self.assertTrue(result['success'])


def run_all_tests():
    """Executa todos os testes com relatório detalhado"""
    
    print("=" * 80)
    print("🧪 EXECUTANDO TESTES UNITÁRIOS TTS - GENERATE_NARRATION")
    print("=" * 80)
    
    # Configurar logging para testes
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Descobrir e executar todos os testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Executar com relatório detalhado
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Relatório final
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 80)
    print(f"✅ Testes executados: {result.testsRun}")
    print(f"❌ Falhas: {len(result.failures)}")
    print(f"🚫 Erros: {len(result.errors)}")
    print(f"⏭️ Ignorados: {len(result.skipped)}")
    
    if result.failures:
        print(f"\n❌ FALHAS:")
        for test, failure in result.failures:
            print(f"   - {test}: {failure}")
    
    if result.errors:
        print(f"\n🚫 ERROS:")
        for test, error in result.errors:
            print(f"   - {test}: {error}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🎯 Taxa de sucesso: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM!")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_all_tests() 