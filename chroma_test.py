import chromadb

# 1. Initialize Chroma with automatic persistence to your hard drive
# This will physically create a folder called 'chroma_db' in your project directory
print("1. Initializing ChromaDB Persistent Client...")
client = chromadb.PersistentClient(path="./chroma_db")

# 2. Create a Collection (Think of this like a table in a SQL database)
# We use get_or_create so the script doesn't crash if you run it multiple times
collection = client.get_or_create_collection(name="aegis_agronomy")

print("2. Adding documents and metadata to Chroma...")
# 3. Add data WITH METADATA
# Chroma automatically downloads a default embedding model (all-MiniLM-L6-v2)
# and embeds these sentences for you behind the scenes.
collection.add(
    documents=[
        "Acidic soils with a pH below 5.5 frequently exhibit aluminum toxicity.",
        "Phosphorus bioavailability is highly pH-dependent in alkaline soils.",
        "Telematics systems on agricultural tractors stream real-time CAN bus data.",
        "Modern combine headers utilize automatic terrain contouring sensors."
    ],
    metadatas=[
        {"category": "soil_science", "source": "journal_A"},
        {"category": "soil_science", "source": "journal_B"},
        {"category": "equipment", "source": "manual_X"},
        {"category": "equipment", "source": "manual_Y"}
    ],
    ids=["doc1", "doc2", "doc3", "doc4"] # Every document in Chroma needs a unique ID
)

print(f"Total documents successfully loaded into Chroma: {collection.count()}\n")

# 4. Standard Vector Search
query = "Tell me about tractor data streams."
print(f"--- STANDARD SEARCH for: '{query}' ---")

results = collection.query(
    query_texts=[query],
    n_results=2
)

for i in range(len(results['documents'][0])):
    print(f"Match: {results['documents'][0][i]}")
    print(f"Metadata: {results['metadatas'][0][i]}")
    print(f"Distance: {results['distances'][0][i]:.4f}\n")


# 5. Metadata Filtered Search (The Superpower of Chroma)
print(f"--- FILTERED SEARCH for: '{query}' ---")
print("Filtering ONLY for category == 'soil_science'...")

# We pass the exact same query, but force Chroma to only look at 'soil_science' metadata
filtered_results = collection.query(
    query_texts=[query],
    n_results=2,
    where={"category": "soil_science"}
)

for i in range(len(filtered_results['documents'][0])):
    print(f"Match: {filtered_results['documents'][0][i]}")
    print(f"Metadata: {filtered_results['metadatas'][0][i]}")
    print(f"Distance: {filtered_results['distances'][0][i]:.4f}\n")