from ninja import Schema
from pydantic import EmailStr
from typing import List, Optional
from datetime import datetime
class LoginSchema(Schema):
    username: str
    password1: str
    password2: str
    email: EmailStr

class SigninSchema(Schema):
    username: str
    password: str

class UserSchema(Schema):
    id:int
    username: str

class UserPro(Schema):
    id: int
    username: str
    email: EmailStr
    

class PostSchema(Schema):
    title: str
    content: str
    author: str
    tags: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    likes: Optional[int] = 0

    class Config:
        orm_mode = True

class CommentSchema(Schema):
    post_id: int
    content: str
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class TagSchema(Schema):
    name: str

    class Config:
        orm_mode = True

class CategorySchema(Schema):
    name: str

    class Config:
        orm_mode = True

class LikeSchema(Schema):
    post_id: int

    class Config:
        orm_mode = True

class SearchSchema(Schema):
    query: str

    class Config:
        orm_mode = True
