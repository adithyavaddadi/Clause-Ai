from vectorstore.pinecone_client import get_pinecone

db = get_pinecone()
print("Pinecone Enabled:", db.enabled)
