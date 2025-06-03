import argparse
import os
import shutil
import fitz  # PyMuPDF
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_embedding_function import get_embedding_function
from chromadb import PersistentClient
from langchain.vectorstores import Chroma
from data.faq_data import load_faq_documents
from dotenv import load_dotenv

CHROMA_PATH = "chroma"
DATA_PATH = "data"

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


def main():
    # Reset database if needed
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Load PDF docs
    pdf_docs = load_documents()

    # Load FAQ docs
    faq_docs = load_faq_documents()

    # Combine both
    documents = pdf_docs + faq_docs

    # Show some samples for debugging
    for i, doc in enumerate(documents[:4]):
        print(f"\n--- Document {i+1} ---")
        print("Metadata:", doc.metadata)
        print("Content Sample:", doc.page_content[:400], "...\n")

    # Split all documents (FAQs will mostly remain one chunk)
    chunks = split_documents(documents)

    # Add to chroma
    add_to_chroma(chunks)


# === Text Cleaning Helpers ===

def fix_common_unicode_errors(text: str) -> str:
    """Replace commonly garbled unicode characters."""
    return (
        text.replace("ß", "s")
            .replace("†", "t")
            .replace("å", "a")
            .replace("√", "n")
            # Extend as needed for your corpus
    )


# === PDF Loader using fitz (PyMuPDF) ===

def extract_clean_text_from_pdf(pdf_path: str) -> list[Document]:
    """Extract and clean text from each page of a PDF, returning LangChain Documents."""
    doc = fitz.open(pdf_path)
    documents = []

    for page_number, page in enumerate(doc, start=1):
        raw_text = page.get_text()
        clean_text = fix_common_unicode_errors(raw_text)

        documents.append(Document(
            page_content=clean_text,
            metadata={"source": pdf_path, "page": page_number}
        ))

    return documents


def load_documents() -> list[Document]:
    """Load and clean all PDFs from the data directory."""
    all_docs = []
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(DATA_PATH, filename)
            docs = extract_clean_text_from_pdf(pdf_path)
            all_docs.extend(docs)
    return all_docs


# === Chroma Vector DB Handling ===

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    chroma_client = PersistentClient(path=CHROMA_PATH)

    db = Chroma(
        client=chroma_client,
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    # Calculate Page IDs
    chunks_with_ids = calculate_chunk_ids(chunks)

    existing_items = db.get(include=[])  # just to fetch IDs
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Add new documents only
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()
