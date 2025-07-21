"""Add audio table

Revision ID: 002_add_audio_table
Revises: 001_initial_migration
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers
revision = '002_add_audio_table'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Criar tabela de áudios/narrações"""
    
    # Criar tabela audios
    op.create_table('audios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        
        # Propriedades do áudio
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('format', sa.String(length=10), nullable=False, default='mp3'),
        sa.Column('bitrate', sa.String(length=20), nullable=True),
        sa.Column('sample_rate', sa.Integer(), nullable=True),
        
        # Conteúdo processado
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('text_length', sa.Integer(), nullable=True),
        
        # Configurações de TTS
        sa.Column('tts_provider', sa.String(length=50), nullable=False, default='bark'),
        sa.Column('voice_type', sa.String(length=50), nullable=False, default='v2/pt_speaker_0'),
        sa.Column('voice_config', sa.Text(), nullable=True),
        
        # Status da geração
        sa.Column('status', sa.String(length=50), nullable=False, default='queued'),
        sa.Column('generation_progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('error_message', sa.Text(), nullable=True),
        
        # Métricas de processamento
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('cache_hit', sa.Boolean(), nullable=False, default=False),
        
        # Relacionamentos
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_file_id', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Estatísticas
        sa.Column('download_count', sa.Integer(), nullable=False, default=0),
        sa.Column('play_count', sa.Integer(), nullable=False, default=0),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['source_file_id'], ['file_uploads.id'], ),
    )
    
    # Criar índices para performance
    op.create_index('ix_audios_uuid', 'audios', ['uuid'], unique=True)
    op.create_index('ix_audios_user_id', 'audios', ['user_id'])
    op.create_index('ix_audios_status', 'audios', ['status'])
    op.create_index('ix_audios_created_at', 'audios', ['created_at'])
    op.create_index('ix_audios_tts_provider', 'audios', ['tts_provider'])


def downgrade() -> None:
    """Remover tabela de áudios"""
    
    # Remover índices
    op.drop_index('ix_audios_tts_provider', table_name='audios')
    op.drop_index('ix_audios_created_at', table_name='audios')
    op.drop_index('ix_audios_status', table_name='audios')
    op.drop_index('ix_audios_user_id', table_name='audios')
    op.drop_index('ix_audios_uuid', table_name='audios')
    
    # Remover tabela
    op.drop_table('audios') 