from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# 用户相关模型
class UserBase(BaseModel):
    Username: str

class UserCreate(UserBase):
    Password: str

class UserLogin(UserBase):
    Password: str

class UserUpdate(BaseModel):
    Avatar: Optional[str] = None

class UserResponse(UserBase):
    UserID: int
    Role: Optional[str] = None
    Avatar: Optional[str] = "/avatar.png"
    CreatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True

# 文章相关模型
class ArticleBase(BaseModel):
    Title: str
    Content: str

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    Title: Optional[str] = None
    Content: Optional[str] = None

class ArticleResponse(ArticleBase):
    ArticleID: int
    AuthorID: int
    PublishedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None
    ViewCount: Optional[int] = 0
    LikeCount: Optional[int] = 0

    class Config:
        orm_mode = True

# 文章评论相关模型
class ArticleCommentBase(BaseModel):
    Content: str

class ArticleCommentCreate(ArticleCommentBase):
    ArticleID: int

class ArticleCommentResponse(ArticleCommentBase):
    CommentID: int
    ArticleID: int
    UserID: int
    CreatedAt: Optional[datetime] = None
    Username: Optional[str] = None  # 用于返回用户名

    class Config:
        orm_mode = True

# 文章点赞相关模型
class ArticleLikeCreate(BaseModel):
    ArticleID: int

class ArticleLikeResponse(BaseModel):
    LikeID: int
    ArticleID: int
    UserID: int
    CreatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True

# 视频相关模型
class VideoBase(BaseModel):
    Title: str
    URL: str
    Description: Optional[str] = None
    ThumbnailURL: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    URL: Optional[str] = None
    ThumbnailURL: Optional[str] = None

class VideoResponse(VideoBase):
    VideoID: int
    AuthorID: int
    PublishedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None
    ViewCount: Optional[int] = 0
    LikeCount: Optional[int] = 0

    class Config:
        orm_mode = True

# 视频评论相关模型
class VideoCommentBase(BaseModel):
    Content: str

class VideoCommentCreate(VideoCommentBase):
    VideoID: int

class VideoCommentResponse(VideoCommentBase):
    CommentID: int
    VideoID: int
    UserID: int
    CreatedAt: Optional[datetime] = None
    Username: Optional[str] = None  # 用于返回用户名

    class Config:
        orm_mode = True

# 视频点赞相关模型
class VideoLikeCreate(BaseModel):
    VideoID: int

class VideoLikeResponse(BaseModel):
    LikeID: int
    VideoID: int
    UserID: int
    CreatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True

# 对话相关模型
class ConversationBase(BaseModel):
    pass

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(BaseModel):
    ConversationID: int
    UserID: int
    StartedAt: Optional[datetime] = None
    EndedAt: Optional[datetime] = None
    Status: Optional[str] = "active"

    class Config:
        orm_mode = True

# 消息相关模型
class MessageBase(BaseModel):
    Content: str

class MessageCreate(MessageBase):
    ConversationID: int
    Sender: str

class MessageResponse(MessageBase):
    MessageID: int
    ConversationID: int
    Sender: str
    Timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True

# 网站访问量相关模型
class WebsiteVisitResponse(BaseModel):
    ID: int
    VisitCount: int

    class Config:
        orm_mode = True

# 学生相关模型
class StudentBase(BaseModel):
    Name: str
    Major: Optional[str] = None
    EnrollmentYear: Optional[int] = None

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    StudentID: int
    CreatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True

# 通用响应模型
class StandardResponse(BaseModel):
    status: int
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# 令牌相关模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None