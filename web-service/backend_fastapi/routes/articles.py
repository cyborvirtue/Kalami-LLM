from fastapi import APIRouter, Depends, HTTPException, status, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas
from routes.users import get_current_user

router = APIRouter(prefix="/api", tags=["articles"])

# 获取文章列表
@router.get("/getarticle", response_model=schemas.StandardResponse)
async def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 计算偏移量
    skip = (page - 1) * page_size
    
    # 查询文章
    articles = db.query(models.Articles)\
        .order_by(desc(models.Articles.PublishedAt))\
        .offset(skip)\
        .limit(page_size)\
        .all()
    
    # 查询作者信息
    result = []
    for article in articles:
        author = db.query(models.Users).filter(models.Users.UserID == article.AuthorID).first()
        author_name = author.Username if author else "Unknown"
        
        result.append({
            "ArticleID": article.ArticleID,
            "Title": article.Title,
            "Content": article.Content,
            "AuthorID": article.AuthorID,
            "AuthorName": author_name,
            "PublishedAt": article.PublishedAt,
            "UpdatedAt": article.UpdatedAt,
            "ViewCount": article.ViewCount,
            "LikeCount": article.LikeCount
        })
    
    return {
        "status": 1,
        "data": result
    }

# 获取单篇文章
@router.get("/getarticle/{article_id}", response_model=schemas.StandardResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Articles).filter(models.Articles.ArticleID == article_id).first()
    if not article:
        return {"status": 0, "message": "Article not found"}
    
    author = db.query(models.Users).filter(models.Users.UserID == article.AuthorID).first()
    author_name = author.Username if author else "Unknown"
    
    return {
        "status": 1,
        "data": {
            "ArticleID": article.ArticleID,
            "Title": article.Title,
            "Content": article.Content,
            "AuthorID": article.AuthorID,
            "AuthorName": author_name,
            "PublishedAt": article.PublishedAt,
            "UpdatedAt": article.UpdatedAt,
            "ViewCount": article.ViewCount,
            "LikeCount": article.LikeCount
        }
    }

# 添加文章
@router.post("/addarticle", response_model=schemas.StandardResponse)
async def add_article(
    article: schemas.ArticleCreate,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 创建新文章
    new_article = models.Articles(
        Title=article.Title,
        Content=article.Content,
        AuthorID=current_user.UserID,
        PublishedAt=datetime.now(),
        UpdatedAt=datetime.now(),
        ViewCount=0,
        LikeCount=0
    )
    
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    return {
        "status": 1,
        "message": "Article added successfully",
        "data": {
            "ArticleID": new_article.ArticleID
        }
    }

# 删除文章
@router.post("/deletearticle", response_model=schemas.StandardResponse)
async def delete_article(
    article_id: int = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    article = db.query(models.Articles).filter(models.Articles.ArticleID == article_id).first()
    if not article:
        return {"status": 0, "message": "Article not found"}
    
    # 检查是否是文章作者或管理员
    if article.AuthorID != current_user.UserID and current_user.Role != "admin":
        return {"status": 0, "message": "Permission denied"}
    
    # 删除文章相关的评论和点赞
    db.query(models.ArticleComments).filter(models.ArticleComments.ArticleID == article_id).delete()
    db.query(models.ArticleLikes).filter(models.ArticleLikes.ArticleID == article_id).delete()
    
    # 删除文章
    db.delete(article)
    db.commit()
    
    return {"status": 1, "message": "Article deleted successfully"}

# 增加文章访问量
@router.post("/viewarticle", response_model=schemas.StandardResponse)
async def view_article(
    article_id: int = Form(...),
    db: Session = Depends(get_db)
):
    article = db.query(models.Articles).filter(models.Articles.ArticleID == article_id).first()
    if not article:
        return {"status": 0, "message": "Article not found"}
    
    # 增加访问量
    article.ViewCount += 1
    db.commit()
    
    return {"status": 1, "message": "View count increased"}

# 喜欢文章
@router.post("/likearticle", response_model=schemas.StandardResponse)
async def like_article(
    article_id: int = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    article = db.query(models.Articles).filter(models.Articles.ArticleID == article_id).first()
    if not article:
        return {"status": 0, "message": "Article not found"}
    
    # 检查是否已经点赞
    existing_like = db.query(models.ArticleLikes).filter(
        models.ArticleLikes.ArticleID == article_id,
        models.ArticleLikes.UserID == current_user.UserID
    ).first()
    
    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        article.LikeCount = max(0, article.LikeCount - 1)  # 确保不会小于0
        db.commit()
        return {"status": 1, "message": "Article unliked successfully"}
    else:
        # 添加点赞
        new_like = models.ArticleLikes(
            ArticleID=article_id,
            UserID=current_user.UserID,
            CreatedAt=datetime.now()
        )
        article.LikeCount += 1
        db.add(new_like)
        db.commit()
        return {"status": 1, "message": "Article liked successfully"}

# 获取文章点赞数
@router.get("/likenumarticle/{article_id}", response_model=schemas.StandardResponse)
async def get_article_like_count(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Articles).filter(models.Articles.ArticleID == article_id).first()
    if not article:
        return {"status": 0, "message": "Article not found"}
    
    return {
        "status": 1,
        "data": {
            "LikeCount": article.LikeCount
        }
    }

# 获取用户是否点赞文章
@router.get("/getlikearticle/{article_id}", response_model=schemas.StandardResponse)
async def get_user_like_article(
    article_id: int,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    like = db.query(models.ArticleLikes).filter(
        models.ArticleLikes.ArticleID == article_id,
        models.ArticleLikes.UserID == current_user.UserID
    ).first()
    
    return {
        "status": 1,
        "data": {
            "isLiked": like is not None
        }
    }

# 评论文章
@router.post("/commentarticle", response_model=schemas.StandardResponse)
async def comment_article(
    article_id: int = Form(...),
    content: str = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    article = db.query(models.Articles).filter(models.Articles.ArticleID == article_id).first()
    if not article:
        return {"status": 0, "message": "Article not found"}
    
    # 创建评论
    new_comment = models.ArticleComments(
        ArticleID=article_id,
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

# 获取文章评论
@router.get("/showcommentarticle/{article_id}", response_model=schemas.StandardResponse)
async def get_article_comments(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Articles).filter(models.Articles.ArticleID == article_id).first()
    if not article:
        return {"status": 0, "message": "Article not found"}
    
    comments = db.query(models.ArticleComments).filter(
        models.ArticleComments.ArticleID == article_id
    ).order_by(desc(models.ArticleComments.CreatedAt)).all()
    
    result = []
    for comment in comments:
        user = db.query(models.Users).filter(models.Users.UserID == comment.UserID).first()
        username = user.Username if user else "Unknown"
        
        result.append({
            "CommentID": comment.CommentID,
            "ArticleID": comment.ArticleID,
            "UserID": comment.UserID,
            "Username": username,
            "Content": comment.Content,
            "CreatedAt": comment.CreatedAt
        })
    
    return {
        "status": 1,
        "data": result
    }

# 删除文章评论
@router.post("/deletecommentarticle", response_model=schemas.StandardResponse)
async def delete_article_comment(
    comment_id: int = Form(...),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(models.ArticleComments).filter(models.ArticleComments.CommentID == comment_id).first()
    if not comment:
        return {"status": 0, "message": "Comment not found"}
    
    # 检查是否是评论作者或管理员
    if comment.UserID != current_user.UserID and current_user.Role != "admin":
        return {"status": 0, "message": "Permission denied"}
    
    # 删除评论
    db.delete(comment)
    db.commit()
    
    return {"status": 1, "message": "Comment deleted successfully"}

# 获取文章页数
@router.get("/getarticlepagecount", response_model=schemas.StandardResponse)
async def get_article_page_count(
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 获取文章总数
    total_articles = db.query(models.Articles).count()
    
    # 计算总页数
    total_pages = (total_articles + page_size - 1) // page_size
    
    return {
        "status": 1,
        "data": {
            "TotalPages": total_pages
        }
    }

# 获取文章总数
@router.get("/getarticletotal", response_model=schemas.StandardResponse)
async def get_article_total(db: Session = Depends(get_db)):
    # 获取文章总数
    total_articles = db.query(models.Articles).count()
    
    return {
        "status": 1,
        "data": {
            "TotalArticles": total_articles
        }
    }