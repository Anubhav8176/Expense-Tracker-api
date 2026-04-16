from core.config import settings
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Annotated
from fastapi import Depends,HTTPException
from sqlmodel import Session
import uuid

from db.User import User
from db.session import get_db


secret_key = settings.SECRET_KEY
algorithm = settings.ALGORITHM
access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str)->str:
	return pwd_context.hash(password)
	
def verify_password(plain: str, hashed: str)->bool:
	return pwd_context.verify(plain, hashed)

	
def create_access_token(user_id: str)->str:
	payload = {
		"user_id": user_id,
		"exp":  datetime.now(timezone.utc)+timedelta(minutes=access_token_expire_minutes),
		"type": "access_token"
	}
	return jwt.encode(payload, secret_key, algorithm=algorithm)
	
def create_refresh_token(user_id: str):
	payload = {
		"user_id": user_id,
		"exp": datetime.now(timezone.utc)+timedelta(days=refresh_token_expire_days),
		"type": "refresh_token"
	}
	return jwt.encode(payload, secret_key, algorithm=algorithm)
	
def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
	session: Annotated[Session, Depends(get_db)]
) -> User:
	try:
		token_data = jwt.decode(token, secret_key, algorithms=[algorithm])
		user_id = token_data.get("user_id")
		if user_id is not None:
			user =  session.query(User).filter(User.id == uuid.UUID(user_id)).first()
			if user is not None:
				return user
			else:
				raise HTTPException(status_code=404, detail="User not found with token!")
		else:
			raise HTTPException(status_code=401, detail="Invalid token, no user id found!")
	except JWTError:
		raise HTTPException(status_code=401, detail="Invalid token!")