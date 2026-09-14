from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime

from auth import validators

class UserCreate(BaseModel):
    """회원가입 시 요청받을 데이터"""
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        return validators.validate_username(v)
    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validators.validate_password(v)

class UserLogin(BaseModel):
    """로그인 시 요청받을 데이터"""
    username: str
    password: str

class UserResponse(BaseModel):
    """응답으로 내려줄 데이터 (비밀번호 제외)"""
    id: int
    username: str
    created_at: datetime

    # SQLAlchemy 모델(ORM)을 Pydantic 모델로 변환할 수 있도록 설정
    model_config = ConfigDict(from_attributes=True) # Pydantic v2 표준 방식

class Token(BaseModel):
    access_token: str
    refresh_token: str  # 추가
    token_type: str = "bearer"

# 토큰 디코딩 후 payload 검증용 (선택이지만 흔히 씀)
class TokenData(BaseModel):
    username: Optional[str] = None

# 채팅 메시지 요청 데이터 구조
    # min_length, max_length: 최소 및 최대 길이 검증
    # Field는 pydantic V2에서 권장하는 방식 (Field(제약조건, ...))
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000) # 메시지는 비어있지 않아야 함

# 채팅 내역 반환 데이터 구조
class ChatResponse(BaseModel):
    id: int
    user_message: str # 유저가 보낸 메시지
    ai_response: Optional[str] = None # ai가 생성한 응답 
    error_status: Optional[str] = None # 에러 발생시 에러 상태 코드
    created_at: datetime # 생성 시각

    model_config = ConfigDict(from_attributes=True)
