from fastapi import FastAPI, Depends, HTTPException, status, UploadedFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import json
import time
import uuid
import hashlib
import base64
import requests
import websockets
import asyncio
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# 导入数据库模型和工具
from database import engine, SessionLocal, Base
import models
import schemas

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(title="科研学习助手API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT设置
SECRET_KEY = "your_secret_key"  # 生产环境中应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 讯飞星火大模型API配置
APPID = "d900ec04"
APIKEY = "a0cfd3a9e05b9d8aaa9cad33112e047a"
APISECRET = "ZjE5NmJlNjQwOTg3YzA2ZGZiNzAxYWVh"
SPARK_API = "wss://spark-api.xf-yun.com/v3.1/chat"

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 获取密码哈希
def get_password_hash(password):
    return pwd_context.hash(password)

# 验证用户
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.Users).filter(models.Users.Username == username).first()
    if not user:
        return False
    if not verify_password(password, user.Password):
        return False
    return user

# 包含路由模块
from routes import users, articles, videos, conversations, website_visits

# 注册路由
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(videos.router)
app.include_router(conversations.router)
app.include_router(website_visits.router)

# 根路由
@app.get("/")
def read_root():
    return {"message": "Welcome to Research Learning Assistant API"}

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)