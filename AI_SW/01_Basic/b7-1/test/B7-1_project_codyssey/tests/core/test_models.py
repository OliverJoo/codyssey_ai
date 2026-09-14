from core.models import User
from sqlalchemy import Column, Integer, String, DateTime

def test_user_model_attributes():
    assert hasattr(User, "id")
    assert hasattr(User, "username")
    assert hasattr(User, "hashed_password")
    assert hasattr(User, "created_at")
    assert User.__tablename__ == "users"

from core.models import ChatLog

def test_chatlog_model_attributes():
    assert hasattr(ChatLog, "id")
    assert hasattr(ChatLog, "user_id")
    assert hasattr(ChatLog, "user_message")
    assert hasattr(ChatLog, "ai_response")
    assert hasattr(ChatLog, "error_status")
    assert hasattr(ChatLog, "created_at")
    assert ChatLog.__tablename__ == "chat_logs"
