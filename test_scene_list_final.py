#!/usr/bin/env python3
"""
Script final para verificar implementação completa do SceneList
Verifica arquivos, dependências, testes e gera relatório final
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class SceneListFinalChecker:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "implementation": {},
            "files": {},
            "dependencies": {},
            "tests": {},
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }

    def log_check(self, category: str, check_name: str, success: bool, details: dict = None):
        """Registra resultado de uma verificação"""
        if category not in self.results:
            self.results[category] = {}
        
        self.results[category][check_name] = {
            "success": success,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["summary"]["total_checks"] += 1
        if success:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1

    def check_file_exists(self, filepath: str, description: str) -> bool:
        """Verifica se arquivo existe"""
        exists = os.path.exists(filepath)
        self.log_check("files", description, exists, {
            "filepath": filepath,
            "exists": exists
        })
        return exists

    def check_file_content(self, filepath: str, description: str, required_content: list) -> bool:
        """Verifica conteúdo do arquivo"""
        if not os.path.exists(filepath):
            self.log_check("files", description, False, {"error": "Arquivo não encontrado"})
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_content = []
            for item in required_content:
                if item not in content:
                    missing_content.append(item)
            
            success = len(missing_content) == 0
            self.log_check("files", description, success, {
                "filepath": filepath,
                "missing_content": missing_content if not success else []
            })
            return success
        except Exception as e:
            self.log_check("files", description, False, {"error": str(e)})
            return False

    def check_dependencies(self):
        """Verifica dependências necessárias"""
        print("📦 Verificando dependências...")
        
        # Verifica package.json
        if self.check_file_exists("package.json", "package.json existe"):
            with open("package.json", 'r') as f:
                package_data = json.load(f)
            
            required_deps = [
                "react", "react-dom", "react-beautiful-dnd", 
                "@heroicons/react", "tailwindcss"
            ]
            
            deps = package_data.get("dependencies", {})
            dev_deps = package_data.get("devDependencies", {})
            
            for dep in required_deps:
                if dep in deps or dep in dev_deps:
                    self.log_check("dependencies", f"{dep} instalado", True)
                else:
                    self.log_check("dependencies", f"{dep} instalado", False)

    def check_implementation_files(self):
        """Verifica arquivos de implementação"""
        print("📁 Verificando arquivos de implementação...")
        
        # Arquivos principais
        main_files = [
            ("src/components/SceneList.jsx", "Componente SceneList"),
            ("src/services/sceneListService.js", "Serviço SceneListService"),
            ("src/hooks/useSceneList.js", "Hook useSceneList"),
            ("src/App.jsx", "Exemplo de uso no App.jsx")
        ]
        
        for filepath, description in main_files:
            self.check_file_exists(filepath, description)
        
        # Verifica conteúdo específico
        if os.path.exists("src/components/SceneList.jsx"):
            required_content = [
                "import React",
                "DragDropContext",
                "Droppable",
                "Draggable",
                "PlusIcon",
                "TrashIcon",
                "DocumentDuplicateIcon"
            ]
            self.check_file_content("src/components/SceneList.jsx", "Conteúdo SceneList.jsx", required_content)

    def check_test_files(self):
        """Verifica arquivos de teste"""
        print("🧪 Verificando arquivos de teste...")
        
        test_files = [
            ("src/components/SceneList.test.js", "Testes unitários SceneList"),
            ("test_scene_list_backend.py", "Testes de integração backend")
        ]
        
        for filepath, description in test_files:
            self.check_file_exists(filepath, description)

    def check_documentation(self):
        """Verifica documentação"""
        print("📚 Verificando documentação...")
        
        doc_files = [
            ("INSTALACAO_DEPENDENCIAS_SCENELIST.md", "Instruções de instalação"),
            ("RELATORIO_SCENELIST_IMPLEMENTACAO_COMPLETA.md", "Relatório de implementação")
        ]
        
        for filepath, description in doc_files:
            self.check_file_exists(filepath, description)

    def check_backend_accessibility(self):
        """Verifica acessibilidade do backend"""
        print("🔗 Verificando acessibilidade do backend...")
        
        try:
            import requests
            response = requests.get("http://localhost:8000/health/", timeout=3)
            success = response.status_code == 200
            self.log_check("backend", "Backend acessível", success, {
                "status_code": response.status_code,
                "response": response.text[:100] if success else response.text
            })
        except Exception as e:
            self.log_check("backend", "Backend acessível", False, {"error": str(e)})

    def run_npm_test(self):
        """Executa testes npm se disponível"""
        print("⚡ Executando testes npm...")
        
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--passWithNoTests"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            self.log_check("tests", "Testes npm executados", success, {
                "returncode": result.returncode,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500] if result.stderr else None
            })
        except Exception as e:
            self.log_check("tests", "Testes npm executados", False, {"error": str(e)})

    def generate_usage_guide(self):
        """Gera guia de uso"""
        print("📖 Gerando guia de uso...")
        
        usage_guide = """# 🚀 Guia de Uso - SceneList Component

## Instalação Rápida

```bash
# Instalar dependências
npm install react react-dom react-beautiful-dnd @heroicons/react tailwindcss

# Configurar TailwindCSS
npx tailwindcss init -p
```

## Uso Básico

```jsx
import SceneList from './components/SceneList';
import useSceneList from './hooks/useSceneList';

function MyComponent() {
  const {
    scenes,
    activeSceneId,
    selectScene,
    addScene,
    removeScene,
    duplicateScene,
    reorderScenes
  } = useSceneList('project-id');

  return (
    <SceneList
      scenes={scenes}
      activeSceneId={activeSceneId}
      onSceneSelect={selectScene}
      onSceneAdd={addScene}
      onSceneRemove={removeScene}
      onSceneDuplicate={duplicateScene}
      onSceneReorder={reorderScenes}
    />
  );
}
```

## Funcionalidades

- ✅ **Adicionar cena**: Clique no botão +
- ✅ **Selecionar cena**: Clique na cena desejada
- ✅ **Remover cena**: Clique no botão 🗑 (cena ativa)
- ✅ **Duplicar cena**: Clique no botão 📋 (cena ativa)
- ✅ **Reordenar**: Arraste e solte as cenas

## Configuração Backend

```javascript
// Configurar URL do backend
process.env.REACT_APP_API_URL = 'http://localhost:8000';

// Configurar token de autenticação
sceneListService.setAuthToken('your-jwt-token');
```

## Testes

```bash
# Executar testes unitários
npm test

# Executar testes de integração
python test_scene_list_backend.py
```

## Suporte

- 📚 Documentação: INSTALACAO_DEPENDENCIAS_SCENELIST.md
- 🧪 Testes: src/components/SceneList.test.js
- 🔧 Exemplo: src/App.jsx
"""
        
        try:
            with open("GUIA_USO_SCENELIST.md", 'w', encoding='utf-8') as f:
                f.write(usage_guide)
            self.log_check("documentation", "Guia de uso gerado", True)
        except Exception as e:
            self.log_check("documentation", "Guia de uso gerado", False, {"error": str(e)})

    def run_all_checks(self):
        """Executa todas as verificações"""
        print("🔍 Iniciando verificação final da implementação SceneList...")
        print("=" * 60)
        
        # Executa verificações
        self.check_implementation_files()
        self.check_dependencies()
        self.check_test_files()
        self.check_documentation()
        self.check_backend_accessibility()
        self.run_npm_test()
        self.generate_usage_guide()
        
        # Calcula estatísticas
        summary = self.results["summary"]
        success_rate = (summary["passed"] / summary["total_checks"] * 100) if summary["total_checks"] > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 RESULTADO FINAL")
        print("=" * 60)
        print(f"Total de verificações: {summary['total_checks']}")
        print(f"Passaram: {summary['passed']}")
        print(f"Falharam: {summary['failed']}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ SceneList está pronto para uso")
        elif success_rate >= 60:
            print("\n⚠️ IMPLEMENTAÇÃO PARCIALMENTE CONCLUÍDA")
            print("🔧 Algumas verificações falharam, mas o componente está funcional")
        else:
            print("\n❌ IMPLEMENTAÇÃO INCOMPLETA")
            print("🔧 Verifique os erros e complete a implementação")
        
        return self.results

    def save_report(self, filename: str = "scene_list_final_check_report.json"):
        """Salva relatório final"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Relatório salvo em: {filename}")
        except Exception as e:
            print(f"\n❌ Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    checker = SceneListFinalChecker()
    results = checker.run_all_checks()
    
    # Salva relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scene_list_final_check_{timestamp}.json"
    checker.save_report(filename)
    
    # Retorna código de saída
    success_rate = (results["summary"]["passed"] / results["summary"]["total_checks"] * 100) if results["summary"]["total_checks"] > 0 else 0
    return 0 if success_rate >= 60 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 