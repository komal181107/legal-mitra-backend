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

        # =========================================
        # RAG DOCUMENT CONTEXT
        # =========================================

        context_parts = []

        for i, doc in enumerate(laws):

            source = doc.metadata.get(
                "source",
                "Unknown"
            )

            page = doc.metadata.get(
                "page",
                "Unknown"
            )

            context_parts.append(
                f"""
DOCUMENT {i + 1}

SOURCE FILE:
{source}

PAGE:
{page}

CONTENT:
{doc.page_content}
"""
            )

        context = "\n".join(context_parts)

        # =========================================
        # DEBUG
        # =========================================

        print("\n========================================")
        print("CONTEXT SENT TO LLM")
        print("========================================")
        print(context[:8000])
        print("========================================")

        # =========================================
        # PROMPT
        # =========================================

        prompt = f"""
You are Legal Mitra, a legal information assistant.

Answer the user's question ONLY using the legal documents provided below.

STRICT RULES:

1. Answer only from the provided legal context.
2. Do not invent any legal fact.
3. Do not invent section numbers.
4. Do not invent punishments.
5. Do not use outside knowledge.
6. Give a complete and clear answer to the user's question.
7. Use simple English.
8. Do not mention that you are an AI.
9. Do not write "Source 1", "Source 2", etc.
10. Do not write the source or page in the middle of the answer.
11. At the VERY END, write exactly ONE source line in this format:

Source: FILE_NAME | Page: PAGE_NUMBER

12. Choose the source and page that most directly supports your answer.
13. If multiple retrieved documents exist, choose only the most relevant one for the final source line.
14. If the answer is not available in the provided legal documents, say:

I could not find this information in the provided legal documents.

USER QUESTION:

{question}

LEGAL DOCUMENT CONTEXT:

{context}

Now answer the question clearly and completely.

Remember:
- Answer first.
- Source line must be LAST.
- Only ONE source/page line.
"""

        # =========================================
        # OPENROUTER
        # =========================================

        response = self.client.chat.completions.create(

            model="openai/gpt-oss-20b:free",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content

        # =========================================
        # CLEAN ANSWER
        # =========================================

        answer = answer.strip()

        print("\n========================================")
        print("LLM ANSWER")
        print("========================================")
        print(answer)
        print("========================================")

        return answer