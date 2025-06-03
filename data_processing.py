import os
from langchain.embeddings import HuggingFaceEmbeddings
from chromadb import PersistentClient

def process_course_materials(data_folder):
    """
    Process and embed course materials using ChromaDB.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    client = PersistentClient(path="./data/embeddings")
    
    collection = client.create_collection("course_materials")
    
    for file in os.listdir(data_folder):
        if file.endswith(".txt"):
            with open(os.path.join(data_folder, file), "r") as f:
                content = f.read()
                collection.add(documents=[content], ids=[file])
    
    return "Course materials processed and stored in the database."

def fetch_course_materials(query):
    """
    Retrieve relevant course materials based on user input.
    """
    client = PersistentClient(path="./data/embeddings")
    collection = client.get_collection("course_materials")
    
    # Perform the query
    results = collection.query(query_texts=[query], n_results=3)
    print("Query Results:", results)  # Debugging: Check results structure

    # Extract documents from the results
    if "documents" in results and results["documents"]:
        # Flatten the nested list of documents
        return [doc for docs_list in results["documents"] for doc in docs_list]
    else:
        return []


