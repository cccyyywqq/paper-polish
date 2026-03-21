from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.user import User, UserPolishHistory
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token, HistoryCreate, HistoryResponse
from ..utils.auth import hash_password, verify_password, create_access_token, get_current_user
from ..utils import logger

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"User registered: {user.username}")
    return user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    logger.info(f"User logged in: {user.username}")

    return {"access_token": token}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.execute(select(User).where(User.id == int(current_user["sub"])))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/history", response_model=HistoryResponse)
async def save_history(
    history_data: HistoryCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    history = UserPolishHistory(
        user_id=int(current_user["sub"]),
        original_text=history_data.original_text,
        polished_text=history_data.polished_text,
        operation_type=history_data.operation_type,
        style=history_data.style,
    )
    db.add(history)
    await db.commit()
    await db.refresh(history)

    return history


@router.get("/history", response_model=list[HistoryResponse])
async def get_history(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.execute(
        select(UserPolishHistory)
        .where(UserPolishHistory.user_id == int(current_user["sub"]))
        .order_by(UserPolishHistory.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()
