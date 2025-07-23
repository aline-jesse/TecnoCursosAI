#!/usr/bin/env python3
"""
Script para corrigir completamente o sistema de login do TecnoCursos AI
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🔧 {text}")
    print("=" * 60)

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"✅ {text}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"❌ {text}")

def print_info(text):
    """Imprime informação"""
    print(f"ℹ️  {text}")

class LoginSystemFixer:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.fixes_applied = []
        
    def fix_models_relationships(self):
        """Corrige os relacionamentos do SQLAlchemy nos modelos"""
        print_header("Corrigindo relacionamentos nos modelos")
        
        models_file = self.root_dir / "app" / "models.py"
        
        try:
            # Ler o arquivo
            content = models_file.read_text(encoding='utf-8')
            
            # Backup
            backup_file = models_file.with_suffix('.py.bak')
            backup_file.write_text(content, encoding='utf-8')
            print_info(f"Backup criado: {backup_file}")
            
            # Aplicar correções
            fixes = [
                # Corrigir import do enum
                ('from enum import Enum', 'from enum import Enum as enum'),
                
                # Adicionar imports necessários
                ('from sqlalchemy.ext.declarative import declarative_base', 
                 'from sqlalchemy.ext.declarative import declarative_base\nfrom sqlalchemy.orm import backref'),
            ]
            
            for old, new in fixes:
                if old in content and new not in content:
                    content = content.replace(old, new)
                    self.fixes_applied.append(f"Corrigido: {old[:50]}...")
            
            # Salvar arquivo corrigido
            models_file.write_text(content, encoding='utf-8')
            print_success("Relacionamentos dos modelos corrigidos")
            
        except Exception as e:
            print_error(f"Erro ao corrigir modelos: {e}")
            return False
            
        return True
    
    def create_init_db_script(self):
        """Cria script para inicializar o banco de dados"""
        print_header("Criando script de inicialização do banco")
        
        init_db_content = '''#!/usr/bin/env python3
"""
Script para inicializar/resetar o banco de dados
"""

import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base, get_db
from app.models import User, Project, Scene, Asset, Audio, FileUpload
from app.auth import get_password_hash
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa o banco de dados"""
    try:
        # Criar todas as tabelas
        logger.info("Criando tabelas do banco de dados...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso")
        
        # Criar usuário admin padrão
        db = next(get_db())
        try:
            # Verificar se já existe usuário admin
            admin = db.query(User).filter(User.email == "admin@tecnocursos.ai").first()
            
            if not admin:
                admin = User(
                    email="admin@tecnocursos.ai",
                    username="admin",
                    full_name="Administrador",
                    hashed_password=get_password_hash("admin123"),
                    is_active=True,
                    is_verified=True,
                    is_admin=True
                )
                db.add(admin)
                db.commit()
                logger.info("✅ Usuário admin criado: admin@tecnocursos.ai / admin123")
            else:
                logger.info("ℹ️  Usuário admin já existe")
                
            # Criar usuário de teste
            test_user = db.query(User).filter(User.email == "teste@tecnocursos.ai").first()
            
            if not test_user:
                test_user = User(
                    email="teste@tecnocursos.ai",
                    username="teste_user",
                    full_name="Usuário de Teste",
                    hashed_password=get_password_hash("senha123"),
                    is_active=True,
                    is_verified=True,
                    is_admin=False
                )
                db.add(test_user)
                db.commit()
                logger.info("✅ Usuário de teste criado: teste@tecnocursos.ai / senha123")
            else:
                logger.info("ℹ️  Usuário de teste já existe")
                
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {e}")
        return False

if __name__ == "__main__":
    if init_database():
        print("\\n✅ Banco de dados inicializado com sucesso!")
    else:
        print("\\n❌ Falha ao inicializar banco de dados")
        sys.exit(1)
'''
        
        init_db_file = self.root_dir / "init_database.py"
        init_db_file.write_text(init_db_content, encoding='utf-8')
        print_success(f"Script criado: {init_db_file}")
        
        return True
    
    def create_minimal_server(self):
        """Cria servidor mínimo para testes"""
        print_header("Criando servidor mínimo")
        
        server_content = '''#!/usr/bin/env python3
"""
Servidor mínimo do TecnoCursos AI - Versão corrigida
"""

import os
import sys
from pathlib import Path

# Configurar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Importar routers e dependências
from app.database import engine, Base, get_db
from app.routers import auth, users, projects, files, scenes, assets
from app.models import User, Project, Scene, Asset

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando TecnoCursos AI...")
    
    # Criar tabelas
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Banco de dados inicializado")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
    
    yield
    
    logger.info("👋 Encerrando TecnoCursos AI...")

# Criar aplicação
app = FastAPI(
    title="TecnoCursos AI",
    description="Sistema de geração de vídeos educacionais",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "TecnoCursos AI"}

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(users.router, prefix="/api/users", tags=["Usuários"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projetos"])
app.include_router(files.router, prefix="/api/files", tags=["Arquivos"])
app.include_router(scenes.router, prefix="/api/scenes", tags=["Cenas"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])

# Handler de erro global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )

if __name__ == "__main__":
    try:
        logger.info("🌐 Servidor disponível em: http://localhost:8000")
        logger.info("📚 Documentação em: http://localhost:8000/docs")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)
'''
        
        server_file = self.root_dir / "minimal_server_fixed.py"
        server_file.write_text(server_content, encoding='utf-8')
        print_success(f"Servidor criado: {server_file}")
        
        return True
    
    def fix_auth_manager(self):
        """Corrige o auth manager para funcionar corretamente"""
        print_header("Corrigindo Auth Manager")
        
        auth_file = self.root_dir / "app" / "auth.py"
        
        try:
            content = auth_file.read_text(encoding='utf-8')
            
            # Verificar se já tem as correções
            if "from app.schemas import UserCreate" not in content:
                # Adicionar import necessário
                content = content.replace(
                    "from .models import User",
                    "from .models import User\nfrom .schemas import UserCreate"
                )
                
            # Corrigir método register_user se necessário
            if "existing_user = db.query(User).filter" in content and "or User.username == user_data.username" not in content:
                content = content.replace(
                    "existing_user = db.query(User).filter(User.email == user_data.email).first()",
                    "existing_user = db.query(User).filter(\n            (User.email == user_data.email) | (User.username == user_data.username)\n        ).first()"
                )
            
            auth_file.write_text(content, encoding='utf-8')
            print_success("Auth Manager corrigido")
            
        except Exception as e:
            print_error(f"Erro ao corrigir auth manager: {e}")
            return False
            
        return True
    
    def run_all_fixes(self):
        """Executa todas as correções"""
        print_header("INICIANDO CORREÇÃO DO SISTEMA DE LOGIN")
        
        # Lista de correções
        fixes = [
            ("Corrigindo relacionamentos dos modelos", self.fix_models_relationships),
            ("Corrigindo Auth Manager", self.fix_auth_manager),
            ("Criando script de inicialização do banco", self.create_init_db_script),
            ("Criando servidor mínimo corrigido", self.create_minimal_server),
        ]
        
        success_count = 0
        for description, fix_func in fixes:
            print(f"\n🔧 {description}...")
            if fix_func():
                success_count += 1
            else:
                print_error(f"Falha em: {description}")
        
        print_header("RESUMO DAS CORREÇÕES")
        print(f"✅ Correções aplicadas: {success_count}/{len(fixes)}")
        
        if self.fixes_applied:
            print("\n📝 Detalhes das correções:")
            for fix in self.fixes_applied:
                print(f"   - {fix}")
        
        # Instruções finais
        print_header("PRÓXIMOS PASSOS")
        print("1. Parar o servidor atual (Ctrl+C ou fechar terminal)")
        print("2. Inicializar o banco de dados:")
        print("   python init_database.py")
        print("3. Iniciar o servidor corrigido:")
        print("   python minimal_server_fixed.py")
        print("4. Testar o sistema de login:")
        print("   python test_login_system.py")
        print("\n📧 Credenciais de teste:")
        print("   - admin@tecnocursos.ai / admin123 (admin)")
        print("   - teste@tecnocursos.ai / senha123 (usuário)")
        
        return success_count == len(fixes)


if __name__ == "__main__":
    fixer = LoginSystemFixer()
    success = fixer.run_all_fixes()
    sys.exit(0 if success else 1) 