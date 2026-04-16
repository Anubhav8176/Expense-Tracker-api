from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from core.authentication import create_access_token, create_refresh_token, hash_password, refresh_token_expire_days, verify_password
from db.RefreshToken import RefreshToken
from db.User import User
from db.session import get_db
from schemas.models import AuthResponse, LoginRequest, UserCreate

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db=Depends(get_db)) -> AuthResponse:
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered!")

    user_dict = user_create.model_dump()
    user_dict.pop("password")
    user_dict["hashed_password"] = hash_password(user_create.password)

    new_user = User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(str(new_user.id))
    refresh_token = create_refresh_token(str(new_user.id))

    new_token = RefreshToken(
        user_id=new_user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        is_revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=refresh_token_expire_days)
    )
    db.add(new_token)
    db.commit()

    return AuthResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login")
def login_user(login_request: LoginRequest, db=Depends(get_db)) -> AuthResponse:
    user = db.query(User).filter(User.email == login_request.email).first()

    if user is None:
        raise HTTPException(status_code=401, detail="No user found with the email!")

    is_password_valid = verify_password(plain=login_request.password, hashed=user.hashed_password)
    if not is_password_valid:
        raise HTTPException(status_code=401, detail="Credentials don't match!")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})

    new_token = RefreshToken(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        is_revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=refresh_token_expire_days)
    )
    db.add(new_token)
    db.commit()

    return AuthResponse(access_token=access_token, refresh_token=refresh_token)