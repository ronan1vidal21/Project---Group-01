from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    points = Column(Integer, default=0)

    # Link to ActionType
    actions = relationship("ActionType", back_populates="user")
    challenges = relationship("ChallengeProgress", back_populates="user")



class ActionType(Base):
    __tablename__ = "action_types"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_name = Column(String)
    points = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="actions")


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    goal = Column(Integer, nullable=False)
    reward_points = Column(Integer, nullable=False)

    progress_records = relationship("ChallengeProgress", back_populates="challenge")


class ChallengeProgress(Base):
    __tablename__ = "challenge_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    progress = Column(Integer, default=0)

    user = relationship("User", back_populates="challenges")
    challenge = relationship("Challenge", back_populates="progress_records")
