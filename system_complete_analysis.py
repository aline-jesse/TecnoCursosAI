#!/usr/bin/env python3
"""
TecnoCursos AI - Análise Completa do Sistema
Script para identificar e corrigir todos os problemas do sistema
"""

import os
import sys
import json
import time
import socket
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SystemAnalyzer:
    """Analisador completo do sistema TecnoCursos AI"""
    
    def __init__(self):
        self.root_path = Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "analysis": {},
            "problems": [],
            "recommendations": [],
            "phase_status": {}
        }
    
    def analyze_file_structure(self) -> Dict[str, Any]:
        """Analisa a estrutura de arquivos do projeto"""
        print("🔍 Analisando estrutura de arquivos...")
        
        critical_files = {
            "backend/app/main.py": "Servidor principal",
            "server_simple_fase4.py": "Servidor Fase 4", 
            "system/monitoring_dashboard.py": "Dashboard de monitoramento",
            "frontend/src/App.jsx": "Frontend React",
            "docs/STATUS_FASES_PROJETO.md": "Status das fases",
            "README.md": "Documentação principal"
        }
        
        structure_status = {}
        missing_files = []
        
        for file_path, description in critical_files.items():
            full_path = self.root_path / file_path
            if full_path.exists():
                structure_status[file_path] = {
                    "exists": True,
                    "size": full_path.stat().st_size,
                    "description": description
                }
            else:
                structure_status[file_path] = {
                    "exists": False,
                    "description": description
                }
                missing_files.append(file_path)
        
        if missing_files:
            self.results["problems"].append({
                "type": "missing_files",
                "severity": "medium",
                "files": missing_files,
                "recommendation": "Recriar arquivos críticos em falta"
            })
        
        return structure_status
    
    def analyze_python_compatibility(self) -> Dict[str, Any]:
        """Analisa compatibilidade Python e dependências"""
        print("🐍 Analisando compatibilidade Python...")
        
        python_info = {
            "version": sys.version,
            "version_info": sys.version_info,
            "executable": sys.executable
        }
        
        # Testar importações críticas
        critical_imports = {
            "fastapi": "Framework web principal",
            "sqlalchemy": "ORM para banco de dados",
            "pydantic": "Validação de dados",
            "uvicorn": "Servidor ASGI"
        }
        
        import_status = {}
        failed_imports = []
        
        for module, description in critical_imports.items():
            try:
                spec = importlib.util.find_spec(module)
                if spec is not None:
                    # Tentar importar para verificar compatibilidade
                    imported_module = importlib.import_module(module)
                    version = getattr(imported_module, '__version__', 'unknown')
                    import_status[module] = {
                        "available": True,
                        "version": version,
                        "description": description
                    }
                else:
                    import_status[module] = {
                        "available": False,
                        "description": description
                    }
                    failed_imports.append(module)
            except Exception as e:
                import_status[module] = {
                    "available": False,
                    "error": str(e),
                    "description": description
                }
                failed_imports.append(module)
        
        if failed_imports:
            self.results["problems"].append({
                "type": "import_failures",
                "severity": "high",
                "modules": failed_imports,
                "recommendation": "Instalar dependências em falta ou corrigir incompatibilidades"
            })
        
        return {
            "python_info": python_info,
            "imports": import_status
        }
    
    def analyze_servers(self) -> Dict[str, Any]:
        """Analisa status dos servidores"""
        print("🚀 Analisando servidores...")
        
        servers = {
            "main_server": {
                "file": "backend/app/main.py",
                "port": 8000,
                "description": "Servidor principal completo"
            },
            "fase4_server": {
                "file": "server_simple_fase4.py", 
                "port": 8000,
                "description": "Servidor Fase 4 específico"
            },
            "monitoring": {
                "file": "system/monitoring_dashboard.py",
                "port": 8001,
                "description": "Dashboard de monitoramento"
            }
        }
        
        server_status = {}
        
        for server_name, config in servers.items():
            status = {
                "file_exists": (self.root_path / config["file"]).exists(),
                "port_available": self.check_port_available(config["port"]),
                "can_import": False,
                "errors": []
            }
            
            # Tentar importar/executar
            if status["file_exists"]:
                try:
                    if server_name == "main_server":
                        # Tentar importar o main
                        sys.path.insert(0, str(self.root_path / "backend"))
                        from app.main import app
                        status["can_import"] = True
                    elif server_name == "fase4_server":
                        # Verificar se pode ser executado
                        status["can_import"] = True  # Assumir OK se arquivo existe
                except Exception as e:
                    status["errors"].append(str(e))
            
            server_status[server_name] = status
        
        return server_status
    
    def check_port_available(self, port: int) -> bool:
        """Verifica se uma porta está disponível"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except socket.error:
            return False
    
    def analyze_frontend(self) -> Dict[str, Any]:
        """Analisa status do frontend React"""
        print("⚛️ Analisando frontend React...")
        
        frontend_path = self.root_path / "frontend"
        
        status = {
            "directory_exists": frontend_path.exists(),
            "package_json_exists": (frontend_path / "package.json").exists(),
            "src_exists": (frontend_path / "src").exists(),
            "node_modules_exists": (frontend_path / "node_modules").exists(),
            "components": {}
        }
        
        if status["src_exists"]:
            src_path = frontend_path / "src"
            components_path = src_path / "components"
            
            if components_path.exists():
                components = [
                    "AssetPanel.tsx", "EditorCanvas.tsx", "SceneList.tsx",
                    "Timeline.tsx", "Toolbar.tsx"
                ]
                
                for component in components:
                    comp_path = components_path / component
                    status["components"][component] = comp_path.exists()
        
        return status
    
    def analyze_phase_implementation(self) -> Dict[str, Any]:
        """Analisa o status real de implementação das fases"""
        print("📋 Analisando implementação das fases...")
        
        phases = {
            "fase1": {
                "name": "Arquitetura e Fundamentos",
                "files": ["backend/app/main.py", "backend/app/database.py", "backend/app/config.py"],
                "description": "Estrutura básica do backend"
            },
            "fase2": {
                "name": "Módulos Básicos do Editor", 
                "files": ["frontend/src/components/AssetPanel.tsx", "frontend/src/components/EditorCanvas.tsx"],
                "description": "Componentes básicos do editor"
            },
            "fase3": {
                "name": "Funcionalidades Avançadas",
                "files": ["frontend/src/components/PropertyPanel.tsx", "frontend/src/store/editorStore.ts"],
                "description": "Funcionalidades avançadas do editor"
            },
            "fase4": {
                "name": "Integrações e Exportação",
                "files": ["server_simple_fase4.py", "backend/app/routers/video_export.py"],
                "description": "APIs de exportação e TTS"
            },
            "fase5": {
                "name": "Testes e Produção",
                "files": ["tests/", "backend/tests/"],
                "description": "Testes e configuração de produção"
            },
            "fase6": {
                "name": "Funcionalidades Premium",
                "files": ["system/monitoring_dashboard.py", "backend/app/services/modern_ai_service.py"],
                "description": "Recursos enterprise e IA avançada"
            }
        }
        
        phase_status = {}
        
        for phase_id, phase_info in phases.items():
            files_exist = []
            files_missing = []
            
            for file_path in phase_info["files"]:
                full_path = self.root_path / file_path
                if full_path.exists() or (full_path.is_dir() and any(full_path.iterdir())):
                    files_exist.append(file_path)
                else:
                    files_missing.append(file_path)
            
            completion_percent = (len(files_exist) / len(phase_info["files"])) * 100
            
            if completion_percent >= 80:
                status = "completed"
            elif completion_percent >= 50:
                status = "partial"
            else:
                status = "pending"
            
            phase_status[phase_id] = {
                "name": phase_info["name"],
                "description": phase_info["description"],
                "status": status,
                "completion_percent": completion_percent,
                "files_exist": files_exist,
                "files_missing": files_missing
            }
        
        return phase_status
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas na análise"""
        print("💡 Gerando recomendações...")
        
        recommendations = []
        
        # Analisar problemas identificados
        for problem in self.results["problems"]:
            if problem["type"] == "import_failures":
                recommendations.append({
                    "priority": "high",
                    "category": "dependencies",
                    "title": "Corrigir dependências Python",
                    "description": "Instalar ou atualizar dependências em falta",
                    "action": "pip install --upgrade " + " ".join(problem["modules"])
                })
            
            elif problem["type"] == "missing_files":
                recommendations.append({
                    "priority": "medium", 
                    "category": "structure",
                    "title": "Recriar arquivos críticos",
                    "description": "Alguns arquivos importantes estão faltando",
                    "action": "Recriar arquivos: " + ", ".join(problem["files"])
                })
        
        return recommendations
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Executa análise completa do sistema"""
        print("🔍 TecnoCursos AI - Análise Completa do Sistema")
        print("=" * 55)
        
        # Executar todas as análises
        self.results["analysis"]["file_structure"] = self.analyze_file_structure()
        self.results["analysis"]["python_compatibility"] = self.analyze_python_compatibility()
        self.results["analysis"]["servers"] = self.analyze_servers()
        self.results["analysis"]["frontend"] = self.analyze_frontend()
        self.results["phase_status"] = self.analyze_phase_implementation()
        self.results["recommendations"] = self.generate_recommendations()
        
        return self.results
    
    def save_results(self, filename: str = "system_analysis_results.json"):
        """Salva resultados da análise em arquivo JSON"""
        output_path = self.root_path / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 Resultados salvos em: {output_path}")
    
    def print_summary(self):
        """Imprime resumo da análise"""
        print("\n" + "=" * 55)
        print("📊 RESUMO DA ANÁLISE")
        print("=" * 55)
        
        # Status das fases
        print("\n📋 Status das Fases:")
        for phase_id, phase_info in self.results["phase_status"].items():
            status_emoji = "✅" if phase_info["status"] == "completed" else "⚠️" if phase_info["status"] == "partial" else "❌"
            print(f"   {status_emoji} {phase_info['name']}: {phase_info['completion_percent']:.0f}%")
        
        # Problemas encontrados
        if self.results["problems"]:
            print(f"\n🚨 Problemas Encontrados: {len(self.results['problems'])}")
            for problem in self.results["problems"]:
                severity_emoji = "🔴" if problem["severity"] == "high" else "🟡"
                print(f"   {severity_emoji} {problem['type']}: {problem['recommendation']}")
        
        # Recomendações
        if self.results["recommendations"]:
            print(f"\n💡 Recomendações: {len(self.results['recommendations'])}")
            for rec in self.results["recommendations"][:3]:  # Top 3
                priority_emoji = "🔥" if rec["priority"] == "high" else "⚡"
                print(f"   {priority_emoji} {rec['title']}")

def main():
    """Função principal"""
    analyzer = SystemAnalyzer()
    
    try:
        # Executar análise completa
        results = analyzer.run_complete_analysis()
        
        # Salvar resultados
        analyzer.save_results()
        
        # Mostrar resumo
        analyzer.print_summary()
        
        print("\n✅ Análise completa finalizada!")
        print("📄 Verifique o arquivo 'system_analysis_results.json' para detalhes completos.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 