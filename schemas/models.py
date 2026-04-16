from pydantic import BaseModel


class UserCreate(BaseModel):
	name: str
	email: str
	password: str
	

class LoginRequest(BaseModel):
	email: str
	password: str
	

class AuthResponse(BaseModel):
	access_token: str
	refresh_token: str
	
class ExpenseCreate(BaseModel):
	title: str
	desc: str
	amount: float
	category: str
	type: str
	
	
class VerifyTokenRequest(BaseModel):
	refresh_token: str