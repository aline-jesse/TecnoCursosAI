#!/usr/bin/env python3
"""
Teste da API Avatar - TecnoCursosAI
Script para testar todos os endpoints da API avatar
"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8003"

def test_health():
    """Testar health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_root():
    """Testar endpoint raiz"""
    print("\n🏠 Testando endpoint raiz...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint raiz OK: {data['message']}")
            return True
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no endpoint raiz: {e}")
        return False

def test_generate_video():
    """Testar geração de vídeo"""
    print("\n🎬 Testando geração de vídeo...")
    
    request_data = {
        "title": "Curso de Python Básico",
        "slides": [
            {
                "title": "Introdução ao Python",
                "content": "Python é uma linguagem de programação de alto nível.\n• Sintaxe simples\n• Fácil de aprender\n• Multiplataforma"
            },
            {
                "title": "Primeiro Programa",
                "content": "Vamos criar nosso primeiro programa:\n\nprint('Olá, mundo!')\n\nEste é o tradicional 'Hello World' em Python."
            }
        ],
        "narration_text": "Bem-vindos ao curso de Python!",
        "avatar_style": "professional",
        "video_quality": "hd"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/generate",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"✅ Job criado: {job_id}")
            print(f"   Status: {job_data['status']}")
            return job_id
        else:
            print(f"❌ Geração falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        return None

def test_job_status(job_id):
    """Testar status do job"""
    print(f"\n📊 Testando status do job {job_id[:8]}...")
    
    max_attempts = 30  # 30 segundos máximo
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE}/status/{job_id}")
            
            if response.status_code == 200:
                job_data = response.json()
                status = job_data["status"]
                progress = job_data["progress"]
                message = job_data["message"]
                
                print(f"   Status: {status} ({progress:.1f}%) - {message}")
                
                if status == "completed":
                    print("✅ Job concluído com sucesso!")
                    return True
                elif status == "error":
                    print(f"❌ Job falhou: {job_data.get('error_details', 'Erro desconhecido')}")
                    return False
                else:
                    time.sleep(1)
                    attempt += 1
            else:
                print(f"❌ Erro ao consultar status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            return False
    
    print("⏰ Timeout na geração do vídeo")
    return False

def test_download_video(job_id):
    """Testar download do vídeo"""
    print(f"\n⬇️ Testando download do vídeo {job_id[:8]}...")
    
    try:
        response = requests.get(f"{API_BASE}/download/{job_id}")
        
        if response.status_code == 200:
            # Salvar arquivo
            filename = f"test_avatar_api_{job_id[:8]}.mp4"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Vídeo baixado: {filename}")
            print(f"   Tamanho: {file_size / 1024:.1f} KB")
            return True
        else:
            print(f"❌ Download falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return False

def test_list_jobs():
    """Testar listagem de jobs"""
    print("\n📋 Testando listagem de jobs...")
    
    try:
        response = requests.get(f"{API_BASE}/jobs")
        
        if response.status_code == 200:
            data = response.json()
            total_jobs = data["total"]
            print(f"✅ Jobs listados: {total_jobs} jobs encontrados")
            
            if total_jobs > 0:
                print("   Jobs:")
                for job in data["jobs"][:3]:  # Mostrar apenas os 3 primeiros
                    print(f"     {job['job_id'][:8]} - {job['status']} - {job['message']}")
            
            return True
        else:
            print(f"❌ Listagem falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE COMPLETO DA API AVATAR")
    print("=" * 50)
    
    # Testes sequenciais
    tests = [
        ("Health Check", test_health),
        ("Endpoint Raiz", test_root),
        ("Listar Jobs", test_list_jobs),
    ]
    
    results = {}
    
    # Executar testes básicos
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results[test_name] = False
    
    # Verificar se API está funcionando antes de testar geração
    if not results.get("Health Check", False):
        print("\n❌ API não está funcionando. Parando testes.")
        return False
    
    # Teste de geração completa
    print(f"\n{'='*20} GERAÇÃO DE VÍDEO {'='*20}")
    job_id = test_generate_video()
    
    if job_id:
        # Aguardar conclusão
        if test_job_status(job_id):
            # Tentar download
            results["Download Vídeo"] = test_download_video(job_id)
        else:
            results["Download Vídeo"] = False
    else:
        results["Geração de Vídeo"] = False
        results["Download Vídeo"] = False
    
    # Resumo final
    print(f"\n{'='*50}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*50}")
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:20} {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\nResultado: {passed}/{total} testes passaram ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 API Avatar está funcional!")
        return True
    else:
        print("⚠️ API precisa de correções")
        return False

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 