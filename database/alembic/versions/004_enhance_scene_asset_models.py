"""Enhanced Scene and Asset Models

Revision ID: 004_enhance_scene_asset_models
Revises: 003_add_scenes_assets
Create Date: 2025-01-17 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_enhance_scene_asset_models'
down_revision = '003_add_scenes_assets'
branch_labels = None
depends_on = None


def upgrade():
    """Add enhanced fields to Scene and Asset models and create new tables."""
    
    # === Enhance Scene table ===
    with op.batch_alter_table('scenes', schema=None) as batch_op:
        # Template and style
        batch_op.add_column(sa.Column('template_id', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('template_version', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('style_preset', sa.String(50), nullable=True, default='default'))
        
        # Layout and composition
        batch_op.add_column(sa.Column('background_asset_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('layout_type', sa.String(50), nullable=True, default='free'))
        batch_op.add_column(sa.Column('layout_config', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('aspect_ratio', sa.String(10), nullable=True, default='16:9'))
        batch_op.add_column(sa.Column('resolution', sa.String(20), nullable=True, default='1920x1080'))
        
        # Enhanced transitions
        batch_op.add_column(sa.Column('transition_config', sa.Text(), nullable=True))
        
        # Audio configuration
        batch_op.add_column(sa.Column('audio_track_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('background_music_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('audio_volume', sa.Float(), nullable=True, default=1.0))
        batch_op.add_column(sa.Column('music_volume', sa.Float(), nullable=True, default=0.3))
        
        # Animation configuration
        batch_op.add_column(sa.Column('animation_preset', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('animation_config', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('entrance_animation', sa.String(50), nullable=True, default='none'))
        batch_op.add_column(sa.Column('exit_animation', sa.String(50), nullable=True, default='none'))
        
        # Versioning and collaboration
        batch_op.add_column(sa.Column('version', sa.Integer(), nullable=True, default=1))
        batch_op.add_column(sa.Column('parent_scene_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_template', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('is_public_template', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_modified_by', sa.Integer(), nullable=True))
        
        # Enhanced metadata
        batch_op.add_column(sa.Column('is_locked', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('tags', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('custom_properties', sa.Text(), nullable=True))
        
        # Analytics
        batch_op.add_column(sa.Column('view_count', sa.Integer(), nullable=True, default=0))
        batch_op.add_column(sa.Column('render_count', sa.Integer(), nullable=True, default=0))
        batch_op.add_column(sa.Column('last_rendered', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('render_time_avg', sa.Float(), nullable=True))
        
        # Foreign keys
        batch_op.create_foreign_key('fk_scenes_audio_track', 'audios', ['audio_track_id'], ['id'])
        batch_op.create_foreign_key('fk_scenes_background_music', 'assets', ['background_music_id'], ['id'])
        batch_op.create_foreign_key('fk_scenes_created_by', 'users', ['created_by'], ['id'])
        batch_op.create_foreign_key('fk_scenes_last_modified_by', 'users', ['last_modified_by'], ['id'])
        batch_op.create_foreign_key('fk_scenes_parent_scene', 'scenes', ['parent_scene_id'], ['id'])
        batch_op.create_foreign_key('fk_scenes_background_asset', 'assets', ['background_asset_id'], ['id'])

    # === Enhance Asset table ===
    with op.batch_alter_table('assets', schema=None) as batch_op:
        # Make scene_id nullable for library assets
        batch_op.alter_column('scene_id', nullable=True)
        
        # Project relationship for library assets
        batch_op.add_column(sa.Column('project_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('subtipo', sa.String(50), nullable=True))
        
        # File and resource metadata
        batch_op.add_column(sa.Column('file_size', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('file_hash', sa.String(64), nullable=True))
        batch_op.add_column(sa.Column('mime_type', sa.String(100), nullable=True))
        
        # Library functionality
        batch_op.add_column(sa.Column('is_library_asset', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('is_public', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('is_premium', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('library_category', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('library_tags', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('license_type', sa.String(50), nullable=True, default='standard'))
        
        # File metadata
        batch_op.add_column(sa.Column('width', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('height', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('format', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('color_profile', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('metadata_json', sa.Text(), nullable=True))
        
        # Enhanced audio features
        batch_op.add_column(sa.Column('start_time', sa.Float(), nullable=True, default=0.0))
        batch_op.add_column(sa.Column('end_time', sa.Float(), nullable=True))
        
        # Enhanced text features
        batch_op.add_column(sa.Column('fonte_peso', sa.String(20), nullable=True, default='normal'))
        batch_op.add_column(sa.Column('fonte_estilo', sa.String(20), nullable=True, default='normal'))
        batch_op.add_column(sa.Column('linha_altura', sa.Float(), nullable=True, default=1.2))
        batch_op.add_column(sa.Column('letra_espacamento', sa.Float(), nullable=True, default=0.0))
        
        # Image/video features
        batch_op.add_column(sa.Column('crop_x', sa.Float(), nullable=True, default=0.0))
        batch_op.add_column(sa.Column('crop_y', sa.Float(), nullable=True, default=0.0))
        batch_op.add_column(sa.Column('crop_width', sa.Float(), nullable=True, default=1.0))
        batch_op.add_column(sa.Column('crop_height', sa.Float(), nullable=True, default=1.0))
        batch_op.add_column(sa.Column('filters', sa.Text(), nullable=True))
        
        # Enhanced animation
        batch_op.add_column(sa.Column('animacao_loop', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('easing_function', sa.String(50), nullable=True, default='ease'))
        
        # Timeline features
        batch_op.add_column(sa.Column('timeline_start', sa.Float(), nullable=True, default=0.0))
        batch_op.add_column(sa.Column('timeline_end', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('timeline_locked', sa.Boolean(), nullable=True, default=False))
        
        # Versioning and collaboration
        batch_op.add_column(sa.Column('version', sa.Integer(), nullable=True, default=1))
        batch_op.add_column(sa.Column('parent_asset_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_modified_by', sa.Integer(), nullable=True))
        
        # Enhanced metadata
        batch_op.add_column(sa.Column('is_favorite', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('custom_properties', sa.Text(), nullable=True))
        
        # Analytics
        batch_op.add_column(sa.Column('usage_count', sa.Integer(), nullable=True, default=0))
        batch_op.add_column(sa.Column('download_count', sa.Integer(), nullable=True, default=0))
        batch_op.add_column(sa.Column('rating_avg', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('rating_count', sa.Integer(), nullable=True, default=0))
        
        # Processing
        batch_op.add_column(sa.Column('processing_status', sa.String(50), nullable=True, default='ready'))
        batch_op.add_column(sa.Column('processing_progress', sa.Float(), nullable=True, default=100.0))
        batch_op.add_column(sa.Column('optimized_variants', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('thumbnail_path', sa.String(500), nullable=True))
        
        # Foreign keys
        batch_op.create_foreign_key('fk_assets_project', 'projects', ['project_id'], ['id'])
        batch_op.create_foreign_key('fk_assets_created_by', 'users', ['created_by'], ['id'])
        batch_op.create_foreign_key('fk_assets_last_modified_by', 'users', ['last_modified_by'], ['id'])
        batch_op.create_foreign_key('fk_assets_parent_asset', 'assets', ['parent_asset_id'], ['id'])

    # === Create SceneTemplate table ===
    op.create_table('scene_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('style', sa.String(50), nullable=False),
        sa.Column('aspect_ratio', sa.String(10), nullable=True),
        sa.Column('resolution', sa.String(20), nullable=True),
        sa.Column('background_type', sa.String(50), nullable=True),
        sa.Column('background_config', sa.Text(), nullable=True),
        sa.Column('layout_type', sa.String(50), nullable=True),
        sa.Column('layout_config', sa.Text(), nullable=True),
        sa.Column('template_data', sa.Text(), nullable=False),
        sa.Column('default_assets', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('rating_avg', sa.Float(), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_scene_templates_id'), 'scene_templates', ['id'], unique=False)
    op.create_index(op.f('ix_scene_templates_uuid'), 'scene_templates', ['uuid'], unique=True)

    # === Create AssetRating table ===
    op.create_table('asset_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_ratings_id'), 'asset_ratings', ['id'], unique=False)

    # === Create SceneComment table ===
    op.create_table('scene_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('comment_type', sa.String(50), nullable=True),
        sa.Column('position_x', sa.Float(), nullable=True),
        sa.Column('position_y', sa.Float(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True),
        sa.Column('is_important', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['scene_comments.id'], ),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_scene_comments_id'), 'scene_comments', ['id'], unique=False)
    op.create_index(op.f('ix_scene_comments_uuid'), 'scene_comments', ['uuid'], unique=True)


def downgrade():
    """Remove enhanced fields and new tables."""
    
    # Drop new tables
    op.drop_table('scene_comments')
    op.drop_table('asset_ratings')
    op.drop_table('scene_templates')
    
    # Remove columns from assets table
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.drop_constraint('fk_assets_parent_asset', type_='foreignkey')
        batch_op.drop_constraint('fk_assets_last_modified_by', type_='foreignkey')
        batch_op.drop_constraint('fk_assets_created_by', type_='foreignkey')
        batch_op.drop_constraint('fk_assets_project', type_='foreignkey')
        
        batch_op.drop_column('thumbnail_path')
        batch_op.drop_column('optimized_variants')
        batch_op.drop_column('processing_progress')
        batch_op.drop_column('processing_status')
        batch_op.drop_column('rating_count')
        batch_op.drop_column('rating_avg')
        batch_op.drop_column('download_count')
        batch_op.drop_column('usage_count')
        batch_op.drop_column('custom_properties')
        batch_op.drop_column('is_favorite')
        batch_op.drop_column('last_modified_by')
        batch_op.drop_column('created_by')
        batch_op.drop_column('parent_asset_id')
        batch_op.drop_column('version')
        batch_op.drop_column('timeline_locked')
        batch_op.drop_column('timeline_end')
        batch_op.drop_column('timeline_start')
        batch_op.drop_column('easing_function')
        batch_op.drop_column('animacao_loop')
        batch_op.drop_column('filters')
        batch_op.drop_column('crop_height')
        batch_op.drop_column('crop_width')
        batch_op.drop_column('crop_y')
        batch_op.drop_column('crop_x')
        batch_op.drop_column('letra_espacamento')
        batch_op.drop_column('linha_altura')
        batch_op.drop_column('fonte_estilo')
        batch_op.drop_column('fonte_peso')
        batch_op.drop_column('end_time')
        batch_op.drop_column('start_time')
        batch_op.drop_column('metadata_json')
        batch_op.drop_column('color_profile')
        batch_op.drop_column('format')
        batch_op.drop_column('duration')
        batch_op.drop_column('height')
        batch_op.drop_column('width')
        batch_op.drop_column('license_type')
        batch_op.drop_column('library_tags')
        batch_op.drop_column('library_category')
        batch_op.drop_column('is_premium')
        batch_op.drop_column('is_public')
        batch_op.drop_column('is_library_asset')
        batch_op.drop_column('mime_type')
        batch_op.drop_column('file_hash')
        batch_op.drop_column('file_size')
        batch_op.drop_column('subtipo')
        batch_op.drop_column('description')
        batch_op.drop_column('project_id')
        
        batch_op.alter_column('scene_id', nullable=False)
    
    # Remove columns from scenes table
    with op.batch_alter_table('scenes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_scenes_background_asset', type_='foreignkey')
        batch_op.drop_constraint('fk_scenes_parent_scene', type_='foreignkey')
        batch_op.drop_constraint('fk_scenes_last_modified_by', type_='foreignkey')
        batch_op.drop_constraint('fk_scenes_created_by', type_='foreignkey')
        batch_op.drop_constraint('fk_scenes_background_music', type_='foreignkey')
        batch_op.drop_constraint('fk_scenes_audio_track', type_='foreignkey')
        
        batch_op.drop_column('render_time_avg')
        batch_op.drop_column('last_rendered')
        batch_op.drop_column('render_count')
        batch_op.drop_column('view_count')
        batch_op.drop_column('custom_properties')
        batch_op.drop_column('tags')
        batch_op.drop_column('is_locked')
        batch_op.drop_column('last_modified_by')
        batch_op.drop_column('created_by')
        batch_op.drop_column('is_public_template')
        batch_op.drop_column('is_template')
        batch_op.drop_column('parent_scene_id')
        batch_op.drop_column('version')
        batch_op.drop_column('exit_animation')
        batch_op.drop_column('entrance_animation')
        batch_op.drop_column('animation_config')
        batch_op.drop_column('animation_preset')
        batch_op.drop_column('music_volume')
        batch_op.drop_column('audio_volume')
        batch_op.drop_column('background_music_id')
        batch_op.drop_column('audio_track_id')
        batch_op.drop_column('transition_config')
        batch_op.drop_column('resolution')
        batch_op.drop_column('aspect_ratio')
        batch_op.drop_column('layout_config')
        batch_op.drop_column('layout_type')
        batch_op.drop_column('background_asset_id')
        batch_op.drop_column('style_preset')
        batch_op.drop_column('template_version')
        batch_op.drop_column('template_id') 