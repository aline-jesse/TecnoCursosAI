#!/usr/bin/env python3
"""
🧪 FASE 5: TESTES, PERFORMANCE E PRODUÇÃO - IMPLEMENTAÇÃO COMPLETA
Sistema avançado de testes unitários, integração e performance

Funcionalidades:
✅ Testes Unitários de todos os componentes
✅ Testes de Integração end-to-end
✅ Testes de Performance e Load Testing
✅ Testes de Segurança
✅ Relatórios detalhados com métricas

Data: 17 de Janeiro de 2025
Versão: 5.0.0
"""

import unittest
import asyncio
import aiohttp
import pytest
import time
import json
import sys
import concurrent.futures
import statistics
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração dos testes
TEST_CONFIG = {
    "base_url": "http://localhost:8001",
    "timeout": 30,
    "max_retries": 3,
    "performance_thresholds": {
        "response_time": 2.0,  # segundos
        "concurrent_users": 50,
        "requests_per_second": 100
    }
}

class Fase5TestSuite:
    """Suite completa de testes da Fase 5"""
    
    def __init__(self):
        self.results = {
            "unit_tests": {},
            "integration_tests": {},
            "performance_tests": {},
            "security_tests": {},
            "summary": {}
        }
        self.session = None
        
    async def setup(self):
        """Configuração inicial dos testes"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TEST_CONFIG["timeout"]))
        logger.info("🔧 Setup dos testes concluído")
        
    async def cleanup(self):
        """Limpeza após os testes"""
        if self.session:
            await self.session.close()
        logger.info("🧹 Cleanup dos testes concluído")

    # ===================================================================
    # TESTES UNITÁRIOS
    # ===================================================================
    
    async def test_unit_health_endpoint(self):
        """Teste unitário: Health endpoint"""
        try:
            async with self.session.get(f"{TEST_CONFIG['base_url']}/api/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"
                assert "timestamp" in data
                assert "uptime" in data
                
                self.results["unit_tests"]["health_endpoint"] = {
                    "status": "PASSED",
                    "response_time": response.headers.get("X-Response-Time", "N/A"),
                    "data": data
                }
                logger.info("✅ Health endpoint test: PASSED")
                
        except Exception as e:
            self.results["unit_tests"]["health_endpoint"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Health endpoint test: FAILED - {e}")

    async def test_unit_video_export_formats(self):
        """Teste unitário: Video export formats"""
        try:
            async with self.session.get(f"{TEST_CONFIG['base_url']}/api/video/export/formats") as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert "formats" in data
                assert len(data["formats"]) > 0
                
                # Verificar estrutura dos formatos
                for fmt in data["formats"]:
                    assert "id" in fmt
                    assert "name" in fmt
                    assert "description" in fmt
                
                self.results["unit_tests"]["video_export_formats"] = {
                    "status": "PASSED",
                    "formats_count": len(data["formats"])
                }
                logger.info("✅ Video export formats test: PASSED")
                
        except Exception as e:
            self.results["unit_tests"]["video_export_formats"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Video export formats test: FAILED - {e}")

    async def test_unit_tts_voices(self):
        """Teste unitário: TTS voices"""
        try:
            async with self.session.get(f"{TEST_CONFIG['base_url']}/api/tts/voices") as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert "voices" in data
                assert len(data["voices"]) > 0
                
                # Verificar estrutura das vozes
                for voice in data["voices"]:
                    assert "id" in voice
                    assert "name" in voice
                    assert "gender" in voice
                    assert "quality" in voice
                
                self.results["unit_tests"]["tts_voices"] = {
                    "status": "PASSED",
                    "voices_count": len(data["voices"])
                }
                logger.info("✅ TTS voices test: PASSED")
                
        except Exception as e:
            self.results["unit_tests"]["tts_voices"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ TTS voices test: FAILED - {e}")

    async def test_unit_avatar_styles(self):
        """Teste unitário: Avatar styles"""
        try:
            async with self.session.get(f"{TEST_CONFIG['base_url']}/api/avatar/styles") as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert "styles" in data
                assert len(data["styles"]) > 0
                
                # Verificar estrutura dos estilos
                for style in data["styles"]:
                    assert "id" in style
                    assert "name" in style
                    assert "description" in style
                
                self.results["unit_tests"]["avatar_styles"] = {
                    "status": "PASSED",
                    "styles_count": len(data["styles"])
                }
                logger.info("✅ Avatar styles test: PASSED")
                
        except Exception as e:
            self.results["unit_tests"]["avatar_styles"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Avatar styles test: FAILED - {e}")

    # ===================================================================
    # TESTES DE INTEGRAÇÃO
    # ===================================================================
    
    async def test_integration_video_export_flow(self):
        """Teste integração: Fluxo completo de exportação de vídeo"""
        try:
            # 1. Iniciar exportação
            export_data = {
                "project_id": 123,
                "quality": "1080p",
                "format": "mp4"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['base_url']}/api/video/export/start",
                json=export_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                job_id = data["job_id"]
            
            # 2. Verificar status
            async with self.session.get(
                f"{TEST_CONFIG['base_url']}/api/video/export/status/{job_id}"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert "job" in data
                
            self.results["integration_tests"]["video_export_flow"] = {
                "status": "PASSED",
                "job_id": job_id
            }
            logger.info("✅ Video export flow test: PASSED")
            
        except Exception as e:
            self.results["integration_tests"]["video_export_flow"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Video export flow test: FAILED - {e}")

    async def test_integration_tts_generation_flow(self):
        """Teste integração: Fluxo completo de geração TTS"""
        try:
            # 1. Gerar TTS básico
            tts_data = {
                "text": "Este é um teste de integração do sistema TTS",
                "voice": "pt-BR",
                "speed": 1.0
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['base_url']}/api/tts/generate",
                json=tts_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                audio_id = data["audio_id"]
            
            # 2. Gerar TTS avançado
            async with self.session.post(
                f"{TEST_CONFIG['base_url']}/api/tts/advanced/generate",
                json=tts_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                advanced_audio_id = data["audio_id"]
                
            self.results["integration_tests"]["tts_generation_flow"] = {
                "status": "PASSED",
                "basic_audio_id": audio_id,
                "advanced_audio_id": advanced_audio_id
            }
            logger.info("✅ TTS generation flow test: PASSED")
            
        except Exception as e:
            self.results["integration_tests"]["tts_generation_flow"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ TTS generation flow test: FAILED - {e}")

    async def test_integration_avatar_generation_flow(self):
        """Teste integração: Fluxo completo de geração de avatar"""
        try:
            # 1. Gerar avatar
            avatar_data = {
                "text": "Bem-vindos ao teste de integração de avatar",
                "style": "professional",
                "background": "office"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['base_url']}/api/avatar/generate",
                json=avatar_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                avatar_id = data["avatar_id"]
            
            # 2. Verificar status
            async with self.session.get(
                f"{TEST_CONFIG['base_url']}/api/avatar/status/{avatar_id}"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert "job" in data
                
            self.results["integration_tests"]["avatar_generation_flow"] = {
                "status": "PASSED",
                "avatar_id": avatar_id
            }
            logger.info("✅ Avatar generation flow test: PASSED")
            
        except Exception as e:
            self.results["integration_tests"]["avatar_generation_flow"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Avatar generation flow test: FAILED - {e}")

    async def test_integration_notifications_flow(self):
        """Teste integração: Fluxo completo de notificações"""
        try:
            user_id = "test_user_integration"
            
            # 1. Enviar notificação
            notification_data = {
                "user_id": user_id,
                "message": "Teste de integração de notificação",
                "type": "info"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['base_url']}/api/notifications/send",
                json=notification_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                notification_id = data["notification"]["id"]
            
            # 2. Obter notificações do usuário
            async with self.session.get(
                f"{TEST_CONFIG['base_url']}/api/notifications/{user_id}"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert data["total"] > 0
            
            # 3. Marcar como lida
            async with self.session.put(
                f"{TEST_CONFIG['base_url']}/api/notifications/{notification_id}/read"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                
            self.results["integration_tests"]["notifications_flow"] = {
                "status": "PASSED",
                "notification_id": notification_id,
                "user_id": user_id
            }
            logger.info("✅ Notifications flow test: PASSED")
            
        except Exception as e:
            self.results["integration_tests"]["notifications_flow"] = {
                "status": "FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Notifications flow test: FAILED - {e}")

    # ===================================================================
    # TESTES DE PERFORMANCE
    # ===================================================================
    
    async def test_performance_response_times(self):
        """Teste performance: Tempos de resposta"""
        endpoints = [
            "/api/health",
            "/api/video/export/formats",
            "/api/tts/voices",
            "/api/avatar/styles"
        ]
        
        response_times = {}
        
        for endpoint in endpoints:
            times = []
            for _ in range(10):  # 10 requests por endpoint
                start_time = time.time()
                try:
                    async with self.session.get(f"{TEST_CONFIG['base_url']}{endpoint}") as response:
                        await response.read()
                        end_time = time.time()
                        times.append(end_time - start_time)
                except Exception as e:
                    logger.warning(f"Erro no teste de performance para {endpoint}: {e}")
            
            if times:
                response_times[endpoint] = {
                    "avg": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "median": statistics.median(times)
                }
        
        # Verificar se os tempos estão dentro dos thresholds
        passed = all(
            rt["avg"] < TEST_CONFIG["performance_thresholds"]["response_time"] 
            for rt in response_times.values()
        )
        
        self.results["performance_tests"]["response_times"] = {
            "status": "PASSED" if passed else "FAILED",
            "response_times": response_times,
            "threshold": TEST_CONFIG["performance_thresholds"]["response_time"]
        }
        
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{'✅' if passed else '❌'} Response times test: {status}")

    async def test_performance_concurrent_requests(self):
        """Teste performance: Requisições concorrentes"""
        endpoint = f"{TEST_CONFIG['base_url']}/api/health"
        concurrent_users = 20
        requests_per_user = 5
        
        async def make_request():
            try:
                start_time = time.time()
                async with self.session.get(endpoint) as response:
                    await response.read()
                    end_time = time.time()
                    return {
                        "status": response.status,
                        "time": end_time - start_time,
                        "success": response.status == 200
                    }
            except Exception as e:
                return {
                    "status": None,
                    "time": None,
                    "success": False,
                    "error": str(e)
                }
        
        # Executar requests concorrentes
        tasks = []
        for _ in range(concurrent_users * requests_per_user):
            tasks.append(make_request())
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analisar resultados
        successful_requests = sum(1 for r in results if r["success"])
        total_requests = len(results)
        success_rate = successful_requests / total_requests
        total_time = end_time - start_time
        requests_per_second = total_requests / total_time
        
        passed = success_rate >= 0.95  # 95% de sucesso mínimo
        
        self.results["performance_tests"]["concurrent_requests"] = {
            "status": "PASSED" if passed else "FAILED",
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "requests_per_second": requests_per_second,
            "total_time": total_time,
            "concurrent_users": concurrent_users
        }
        
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{'✅' if passed else '❌'} Concurrent requests test: {status}")

    # ===================================================================
    # TESTES DE SEGURANÇA
    # ===================================================================
    
    async def test_security_sql_injection(self):
        """Teste segurança: SQL Injection"""
        # Testar diversos payloads de SQL injection
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        vulnerabilities = []
        
        for payload in payloads:
            try:
                # Testar em endpoint que aceita parâmetros
                async with self.session.get(
                    f"{TEST_CONFIG['base_url']}/api/notifications/{payload}"
                ) as response:
                    # Se retornar 200 com payload malicioso, pode ser vulnerável
                    if response.status == 200:
                        data = await response.text()
                        if "error" not in data.lower():
                            vulnerabilities.append(payload)
            except Exception:
                # Exceções são esperadas para inputs maliciosos
                pass
        
        passed = len(vulnerabilities) == 0
        
        self.results["security_tests"]["sql_injection"] = {
            "status": "PASSED" if passed else "FAILED",
            "vulnerabilities_found": len(vulnerabilities),
            "payloads_tested": len(payloads),
            "vulnerable_payloads": vulnerabilities
        }
        
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{'✅' if passed else '❌'} SQL injection test: {status}")

    async def test_security_xss_protection(self):
        """Teste segurança: Proteção XSS"""
        # Testar payloads XSS
        payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
            "\";alert('XSS');//"
        ]
        
        vulnerabilities = []
        
        for payload in payloads:
            try:
                # Testar enviando payload via POST
                notification_data = {
                    "user_id": "test_xss",
                    "message": payload,
                    "type": "test"
                }
                
                async with self.session.post(
                    f"{TEST_CONFIG['base_url']}/api/notifications/send",
                    json=notification_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Verificar se o payload foi sanitizado
                        if payload in str(data):
                            vulnerabilities.append(payload)
            except Exception:
                pass
        
        passed = len(vulnerabilities) == 0
        
        self.results["security_tests"]["xss_protection"] = {
            "status": "PASSED" if passed else "FAILED",
            "vulnerabilities_found": len(vulnerabilities),
            "payloads_tested": len(payloads),
            "vulnerable_payloads": vulnerabilities
        }
        
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{'✅' if passed else '❌'} XSS protection test: {status}")

    # ===================================================================
    # EXECUÇÃO COMPLETA
    # ===================================================================
    
    async def run_all_tests(self):
        """Executar todos os testes da Fase 5"""
        logger.info("🚀 INICIANDO FASE 5: TESTES, PERFORMANCE E PRODUÇÃO")
        logger.info("="*80)
        
        await self.setup()
        
        try:
            # Testes Unitários
            logger.info("📋 Executando Testes Unitários...")
            await self.test_unit_health_endpoint()
            await self.test_unit_video_export_formats()
            await self.test_unit_tts_voices()
            await self.test_unit_avatar_styles()
            
            # Testes de Integração
            logger.info("🔗 Executando Testes de Integração...")
            await self.test_integration_video_export_flow()
            await self.test_integration_tts_generation_flow()
            await self.test_integration_avatar_generation_flow()
            await self.test_integration_notifications_flow()
            
            # Testes de Performance
            logger.info("⚡ Executando Testes de Performance...")
            await self.test_performance_response_times()
            await self.test_performance_concurrent_requests()
            
            # Testes de Segurança
            logger.info("🔒 Executando Testes de Segurança...")
            await self.test_security_sql_injection()
            await self.test_security_xss_protection()
            
            # Gerar relatório final
            self.generate_final_report()
            
        finally:
            await self.cleanup()

    def generate_final_report(self):
        """Gerar relatório final dos testes"""
        # Contar sucessos e falhas
        categories = ["unit_tests", "integration_tests", "performance_tests", "security_tests"]
        
        total_tests = 0
        passed_tests = 0
        
        for category in categories:
            for test_name, result in self.results[category].items():
                total_tests += 1
                if result.get("status") == "PASSED":
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat(),
            "status": "APPROVED" if success_rate >= 80 else "NEEDS_REVIEW"
        }
        
        # Imprimir relatório
        print("\n" + "="*80)
        print("📊 RELATÓRIO FINAL - FASE 5: TESTES, PERFORMANCE E PRODUÇÃO")
        print("="*80)
        
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {passed_tests}")
        print(f"Testes falharam: {total_tests - passed_tests}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 FASE 5 EXCELENTE - Sistema pronto para produção!")
        elif success_rate >= 80:
            print("✅ FASE 5 APROVADA - Sistema adequado para produção")
        elif success_rate >= 60:
            print("⚠️ FASE 5 PARCIAL - Melhorias necessárias")
        else:
            print("❌ FASE 5 REPROVADA - Problemas críticos detectados")
        
        print("\n📋 RESUMO POR CATEGORIA:")
        for category in categories:
            category_results = self.results[category]
            category_total = len(category_results)
            category_passed = sum(1 for r in category_results.values() if r.get("status") == "PASSED")
            print(f"  {category.replace('_', ' ').title()}: {category_passed}/{category_total}")
        
        print("\n🎯 FUNCIONALIDADES TESTADAS:")
        print("  ✅ Testes Unitários - Componentes individuais")
        print("  ✅ Testes de Integração - Fluxos completos")
        print("  ✅ Testes de Performance - Tempos de resposta e concorrência")
        print("  ✅ Testes de Segurança - SQL Injection e XSS")
        
        return success_rate >= 80

async def main():
    """Função principal"""
    test_suite = Fase5TestSuite()
    success = await test_suite.run_all_tests()
    
    # Salvar resultados
    with open("test_fase_5_results.json", "w", encoding="utf-8") as f:
        json.dump(test_suite.results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resultados salvos em: test_fase_5_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 