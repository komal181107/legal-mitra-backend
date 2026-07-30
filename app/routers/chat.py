from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies import get_current_user
from app.models import User, ChatHistory, Conversation
from app.schemas.chat_schema import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.chat_service import ChatService


router = APIRouter()

chat_service = ChatService()


# =========================================
# CHAT
# =========================================

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    answer = chat_service.generate_response(
        request.question,
        current_user.id
    )

    return ChatResponse(answer=answer)


# =========================================
# CHAT HISTORY
# =========================================


@router.get("/chat/history", response_model=list[ChatHistoryResponse])
def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        chats = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.user_id == current_user.id
            )
            .order_by(ChatHistory.created_at.desc())
            .all()
        )

        result = []

        for chat in chats:
            result.append({
                "id": chat.id,
                "question": chat.question or "",
                "answer": chat.answer or "",
                "created_at": chat.created_at
            })

        return result

    finally:
        db.close()


# =========================================
# ALL CONVERSATIONS
# =========================================

@router.get("/conversations")
def get_conversations(
    current_user: User = Depends(get_current_user)
):
    db: Session = SessionLocal()

    try:
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == current_user.id
            )
            .order_by(Conversation.created_at.desc())
            .all()
        )

        return [
            {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at
            }
            for conversation in conversations
        ]

    finally:
        db.close()


# =========================================
# SINGLE CONVERSATION HISTORY
# =========================================

@router.get("/conversations/{conversation_id}")
def get_conversation_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    db: Session = SessionLocal()

    try:
        history = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.conversation_id == conversation_id,
                ChatHistory.user_id == current_user.id
            )
            .order_by(ChatHistory.created_at.asc())
            .all()
        )

        return [
            {
                "id": chat.id,
                "question": chat.question,
                "answer": chat.answer,
                "created_at": chat.created_at
            }
            for chat in history
        ]

    finally:
        db.close()


# =========================================
# UPDATE CHAT
# =========================================

@router.put("/chat-history/{chat_id}")
def update_chat_history(
    chat_id: int,
    question: str,
    answer: str,
    current_user: User = Depends(get_current_user)
):
    db: Session = SessionLocal()

    try:
        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.id == chat_id,
                ChatHistory.user_id == current_user.id
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat history not found"
            )

        chat.question = question
        chat.answer = answer

        db.commit()
        db.refresh(chat)

        return {
            "message": "Chat history updated successfully",
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer
        }

    finally:
        db.close()


# =========================================
# DELETE CHAT
# =========================================

@router.get(
    "/chat/history",
    response_model=list[ChatHistoryResponse]
)
def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        chats = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.user_id == current_user.id
            )
            .order_by(ChatHistory.created_at.desc())
            .all()
        )

        result = []

        for chat in chats:
            result.append({
                "id": chat.id,
                "question": chat.question or "",
                "answer": chat.answer or "",
                "created_at": chat.created_at
            })

        return result

    finally:
        db.close()