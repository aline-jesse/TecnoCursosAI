from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TecnoCursosAI"
    DATABASE_URL: str = "sqlite:///./tecno_cursos.db"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
