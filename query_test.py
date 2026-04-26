import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="aegis_papers")

print(f"Collection contains {collection.count()} chunks.\n")

queries = [
    "What machine learning methods are used?",
    "What were the main findings or results?",
    "What are the limitations of this study?",
]

for query in queries:
    print(f"QUERY: {query}")
    results = collection.query(query_texts=[query], n_results=2)
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        print(f"  [{i+1}] page={meta['page']} chunk_id={meta['chunk_id']} distance={dist:.4f}")
        print(f"       {doc[:200]}...")
    print()
