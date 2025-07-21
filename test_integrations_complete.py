#!/usr/bin/env python3
"""
Teste Completo de Todas as Integrações - TecnoCursos AI Enterprise
=================================================================

Script para testar todas as integrações implementadas:
- Integrações de IA (OpenAI, Anthropic)
- Serviços de avatar (D-ID, Synthesia)
- Pagamentos (Stripe, PayPal, PicPay)
- Comunicação (Email, SMS, WhatsApp)
- Cloud Storage (AWS, Google, Azure)
- Monitoramento (Sentry, DataDog)
- Sistema de mocks

Uso:
    python test_integrations_complete.py
    python test_integrations_complete.py --mock-mode
    python test_integrations_complete.py --service openai
"""

import asyncio
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List

# Importar serviços de integração
try:
    from app.services.mock_integration_service import mock_service, MockMode
    from app.services.openai_integration_service import openai_service, structure_content
    from app.services.d_id_integration_service import did_service, create_avatar_video
    from app.services.stripe_integration_service import stripe_service, create_payment
    from app.services.email_integration_service import email_service, send_email
    from app.config import settings, get_api_configs, get_feature_flags
    
    INTEGRATIONS_AVAILABLE = True
    print("✅ Todos os serviços de integração importados com sucesso")
    
except ImportError as e:
    INTEGRATIONS_AVAILABLE = False
    print(f"❌ Erro ao importar serviços: {e}")
    print("📝 Execute: pip install -r requirements.txt")
    sys.exit(1)

class IntegrationTester:
    """Classe principal para testes de integração"""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.results: Dict[str, Any] = {}
        self.start_time = datetime.now()
        
        # Configurar modo mock se solicitado
        if mock_mode:
            mock_service.set_mode(MockMode.REALISTIC)
            print("🎭 Modo mock ativado - todas as APIs usarão mocks")
        else:
            print("🌐 Modo real ativado - tentará usar APIs reais com fallback para mocks")
    
    async def test_all_integrations(self) -> Dict[str, Any]:
        """Testa todas as integrações implementadas"""
        
        print("\n" + "="*80)
        print("🚀 INICIANDO TESTE COMPLETO DE INTEGRAÇÕES")
        print("="*80)
        
        # Lista de testes a executar
        tests = [
            ("mock_service", self.test_mock_service),
            ("openai", self.test_openai_integration),
            ("d_id", self.test_d_id_integration),
            ("stripe", self.test_stripe_integration),
            ("email", self.test_email_integration),
            ("health_checks", self.test_health_checks),
            ("config", self.test_configuration)
        ]
        
        # Executar todos os testes
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Testando: {test_name.upper()}")
                result = await test_func()
                self.results[test_name] = result
                
                if result.get("success", False):
                    print(f"✅ {test_name}: PASSOU")
                else:
                    print(f"❌ {test_name}: FALHOU - {result.get('error', 'Erro desconhecido')}")
                    
            except Exception as e:
                print(f"💥 {test_name}: EXCEÇÃO - {str(e)}")
                self.results[test_name] = {
                    "success": False,
                    "error": str(e),
                    "exception": True
                }
        
        # Gerar relatório final
        return self.generate_final_report()
    
    async def test_mock_service(self) -> Dict[str, Any]:
        """Testa o sistema de mocks"""
        try:
            # Testar configuração de modo
            original_mode = mock_service.mode
            mock_service.set_mode(MockMode.SUCCESS)
            
            # Testar mock OpenAI
            mock_result = await mock_service.mock_openai_completion("Teste de mock")
            
            # Testar mock D-ID
            did_result = await mock_service.mock_d_id_create_video("Teste avatar")
            
            # Testar mock Stripe
            stripe_result = await mock_service.mock_stripe_create_payment_intent(2999)
            
            # Testar mock Email
            email_result = await mock_service.mock_sendgrid_send_email(
                "test@example.com", "Teste", "Conteúdo teste"
            )
            
            # Restaurar modo original
            mock_service.set_mode(original_mode)
            
            # Verificar estatísticas
            stats = mock_service.get_statistics()
            
            return {
                "success": True,
                "mocks_tested": ["openai", "d_id", "stripe", "email"],
                "total_calls": stats["total_calls"],
                "services_called": len(stats["services"]),
                "mode": mock_service.mode.value
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_openai_integration(self) -> Dict[str, Any]:
        """Testa integração OpenAI"""
        try:
            # Teste básico de estruturação
            test_content = """
            Python é uma linguagem de programação popular. 
            É usado para desenvolvimento web, ciência de dados e automação.
            Este é um conteúdo de teste para verificar a integração.
            """
            
            result = await structure_content(
                text=test_content,
                content_type="educational",
                target_audience="beginner"
            )
            
            # Verificar health check
            health = openai_service.health_check()
            
            # Estatísticas
            stats = openai_service.get_usage_statistics(1)
            
            return {
                "success": result.get("success", False),
                "service_enabled": health.get("enabled", False),
                "api_available": health.get("api_available", False),
                "total_requests": stats.get("total_requests", 0),
                "tokens_used": result.get("tokens_used", 0),
                "cost": result.get("cost", 0.0),
                "response_preview": str(result.get("data", {}))[:100] + "..."
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_d_id_integration(self) -> Dict[str, Any]:
        """Testa integração D-ID"""
        try:
            # Criar vídeo avatar teste
            result = await create_avatar_video(
                script="Olá! Este é um teste de integração do avatar D-ID.",
                presenter="amy"
            )
            
            # Verificar créditos (se disponível)
            try:
                credits = await did_service.get_credits_info()
            except:
                credits = {"mock": True}
            
            # Health check
            health = did_service.health_check()
            
            # Status do processamento
            processing_status = did_service.get_processing_status()
            
            return {
                "success": result.status.value not in ["error"],
                "video_id": result.id,
                "status": result.status.value,
                "service_enabled": health.get("enabled", False),
                "queue_size": processing_status.get("queue_size", 0),
                "credits": credits,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_stripe_integration(self) -> Dict[str, Any]:
        """Testa integração Stripe"""
        try:
            # Criar pagamento teste
            result = await create_payment(
                amount=100,  # R$ 1,00 para teste
                description="Teste de integração TecnoCursos AI",
                customer_email="teste@tecnocursos.ai"
            )
            
            # Health check
            health = stripe_service.health_check()
            
            # Estatísticas
            stats = stripe_service.get_payment_statistics(1)
            
            return {
                "success": result.status.value != "failed",
                "payment_id": result.id,
                "status": result.status.value,
                "amount": result.amount,
                "service_enabled": health.get("enabled", False),
                "total_payments": stats.get("total_payments", 0),
                "client_secret": result.client_secret[:20] + "..." if result.client_secret else None,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_email_integration(self) -> Dict[str, Any]:
        """Testa integração de email"""
        try:
            # Enviar email teste
            result = await send_email(
                to_email="teste@tecnocursos.ai",
                subject="Teste de Integração Email - TecnoCursos AI",
                html_content="<h1>Teste</h1><p>Este é um email de teste da integração.</p>",
                text_content="Teste - Este é um email de teste da integração."
            )
            
            # Health check
            health = email_service.health_check()
            
            # Estatísticas
            stats = email_service.get_email_statistics()
            
            return {
                "success": result.status.value in ["sent", "queued"],
                "email_id": result.id,
                "status": result.status.value,
                "provider": result.provider.value,
                "default_provider": health.get("default_provider"),
                "emails_sent": health.get("emails_sent", 0),
                "providers_available": health.get("providers", {}),
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_health_checks(self) -> Dict[str, Any]:
        """Testa health checks de todos os serviços"""
        try:
            health_results = {}
            
            # OpenAI
            health_results["openai"] = openai_service.health_check()
            
            # D-ID
            health_results["d_id"] = did_service.health_check()
            
            # Stripe
            health_results["stripe"] = stripe_service.health_check()
            
            # Email
            health_results["email"] = email_service.health_check()
            
            # Mock Service
            health_results["mock"] = mock_service.health_check()
            
            # Calcular status geral
            services_healthy = sum(
                1 for health in health_results.values() 
                if health.get("status") in ["healthy", "mock_mode"]
            )
            total_services = len(health_results)
            health_percentage = (services_healthy / total_services) * 100
            
            return {
                "success": health_percentage >= 80,  # 80% dos serviços healthy
                "health_percentage": health_percentage,
                "services_healthy": services_healthy,
                "total_services": total_services,
                "detailed_health": health_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_configuration(self) -> Dict[str, Any]:
        """Testa configurações das integrações"""
        try:
            # Configurações de API
            api_configs = get_api_configs()
            
            # Feature flags
            feature_flags = get_feature_flags()
            
            # Contar configurações ativas
            enabled_apis = sum(
                1 for config in api_configs.values() 
                if config.get("enabled", False)
            )
            
            total_apis = len(api_configs)
            config_percentage = (enabled_apis / total_apis) * 100 if total_apis > 0 else 0
            
            return {
                "success": True,
                "config_percentage": config_percentage,
                "enabled_apis": enabled_apis,
                "total_apis": total_apis,
                "environment": settings.environment,
                "mock_mode": settings.mock_external_apis,
                "feature_flags_active": sum(feature_flags.values()),
                "api_configs": {
                    name: {"enabled": config.get("enabled", False)}
                    for name, config in api_configs.items()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Gera relatório final dos testes"""
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Calcular estatísticas
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get("success", False))
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Status geral
        overall_status = "SUCESSO" if success_rate >= 80 else "FALHA"
        
        report = {
            "test_summary": {
                "overall_status": overall_status,
                "success_rate": success_rate,
                "tests_passed": passed_tests,
                "tests_total": total_tests,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            },
            "test_results": self.results,
            "environment": {
                "mock_mode": self.mock_mode,
                "integrations_available": INTEGRATIONS_AVAILABLE,
                "app_environment": settings.environment
            }
        }
        
        # Imprimir relatório
        self.print_final_report(report)
        
        return report
    
    def print_final_report(self, report: Dict[str, Any]):
        """Imprime relatório final formatado"""
        
        print("\n" + "="*80)
        print("📊 RELATÓRIO FINAL DE TESTES DE INTEGRAÇÃO")
        print("="*80)
        
        summary = report["test_summary"]
        
        # Status geral
        status_emoji = "✅" if summary["overall_status"] == "SUCESSO" else "❌"
        print(f"\n{status_emoji} STATUS GERAL: {summary['overall_status']}")
        print(f"📈 Taxa de Sucesso: {summary['success_rate']:.1f}%")
        print(f"🧪 Testes: {summary['tests_passed']}/{summary['tests_total']}")
        print(f"⏱️ Duração: {summary['duration_seconds']:.1f}s")
        print(f"🕐 Timestamp: {summary['timestamp']}")
        
        # Resultados por serviço
        print(f"\n📋 RESULTADOS DETALHADOS:")
        for service, result in report["test_results"].items():
            status = "✅ PASSOU" if result.get("success") else "❌ FALHOU"
            print(f"  {service.upper()}: {status}")
            
            if not result.get("success") and result.get("error"):
                print(f"    Error: {result['error']}")
        
        # Ambiente
        env = report["environment"]
        print(f"\n🔧 AMBIENTE:")
        print(f"  Modo Mock: {'Ativo' if env['mock_mode'] else 'Inativo'}")
        print(f"  Integrações Disponíveis: {'Sim' if env['integrations_available'] else 'Não'}")
        print(f"  Environment: {env['app_environment']}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        if summary["success_rate"] >= 90:
            print("  🎉 Excelente! Todas as integrações estão funcionando perfeitamente.")
        elif summary["success_rate"] >= 80:
            print("  👍 Bom! A maioria das integrações está funcionando.")
            print("  🔧 Verifique os serviços que falharam nos logs acima.")
        else:
            print("  ⚠️ Atenção! Muitas integrações estão falhando.")
            print("  🔧 Verifique as configurações de API keys e conectividade.")
            print("  📖 Consulte a documentação de configuração.")
        
        print("\n" + "="*80)

async def test_specific_service(service_name: str, tester: IntegrationTester):
    """Testa um serviço específico"""
    
    service_map = {
        "mock": tester.test_mock_service,
        "openai": tester.test_openai_integration,
        "d_id": tester.test_d_id_integration,
        "stripe": tester.test_stripe_integration,
        "email": tester.test_email_integration,
        "health": tester.test_health_checks,
        "config": tester.test_configuration
    }
    
    if service_name not in service_map:
        print(f"❌ Serviço '{service_name}' não encontrado.")
        print(f"📋 Serviços disponíveis: {', '.join(service_map.keys())}")
        return
    
    print(f"🧪 Testando serviço específico: {service_name.upper()}")
    
    try:
        result = await service_map[service_name]()
        
        if result.get("success"):
            print(f"✅ {service_name}: SUCESSO")
        else:
            print(f"❌ {service_name}: FALHA - {result.get('error', 'Erro desconhecido')}")
        
        print(f"📊 Detalhes: {result}")
        
    except Exception as e:
        print(f"💥 {service_name}: EXCEÇÃO - {str(e)}")

def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(
        description="Teste completo de integrações TecnoCursos AI"
    )
    parser.add_argument(
        "--mock-mode", 
        action="store_true", 
        help="Força uso de mocks para todos os serviços"
    )
    parser.add_argument(
        "--service", 
        type=str, 
        help="Testa apenas um serviço específico (mock, openai, d_id, stripe, email, health, config)"
    )
    
    args = parser.parse_args()
    
    # Verificar disponibilidade
    if not INTEGRATIONS_AVAILABLE:
        print("❌ Serviços de integração não disponíveis")
        sys.exit(1)
    
    # Criar tester
    tester = IntegrationTester(mock_mode=args.mock_mode)
    
    # Executar testes
    if args.service:
        asyncio.run(test_specific_service(args.service, tester))
    else:
        asyncio.run(tester.test_all_integrations())

if __name__ == "__main__":
    main() 