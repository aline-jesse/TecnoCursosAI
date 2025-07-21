#!/usr/bin/env python3
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
        print("\n✅ Banco de dados inicializado com sucesso!")
    else:
        print("\n❌ Falha ao inicializar banco de dados")
        sys.exit(1)
