#!/usr/bin/env python3
"""
Teste Completo do Sistema Enterprise TecnoCursos AI
==================================================

Script de validação completa de todas as implementações enterprise:
- AI Guardrails Service
- Compliance Service  
- Security Hardening Service
- Intelligent Monitoring Service
- API Versioning Service
- Load Balancing Service
- Auto Documentation Service

Autor: TecnoCursos AI Team
Data: 2024-12-17
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todos os serviços podem ser importados"""
    
    print("🔍 TESTANDO IMPORTAÇÕES DOS SERVIÇOS ENTERPRISE...")
    
    services_status = {}
    
    # AI Guardrails Service
    try:
        from app.services.ai_guardrails_service import ai_guardrails_service, DecisionCategory
        services_status["ai_guardrails"] = "✅ OK"
        print("   ✅ AI Guardrails Service - IMPORTADO")
    except ImportError as e:
        services_status["ai_guardrails"] = f"❌ ERRO: {e}"
        print(f"   ❌ AI Guardrails Service - ERRO: {e}")
    
    # Compliance Service
    try:
        from app.services.ai_compliance_service import ai_compliance_service, ComplianceStandard
        services_status["compliance"] = "✅ OK"
        print("   ✅ Compliance Service - IMPORTADO")
    except ImportError as e:
        services_status["compliance"] = f"❌ ERRO: {e}"
        print(f"   ❌ Compliance Service - ERRO: {e}")
    
    # Security Service
    try:
        from app.services.security_hardening_service import security_hardening_service, ThreatLevel
        services_status["security"] = "✅ OK"
        print("   ✅ Security Hardening Service - IMPORTADO")
    except ImportError as e:
        services_status["security"] = f"❌ ERRO: {e}"
        print(f"   ❌ Security Hardening Service - ERRO: {e}")
    
    # Monitoring Service
    try:
        from app.services.intelligent_monitoring_service import intelligent_monitoring_service, MetricType
        services_status["monitoring"] = "✅ OK"
        print("   ✅ Intelligent Monitoring Service - IMPORTADO")
    except ImportError as e:
        services_status["monitoring"] = f"❌ ERRO: {e}"
        print(f"   ❌ Intelligent Monitoring Service - ERRO: {e}")
    
    # Versioning Service
    try:
        from app.services.api_versioning_service import api_versioning_service, VersionStatus
        services_status["versioning"] = "✅ OK"
        print("   ✅ API Versioning Service - IMPORTADO")
    except ImportError as e:
        services_status["versioning"] = f"❌ ERRO: {e}"
        print(f"   ❌ API Versioning Service - ERRO: {e}")
    
    # Load Balancing Service
    try:
        from app.services.load_balancing_service import load_balancing_service, LoadBalancingAlgorithm
        services_status["load_balancing"] = "✅ OK"
        print("   ✅ Load Balancing Service - IMPORTADO")
    except ImportError as e:
        services_status["load_balancing"] = f"❌ ERRO: {e}"
        print(f"   ❌ Load Balancing Service - ERRO: {e}")
    
    # Documentation Service
    try:
        from app.services.auto_documentation_service import auto_documentation_service, CodeLanguage
        services_status["documentation"] = "✅ OK"
        print("   ✅ Auto Documentation Service - IMPORTADO")
    except ImportError as e:
        services_status["documentation"] = f"❌ ERRO: {e}"
        print(f"   ❌ Auto Documentation Service - ERRO: {e}")
    
    # Enterprise Router
    try:
        from app.routers.enterprise_router import enterprise_router
        services_status["enterprise_router"] = "✅ OK"
        print("   ✅ Enterprise Router - IMPORTADO")
    except ImportError as e:
        services_status["enterprise_router"] = f"❌ ERRO: {e}"
        print(f"   ❌ Enterprise Router - ERRO: {e}")
    
    return services_status

async def test_ai_guardrails():
    """Testa o AI Guardrails Service"""
    
    print("\n🛡️ TESTANDO AI GUARDRAILS SERVICE...")
    
    try:
        from app.services.ai_guardrails_service import ai_guardrails_service, DecisionCategory
        
        # Teste de avaliação de decisão
        decision = await ai_guardrails_service.evaluate_decision(
            action="test_action",
            category=DecisionCategory.CONTENT_GENERATION,
            context={"test": True},
            confidence=0.8
        )
        
        print(f"   ✅ Decisão avaliada: {decision.id}")
        print(f"   ✅ Nível de risco: {decision.risk_level.value}")
        print(f"   ✅ Explicação: {decision.explanation[:50]}...")
        
        # Teste de métricas
        metrics = ai_guardrails_service.get_metrics()
        print(f"   ✅ Métricas obtidas: {len(metrics)} itens")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO no AI Guardrails: {e}")
        return False

async def test_compliance():
    """Testa o Compliance Service"""
    
    print("\n📋 TESTANDO COMPLIANCE SERVICE...")
    
    try:
        from app.services.ai_compliance_service import ai_compliance_service, ComplianceStandard
        
        # Teste de detecção de bias
        detections = await ai_compliance_service.detect_bias(
            "Este é um texto de teste para detectar possível bias de gênero."
        )
        
        print(f"   ✅ Detecções de bias: {len(detections)}")
        
        # Teste de check de compliance
        check = await ai_compliance_service.check_compliance(
            ComplianceStandard.GDPR,
            {"user_consent": True, "contains_personal_data": False}
        )
        
        print(f"   ✅ Check GDPR: {check.status}")
        print(f"   ✅ Findings: {len(check.findings)}")
        
        # Teste de métricas
        metrics = ai_compliance_service.get_compliance_metrics()
        print(f"   ✅ Métricas de compliance: {len(metrics)} itens")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO no Compliance: {e}")
        return False

async def test_security():
    """Testa o Security Hardening Service"""
    
    print("\n🔒 TESTANDO SECURITY HARDENING SERVICE...")
    
    try:
        from app.services.security_hardening_service import security_hardening_service
        
        # Teste de análise de request
        request_data = {
            "client_ip": "192.168.1.100",
            "user_agent": "TestAgent/1.0",
            "method": "GET",
            "url": "/test",
            "headers": {"Content-Type": "application/json"},
            "body": ""
        }
        
        allowed, incidents = await security_hardening_service.analyze_request_security(request_data)
        
        print(f"   ✅ Request analisado - Permitido: {allowed}")
        print(f"   ✅ Incidentes detectados: {len(incidents)}")
        
        # Teste de criptografia
        test_data = "Dados sensíveis para criptografar"
        encrypted = security_hardening_service.encrypt_data(test_data)
        decrypted = security_hardening_service.decrypt_data(encrypted)
        
        print(f"   ✅ Criptografia funcionando: {decrypted == test_data}")
        
        # Teste de métricas
        metrics = security_hardening_service.get_security_metrics()
        print(f"   ✅ Métricas de segurança: {len(metrics)} itens")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO no Security: {e}")
        return False

async def test_monitoring():
    """Testa o Intelligent Monitoring Service"""
    
    print("\n📈 TESTANDO INTELLIGENT MONITORING SERVICE...")
    
    try:
        from app.services.intelligent_monitoring_service import intelligent_monitoring_service, MetricType
        
        # Teste de adição de métrica customizada
        await intelligent_monitoring_service.add_custom_metric(
            MetricType.CPU_USAGE,
            75.5,
            {"source": "test"},
            "test_application"
        )
        
        print("   ✅ Métrica customizada adicionada")
        
        # Teste de saúde do sistema
        health = intelligent_monitoring_service.get_system_health()
        print(f"   ✅ Status de saúde: {health.value}")
        
        # Teste de métricas
        stats = intelligent_monitoring_service.get_monitoring_stats()
        print(f"   ✅ Stats de monitoramento: {len(stats)} itens")
        
        # Teste de dashboard
        dashboard = intelligent_monitoring_service.generate_dashboard_data()
        print(f"   ✅ Dashboard gerado com timestamp: {dashboard['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO no Monitoring: {e}")
        return False

async def test_versioning():
    """Testa o API Versioning Service"""
    
    print("\n🔄 TESTANDO API VERSIONING SERVICE...")
    
    try:
        from app.services.api_versioning_service import api_versioning_service
        
        # Teste de negociação de versão
        headers = {"API-Version": "1.0.0"}
        query_params = {}
        
        version = await api_versioning_service.negotiate_version(headers, query_params)
        print(f"   ✅ Versão negociada: {version}")
        
        # Teste de informações de versão
        version_info = api_versioning_service.get_version_info("1.0.0")
        print(f"   ✅ Info da versão obtida: {version_info['version'] if version_info else 'N/A'}")
        
        # Teste de stats
        stats = api_versioning_service.get_versioning_stats()
        print(f"   ✅ Stats de versionamento: {stats['total_versions']} versões")
        
        # Teste de compatibilidade
        compat = await api_versioning_service.get_compatibility_info("1.0.0", "2.0.0")
        print(f"   ✅ Compatibilidade 1.0.0 -> 2.0.0: {compat['compatibility_level']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO no Versioning: {e}")
        return False

async def test_load_balancing():
    """Testa o Load Balancing Service"""
    
    print("\n⚖️ TESTANDO LOAD BALANCING SERVICE...")
    
    try:
        from app.services.load_balancing_service import load_balancing_service, LoadBalancingAlgorithm
        
        # Registrar servidor de teste
        server = await load_balancing_service.register_server(
            "test_server_1",
            "localhost",
            8000,
            weight=1,
            group="test"
        )
        
        print(f"   ✅ Servidor registrado: {server.id}")
        
        # Teste de seleção de servidor
        selected = await load_balancing_service.select_server(
            client_ip="192.168.1.100",
            group="test"
        )
        
        if selected:
            print(f"   ✅ Servidor selecionado: {selected.id}")
        else:
            print("   ⚠️ Nenhum servidor disponível")
        
        # Teste de métricas
        metrics = load_balancing_service.get_load_balancing_metrics()
        print(f"   ✅ Métricas de load balancing: {metrics['total_servers']} servidores")
        
        # Teste de algorithm change
        load_balancing_service.set_load_balancing_algorithm(LoadBalancingAlgorithm.ROUND_ROBIN)
        print("   ✅ Algoritmo alterado para Round Robin")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO no Load Balancing: {e}")
        return False

async def test_documentation():
    """Testa o Auto Documentation Service"""
    
    print("\n📚 TESTANDO AUTO DOCUMENTATION SERVICE...")
    
    try:
        from app.services.auto_documentation_service import auto_documentation_service, CodeLanguage
        
        # Teste de geração OpenAPI
        openapi_spec = await auto_documentation_service.generate_openapi_spec("2.0.0")
        print(f"   ✅ OpenAPI spec gerado - Versão: {openapi_spec['info']['version']}")
        print(f"   ✅ Paths documentados: {len(openapi_spec['paths'])}")
        
        # Teste de geração de SDK
        python_sdk = await auto_documentation_service.generate_sdk_code(CodeLanguage.PYTHON)
        print(f"   ✅ SDK Python gerado: {len(python_sdk)} caracteres")
        
        # Teste de stats
        stats = auto_documentation_service.get_documentation_stats()
        print(f"   ✅ Stats de documentação: {stats['total_endpoints']} endpoints")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO na Documentation: {e}")
        return False

def test_file_structure():
    """Testa se todos os arquivos foram criados"""
    
    print("\n📁 TESTANDO ESTRUTURA DE ARQUIVOS...")
    
    required_files = [
        "app/services/ai_guardrails_service.py",
        "app/services/ai_compliance_service.py", 
        "app/services/security_hardening_service.py",
        "app/services/intelligent_monitoring_service.py",
        "app/services/api_versioning_service.py",
        "app/services/load_balancing_service.py",
        "app/services/auto_documentation_service.py",
        "app/routers/enterprise_router.py",
        "SISTEMA_ENTERPRISE_FINALIZADO.md"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            existing_files.append(f"{file_path} ({size:,} bytes)")
            print(f"   ✅ {file_path} - {size:,} bytes")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} - NÃO ENCONTRADO")
    
    return len(missing_files) == 0, existing_files, missing_files

async def main():
    """Função principal de teste"""
    
    print("🏢 TESTE COMPLETO DO SISTEMA ENTERPRISE TECNOCURSOS AI")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Resultados dos testes
    test_results = {}
    
    # 1. Teste de importações
    print("\n" + "="*60)
    services_status = test_imports()
    successful_imports = len([s for s in services_status.values() if "✅" in s])
    total_imports = len(services_status)
    test_results["imports"] = successful_imports == total_imports
    
    # 2. Teste de estrutura de arquivos
    print("\n" + "="*60)
    files_ok, existing_files, missing_files = test_file_structure()
    test_results["files"] = files_ok
    
    # 3. Testes funcionais (apenas se imports estão OK)
    if test_results["imports"]:
        print("\n" + "="*60)
        
        # Teste individual de cada serviço
        test_results["ai_guardrails"] = await test_ai_guardrails()
        test_results["compliance"] = await test_compliance()
        test_results["security"] = await test_security()
        test_results["monitoring"] = await test_monitoring()
        test_results["versioning"] = await test_versioning()
        test_results["load_balancing"] = await test_load_balancing()
        test_results["documentation"] = await test_documentation()
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed_tests = len([r for r in test_results.values() if r])
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    for test_name, result in test_results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name.upper()}: {status}")
    
    print("\n" + "="*60)
    print(f"🎯 RESULTADO FINAL:")
    print(f"   Testes Passados: {passed_tests}/{total_tests}")
    print(f"   Taxa de Sucesso: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"   Status: ✅ SISTEMA ENTERPRISE FUNCIONANDO")
        print(f"   Importações: {successful_imports}/{total_imports} serviços")
        print(f"   Arquivos: {len(existing_files)} criados")
    elif success_rate >= 70:
        print(f"   Status: ⚠️ SISTEMA PARCIALMENTE FUNCIONANDO")
    else:
        print(f"   Status: ❌ SISTEMA COM PROBLEMAS")
    
    print("="*60)
    
    # Informações adicionais
    if test_results["files"]:
        print(f"\n📁 ARQUIVOS CRIADOS ({len(existing_files)}):")
        for file_info in existing_files:
            print(f"   📄 {file_info}")
    
    if missing_files:
        print(f"\n❌ ARQUIVOS FALTANDO ({len(missing_files)}):")
        for file_path in missing_files:
            print(f"   📄 {file_path}")
    
    print(f"\n🚀 ENDPOINTS ENTERPRISE DISPONÍVEIS:")
    print(f"   📡 /enterprise/dashboard - Dashboard unificado")
    print(f"   🔍 /enterprise/health - Health check completo")
    print(f"   🛡️ /enterprise/guardrails/* - AI Guardrails")
    print(f"   📋 /enterprise/compliance/* - Compliance")
    print(f"   🔒 /enterprise/security/* - Segurança")
    print(f"   📈 /enterprise/monitoring/* - Monitoramento")
    print(f"   🔄 /enterprise/versioning/* - Versionamento")
    print(f"   ⚖️ /enterprise/load-balancing/* - Load Balancing")
    print(f"   📚 /enterprise/documentation/* - Documentação")
    
    print(f"\n📚 DOCUMENTAÇÃO:")
    print(f"   📖 SISTEMA_ENTERPRISE_FINALIZADO.md - Documentação completa")
    print(f"   🔗 /docs - Swagger UI")
    print(f"   📊 /enterprise/documentation/openapi - OpenAPI Spec")
    
    return success_rate >= 90

if __name__ == "__main__":
    try:
        # Executar testes
        success = asyncio.run(main())
        
        if success:
            print("\n🎉 TODOS OS TESTES PASSARAM - SISTEMA ENTERPRISE OPERACIONAL!")
            sys.exit(0)
        else:
            print("\n⚠️ ALGUNS TESTES FALHARAM - VERIFICAR IMPLEMENTAÇÃO")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO NO TESTE: {e}")
        sys.exit(1) 