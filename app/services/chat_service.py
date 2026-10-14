
from app.database import SessionLocal
from app.models import ChatHistory, Conversation
from app.services.rag_service import RAGService
from app.services.gemini_service import GeminiService


class ChatService:
    def __init__(self):
        print("Creating ChatService...")
        self.rag_service = RAGService()
        self.gemini_service = GeminiService()
        print("ChatService ready.")

    def generate_response(
        self,
        question: str,
        user_id: int,
        conversation_id: int | None = None
    ):
        laws = self.rag_service.search_laws(question)
        answer = self.gemini_service.generate_answer(question, laws)

        sources = []
        for doc in laws:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")

            if isinstance(page, int):
                page += 1

            source_name = str(source).replace("\\", "/").split("/")[-1]
            source_info = f"Source: {source_name} | Page: {page}"

            if source_info not in sources:
                sources.append(source_info)

        if sources:
            answer += "\n\nSources:\n" + "\n".join(
                f"- {source}" for source in sources
            )

        db = SessionLocal()
        try:
            if conversation_id is not None:
                conversation = (
                    db.query(Conversation)
                    .filter(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id
                    )
                    .first()
                )

                if not conversation:
                    raise ValueError("Conversation not found")

            else:
                conversation = Conversation(
                    user_id=user_id,
                    title=question[:30]
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            chat = ChatHistory(
                user_id=user_id,
                conversation_id=conversation.id,
                question=question,
                answer=answer
            )
            db.add(chat)
            db.commit()

            return {
                "answer": answer,
                "conversation_id": conversation.id
            }

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
