"""Add scenes and assets tables

Revision ID: 003_add_scenes_assets
Revises: 002_add_audio_table
Create Date: 2025-01-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003_add_scenes_assets'
down_revision = '002_add_audio_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Migração para adicionar as tabelas de cenas e assets
    Suporte para múltiplas cenas por projeto e múltiplos assets por cena
    """
    
    # Criar tabela scenes
    op.create_table('scenes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('texto', sa.Text(), nullable=True),
        sa.Column('duracao', sa.Float(), nullable=False),
        sa.Column('background_color', sa.String(7), nullable=True),
        sa.Column('background_type', sa.String(50), nullable=True),
        sa.Column('background_config', sa.Text(), nullable=True),
        sa.Column('transition_in', sa.String(50), nullable=True),
        sa.Column('transition_out', sa.String(50), nullable=True),
        sa.Column('transition_duration', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices para a tabela scenes
    op.create_index(op.f('ix_scenes_id'), 'scenes', ['id'], unique=False)
    op.create_index(op.f('ix_scenes_uuid'), 'scenes', ['uuid'], unique=True)
    op.create_index(op.f('ix_scenes_project_id'), 'scenes', ['project_id'], unique=False)
    op.create_index(op.f('ix_scenes_ordem'), 'scenes', ['ordem'], unique=False)
    
    # Criar tabela assets
    op.create_table('assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('caminho_arquivo', sa.String(500), nullable=True),
        sa.Column('url_external', sa.String(500), nullable=True),
        
        # Posicionamento e transformações
        sa.Column('posicao_x', sa.Float(), nullable=True),
        sa.Column('posicao_y', sa.Float(), nullable=True),
        sa.Column('escala', sa.Float(), nullable=True),
        sa.Column('rotacao', sa.Float(), nullable=True),
        sa.Column('opacidade', sa.Float(), nullable=True),
        sa.Column('camada', sa.Integer(), nullable=True),
        
        # Dimensões
        sa.Column('largura', sa.Float(), nullable=True),
        sa.Column('altura', sa.Float(), nullable=True),
        
        # Configurações específicas
        sa.Column('config_json', sa.Text(), nullable=True),
        
        # Para assets de áudio
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('loop', sa.Boolean(), nullable=True),
        sa.Column('fade_in', sa.Float(), nullable=True),
        sa.Column('fade_out', sa.Float(), nullable=True),
        
        # Para assets de texto
        sa.Column('texto_conteudo', sa.Text(), nullable=True),
        sa.Column('fonte_familia', sa.String(100), nullable=True),
        sa.Column('fonte_tamanho', sa.Float(), nullable=True),
        sa.Column('fonte_cor', sa.String(7), nullable=True),
        sa.Column('texto_alinhamento', sa.String(20), nullable=True),
        
        # Para assets de animação
        sa.Column('animacao_tipo', sa.String(50), nullable=True),
        sa.Column('animacao_duracao', sa.Float(), nullable=True),
        sa.Column('animacao_delay', sa.Float(), nullable=True),
        sa.Column('animacao_config', sa.Text(), nullable=True),
        
        # Status e metadados
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices para a tabela assets
    op.create_index(op.f('ix_assets_id'), 'assets', ['id'], unique=False)
    op.create_index(op.f('ix_assets_uuid'), 'assets', ['uuid'], unique=True)
    op.create_index(op.f('ix_assets_scene_id'), 'assets', ['scene_id'], unique=False)
    op.create_index(op.f('ix_assets_tipo'), 'assets', ['tipo'], unique=False)
    op.create_index(op.f('ix_assets_camada'), 'assets', ['camada'], unique=False)
    
    print("✅ Tabelas 'scenes' e 'assets' criadas com sucesso!")
    print("📝 Suporte para múltiplas cenas por projeto implementado")
    print("🎨 Suporte para múltiplos assets por cena implementado")


def downgrade() -> None:
    """
    Reverter a migração removendo as tabelas scenes e assets
    """
    
    # Remover índices da tabela assets
    op.drop_index(op.f('ix_assets_camada'), table_name='assets')
    op.drop_index(op.f('ix_assets_tipo'), table_name='assets')
    op.drop_index(op.f('ix_assets_scene_id'), table_name='assets')
    op.drop_index(op.f('ix_assets_uuid'), table_name='assets')
    op.drop_index(op.f('ix_assets_id'), table_name='assets')
    
    # Remover tabela assets
    op.drop_table('assets')
    
    # Remover índices da tabela scenes
    op.drop_index(op.f('ix_scenes_ordem'), table_name='scenes')
    op.drop_index(op.f('ix_scenes_project_id'), table_name='scenes')
    op.drop_index(op.f('ix_scenes_uuid'), table_name='scenes')
    op.drop_index(op.f('ix_scenes_id'), table_name='scenes')
    
    # Remover tabela scenes
    op.drop_table('scenes')
    
    print("❌ Tabelas 'scenes' e 'assets' removidas") 