from fastapi import APIRouter, Depends, HTTPException, status, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas
from routes.users import get_current_user

router = APIRouter(prefix="/api", tags=["videos"])

# 获取视频列表
@router.get("/getvideo", response_model=schemas.StandardResponse)
async def get_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 计算偏移量
    skip = (page - 1) * page_size
    
    # 查询视频
    videos = db.query(models.Videos)\
        .order_by(desc(models.Videos.PublishedAt))\
        .offset(skip)\
        .limit(page_size)\
        .all()
    
    # 查询作者信息
    result = []
    for video in videos:
        author = db.query(models.Users).filter(models.Users.UserID == video.AuthorID).first()
        author_name = author.Username if author else "Unknown"
        
        result.append({
            "VideoID": video.VideoID,
            "Title": video.Title,
            "Description": video.Description,
            "URL": video.URL,
            "ThumbnailURL": video.ThumbnailURL,
            "AuthorID": video.AuthorID,
            "AuthorName": author_name,
            "PublishedAt": video.PublishedAt,
            "UpdatedAt": video.UpdatedAt,
            "ViewCount": video.ViewCount,
            "LikeCount": video.LikeCount
        })
    
    return {
        "status": 1,
        "data": result
    }

# 获取单个视频
@router.get("/getvideo/{video_id}", response_model=schemas.StandardResponse)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(models.Videos).filter(models.Videos.VideoID == video_id).first()
    if not video:
        return {"status": 0, "message": "Video not found"}
    
    author = db.query(models.Users).filter(models.Users.UserID == video.AuthorID).first()
    author_name = author.Username if author else "Unknown"
    
    return {
        "status": 1,
        "data": {
            "VideoID": video.VideoID,
            "Title": video.Title,
            "Description": video.Description,
            "URL": video.URL,
            "ThumbnailURL": video.ThumbnailURL,
            "AuthorID": video.AuthorID,
            "AuthorName": author_name,
            "PublishedAt": video.PublishedAt,
            "UpdatedAt": video.UpdatedAt,
            "ViewCount": video.ViewCount,
            "LikeCount": video.LikeCount
        }
    }

# 添加视频
@router.post("/addvideo", response_model=schemas.StandardResponse)
async def add_video(
    video: schemas.VideoCreate,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 创建新视频
    new_video = models.Videos(
        Title=video.Title,
        Description=video.Description,
        URL=video.URL,
        ThumbnailURL=video.ThumbnailURL,
        AuthorID=current_user.UserID,
        PublishedAt=datetime.now(),
        UpdatedAt=datetime.now(),
        ViewCount=0,
        LikeCount=0
    )
    
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    
    return {
        "status": 1,
        "message": "Video added successfully",
        "data": {
            "VideoID": new_video.VideoID
        }
    }

# 删除视频
@router.post("/deletevideo", response_model=schemas.StandardResponse)
async def delete_video(
    video_id: int = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(models.Videos).filter(models.Videos.VideoID == video_id).first()
    if not video:
        return {"status": 0, "message": "Video not found"}
    
    # 检查是否是视频作者或管理员
    if video.AuthorID != current_user.UserID and current_user.Role != "admin":
        return {"status": 0, "message": "Permission denied"}
    
    # 删除视频相关的评论和点赞
    db.query(models.VideoComments).filter(models.VideoComments.VideoID == video_id).delete()
    db.query(models.VideoLikes).filter(models.VideoLikes.VideoID == video_id).delete()
    
    # 删除视频
    db.delete(video)
    db.commit()
    
    return {"status": 1, "message": "Video deleted successfully"}

# 增加视频访问量
@router.post("/viewvideo", response_model=schemas.StandardResponse)
async def view_video(
    video_id: int = Form(...),
    db: Session = Depends(get_db)
):
    video = db.query(models.Videos).filter(models.Videos.VideoID == video_id).first()
    if not video:
        return {"status": 0, "message": "Video not found"}
    
    # 增加访问量
    video.ViewCount += 1
    db.commit()
    
    return {"status": 1, "message": "View count increased"}

# 喜欢视频
@router.post("/likevideo", response_model=schemas.StandardResponse)
async def like_video(
    video_id: int = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(models.Videos).filter(models.Videos.VideoID == video_id).first()
    if not video:
        return {"status": 0, "message": "Video not found"}
    
    # 检查是否已经点赞
    existing_like = db.query(models.VideoLikes).filter(
        models.VideoLikes.VideoID == video_id,
        models.VideoLikes.UserID == current_user.UserID
    ).first()
    
    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        video.LikeCount = max(0, video.LikeCount - 1)  # 确保不会小于0
        db.commit()
        return {"status": 1, "message": "Video unliked successfully"}
    else:
        # 添加点赞
        new_like = models.VideoLikes(
            VideoID=video_id,
            UserID=current_user.UserID,
            CreatedAt=datetime.now()
        )
        video.LikeCount += 1
        db.add(new_like)
        db.commit()
        return {"status": 1, "message": "Video liked successfully"}

# 获取视频点赞数
@router.get("/likenumvideo/{video_id}", response_model=schemas.StandardResponse)
async def get_video_like_count(video_id: int, db: Session = Depends(get_db)):
    video = db.query(models.Videos).filter(models.Videos.VideoID == video_id).first()
    if not video:
        return {"status": 0, "message": "Video not found"}
    
    return {
        "status": 1,
        "data": {
            "LikeCount": video.LikeCount
        }
    }

# 获取用户是否点赞视频
@router.get("/getlikevideo/{video_id}", response_model=schemas.StandardResponse)
async def get_user_like_video(
    video_id: int,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    like = db.query(models.VideoLikes).filter(
        models.VideoLikes.VideoID == video_id,
        models.VideoLikes.UserID == current_user.UserID
    ).first()
    
    return {
        "status": 1,
        "data": {
            "isLiked": like is not None
        }
    }

# 评论视频
@router.post("/commentvideo", response_model=schemas.StandardResponse)
async def comment_video(
    video_id: int = Form(...),
    content: str = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(models.Videos).filter(models.Videos.VideoID == video_id).first()
    if not video:
        return {"status": 0, "message": "Video not found"}
    
    # 创建评论
    new_comment = models.VideoComments(
        VideoID=video_id,
        UserID=current_user.UserID,
        Content=content,
        CreatedAt=datetime.now()
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {
        "status": 1,
        "message": "Comment added successfully",
        "data": {
            "CommentID": new_comment.CommentID
        }
    }

# 获取视频评论
@router.get("/showcommentvideo/{video_id}", response_model=schemas.StandardResponse)
async def get_video_comments(video_id: int, db: Session = Depends(get_db)):
    video = db.query(models.Videos).filter(models.Videos.VideoID == video_id).first()
    if not video:
        return {"status": 0, "message": "Video not found"}
    
    comments = db.query(models.VideoComments).filter(
        models.VideoComments.VideoID == video_id
    ).order_by(desc(models.VideoComments.CreatedAt)).all()
    
    result = []
    for comment in comments:
        user = db.query(models.Users).filter(models.Users.UserID == comment.UserID).first()
        username = user.Username if user else "Unknown"
        
        result.append({
            "CommentID": comment.CommentID,
            "VideoID": comment.VideoID,
            "UserID": comment.UserID,
            "Username": username,
            "Content": comment.Content,
            "CreatedAt": comment.CreatedAt
        })
    
    return {
        "status": 1,
        "data": result
    }

# 删除视频评论
@router.post("/deletecommentvideo", response_model=schemas.StandardResponse)
async def delete_video_comment(
    comment_id: int = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(models.VideoComments).filter(models.VideoComments.CommentID == comment_id).first()
    if not comment:
        return {"status": 0, "message": "Comment not found"}
    
    # 检查是否是评论作者或管理员
    if comment.UserID != current_user.UserID and current_user.Role != "admin":
        return {"status": 0, "message": "Permission denied"}
    
    # 删除评论
    db.delete(comment)
    db.commit()
    
    return {"status": 1, "message": "Comment deleted successfully"}

# 获取视频页数
@router.get("/getvideopagecount", response_model=schemas.StandardResponse)
async def get_video_page_count(
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 获取视频总数
    total_videos = db.query(models.Videos).count()
    
    # 计算总页数
    total_pages = (total_videos + page_size - 1) // page_size
    
    return {
        "status": 1,
        "data": {
            "TotalPages": total_pages
        }
    }

# 获取视频总数
@router.get("/getvideototal", response_model=schemas.StandardResponse)
async def get_video_total(db: Session = Depends(get_db)):
    # 获取视频总数
    total_videos = db.query(models.Videos).count()
    
    return {
        "status": 1,
        "data": {
            "TotalVideos": total_videos
        }
    }