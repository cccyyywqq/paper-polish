from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.user import User, UserPolishHistory
from ..schemas.user import UserCreate, UserLogin, HistoryCreate
from ..schemas.response import UserResponse, TokenResponse, HistoryItemResponse, HistoryListResponse
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
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"User registered: {user.username}")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    logger.info(f"User logged in: {user.username}")

    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    result = await db.execute(select(User).where(User.id == int(current_user["sub"])))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/history", response_model=HistoryItemResponse)
async def save_history(
    history_data: HistoryCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

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

    return HistoryItemResponse(
        id=history.id,
        original_text=history.original_text,
        polished_text=history.polished_text,
        operation_type=history.operation_type,
        style=history.style,
        created_at=history.created_at,
    )


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    result = await db.execute(
        select(UserPolishHistory)
        .where(UserPolishHistory.user_id == int(current_user["sub"]))
        .order_by(UserPolishHistory.created_at.desc())
        .limit(50)
    )
    items = result.scalars().all()

    return HistoryListResponse(
        data=[
            HistoryItemResponse(
                id=item.id,
                original_text=item.original_text,
                polished_text=item.polished_text,
                operation_type=item.operation_type,
                style=item.style,
                created_at=item.created_at,
            )
            for item in items
        ]
    )
