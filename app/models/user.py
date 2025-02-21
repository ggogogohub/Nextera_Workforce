from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserInDB(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    full_name: str
    role: str = "employee"
