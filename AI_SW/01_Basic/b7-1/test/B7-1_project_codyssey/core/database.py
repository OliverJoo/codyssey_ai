from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

# SQLite 데이터베이스 엔진 생성
# check_same_thread=False는 FastAPI가 멀티스레드 환경에서 SQLite를 안전하게 사용하도록 설정합니다.
engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)

# 데이터베이스 세션을 생성하는 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델(테이블)이 상속받을 기본 클래스
Base = declarative_base()

def get_db():
    """
    요청(Request)당 하나의 독립적인 데이터베이스 세션을 생성하고,
    요청이 끝나면 세션을 안전하게 닫아주는 의존성(Dependency) 함수입니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
