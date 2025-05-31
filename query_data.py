import os
import argparse
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from get_embedding_function import get_embedding_function

# Load environment variables
load_dotenv()

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

CLASSIFIER_PROMPT_TEMPLATE = """
You're a smart assistant. Classify the following question.

Does it require reading the **entire document** ("global") or just **a few relevant parts** ("local")?

Note: If the question asks for all names, all titles, or a comprehensive list of things mentioned anywhere in the document, classify it as "global".

Question:
"{query}"

Respond with just one word: "global" or "local".
"""

def classify_question_llm(query: str, model) -> str:
    classifier_prompt = CLASSIFIER_PROMPT_TEMPLATE.format(query=query)
    response = model.invoke(classifier_prompt)
    decision = response.content.strip().lower()
    return decision

def find_faq_answer(query_text: str, top_k: int = 1, similarity_threshold: float = 0.45) -> str | None:
    """
    Search FAQ entries in the Chroma DB for the closest match to query_text.
    Returns the answer string if a good match is found, else None.
    """
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Search only FAQ documents by metadata filter
    # (Note: filter by 'source' if your Chroma DB supports metadata filtering)
    # If your Chroma version does not support metadata filtering, you can filter results after retrieval
    
    results = db.similarity_search_with_score(query_text, k=top_k)

    # DEBUG PRINT to inspect what's happening
    for doc, score in results:
        print(f"Score: {score}, Source: {doc.metadata.get('source')}, Content: {doc.page_content[:100]}")
    

    # Filter results to those from FAQ source only
    faq_results = [(doc, score) for doc, score in results if doc.metadata.get("source") == "FAQ"]

    if not faq_results:
        return None
    
    best_doc, best_score = faq_results[0]
    print(f"Best FAQ match score: {best_score}")
    print(f"FAQ content: {best_doc.page_content[:100]}...")

    
    # Only return answer if similarity score is above threshold
    # (lower score = better similarity for some implementations; adjust accordingly)
    # Here assuming score is cosine similarity distance (lower better)
    if best_score >= similarity_threshold:  # adjust if necessary
        return None
    
    # Extract answer from doc content:
    # Format: "Q: question\nA: answer"
    content = best_doc.page_content
    # Split by lines and find answer line
    for line in content.splitlines():
        if line.strip().startswith("A:"):
            answer = line.strip()[2:].strip()
            return answer
    
    return None

def query_rag(query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    model = ChatOpenAI(model="gpt-4o", temperature=0)

    # Use LLM to classify the query
    decision = classify_question_llm(query_text, model)
    print(f"🤖 LLM classified the query as: {decision.upper()}")

    if decision == "global":
        print("🌀 Global question detected.")

        # First, try to answer from FAQ
        faq_answer = find_faq_answer(query_text)
        if faq_answer:
            print("✅ Matched FAQ answer found. Returning FAQ response.")
            print(f"Response: {faq_answer}\nSources: FAQ")
            return faq_answer

        print("❌ No FAQ match found. Using similarity search (k=5) over entire document...")

        # Use top-k similarity search over entire document as fallback
        results = db.similarity_search_with_score(query_text, k=5)
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        response = model.invoke(prompt)
        sources = [doc.metadata.get("id", None) for doc, _score in results]
        print(f"Response: {response.content}\nSources: {sources}")
        return response.content

    else:
        print("🔍 Local question detected. Using top-k retrieval (k=5)...")
        results = db.similarity_search_with_score(query_text, k=5)
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        response = model.invoke(prompt)
        sources = [doc.metadata.get("id", None) for doc, _score in results]
        print(f"Response: {response.content}\nSources: {sources}")
        return response.content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_rag(args.query_text)

if __name__ == "__main__":
    main()
