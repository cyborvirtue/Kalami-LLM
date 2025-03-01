from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api", tags=["website_visits"])

# 增加网站访问量
@router.post("/addwebviews", response_model=schemas.StandardResponse)
async def add_website_visits(db: Session = Depends(get_db)):
    # 获取网站访问记录
    visit = db.query(models.WebsiteVisits).first()
    
    if not visit:
        # 如果没有记录，创建新记录
        visit = models.WebsiteVisits(VisitCount=1)
        db.add(visit)
    else:
        # 增加访问量
        visit.VisitCount += 1
    
    db.commit()
    return {"status": 1}

# 获取网站访问量
@router.get("/getwebviews", response_model=schemas.StandardResponse)
async def get_website_visits(db: Session = Depends(get_db)):
    # 获取网站访问记录
    visit = db.query(models.WebsiteVisits).first()
    
    if not visit:
        # 如果没有记录，返回0
        return {"status": 1, "visitCount": 0}
    
    return {"status": 1, "visitCount": visit.VisitCount}