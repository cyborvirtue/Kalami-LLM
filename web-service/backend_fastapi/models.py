from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Users(Base):
    __tablename__ = "Users"

    UserID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Username = Column(String(255), unique=True, index=True, nullable=False)
    Password = Column(String(255), nullable=False)
    Role = Column(String(50), nullable=True)
    Avatar = Column(String(255), default="/avatar.png")
    CreatedAt = Column(DateTime, default=datetime.now)

    # 关系
    articles = relationship("Articles", back_populates="author")
    article_comments = relationship("ArticleComments", back_populates="user")
    article_likes = relationship("ArticleLikes", back_populates="user")
    videos = relationship("Videos", back_populates="author")
    video_comments = relationship("VideoComments", back_populates="user")
    video_likes = relationship("VideoLikes", back_populates="user")
    conversations = relationship("Conversations", back_populates="user")

class Articles(Base):
    __tablename__ = "Articles"

    ArticleID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Title = Column(String(255), nullable=False)
    Content = Column(Text, nullable=False)
    AuthorID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    PublishedAt = Column(DateTime, default=datetime.now)
    UpdatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    ViewCount = Column(Integer, default=0)
    LikeCount = Column(Integer, default=0)

    # 关系
    author = relationship("Users", back_populates="articles")
    comments = relationship("ArticleComments", back_populates="article")
    likes = relationship("ArticleLikes", back_populates="article")

class ArticleComments(Base):
    __tablename__ = "ArticleComments"

    CommentID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ArticleID = Column(Integer, ForeignKey("Articles.ArticleID"), nullable=False)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    Content = Column(Text, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.now)

    # 关系
    article = relationship("Articles", back_populates="comments")
    user = relationship("Users", back_populates="article_comments")

class ArticleLikes(Base):
    __tablename__ = "ArticleLikes"

    LikeID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ArticleID = Column(Integer, ForeignKey("Articles.ArticleID"), nullable=False)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.now)

    # 关系
    article = relationship("Articles", back_populates="likes")
    user = relationship("Users", back_populates="article_likes")

class Videos(Base):
    __tablename__ = "Videos"

    VideoID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Title = Column(String(255), nullable=False)
    Description = Column(Text, nullable=True)
    URL = Column(String(255), nullable=False)
    ThumbnailURL = Column(String(255), nullable=True)
    AuthorID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    PublishedAt = Column(DateTime, default=datetime.now)
    UpdatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    ViewCount = Column(Integer, default=0)
    LikeCount = Column(Integer, default=0)

    # 关系
    author = relationship("Users", back_populates="videos")
    comments = relationship("VideoComments", back_populates="video")
    likes = relationship("VideoLikes", back_populates="video")

class VideoComments(Base):
    __tablename__ = "VideoComments"

    CommentID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    VideoID = Column(Integer, ForeignKey("Videos.VideoID"), nullable=False)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    Content = Column(Text, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.now)

    # 关系
    video = relationship("Videos", back_populates="comments")
    user = relationship("Users", back_populates="video_comments")

class VideoLikes(Base):
    __tablename__ = "VideoLikes"

    LikeID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    VideoID = Column(Integer, ForeignKey("Videos.VideoID"), nullable=False)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.now)

    # 关系
    video = relationship("Videos", back_populates="likes")
    user = relationship("Users", back_populates="video_likes")

class Conversations(Base):
    __tablename__ = "Conversations"

    ConversationID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    StartedAt = Column(DateTime, default=datetime.now)
    EndedAt = Column(DateTime, nullable=True)
    Status = Column(String(50), default="active")

    # 关系
    user = relationship("Users", back_populates="conversations")
    messages = relationship("Messages", back_populates="conversation")

class Messages(Base):
    __tablename__ = "Messages"

    MessageID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ConversationID = Column(Integer, ForeignKey("Conversations.ConversationID"), nullable=False)
    Sender = Column(String(50), nullable=False)  # 'user' or 'bot'
    Content = Column(Text, nullable=False)
    Timestamp = Column(DateTime, default=datetime.now)

    # 关系
    conversation = relationship("Conversations", back_populates="messages")

class WebsiteVisits(Base):
    __tablename__ = "WebsiteVisits"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    VisitCount = Column(Integer, default=0)

class Students(Base):
    __tablename__ = "Students"

    StudentID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(255), nullable=False)
    Major = Column(String(255), nullable=True)
    EnrollmentYear = Column(Integer, nullable=True)
    CreatedAt = Column(DateTime, default=datetime.now)