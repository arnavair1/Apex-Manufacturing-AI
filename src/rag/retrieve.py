from pathlib import Path

import joblib
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rag"
    / "knowledge_base.joblib"
)


def load_knowledge_base():

    if not KNOWLEDGE_BASE_PATH.exists():

        raise FileNotFoundError(
            "Knowledge base does not exist. "
            "Run build_knowledge_base.py first."
        )

    return joblib.load(KNOWLEDGE_BASE_PATH)


def retrieve_documents(query, top_k=3):

    knowledge_base = load_knowledge_base()

    vectorizer = knowledge_base["vectorizer"]
    matrix = knowledge_base["matrix"]
    chunks = knowledge_base["chunks"]

    query_vector = vectorizer.transform([query])

    similarity_scores = cosine_similarity(
        query_vector,
        matrix,
    )[0]

    ranked_indexes = similarity_scores.argsort()[::-1]

    results = []

    for index in ranked_indexes[:top_k]:

        results.append(
            {
                "source": chunks[index]["source"],
                "title": chunks[index]["title"],
                "text": chunks[index]["text"],
                "score": float(similarity_scores[index]),
            }
        )

    return results


def print_results(query, results):

    print()
    print("===== RAG SEARCH =====")
    print(f"Question: {query}")
    print()

    for number, result in enumerate(results, start=1):

        print(f"--- RESULT {number} ---")

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Section: {result['title']}"
        )

        print(
            f"Similarity: {result['score']:.4f}"
        )

        print()

        print(result["text"])

        print()


if __name__ == "__main__":

    question = (
        "What should we check when "
        "a machine has high vibration?"
    )

    results = retrieve_documents(
        question,
        top_k=3,
    )

    print_results(
        question,
        results,
    )