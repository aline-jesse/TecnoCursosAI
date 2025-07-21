#!/usr/bin/env python3
"""
Script de Instalação de Dependências - TecnoCursos AI
Instala todas as dependências necessárias para o sistema
"""

import subprocess
import sys
import os
import importlib
from pathlib import Path

def print_banner():
    """Exibe banner do instalador"""
    print("=" * 80)
    print("INSTALADOR DE DEPENDENCIAS - TECNOCURSOS AI")
    print("=" * 80)
    print("Instalando dependências necessárias para o sistema")
    print("=" * 80)

def check_python_version():
    """Verifica a versão do Python"""
    print("🔍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} não é compatível")
        print("Python 3.8+ é necessário")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_package(package_name, pip_name=None):
    """Instala um pacote Python"""
    if pip_name is None:
        pip_name = package_name
    
    try:
        # Tentar importar primeiro
        importlib.import_module(package_name)
        print(f"✅ {package_name} já está instalado")
        return True
    except ImportError:
        print(f"📦 Instalando {package_name}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", pip_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package_name} instalado com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {package_name}: {e}")
            return False

def install_dependencies():
    """Instala todas as dependências necessárias"""
    print("\n📦 Instalando dependências...")
    
    dependencies = [
        ("requests", "requests"),
        ("psutil", "psutil"),
        ("pathlib", "pathlib2"),  # Para Python < 3.4
        ("json", None),  # Built-in
        ("logging", None),  # Built-in
        ("subprocess", None),  # Built-in
        ("threading", None),  # Built-in
        ("socket", None),  # Built-in
        ("time", None),  # Built-in
        ("os", None),  # Built-in
        ("sys", None),  # Built-in
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for package_name, pip_name in dependencies:
        if pip_name is None:
            # Built-in module
            try:
                importlib.import_module(package_name)
                print(f"✅ {package_name} (built-in) - OK")
                success_count += 1
            except ImportError:
                print(f"❌ {package_name} não disponível")
        else:
            if install_package(package_name, pip_name):
                success_count += 1
    
    print(f"\n📊 Resultado: {success_count}/{total_count} dependências instaladas")
    return success_count == total_count

def create_requirements_file():
    """Cria arquivo requirements.txt"""
    requirements = [
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "pathlib2>=2.3.0;python_version<'3.4'"
    ]
    
    try:
        with open('requirements.txt', 'w') as f:
            for req in requirements:
                f.write(req + '\n')
        print("✅ requirements.txt criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar requirements.txt: {e}")
        return False

def verify_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("\n🔍 Verificando instalação...")
    
    # Testar imports
    try:
        import requests
        print("✅ requests - OK")
    except ImportError:
        print("❌ requests - FALHOU")
        return False
    
    try:
        import psutil
        print("✅ psutil - OK")
    except ImportError:
        print("❌ psutil - FALHOU")
        return False
    
    # Testar funcionalidades básicas
    try:
        import requests
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ requests funcional - OK")
        else:
            print("❌ requests não está funcionando")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar requests: {e}")
        return False
    
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        print(f"✅ psutil funcional - CPU: {cpu_percent}%")
    except Exception as e:
        print(f"❌ Erro ao testar psutil: {e}")
        return False
    
    return True

def create_startup_scripts():
    """Cria scripts de inicialização"""
    print("\n📝 Criando scripts de inicialização...")
    
    # Script para Windows
    windows_script = """@echo off
echo Iniciando TecnoCursos AI...
python start_optimized_system.py
pause
"""
    
    try:
        with open('start.bat', 'w') as f:
            f.write(windows_script)
        print("✅ start.bat criado")
    except Exception as e:
        print(f"❌ Erro ao criar start.bat: {e}")
    
    # Script para Linux/Mac
    unix_script = """#!/bin/bash
echo "Iniciando TecnoCursos AI..."
python3 start_optimized_system.py
"""
    
    try:
        with open('start.sh', 'w') as f:
            f.write(unix_script)
        # Tornar executável
        os.chmod('start.sh', 0o755)
        print("✅ start.sh criado")
    except Exception as e:
        print(f"❌ Erro ao criar start.sh: {e}")

def main():
    """Função principal"""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        return False
    
    # Instalar dependências
    if not install_dependencies():
        print("❌ Falha na instalação de dependências")
        return False
    
    # Criar requirements.txt
    create_requirements_file()
    
    # Verificar instalação
    if not verify_installation():
        print("❌ Falha na verificação da instalação")
        return False
    
    # Criar scripts de inicialização
    create_startup_scripts()
    
    print("\n" + "=" * 80)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print("✅ Todas as dependências foram instaladas")
    print("✅ Sistema pronto para uso")
    print("✅ Scripts de inicialização criados")
    print("\nPara iniciar o sistema:")
    print("  Windows: start.bat")
    print("  Linux/Mac: ./start.sh")
    print("  Manual: python start_optimized_system.py")
    print("\nAcesse: http://localhost:8000")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 