from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import time
import hashlib
import base64
import hmac
import websockets
import asyncio
import uuid

from database import get_db
import models
import schemas
from routes.users import get_current_user
from main import APPID, APIKEY, APISECRET, SPARK_API

router = APIRouter(prefix="/api", tags=["conversations"])

# 生成请求参数
def generate_request_parameters(question, conversation_id):
    # 生成RFC1123格式的时间戳
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    # 拼接字符串
    signature_origin = f"host: spark-api.xf-yun.com\ndate: {date}\nGET /v3.1/chat HTTP/1.1"
    # 进行hmac-sha256进行加密
    signature_sha = hmac.new(APISECRET.encode('utf-8'), signature_origin.encode('utf-8'),
                           digestmod=hashlib.sha256).digest()
    signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = f'api_key="{APIKEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    
    # 请求参数
    params = {
        'authorization': authorization,
        'date': date,
        'host': 'spark-api.xf-yun.com'
    }
    
    # 构建请求体
    data = {
        "header": {
            "app_id": APPID,
            "uid": str(uuid.uuid4())
        },
        "parameter": {
            "chat": {
                "domain": "generalv3.1",
                "temperature": 0.5,
                "max_tokens": 2048
            }
        },
        "payload": {
            "message": {
                "text": [{
                    "role": "user",
                    "content": question
                }]
            }
        }
    }
    
    return params, data

# 聊天机器人
@router.post("/chat", response_model=schemas.StandardResponse)
async def chatbot(
    question: str = Form(...),
    conversation_id: int = Form(None),
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 如果没有提供对话ID，创建新的对话
    if not conversation_id:
        new_conversation = models.Conversations(
            UserID=current_user.UserID,
            StartedAt=datetime.now(),
            Status="active"
        )
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        conversation_id = new_conversation.ConversationID
    else:
        # 检查对话是否存在且属于当前用户
        conversation = db.query(models.Conversations).filter(
            models.Conversations.ConversationID == conversation_id,
            models.Conversations.UserID == current_user.UserID
        ).first()
        if not conversation:
            return {"status": 0, "message": "Conversation not found or not authorized"}
    
    # 保存用户消息
    user_message = models.Messages(
        ConversationID=conversation_id,
        Sender="user",
        Content=question,
        Timestamp=datetime.now()
    )
    db.add(user_message)
    db.commit()
    
    try:
        # 生成请求参数
        params, data = generate_request_parameters(question, conversation_id)
        
        # 调用讯飞星火大模型API
        async with websockets.connect(f"{SPARK_API}?{params}") as websocket:
            await websocket.send(json.dumps(data))
            response_text = ""
            
            while True:
                response = await websocket.recv()
                response_json = json.loads(response)
                code = response_json["header"]["code"]
                
                if code != 0:
                    return {"status": 0, "message": f"Error: {response_json}"}
                
                choices = response_json["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                response_text += content
                
                if status == 2:
                    break
        
        # 保存机器人回复
        bot_message = models.Messages(
            ConversationID=conversation_id,
            Sender="bot",
            Content=response_text,
            Timestamp=datetime.now()
        )
        db.add(bot_message)
        db.commit()
        
        return {
            "status": 1,
            "data": {
                "ConversationID": conversation_id,
                "Answer": response_text
            }
        }
    except Exception as e:
        return {"status": 0, "message": f"Error: {str(e)}"}

# 获取对话记录
@router.get("/addonversation", response_model=schemas.StandardResponse)
async def get_conversations(
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 获取用户的所有对话
    conversations = db.query(models.Conversations).filter(
        models.Conversations.UserID == current_user.UserID
    ).order_by(desc(models.Conversations.StartedAt)).all()
    
    result = []
    for conversation in conversations:
        # 获取对话中的消息
        messages = db.query(models.Messages).filter(
            models.Messages.ConversationID == conversation.ConversationID
        ).order_by(models.Messages.Timestamp).all()
        
        message_list = []
        for message in messages:
            message_list.append({
                "MessageID": message.MessageID,
                "Sender": message.Sender,
                "Content": message.Content,
                "Timestamp": message.Timestamp
            })
        
        result.append({
            "ConversationID": conversation.ConversationID,
            "StartedAt": conversation.StartedAt,
            "EndedAt": conversation.EndedAt,
            "Status": conversation.Status,
            "Messages": message_list
        })
    
    return {
        "status": 1,
        "data": result
    }

# 获取单个对话记录
@router.get("/addonversation/{conversation_id}", response_model=schemas.StandardResponse)
async def get_conversation(
    conversation_id: int,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查对话是否存在且属于当前用户
    conversation = db.query(models.Conversations).filter(
        models.Conversations.ConversationID == conversation_id,
        models.Conversations.UserID == current_user.UserID
    ).first()
    
    if not conversation:
        return {"status": 0, "message": "Conversation not found or not authorized"}
    
    # 获取对话中的消息
    messages = db.query(models.Messages).filter(
        models.Messages.ConversationID == conversation_id
    ).order_by(models.Messages.Timestamp).all()
    
    message_list = []
    for message in messages:
        message_list.append({
            "MessageID": message.MessageID,
            "Sender": message.Sender,
            "Content": message.Content,
            "Timestamp": message.Timestamp
        })
    
    return {
        "status": 1,
        "data": {
            "ConversationID": conversation.ConversationID,
            "StartedAt": conversation.StartedAt,
            "EndedAt": conversation.EndedAt,
            "Status": conversation.Status,
            "Messages": message_list
        }
    }