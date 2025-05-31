from langchain.schema.document import Document

FAQ_QUESTIONS = [
    {
        "question": "What are the all the different names or titles used for Krishna in the Gita?",
        "answer": (
            "Krishna, Vasudeva, Keshava, Govinda, Madhava, Hrishikesha, Janardana, Achyuta, "
            "Madhusudana, Jagannivasa, Parthasarathi, Yogeshwara, Bhagavan, Ishwara, Adideva, "
            "Purushottama, Devesha, Lokeshwara, Sarvaloka Maheshwara, Mahabaho, Saurin, Yadava, "
            "Pandava Sakha, Atman, Brahman, Paramatma, Kalosmi, Vishvarupa, Jagatpati, Jagatguru."
        )
    },
    {
        "question": "What are the different names or titles used for Arjuna in the Gita?",
        "answer": (
            "Arjuna, Partha, Dhananjaya, Gudakesha, Bharata, Kesava, Savyasachi, Kaunteya."
        )
    },
    {
        "question": "List all types of yoga discussed in the Gita.",
        "answer": (
            "Karma Yoga, Jnana Yoga, Bhakti Yoga, Raja Yoga, Dhyana Yoga, Sankhya Yoga, "
            "Jnana-Vijnana Yoga, Ksetra-Ksetrajna Vibhaga Yoga."
        )
    },
    {
        "question": "What are all the different paths to liberation mentioned in the Gita?",
        "answer": (
            "Karma Yoga (selfless action), Jnana Yoga (knowledge), Bhakti Yoga (devotion), "
            "Dhyana Yoga (meditation)."
        )
    },
    {
        "question": "Which all characters are mentioned in the Bhagavad Gita?",
        "answer": (
            "Krishna, Arjuna, Dhritarashtra, Sanjaya, Bhishma, Drona, Karna, Yudhishthira, "
            "Duryodhana, and others."
        )
    },
    {
        "question": "List all the kings or warriors referenced in the Gita.",
        "answer": (
            "Dhritarashtra, Arjuna, Bhishma, Drona, Karna, Yudhishthira, Duryodhana, Shalya, "
            "and others."
        )
    },
    {
        "question": "What is the structure of the Gita across its 18 chapters?",
        "answer": (
            "Chapters 1–6: Karma Yoga and Dhyana Yoga, Chapters 7–12: Bhakti Yoga, "
            "Chapters 13–18: Jnana Yoga and synthesis of all paths."
        )
    },
]

def load_faq_documents():
    faq_docs = []
    for i, faq in enumerate(FAQ_QUESTIONS):
        content = f"Q: {faq['question']}\nA: {faq['answer']}"
        metadata = {
            "source": "FAQ",
            "page": 0,
            "id": f"FAQ:{i}"
        }
        faq_docs.append(Document(page_content=content, metadata=metadata))
    return faq_docs
