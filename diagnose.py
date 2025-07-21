#!/usr/bin/env python3
"""
TecnoCursos AI - Sistema de Diagnóstico
Verifica se todos os componentes estão funcionando
"""

import requests
import json
import os
from datetime import datetime

def main():
    print("=== TecnoCursos AI - Diagnostico do Sistema ===")
    print(f"Timestamp: {datetime.now()}")
    print()

    # Teste 1: Verificar se o servidor está rodando
    print("1. Testando conexao com o backend...")
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"   OK - Servidor responde - Status: {response.status_code}")
        
        # Testar endpoint específico
        health_response = requests.get('http://localhost:8000/api/editor/health', timeout=5)
        if health_response.status_code == 200:
            print("   OK - API do editor funcionando")
        else:
            print(f"   AVISO - API responde mas com status: {health_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ERRO - Servidor nao esta rodando na porta 8000")
        print("   SOLUCAO - Execute: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"   ERRO - {e}")

    print()

    # Teste 2: Verificar arquivos
    print("2. Verificando arquivos...")
    files_to_check = [
        'editor_integrated.html',
        'test_editor.html', 
        'app/main.py',
        'app/routers/video_editor_advanced.py',
        'app/services/autosave_service.py',
        'app/services/collaboration_service.py',
        'app/services/ai_features_service.py'
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   OK - {file_path} - {size:,} bytes")
        else:
            print(f"   ERRO - {file_path} - Arquivo nao encontrado")

    print()

    # Teste 3: Verificar diretórios de dados
    print("3. Verificando diretorios de dados...")
    data_dirs = [
        'data/autosave',
        'data/collaboration', 
        'data/ai_features',
        'data/exports',
        'data/uploads'
    ]

    for dir_path in data_dirs:
        if os.path.exists(dir_path):
            files_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            print(f"   OK - {dir_path} - {files_count} arquivos")
        else:
            print(f"   AVISO - {dir_path} - Diretorio nao existe (sera criado automaticamente)")

    print()
    print("=== INSTRUCOES ===")
    print("1. Para testar a interface:")
    print("   - Abra test_editor.html no navegador")
    print("   - Ou abra editor_integrated.html")
    print()
    print("2. Para iniciar o backend:")
    print("   cd TecnoCursosAI")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("3. Para verificar erros:")
    print("   - Abra F12 no navegador (Console)")
    print("   - Verifique se ha erros de JavaScript")
    print()

if __name__ == "__main__":
    main()