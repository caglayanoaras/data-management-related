from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    # Later: DATABASE_URL = "mssql+pyodbc://user:pass@host/dbname?driver=ODBC+Driver+17+for+SQL+Server"
    ENV: str = "development"
    SECRET_KEY: str = "development-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    COOKIE_NAME: str = "access_token"
    COOKIE_MAX_AGE: int = 60 * 60 * 24 * 1  # 1 days in seconds
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "strict"
    
    class Config:
        env_file = ".env"

settings = Settings()