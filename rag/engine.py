import os
import fitz  # PyMuPDF
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any

class RAGEngine:
    def __init__(self, collection_name: str = "schemes"):
        # Initialize in-memory Qdrant for the hackathon prototype
        self.client = QdrantClient(":memory:")
        self.collection_name = collection_name
        
        # Load embedding model (BGE-m3 as requested, using HuggingFaceEmbeddings)
        # Note: BGE-m3 is heavy, but fits the multilingual requirement
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
        
        # Create collection
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def ingest_mock_data(self):
        \"\"\"
        Ingests mock clauses for the PM-Kisan & Mukhyamantri Kisan Sahay Yojana 
        demo scenario to ensure deterministic demonstration.
        \"\"\"
        mock_clauses = [
            {
                "scheme_name": "PM-Kisan",
                "issuing_authority": "Central Government",
                "scope": "central",
                "state_name": "All",
                "effective_date": "2019-02-01",
                "section_id": "Section 3",
                "clause_id": "Clause B",
                "text": "Eligible farmers must possess a digital land record showing ownership of up to 2 hectares (approx. 5 acres) to receive the ₹6,000 annual support."
            },
            {
                "scheme_name": "Mukhyamantri Kisan Sahay Yojana",
                "issuing_authority": "Gujarat State Government",
                "scope": "state",
                "state_name": "Gujarat",
                "effective_date": "2020-08-10",
                "section_id": "Section 1",
                "clause_id": "Clause 4",
                "text": "Farmers in Gujarat holding up to 2 hectares of land are eligible for crop loss compensation. A physical possession token is acceptable in lieu of a digital land record."
            }
        ]

        # Embed and insert
        points = []
        for i, clause in enumerate(mock_clauses):
            vector = self.embeddings.embed_query(clause["text"])
            payload = clause.copy()
            points.append(PointStruct(id=i, vector=vector, payload=payload))

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Ingested {len(points)} mock clauses for demo.")

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vector = self.embeddings.embed_query(query)
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        
        results = []
        for hit in hits:
            # We strictly return the payload (which contains our clause_id and text)
            # which is critical for the architectural citation validator.
            results.append(hit.payload)
        
        return results

if __name__ == "__main__":
    # Test instantiation and ingestion
    rag = RAGEngine()
    rag.ingest_mock_data()
    print("Testing retrieval for 'farmer land record':")
    res = rag.retrieve("farmer land record requirements", top_k=2)
    for r in res:
        print(f"[{r['scheme_name']}] {r['section_id']}, {r['clause_id']}: {r['text']}")
