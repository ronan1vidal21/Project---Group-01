from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# =========================
# USER SCHEMAS
# =========================
class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    username: str
    password: str


class UserLogin(BaseModel):
    password: str
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    points: int

    class Config:
        from_attributes = True


# =========================
# ACTION TYPE SCHEMAS
# =========================
class ActionTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class ActionTypeCreate(ActionTypeBase):
    pass


class ActionTypeOut(ActionTypeBase):
    id: int

    model_config = {
        "from_attributes": True
    }


# =========================
# ACTION LOG SCHEMAS
# =========================
class LogActionBase(BaseModel):
    user_id: int
    action_name: str
    points: int


class ActionLogRequest(BaseModel):
    username: str
    action_name: str
    quantity: float

class LogActionCreate(LogActionBase):
    pass


class LogActionOut(LogActionBase):
    id: int
    username: Optional[str] = None
    action_name: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


# =========================
# LEADERBOARD SCHEMAS
# =========================
class LeaderboardEntry(BaseModel):
    username: str
    total_points: int

    model_config = {
        "from_attributes": True
    }


# ---------------------
# LOG ACTION SCHEMAS
# ---------------------
class LogActionIn(BaseModel):
    user_id: int
    action_type_id: int
    quantity: int


class LogActionOut(BaseModel):
    id: int
    user_id: int
    action_type_id: int
    quantity: int
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }
