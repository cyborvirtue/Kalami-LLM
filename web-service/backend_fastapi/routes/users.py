from fastapi import APIRouter, Depends, HTTPException, status, UploadedFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import base64
from datetime import datetime, timedelta

from database import get_db
import models
import schemas
from main import create_access_token, get_password_hash, verify_password, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        from jose import jwt, JWTError
        from main import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.Users).filter(models.Users.Username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# 登录
@router.post("/login", response_model=schemas.StandardResponse)
async def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.Username, form_data.Password)
    if not user:
        return {"status": 0, "message": "Incorrect username or password"}
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.Username}, expires_delta=access_token_expires
    )
    
    return {
        "status": 1,
        "message": "Login successful.",
        "data": {
            "user": {
                "UserID": user.UserID,
                "Username": user.Username,
                "Role": user.Role,
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    }

# 注册
@router.post("/signup", response_model=schemas.StandardResponse)
async def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    db_user = db.query(models.Users).filter(models.Users.Username == user_data.Username).first()
    if db_user:
        return {"status": 0, "message": "Username already registered"}
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.Password)
    new_user = models.Users(
        Username=user_data.Username,
        Password=hashed_password,
        Role="user",
        Avatar="/avatar.png"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"status": 1, "message": "User created successfully"}

# 获取用户信息
@router.get("/getuser", response_model=schemas.StandardResponse)
async def get_user(current_user: models.Users = Depends(get_current_user)):
    return {
        "status": 1,
        "data": {
            "UserID": current_user.UserID,
            "Username": current_user.Username,
            "Role": current_user.Role,
            "Avatar": current_user.Avatar
        }
    }

# 更新头像
@router.post("/updateavatar", response_model=schemas.StandardResponse)
async def update_avatar(avatar: str = Form(...), current_user: models.Users = Depends(get_current_user), db: Session = Depends(get_db)):
    # 更新用户头像
    current_user.Avatar = avatar
    db.commit()
    
    return {"status": 1, "message": "Avatar updated successfully"}

# 获取学生信息
@router.get("/getstudent/{student_id}", response_model=schemas.StandardResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Students).filter(models.Students.StudentID == student_id).first()
    if not student:
        return {"status": 0, "message": "Student not found"}
    
    return {
        "status": 1,
        "data": {
            "StudentID": student.StudentID,
            "Name": student.Name,
            "Major": student.Major,
            "EnrollmentYear": student.EnrollmentYear
        }
    }

# 获取所有学生
@router.get("/getallstudents", response_model=schemas.StandardResponse)
async def get_all_students(db: Session = Depends(get_db)):
    students = db.query(models.Students).all()
    
    return {
        "status": 1,
        "data": [
            {
                "StudentID": student.StudentID,
                "Name": student.Name,
                "Major": student.Major,
                "EnrollmentYear": student.EnrollmentYear
            } for student in students
        ]
    }