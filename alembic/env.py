"""
Configuração do Ambiente Alembic - TecnoCursosAI
Script de configuração para migrações de banco de dados
"""

import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importar modelos e configurações
from app.models import Base
from app.config import get_settings

# Configurações
settings = get_settings()

# Configuração do Alembic
config = context.config

# Sobrescrever URL do banco com configurações da aplicação
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpretar arquivo de configuração para logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados dos modelos para autogeneração
target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    """
    Função para filtrar objetos durante a migração
    
    Args:
        object: Objeto SQLAlchemy
        name: Nome do objeto
        type_: Tipo do objeto (table, column, etc.)
        reflected: Se foi refletido do banco
        compare_to: Objeto de comparação
    
    Returns:
        True se o objeto deve ser incluído
    """
    
    # Excluir tabelas temporárias
    if type_ == "table" and name.startswith("temp_"):
        return False
    
    # Excluir views (se houver)
    if type_ == "table" and name.endswith("_view"):
        return False
    
    return True

def get_url():
    """Obter URL do banco de dados"""
    return settings.database_url

def run_migrations_offline():
    """
    Executar migrações em modo 'offline'
    
    Configura o contexto apenas com URL, sem Engine.
    Útil para gerar scripts SQL sem conectar ao banco.
    """
    
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    Executar migrações em modo 'online'
    
    Cria Engine e associa conexão com contexto.
    """
    
    # Configuração do engine
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
            # Configurações específicas para MySQL
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()

def run_data_migrations():
    """
    Executar migrações de dados (seeds)
    Função customizada para popular dados iniciais
    """
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import User, UserStatus
    
    # Criar engine e sessão
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        try:
            # Verificar se já existem usuários
            user_count = session.query(User).count()
            
            if user_count == 0:
                # Criar usuário administrador padrão
                admin_user = User(
                    name="Administrador",
                    email="admin@tecnocursosai.com",
                    is_active=True,
                    status=UserStatus.ACTIVE,
                    company="TecnoCursosAI"
                )
                
                session.add(admin_user)
                session.commit()
                
                print("✅ Usuário administrador criado")
            else:
                print("ℹ️ Dados iniciais já existem")
                
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao executar migração de dados: {e}")
            raise

# Função principal para determinar modo de execução
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 