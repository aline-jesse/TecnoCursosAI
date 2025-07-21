#!/usr/bin/env python3
"""
Script de inicialização de dados para o TecnoCursosAI

Este script cria dados de exemplo para desenvolvimento e testes:
- Usuário administrador padrão
- Usuários de exemplo
- Projetos e cursos de exemplo
- Categorias padrão
"""

import sys
import os

# Adicionar o diretório pai ao path para importar os módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Project, DifficultyLevel, ProjectStatus
from app.auth import get_password_hash
from app.config import settings
from datetime import datetime
import json


def create_admin_user(db: Session) -> User:
    """Criar usuário administrador padrão"""
    admin_email = "admin@tecnocursos.ai"
    admin_username = "admin"
    
    # Verificar se já existe
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if existing_admin:
        print(f"✅ Usuário admin já existe: {admin_email}")
        return existing_admin
    
    admin_user = User(
        username=admin_username,
        email=admin_email,
        full_name="Administrador TecnoCursos",
        hashed_password=get_password_hash("TecnoCursos2024!"),
        is_active=True,
        is_superuser=True,
        bio="Administrador principal do sistema TecnoCursosAI",
        phone="+55 11 99999-9999",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✅ Usuário admin criado: {admin_email}")
    print(f"   Username: {admin_username}")
    print(f"   Senha: TecnoCursos2024!")
    
    return admin_user


def create_sample_users(db: Session) -> list[User]:
    """Criar usuários de exemplo"""
    sample_users_data = [
        {
            "username": "professor_joao",
            "email": "joao.silva@tecnocursos.ai",
            "full_name": "João Silva",
            "password": "Professor123!",
            "bio": "Professor especialista em Python e desenvolvimento web",
            "phone": "+55 11 98888-8888",
            "is_superuser": False
        },
        {
            "username": "professora_maria",
            "email": "maria.santos@tecnocursos.ai",
            "full_name": "Maria Santos",
            "password": "Professora123!",
            "bio": "Especialista em ciência de dados e machine learning",
            "phone": "+55 11 97777-7777",
            "is_superuser": False
        },
        {
            "username": "dev_carlos",
            "email": "carlos.dev@tecnocursos.ai",
            "full_name": "Carlos Desenvolvedor",
            "password": "DevCarlos123!",
            "bio": "Desenvolvedor Full Stack com 10+ anos de experiência",
            "phone": "+55 11 96666-6666",
            "is_superuser": False
        }
    ]
    
    created_users = []
    
    for user_data in sample_users_data:
        # Verificar se já existe
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"✅ Usuário já existe: {user_data['email']}")
            created_users.append(existing_user)
            continue
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=get_password_hash(user_data["password"]),
            is_active=True,
            is_superuser=user_data["is_superuser"],
            bio=user_data["bio"],
            phone=user_data["phone"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
        
        print(f"✅ Usuário criado: {user_data['email']}")
        print(f"   Username: {user_data['username']}")
        print(f"   Senha: {user_data['password']}")
    
    return created_users


def create_sample_projects(db: Session, users: list[User]) -> list[Project]:
    """Criar projetos de exemplo"""
    
    sample_projects_data = [
        {
            "title": "Python Fundamentals: Do Zero ao Avançado",
            "description": "Curso completo de Python para iniciantes e intermediários. Aprenda desde os conceitos básicos até programação orientada a objetos, manipulação de dados e desenvolvimento web.",
            "category": "programacao",
            "difficulty_level": DifficultyLevel.BEGINNER,
            "status": ProjectStatus.PUBLISHED,
            "is_public": True,
            "tags": ["python", "programacao", "iniciante", "algoritmos", "estruturas-dados"],
            "estimated_duration_hours": 40,
            "price": 199.90,
            "discount_percentage": 20,
            "requirements": "Nenhum conhecimento prévio necessário. Apenas vontade de aprender!",
            "learning_objectives": "Dominar a sintaxe Python, entender conceitos de programação, criar projetos práticos",
            "target_audience": "Iniciantes em programação, estudantes, profissionais em transição de carreira",
            "language": "pt-BR",
            "completion_certificate": True,
            "featured": True
        },
        {
            "title": "Machine Learning com Python e Scikit-learn",
            "description": "Aprenda Machine Learning na prática com Python. Desde regressão linear até redes neurais, com projetos reais e datasets do mundo real.",
            "category": "ciencia-dados",
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "status": ProjectStatus.PUBLISHED,
            "is_public": True,
            "tags": ["machine-learning", "python", "scikit-learn", "ia", "dados"],
            "estimated_duration_hours": 60,
            "price": 299.90,
            "discount_percentage": 15,
            "requirements": "Conhecimento básico de Python e matemática",
            "learning_objectives": "Implementar algoritmos de ML, avaliar modelos, fazer predições",
            "target_audience": "Desenvolvedores Python, analistas de dados, estudantes de IA",
            "language": "pt-BR",
            "completion_certificate": True,
            "featured": True
        },
        {
            "title": "Desenvolvimento Web Full Stack com FastAPI",
            "description": "Crie APIs modernas e escaláveis com FastAPI. Aprenda desde o básico até deploy em produção com Docker e CI/CD.",
            "category": "desenvolvimento-web",
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "status": ProjectStatus.PUBLISHED,
            "is_public": True,
            "tags": ["fastapi", "python", "api", "web", "backend"],
            "estimated_duration_hours": 45,
            "price": 249.90,
            "discount_percentage": 25,
            "requirements": "Conhecimento básico de Python e desenvolvimento web",
            "learning_objectives": "Criar APIs RESTful, implementar autenticação, fazer deploy",
            "target_audience": "Desenvolvedores web, programadores Python",
            "language": "pt-BR",
            "completion_certificate": True,
            "featured": False
        },
        {
            "title": "React.js: Criando Interfaces Modernas",
            "description": "Domine o React.js e crie interfaces de usuário modernas e responsivas. Hooks, Context API, Redux e muito mais.",
            "category": "frontend",
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "status": ProjectStatus.PUBLISHED,
            "is_public": True,
            "tags": ["react", "javascript", "frontend", "spa", "hooks"],
            "estimated_duration_hours": 50,
            "price": 279.90,
            "discount_percentage": 10,
            "requirements": "JavaScript ES6+, HTML, CSS",
            "learning_objectives": "Criar SPAs com React, gerenciar estado, otimizar performance",
            "target_audience": "Desenvolvedores frontend, web developers",
            "language": "pt-BR",
            "completion_certificate": True,
            "featured": False
        },
        {
            "title": "DevOps com Docker e Kubernetes",
            "description": "Aprenda containerização e orquestração. Do Docker básico ao Kubernetes em produção, incluindo CI/CD e monitoramento.",
            "category": "devops",
            "difficulty_level": DifficultyLevel.ADVANCED,
            "status": ProjectStatus.PUBLISHED,
            "is_public": True,
            "tags": ["docker", "kubernetes", "devops", "containers", "ci-cd"],
            "estimated_duration_hours": 70,
            "price": 399.90,
            "discount_percentage": 30,
            "requirements": "Experiência com Linux e desenvolvimento de software",
            "learning_objectives": "Containerizar aplicações, usar Kubernetes, implementar CI/CD",
            "target_audience": "Desenvolvedores, administradores de sistema, DevOps",
            "language": "pt-BR",
            "completion_certificate": True,
            "featured": True
        },
        {
            "title": "Análise de Dados com Pandas e Numpy",
            "description": "Manipule e analise dados como um profissional. Pandas, Numpy, visualização com Matplotlib e Seaborn.",
            "category": "ciencia-dados",
            "difficulty_level": DifficultyLevel.BEGINNER,
            "status": ProjectStatus.DRAFT,
            "is_public": False,
            "tags": ["pandas", "numpy", "python", "analise-dados", "matplotlib"],
            "estimated_duration_hours": 35,
            "price": 189.90,
            "discount_percentage": 0,
            "requirements": "Conhecimento básico de Python",
            "learning_objectives": "Manipular DataFrames, criar visualizações, análise estatística",
            "target_audience": "Analistas de dados, cientistas de dados iniciantes",
            "language": "pt-BR",
            "completion_certificate": True,
            "featured": False
        }
    ]
    
    created_projects = []
    
    for i, project_data in enumerate(sample_projects_data):
        # Distribuir projetos entre os usuários
        owner = users[i % len(users)]
        
        # Verificar se já existe
        existing_project = db.query(Project).filter(Project.title == project_data["title"]).first()
        if existing_project:
            print(f"✅ Projeto já existe: {project_data['title']}")
            created_projects.append(existing_project)
            continue
        
        project = Project(
            title=project_data["title"],
            description=project_data["description"],
            category=project_data["category"],
            difficulty_level=project_data["difficulty_level"],
            status=project_data["status"],
            is_public=project_data["is_public"],
            tags=project_data["tags"],
            estimated_duration_hours=project_data["estimated_duration_hours"],
            price=project_data["price"],
            discount_percentage=project_data["discount_percentage"],
            requirements=project_data["requirements"],
            learning_objectives=project_data["learning_objectives"],
            target_audience=project_data["target_audience"],
            language=project_data["language"],
            completion_certificate=project_data["completion_certificate"],
            featured=project_data["featured"],
            owner_id=owner.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            rating=4.5 + (i * 0.1),  # Ratings variados
            total_ratings=50 + (i * 10),
            total_students=100 + (i * 50)
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        created_projects.append(project)
        
        print(f"✅ Projeto criado: {project_data['title']}")
        print(f"   Categoria: {project_data['category']}")
        print(f"   Proprietário: {owner.full_name}")
    
    return created_projects


def create_database_tables():
    """Criar todas as tabelas do banco de dados"""
    print("🔧 Criando tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")


def main():
    """Função principal do script"""
    print("🚀 Iniciando script de inicialização de dados...")
    print(f"📋 Ambiente: {settings.ENVIRONMENT}")
    print(f"💾 Database URL: {settings.DATABASE_URL}")
    print("=" * 60)
    
    # Criar tabelas
    create_database_tables()
    
    # Inicializar sessão do banco
    db = SessionLocal()
    
    try:
        # Criar usuário administrador
        print("\n👤 Criando usuário administrador...")
        admin_user = create_admin_user(db)
        
        # Criar usuários de exemplo
        print("\n👥 Criando usuários de exemplo...")
        sample_users = create_sample_users(db)
        
        # Criar projetos de exemplo
        print("\n📚 Criando projetos de exemplo...")
        all_users = [admin_user] + sample_users
        sample_projects = create_sample_projects(db, all_users)
        
        print("\n" + "=" * 60)
        print("✅ Inicialização concluída com sucesso!")
        print(f"📊 Estatísticas:")
        print(f"   • Usuários criados: {len(all_users)}")
        print(f"   • Projetos criados: {len(sample_projects)}")
        print(f"   • Projetos publicados: {len([p for p in sample_projects if p.status == ProjectStatus.PUBLISHED])}")
        print(f"   • Projetos em destaque: {len([p for p in sample_projects if p.featured])}")
        
        print("\n🔐 Credenciais de acesso:")
        print("   Admin:")
        print("     Username: admin")
        print("     Email: admin@tecnocursos.ai")
        print("     Senha: TecnoCursos2024!")
        
        print(f"\n🌐 Acesse a aplicação em: http://localhost:{settings.PORT}")
        print(f"📖 Documentação da API: http://localhost:{settings.PORT}/docs")
        
    except Exception as e:
        print(f"❌ Erro durante a inicialização: {str(e)}")
        db.rollback()
        return 1
    
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 