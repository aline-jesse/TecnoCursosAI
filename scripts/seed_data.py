import os
from app.database import SessionLocal, Base, engine
from app.models import User, Project, Scene, Asset
from app.auth import get_password_hash

def run_seed():
    db = SessionLocal()
    # Usuário admin
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
    db.refresh(admin)
    # Projeto exemplo
    project = Project(
        name="Projeto Exemplo",
        description="Projeto de exemplo para seed",
        slug="projeto-exemplo",
        status="draft",
        owner_id=admin.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    # Cenas exemplo
    for i in range(3):
        scene = Scene(
            project_id=project.id,
            name=f"Cena {i+1}",
            ordem=i,
            texto=f"Texto da cena {i+1}",
            duracao=5.0,
            background_type="solid",
            background_config="{}",
            is_active=True
        )
        db.add(scene)
        db.commit()
        db.refresh(scene)
        # Asset exemplo
        asset = Asset(
            name=f"Asset Cena {i+1}",
            tipo="image",
            caminho_arquivo=f"/static/uploads/asset_cena_{i+1}.png",
            scene_id=scene.id,
            project_id=project.id,
            is_library_asset=False,
            is_public=False
        )
        db.add(asset)
        db.commit()
    db.close()

if __name__ == "__main__":
    print("Populando banco de dados com dados de exemplo...")
    Base.metadata.create_all(bind=engine)
    run_seed()
    print("Seed concluído com sucesso!")
