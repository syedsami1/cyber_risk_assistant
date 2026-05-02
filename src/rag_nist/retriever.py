import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os

class NISTRetriever:
    def __init__(self, nist_csv_path, persist_directory="./chroma_db"):
        self.nist_csv_path = nist_csv_path
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection_name = "nist_800_53_controls"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        
        if self.collection.count() == 0:
            self._ingest_data()

    def _ingest_data(self):
        df = pd.read_csv(self.nist_csv_path)
        # Assuming columns: identifier, name, control_text, discussion
        df = df.fillna("")
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in df.iterrows():
            # Combine identifier, name, text and discussion for embedding
            text = f"Control {row['identifier']}: {row['name']}\n\nText: {row['control_text']}\n\nDiscussion: {row['discussion']}"
            documents.append(text)
            metadatas.append({
                "identifier": row['identifier'],
                "name": row['name']
            })
            ids.append(row['identifier'])
            
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            self.collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )

    def retrieve_controls(self, query, n_results=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
