from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead)
def register(data: UserCreate, session: Session = Depends(get_session)):
    # 檢查使用者是否存在
    statement = select(User).where(User.username == data.username)
    existing = session.exec(statement).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=data.username,
        hashed_password=hash_password(data.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):

    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"user_id": user.id})

    return {"access_token": token, "token_type": "bearer"}

@router.get("/protected")
def protected_route(user: User = Depends(get_current_user)):
    return {"msg": f"Hello {user.username}, you accessed a protected route!"}