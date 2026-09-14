from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    """사용자 계정 정보를 저장하는 테이블 모델"""
    __tablename__ = "users"

    # 고유 식별자 (PK)
    id = Column(Integer, primary_key=True, index=True)
    # 로그인 아이디
    username = Column(String(50), unique=True, index=True, nullable=False)
    # 암호화된 비밀번호
    hashed_password = Column(String, nullable=False)
    # 계정 생성 시간 (DB 서버 시간 기준 자동 생성)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatLog(Base):
    """사용자와 AI 간의 대화 기록을 저장하는 테이블 모델"""
    __tablename__ = "chat_logs"

    # 고유 식별자 (PK)
    id = Column(Integer, primary_key=True, index=True)
    # 대화를 작성한 사용자의 ID (FK)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # 사용자가 입력한 질문
    user_message = Column(Text, nullable=False)
    # AI가 생성한 응답 내용
    ai_response = Column(Text, nullable=True)
    # API 호출 실패나 타임아웃 발생 시의 에러 코드
    error_status = Column(String, nullable=True)
    # 대화 생성 시간 (DB 서버 시간 기준 자동 생성)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
