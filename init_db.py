import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def initialize_production_database():
    db_path = "./chroma_db"
    
    # Check if database collections already exist to prevent duplicate writes
    if os.path.exists(db_path) and len(os.listdir(db_path)) > 0:
        print("✅ Vector database already populated.")
        return

    print("📦 Initializing Vector Store on Cloud Container...")
    # Add brief abstracts or text summaries of your 13 published research papers here
    publications = [
        "MicroHybridNet: A dual-branch framework for cellular morphology using advanced attention mapping.",
        "OsteoNet: Deep learning architectures for bone fracture detection and classification.",
        "ReedMap: Satellite remote sensing and computer vision for agricultural crop distribution modeling.",
        # Add quick summary strings for your remaining papers here!
    ]
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Generate and save the database collections locally
    Chroma.from_texts(
        texts=publications,
        embedding=embeddings,
        persist_directory=db_path
    )
    print("🚀 Vector database successfully built and stored!")

if __name__ == "__main__":
    initialize_production_database()