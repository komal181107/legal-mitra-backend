
from openai import OpenAI
from app.config import OPENROUTER_API_KEY


class GeminiService:

    def __init__(self):
        print("Creating GeminiService...")

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        print("GeminiService ready.")

    def generate_answer(self, question: str, laws):

        # Build context from retrieved legal documents
        context_parts = []

        for i, doc in enumerate(laws):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")

            context_parts.append(
                f"""
DOCUMENT {i + 1}
SOURCE FILE: {source}
PAGE: {page}
CONTENT:
{doc.page_content}
"""
            )

        context = "\n".join(context_parts)

        print("\n========== CONTEXT SENT TO LLM ==========")
        print(context[:8000])
        print("=========================================")

        # Keep the prompt inside generate_answer()
        prompt = f"""
You are Legal Mitra, a helpful legal information assistant for people in India.

Explain legal information in simple English and give practical next steps.

RULES:
1. Use the provided legal documents as the primary source.
2. Never invent laws, section numbers, penalties, deadlines, or procedures.
3. Answer the user's actual question directly.
4. For practical problems, explain the possible legal meaning and next steps when supported by the context.
5. Distinguish possible cheating from a simple delivery or contract dispute only when the facts and documents support it.
6. Do not claim a civil case is the only remedy unless the documents establish that.
7. Do not guarantee refunds, complaints, or any legal outcome.
8. If the documents do not answer the question fully, clearly explain the limitation instead of guessing.
9. Legal conclusions may depend on the specific facts.
10. Do not mention that you are an AI.
11. Keep the answer concise and useful.
12. End with exactly one source line:
Source: FILE_NAME | Page: PAGE_NUMBER
13. Use the actual source filename and page from the context. Do not invent them.

USER QUESTION:
{question}

LEGAL DOCUMENT CONTEXT:
{context}

Write the answer now. Put the answer first and the single source line last.
"""

        # Call OpenRouter
        response = self.client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content or ""
        answer = answer.strip()

        print("\n========== LLM ANSWER ==========")
        print(answer)
        print("================================")

        return answer
