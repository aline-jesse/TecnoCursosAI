#!/usr/bin/env python3
"""
Script para verificar e corrigir as senhas dos usuários
"""

import sys
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base, get_db
from app.models import User
from app.auth import get_password_hash, verify_password
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_passwords():
    """Corrige as senhas dos usuários de teste"""
    db = next(get_db())
    
    try:
        # Usuários para corrigir
        users_to_fix = [
            ("admin@tecnocursos.ai", "admin123"),
            ("teste@tecnocursos.ai", "senha123")
        ]
        
        for email, password in users_to_fix:
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                # Verificar se a senha atual está correta
                if not verify_password(password, user.hashed_password):
                    logger.info(f"Corrigindo senha para: {email}")
                    user.hashed_password = get_password_hash(password)
                    db.commit()
                    logger.info(f"✅ Senha corrigida para: {email}")
                else:
                    logger.info(f"✅ Senha já está correta para: {email}")
                    
                # Mostrar informações do usuário
                logger.info(f"   ID: {user.id}")
                logger.info(f"   Username: {user.username}")
                logger.info(f"   Full Name: {user.full_name}")
                logger.info(f"   Active: {user.is_active}")
                logger.info(f"   Admin: {user.is_admin}")
            else:
                logger.warning(f"❌ Usuário não encontrado: {email}")
        
        # Listar todos os usuários
        logger.info("\n📋 Todos os usuários no banco:")
        all_users = db.query(User).all()
        for user in all_users:
            logger.info(f"   - {user.email} ({user.username}) - Admin: {user.is_admin}")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        db.rollback()
        db.close()
        return False

if __name__ == "__main__":
    logger.info("🔧 Verificando e corrigindo senhas dos usuários...")
    
    if fix_passwords():
        logger.info("\n✅ Senhas verificadas/corrigidas com sucesso!")
        logger.info("\n📧 Credenciais para teste:")
        logger.info("   - admin@tecnocursos.ai / admin123")
        logger.info("   - teste@tecnocursos.ai / senha123")
    else:
        logger.error("\n❌ Erro ao corrigir senhas")
        sys.exit(1) 