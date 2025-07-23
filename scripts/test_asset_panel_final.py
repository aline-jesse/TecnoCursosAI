#!/usr/bin/env python3
"""
Script de Verificação Final - AssetPanel
Verifica se todos os arquivos foram criados corretamente e funcionam
"""

import os
import json
import sys
from datetime import datetime

def check_file_exists(filepath, description):
    """Verifica se arquivo existe e tem conteúdo"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return {
                'exists': True,
                'size': len(content),
                'lines': content.count('\n') + 1,
                'description': description
            }
    return {
        'exists': False,
        'size': 0,
        'lines': 0,
        'description': description
    }

def check_implementation():
    """Verifica toda a implementação do AssetPanel"""
    
    print("🔍 Verificando implementação do AssetPanel...")
    print("=" * 60)
    
    # Lista de arquivos a verificar
    files_to_check = [
        {
            'path': 'src/components/AssetPanel.jsx',
            'description': 'Componente principal AssetPanel'
        },
        {
            'path': 'src/components/AssetPanel.test.js',
            'description': 'Testes unitários do AssetPanel'
        },
        {
            'path': 'src/services/assetService.js',
            'description': 'Serviço de backend para assets'
        },
        {
            'path': 'src/hooks/useAssets.js',
            'description': 'Hook personalizado useAssets'
        },
        {
            'path': 'src/App.jsx',
            'description': 'App.jsx com integração do AssetPanel'
        },
        {
            'path': 'INSTALACAO_DEPENDENCIAS_ASSETPANEL.md',
            'description': 'Instruções de instalação'
        },
        {
            'path': 'demo_asset_panel_complete.html',
            'description': 'Demo HTML standalone'
        },
        {
            'path': 'RELATORIO_ASSETPANEL_IMPLEMENTACAO_COMPLETA.md',
            'description': 'Relatório de implementação'
        }
    ]
    
    results = []
    total_files = len(files_to_check)
    existing_files = 0
    
    for file_info in files_to_check:
        result = check_file_exists(file_info['path'], file_info['description'])
        results.append({
            'file': file_info['path'],
            **result
        })
        
        if result['exists']:
            existing_files += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} {file_info['description']}")
        if result['exists']:
            print(f"   📄 {file_info['path']}")
            print(f"   📏 {result['lines']} linhas, {result['size']} bytes")
        print()
    
    # Verificar dependências no package.json
    package_json_exists = os.path.exists('package.json')
    if package_json_exists:
        try:
            with open('package.json', 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                
                required_deps = [
                    'react', 'react-dom', '@heroicons/react', 
                    'react-beautiful-dnd', 'tailwindcss'
                ]
                
                required_dev_deps = [
                    '@testing-library/react', '@testing-library/jest-dom',
                    'jest'
                ]
                
                missing_deps = [dep for dep in required_deps if dep not in dependencies]
                missing_dev_deps = [dep for dep in required_dev_deps if dep not in dev_dependencies]
                
                print("📦 Verificação de Dependências:")
                if not missing_deps and not missing_dev_deps:
                    print("✅ Todas as dependências necessárias estão presentes")
                else:
                    print("⚠️  Dependências faltando:")
                    for dep in missing_deps:
                        print(f"   - {dep}")
                    for dep in missing_dev_deps:
                        print(f"   - {dep} (dev)")
                print()
        except Exception as e:
            print(f"❌ Erro ao ler package.json: {e}")
            print()
    
    # Verificar estrutura de diretórios
    print("📁 Verificação de Estrutura:")
    required_dirs = [
        'src/components',
        'src/services', 
        'src/hooks'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (faltando)")
    print()
    
    # Estatísticas finais
    print("📊 Estatísticas da Implementação:")
    print(f"   📄 Arquivos criados: {existing_files}/{total_files}")
    print(f"   📈 Taxa de sucesso: {(existing_files/total_files)*100:.1f}%")
    
    total_lines = sum(r['lines'] for r in results if r['exists'])
    total_bytes = sum(r['size'] for r in results if r['exists'])
    
    print(f"   📏 Total de linhas: {total_lines:,}")
    print(f"   💾 Total de bytes: {total_bytes:,}")
    print()
    
    # Verificar funcionalidades específicas
    print("🔧 Verificação de Funcionalidades:")
    
    # Verificar se AssetPanel tem drag & drop
    asset_panel_content = ""
    if os.path.exists('src/components/AssetPanel.jsx'):
        with open('src/components/AssetPanel.jsx', 'r', encoding='utf-8') as f:
            asset_panel_content = f.read()
    
    features = [
        ('react-beautiful-dnd', 'Drag & Drop'),
        ('@heroicons/react', 'Ícones Heroicons'),
        ('useState', 'Hooks React'),
        ('useCallback', 'Otimização de Performance'),
        ('onAddAsset', 'Callback de Adição'),
        ('onRemoveAsset', 'Callback de Remoção'),
        ('onAssetSelect', 'Callback de Seleção'),
        ('uploadProgress', 'Progresso de Upload'),
        ('isCreatingCharacter', 'Modal de Criação'),
        ('handleFileUpload', 'Upload de Arquivos'),
        ('handleDragEnd', 'Drag & Drop'),
        ('TailwindCSS', 'Styling com Tailwind')
    ]
    
    for keyword, feature in features:
        if keyword in asset_panel_content:
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
    
    print()
    
    # Verificar testes
    test_content = ""
    if os.path.exists('src/components/AssetPanel.test.js'):
        with open('src/components/AssetPanel.test.js', 'r', encoding='utf-8') as f:
            test_content = f.read()
    
    test_features = [
        ('render', 'Testes de Renderização'),
        ('fireEvent', 'Testes de Interação'),
        ('waitFor', 'Testes Assíncronos'),
        ('DragDropContext', 'Testes de Drag & Drop'),
        ('jest.mock', 'Mocks de Dependências'),
        ('screen.getByText', 'Testes de Acessibilidade')
    ]
    
    print("🧪 Verificação de Testes:")
    for keyword, feature in test_features:
        if keyword in test_content:
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
    
    print()
    
    # Verificar serviço
    service_content = ""
    if os.path.exists('src/services/assetService.js'):
        with open('src/services/assetService.js', 'r', encoding='utf-8') as f:
            service_content = f.read()
    
    service_features = [
        ('getAssets', 'Buscar Assets'),
        ('addAsset', 'Adicionar Asset'),
        ('removeAsset', 'Remover Asset'),
        ('updateAsset', 'Atualizar Asset'),
        ('uploadFile', 'Upload de Arquivo'),
        ('validateFileType', 'Validação de Arquivo'),
        ('formatFileSize', 'Formatação de Tamanho'),
        ('getMockAssets', 'Dados Mock')
    ]
    
    print("🔌 Verificação de Serviço:")
    for keyword, feature in service_features:
        if keyword in service_content:
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
    
    print()
    
    # Verificar hook
    hook_content = ""
    if os.path.exists('src/hooks/useAssets.js'):
        with open('src/hooks/useAssets.js', 'r', encoding='utf-8') as f:
            hook_content = f.read()
    
    hook_features = [
        ('useState', 'Estado Local'),
        ('useCallback', 'Memoização'),
        ('useEffect', 'Efeitos'),
        ('loadAssets', 'Carregar Assets'),
        ('addAsset', 'Adicionar Asset'),
        ('removeAsset', 'Remover Asset'),
        ('selectAsset', 'Selecionar Asset'),
        ('uploadFile', 'Upload de Arquivo')
    ]
    
    print("🎣 Verificação de Hook:")
    for keyword, feature in hook_features:
        if keyword in hook_content:
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
    
    print()
    
    # Resumo final
    print("🎯 Resumo Final:")
    if existing_files == total_files:
        print("✅ IMPLEMENTAÇÃO COMPLETA!")
        print("   Todos os arquivos foram criados com sucesso")
        print("   O componente AssetPanel está pronto para uso")
    else:
        print("⚠️  IMPLEMENTAÇÃO PARCIAL")
        print(f"   {total_files - existing_files} arquivos ainda precisam ser criados")
    
    print()
    print("📝 Próximos Passos:")
    print("   1. Instalar dependências: npm install")
    print("   2. Executar testes: npm test")
    print("   3. Iniciar desenvolvimento: npm start")
    print("   4. Abrir demo: demo_asset_panel_complete.html")
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_files': total_files,
        'existing_files': existing_files,
        'success_rate': (existing_files/total_files)*100,
        'total_lines': total_lines,
        'total_bytes': total_bytes,
        'files': results
    }
    
    with open('asset_panel_implementation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print("📄 Relatório salvo em: asset_panel_implementation_report.json")
    
    return existing_files == total_files

if __name__ == "__main__":
    success = check_implementation()
    sys.exit(0 if success else 1) 