"""聊天路由 - 使用 DeepSeek API"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.models.models import ChatHistory
from app.services.deepseek_service import deepseek_service

router = APIRouter(prefix="/api/chat", tags=["对话聊天"])


async def build_messages(session_id: str, db: AsyncSession, current_message: str) -> list:
    """构建消息历史"""
    from sqlalchemy import select
    from sqlalchemy import desc

    # 获取历史消息
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.session_id == session_id)
        .order_by(desc(ChatHistory.created_at))
        .limit(10)
    )
    history = result.scalars().all()

    # 构建消息列表
    messages = []

    # 系统提示
    messages.append({
        "role": "system",
        "content": "你是一名专业的医保审核助手，可以帮助用户了解医保政策、审核规则等相关问题。"
    })

    # 添加历史消息（按时间顺序）
    for msg in reversed(history):
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # 添加当前消息
    messages.append({
        "role": "user",
        "content": current_message
    })

    return messages


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """流式聊天接口 - 使用 DeepSeek API"""
    # 生成或复用会话ID
    session_id = request.session_id or str(uuid.uuid4())

    # 保存用户消息到本地数据库
    user_message = ChatHistory(
        session_id=session_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()

    # 构建消息历史
    messages = await build_messages(session_id, db, request.message)

    # 流式响应
    async def generate_response():
        assistant_content = []

        try:
            async for chunk in deepseek_service.chat_stream(
                messages=messages,
                temperature=0.7
            ):
                assistant_content.append(chunk)
                yield chunk

            # 保存助手消息到本地数据库
            assistant_message = ChatHistory(
                session_id=session_id,
                role="assistant",
                content="".join(assistant_content)
            )
            db.add(assistant_message)
            await db.commit()

        except Exception as e:
            yield f"\n[系统错误: {str(e)}]"

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "X-Session-Id": session_id
        }
    )


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """非流式聊天接口 - 使用 DeepSeek API"""
    # 生成或复用会话ID
    session_id = request.session_id or str(uuid.uuid4())

    # 保存用户消息
    user_message = ChatHistory(
        session_id=session_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()

    # 构建消息历史
    messages = await build_messages(session_id, db, request.message)

    try:
        response = await deepseek_service.chat(
            messages=messages,
            temperature=0.7,
            stream=False
        )

        answer = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        # 保存助手消息
        assistant_message = ChatHistory(
            session_id=session_id,
            role="assistant",
            content=answer
        )
        db.add(assistant_message)
        await db.commit()

        return ChatResponse(
            message=answer,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API 调用失败: {str(e)}")


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取聊天历史"""
    from sqlalchemy import select
    from sqlalchemy import desc

    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.session_id == session_id)
        .order_by(desc(ChatHistory.created_at))
        .offset(skip)
        .limit(limit)
    )
    messages = result.scalars().all()

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }


@router.get("/sessions")
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取会话列表"""
    from sqlalchemy import select, func

    last_message_time = func.max(ChatHistory.created_at)
    # 获取最近的会话
    result = await db.execute(
        select(
            ChatHistory.session_id,
            last_message_time.label("last_message_time"),
            func.count(ChatHistory.id).label("message_count")
        )
        .group_by(ChatHistory.session_id)
        .order_by(last_message_time.desc())
        .offset(skip)
        .limit(limit)
    )

    sessions = result.all()

    return {
        "total": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "last_message_time": s.last_message_time.isoformat() if s.last_message_time else None,
                "message_count": s.message_count
            }
            for s in sessions
        ]
    }
