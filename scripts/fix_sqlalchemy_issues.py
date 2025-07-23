#!/usr/bin/env python3
"""
Script para corrigir problemas específicos do SQLAlchemy
"""

import subprocess
import sys
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprimir mensagem com status colorido"""
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m", 
        "WARNING": "\033[93m",
        "INFO": "\033[94m"
    }
    color = colors.get(status, colors["INFO"])
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def fix_sqlalchemy_version():
    """Corrigir versão do SQLAlchemy"""
    print_status("🔧 Corrigindo versão do SQLAlchemy...", "INFO")
    
    try:
        # Desinstalar versão atual
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "sqlalchemy", "-y"], check=True)
        print_status("✅ SQLAlchemy desinstalado", "SUCCESS")
        
        # Instalar versão compatível
        subprocess.run([sys.executable, "-m", "pip", "install", "sqlalchemy==2.0.23"], check=True)
        print_status("✅ SQLAlchemy 2.0.23 instalado", "SUCCESS")
        
        return True
    except Exception as e:
        print_status(f"❌ Erro ao corrigir SQLAlchemy: {e}", "ERROR")
        return False

def fix_pydantic_version():
    """Corrigir versão do Pydantic"""
    print_status("🔧 Corrigindo versão do Pydantic...", "INFO")
    
    try:
        # Instalar versão compatível
        subprocess.run([sys.executable, "-m", "pip", "install", "pydantic==2.4.2"], check=True)
        print_status("✅ Pydantic 2.4.2 instalado", "SUCCESS")
        
        return True
    except Exception as e:
        print_status(f"❌ Erro ao corrigir Pydantic: {e}", "ERROR")
        return False

def test_imports():
    """Testar imports corrigidos"""
    print_status("🧪 Testando imports...", "INFO")
    
    try:
        import sqlalchemy
        print_status(f"✅ SQLAlchemy {sqlalchemy.__version__}", "SUCCESS")
        
        import pydantic
        print_status(f"✅ Pydantic {pydantic.__version__}", "SUCCESS")
        
        return True
    except Exception as e:
        print_status(f"❌ Erro nos imports: {e}", "ERROR")
        return False

def main():
    """Função principal"""
    print_status("🔧 CORRIGINDO PROBLEMAS DE DEPENDÊNCIAS", "INFO")
    print_status("=" * 60, "INFO")
    
    # Corrigir SQLAlchemy
    if not fix_sqlalchemy_version():
        return False
    
    # Corrigir Pydantic
    if not fix_pydantic_version():
        return False
    
    # Testar imports
    if not test_imports():
        return False
    
    print_status("=" * 60, "INFO")
    print_status("🎉 CORREÇÕES CONCLUÍDAS!", "SUCCESS")
    print_status("Agora execute: python start_system_complete.py", "INFO")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 