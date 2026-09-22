from pathlib import Path
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_DIRECTORY = PROJECT_ROOT / "data" / "documents"

RAG_DIRECTORY = PROJECT_ROOT / "data" / "processed" / "rag"

RAG_DIRECTORY.mkdir(parents=True, exist_ok=True)

VECTOR_DATABASE_PATH = RAG_DIRECTORY / "knowledge_base.joblib"


def load_documents():
    documents = []

    for file_path in sorted(DOCUMENTS_DIRECTORY.glob("*.md")):

        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(
            {
                "source": file_path.name,
                "text": text,
            }
        )

    return documents


def create_chunks(documents):
    chunks = []

    for document in documents:

        source = document["source"]
        text = document["text"]

        sections = re.split(
            r"\n(?=## )",
            text
        )

        for section in sections:

            section = section.strip()

            if not section:
                continue

            lines = section.splitlines()

            title = lines[0].strip()

            if title.startswith("# "):
                title = title[2:].strip()

            elif title.startswith("## "):
                title = title[3:].strip()

            if len(section) < 50:
                continue

            chunks.append(
                {
                    "source": source,
                    "title": title,
                    "text": section,
                }
            )

    return chunks


def build_knowledge_base():

    print("===== BUILDING MANUFACTURING KNOWLEDGE BASE =====")
    print()

    documents = load_documents()

    print(f"Documents found: {len(documents)}")

    if not documents:
        raise FileNotFoundError(
            f"No Markdown documents found in {DOCUMENTS_DIRECTORY}"
        )

    chunks = create_chunks(documents)

    print(f"Knowledge chunks created: {len(chunks)}")
    print()

    texts = [chunk["text"] for chunk in chunks]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(texts)

    knowledge_base = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "chunks": chunks,
    }

    joblib.dump(
        knowledge_base,
        VECTOR_DATABASE_PATH,
    )

    print("Knowledge base created successfully.")
    print()
    print(f"Saved to:")
    print(VECTOR_DATABASE_PATH)
    print()

    print("===== KNOWLEDGE BASE CONTENT =====")

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"{index}. "
            f"{chunk['source']} | "
            f"{chunk['title']}"
        )


if __name__ == "__main__":
    build_knowledge_base()