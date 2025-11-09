from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app import models, schemas, db
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register")
def register(user: schemas.UserCreate, database: Session = Depends(db.get_db)):
    # ✅ Check password length before hashing
    if len(user.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password error: password cannot be longer than 72 bytes. Please use a shorter password."
        )

    # ✅ Hash password safely
    hashed_pw = pwd_context.hash(user.password)

    # ✅ Create new user
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    database.add(new_user)
    database.commit()
    database.refresh(new_user)

    return {"message": "User registered successfully", "username": new_user.username}


@router.post("/login")
def login(user: schemas.UserLogin, database: Session = Depends(db.get_db)):
    # ✅ Retrieve user
    db_user = database.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Login successful", "username": db_user.username}
