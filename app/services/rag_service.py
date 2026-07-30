from pathlib import Path
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


class RAGService:

    def __init__(self):

        base_dir = Path(__file__).resolve().parents[2]

        self.docs_path = base_dir / "data" / "legal_docs"
        self.index_path = base_dir / "data" / "faiss_index"

        # =========================================
        # EMBEDDINGS
        # =========================================

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # =========================================
        # LOAD EXISTING FAISS INDEX
        # =========================================

        if self.index_path.exists():

            print("Loading existing FAISS index...")

            self.vectorstore = FAISS.load_local(
                str(self.index_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            print("FAISS INDEX LOADED SUCCESSFULLY")

        else:

            self.create_index()

    # =========================================
    # CREATE FAISS INDEX
    # =========================================

    def create_index(self):

        print("Creating FAISS index...")

        documents = []

        for pdf_file in self.docs_path.glob("*.pdf"):

            print("PDF FOUND:", pdf_file)

            loader = PyPDFLoader(str(pdf_file))

            pdf_documents = loader.load()

            print("PAGES LOADED:", len(pdf_documents))

            documents.extend(pdf_documents)

        print("TOTAL DOCUMENTS:", len(documents))

        # =========================================
        # SPLIT DOCUMENTS
        # =========================================

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(documents)

        print("TOTAL CHUNKS:", len(chunks))

        # =========================================
        # CREATE FAISS
        # =========================================

        self.vectorstore = FAISS.from_documents(
            chunks,
            self.embeddings
        )

        self.vectorstore.save_local(
            str(self.index_path)
        )

        print("FAISS INDEX CREATED SUCCESSFULLY")

    # =========================================
    # EXTRACT SECTION NUMBER
    # =========================================

    def extract_section_number(self, question: str):

        patterns = [
            r"section\s*[-]?\s*(\d+[A-Za-z]?)",
            r"sec\.?\s*[-]?\s*(\d+[A-Za-z]?)",
            r"§\s*(\d+[A-Za-z]?)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                question,
                re.IGNORECASE
            )

            if match:
                return match.group(1)

        return None

    # =========================================
    # SEARCH LAWS
    # =========================================

    def search_laws(self, question: str):

        print("\n========================================")
        print("RAG QUESTION")
        print("========================================")
        print(question)

        # =========================================
        # STEP 1: NORMAL SEMANTIC SEARCH
        # =========================================

        semantic_results = self.vectorstore.similarity_search_with_score(
            question,
            k=8
        )

        # =========================================
        # STEP 2: SECTION NUMBER
        # =========================================

        section_number = self.extract_section_number(question)

        print("SECTION DETECTED:", section_number)

        # =========================================
        # STEP 3: IF SECTION EXISTS
        # SEARCH USING SECTION NUMBER TOO
        # =========================================

        section_results = []

        if section_number:

            section_query = f"Section {section_number}"

            section_results = self.vectorstore.similarity_search_with_score(
                section_query,
                k=8
            )

        # =========================================
        # STEP 4: MERGE RESULTS
        # =========================================

        all_results = []

        seen = set()

        for doc, score in semantic_results:

            key = (
                doc.metadata.get("source"),
                doc.metadata.get("page"),
                doc.page_content[:100]
            )

            if key not in seen:

                seen.add(key)

                all_results.append(
                    (doc, score)
                )

        for doc, score in section_results:

            key = (
                doc.metadata.get("source"),
                doc.metadata.get("page"),
                doc.page_content[:100]
            )

            if key not in seen:

                seen.add(key)

                # Section search ko priority dene ke liye
                all_results.append(
                    (doc, score)
                )

        # =========================================
        # STEP 5: KEYWORD BOOST
        # =========================================

        question_words = set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                question.lower()
            )
        )

        scored_results = []

        for doc, original_score in all_results:

            text = doc.page_content.lower()

            keyword_matches = 0

            for word in question_words:

                if len(word) > 3 and word in text:
                    keyword_matches += 1

            # Lower score = better in FAISS
            # Keyword match hone par score improve karo

            adjusted_score = (
                float(original_score)
                - (keyword_matches * 0.05)
            )

            # Section number explicitly document mein ho
            if section_number:

                section_patterns = [
                    f"section {section_number}",
                    f"section\n{section_number}",
                    f"section-{section_number}",
                    f"§ {section_number}"
                ]

                if any(
                    pattern in text
                    for pattern in section_patterns
                ):

                    adjusted_score -= 1.0

            scored_results.append(
                (doc, adjusted_score)
            )

        # =========================================
        # STEP 6: SORT
        # =========================================

        scored_results.sort(
            key=lambda x: x[1]
        )

        final_results = scored_results[:5]

        # =========================================
        # DEBUG OUTPUT
        # =========================================

        print("\n========================================")
        print("FINAL RETRIEVED DOCUMENTS")
        print("========================================")

        documents = []

        for i, (doc, score) in enumerate(final_results):

            print(
                f"\n--- RESULT {i + 1} ---"
            )

            print(
                "SCORE:",
                score
            )

            print(
                "SOURCE:",
                doc.metadata.get(
                    "source",
                    "Unknown"
                )
            )

            print(
                "PAGE:",
                doc.metadata.get(
                    "page",
                    "Unknown"
                )
            )

            print("CONTENT:")

            print(
                doc.page_content[:1000]
            )

            documents.append(doc)

        print(
            "\n========================================"
        )

        return documents