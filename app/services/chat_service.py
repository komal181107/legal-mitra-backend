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

    def generate_response(self, question: str, user_id: int):

        print("\n========================================")
        print("CHAT SERVICE")
        print("========================================")

        print("Question:", question)

        # RAG
        laws = self.rag_service.search_laws(question)

        print("Retrieved documents:", len(laws))

        # LLM
        answer = self.gemini_service.generate_answer(
            question,
            laws
        )

        # Database
        db = SessionLocal()

        try:

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

            print("Chat history saved successfully.")

        finally:
            db.close()

        print("========================================\n")

        return answer

        print("\n========================================")
        print("CHAT SERVICE")
        print("========================================")

        print("Question:", question)

        # -----------------------------------------
        # STEP 1: Search relevant laws
        # -----------------------------------------

        laws = self.rag_service.search_laws(question)

        print("Retrieved documents:", len(laws))

        # -----------------------------------------
        # STEP 2: Send laws to LLM
        # -----------------------------------------

        answer = self.gemini_service.generate_answer(
            question,
            laws
        )



                # =========================================
        # SOURCE + PAGE INFORMATION
        # =========================================

        sources = []

        for doc in laws:

            source = doc.metadata.get(
                "source",
                "Unknown"
            )

            page = doc.metadata.get(
                "page",
                "Unknown"
            )

            if isinstance(page, int):
                page = page + 1

            source_name = str(source).split("\\")[-1]

            source_info = (
                f"Source: {source_name} | Page: {page}"
            )

            if source_info not in sources:
                sources.append(source_info)

        if sources:
            answer += "\n\nSources:\n"

            for source in sources:
                answer += f"- {source}\n"



        # -----------------------------------------
        # STEP 3: Save conversation
        # -----------------------------------------

        db = SessionLocal()

        try:

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

            print("Chat history saved successfully.")

        except Exception as e:

            db.rollback()

            print("Database error:", e)

            raise

        finally:

            db.close()

        print("========================================\n")

        # IMPORTANT:
        # return answer MUST be inside generate_response()
        return answer