from sentence_transformers import SentenceTransformer
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from app.config import settings

class SearchService:
    def __init__(self):
        # Using the biomedical PubMedBERT embedding model
        self.embedding_model = SentenceTransformer(
            "NeuML/biomedbert-base-embeddings",
            cache_folder="/tmp/huggingface"
        )
        self.client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY),
        )

    def retrieve_hybrid(self, query: str, k: int = 7) -> list:
        # Generate query vector with normalization
        query_vector = self.embedding_model.encode(
            query, normalize_embeddings=True
        ).tolist()

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="content_vector",
        )

        results = self.client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["chunk_id", "document_id", "title", "citation", "section", "page_number", "content"],
            top=k,
        )

        chunks = []
        for r in results:
            chunks.append({
                "chunk_id": r["chunk_id"],
                "document": r.get("document_id", "Unknown"),
                "title": r.get("title", ""),
                "citation": r.get("citation", ""),
                "section": r.get("section", "General / Unclassified"),
                "page": r.get("page_number", 0),
                "text": r.get("content", ""),
                "score": float(r.get("@search.score", 0.0)),
            })
        return chunks

search_service = SearchService()
