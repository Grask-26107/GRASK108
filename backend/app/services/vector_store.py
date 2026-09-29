import os
import json
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.hybrid_retriever import hybrid_retriever_service
from app.services.pdf_table_parser import ParsedChunk
from app.core.database import register_standard_db, delete_standard_db

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
        )
        
        self.collection_name = "bis_standards_collection"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Bureau of Indian Standards IS Codes & Specifications"}
        )
        logger.info(f"Initialized ChromaDB vector store at {self.persist_dir}")
        
        # Refresh BM25 index from persistent store
        self._refresh_bm25_index()

    def _refresh_bm25_index(self):
        """Loads all existing documents into the in-memory BM25 sparse index."""
        try:
            total_docs = self.collection.count()
            if total_docs == 0:
                hybrid_retriever_service.sync_bm25_index([])
                return

            all_records = self.collection.get(include=["documents", "metadatas"])
            docs = []
            if all_records and all_records.get("documents"):
                for doc_id, text, meta in zip(all_records.get("ids", []), all_records["documents"], all_records["metadatas"]):
                    table_dict = {}
                    if meta.get("table_json"):
                        try:
                            table_dict = json.loads(meta["table_json"])
                        except Exception:
                            table_dict = {}

                    docs.append({
                        "id": doc_id,
                        "text": text,
                        "is_code": meta.get("is_code", ""),
                        "doc_title": meta.get("doc_title", ""),
                        "clause": meta.get("clause", "General"),
                        "page_number": int(meta.get("page_number", 1)),
                        "is_table": bool(meta.get("is_table", False)),
                        "table_number": meta.get("table_number", ""),
                        "table_title": meta.get("table_title", ""),
                        "table_data": table_dict
                    })

            hybrid_retriever_service.sync_bm25_index(docs)
            logger.info(f"BM25 sparse index synchronized with {len(docs)} documents.")
        except Exception as e:
            logger.warning(f"Could not refresh BM25 index on startup: {e}")

    def add_chunks(self, chunks: List[ParsedChunk]) -> int:
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []
        
        # Track counts per standard for database registration
        is_code = chunks[0].is_code
        doc_title = chunks[0].doc_title
        table_count = sum(1 for c in chunks if c.is_table)
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{chunk.is_code}_{chunk.page_number}_{'tbl' if chunk.is_table else 'txt'}_{idx}_{abs(hash(chunk.text[:50]))}"
            ids.append(chunk_id)
            documents.append(chunk.text)
            
            meta = {
                "is_code": chunk.is_code,
                "doc_title": chunk.doc_title,
                "clause": chunk.clause or "General",
                "page_number": int(chunk.page_number),
                "is_table": bool(chunk.is_table),
                "table_number": chunk.table_number or "",
                "table_title": chunk.table_title or "",
                "table_json": json.dumps(chunk.table_data) if chunk.is_table else ""
            }
            metadatas.append(meta)

        # Generate embeddings
        embeddings = embedding_service.embed_documents(documents)
        
        # Upsert in Chroma
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end = i + batch_size
            self.collection.upsert(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                embeddings=embeddings[i:end]
            )

        # Register in SQLite metadata registry
        register_standard_db(
            is_code=is_code,
            title=doc_title,
            year="2024",
            category="National Standards",
            chunk_count=len(chunks),
            table_count=table_count
        )

        # Refresh BM25 sparse index
        self._refresh_bm25_index()

        logger.info(f"Indexed {len(chunks)} chunks ({table_count} tables) for standard {is_code}.")
        return len(chunks)

    def query(
        self,
        query_text: str,
        n_results: int = 6,
        is_code_filter: Optional[str] = None,
        only_tables: bool = False
    ) -> List[Dict[str, Any]]:
        """Dense vector search with optional IS code and table filtering."""
        query_embedding = embedding_service.embed_query(query_text)
        
        where_clause = {}
        if is_code_filter and is_code_filter.strip():
            where_clause["is_code"] = is_code_filter.strip()
        if only_tables:
            where_clause["is_table"] = True

        chroma_where = where_clause if where_clause else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, max(1, self.collection.count())),
            where=chroma_where,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if results and results.get("documents") and len(results["documents"][0]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]
            ids = results.get("ids", [[]])[0]

            for idx, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
                doc_id = ids[idx] if idx < len(ids) else f"{meta.get('is_code')}_{meta.get('page_number')}_{meta.get('clause')}"
                # Cosine distance to similarity conversion
                similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                table_dict = {}
                if meta.get("table_json"):
                    try:
                        table_dict = json.loads(meta["table_json"])
                    except Exception:
                        table_dict = {}

                retrieved.append({
                    "id": doc_id,
                    "text": doc,
                    "is_code": meta.get("is_code", "Unknown IS Code"),
                    "doc_title": meta.get("doc_title", "Standard"),
                    "clause": meta.get("clause", "Clause 1.0"),
                    "page_number": int(meta.get("page_number", 1)),
                    "is_table": bool(meta.get("is_table", False)),
                    "table_number": meta.get("table_number", ""),
                    "table_title": meta.get("table_title", ""),
                    "table_data": table_dict,
                    "similarity": round(float(similarity), 4),
                    "distance": float(dist)
                })

        return retrieved

    def hybrid_query(
        self,
        query_text: str,
        n_results: int = 5,
        is_code_filter: Optional[str] = None,
        only_tables: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Next-Generation Hybrid Retrieval:
        1. BM25 Sparse Search
        2. ChromaDB Dense Vector Search
        3. Reciprocal Rank Fusion (RRF)
        4. Contextual Neural/Lexical Reranker
        """
        # 1. Dense retrieval (fetch top 10 candidates)
        dense_results = self.query(
            query_text=query_text,
            n_results=10,
            is_code_filter=is_code_filter,
            only_tables=only_tables
        )

        # 2. Sparse BM25 retrieval (fetch top 10 candidates)
        sparse_results = hybrid_retriever_service.bm25_index.search(
            query=query_text,
            top_k=10,
            is_code_filter=is_code_filter
        )

        # 3. Reciprocal Rank Fusion
        fused_candidates = hybrid_retriever_service.reciprocal_rank_fusion(
            dense_results=dense_results,
            sparse_results=sparse_results
        )

        # 4. Contextual Reranking
        final_reranked = hybrid_retriever_service.contextual_rerank(
            query=query_text,
            candidates=fused_candidates,
            top_n=n_results
        )

        return final_reranked if final_reranked else dense_results[:n_results]

    def delete_standard(self, is_code: str) -> int:
        """Deletes all chunks for an IS code."""
        try:
            self.collection.delete(where={"is_code": is_code})
            delete_standard_db(is_code)
            self._refresh_bm25_index()
            logger.info(f"Deleted standard {is_code} from vector store.")
            return 1
        except Exception as e:
            logger.error(f"Error deleting standard {is_code}: {e}")
            return 0

    def get_all_tables(self, is_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all indexed tables."""
        where = {"is_table": True}
        if is_code:
            where = {"$and": [{"is_table": True}, {"is_code": is_code}]}

        try:
            results = self.collection.get(
                where=where,
                include=["metadatas", "documents"]
            )
            tables = []
            if results and results.get("metadatas"):
                for meta, doc in zip(results["metadatas"], results["documents"]):
                    table_dict = {}
                    if meta.get("table_json"):
                        try:
                            table_dict = json.loads(meta["table_json"])
                        except Exception:
                            table_dict = {}
                    
                    tables.append({
                        "id": f"{meta.get('is_code')}_{meta.get('table_number')}",
                        "is_code": meta.get("is_code", ""),
                        "table_number": meta.get("table_number", "Table"),
                        "table_title": meta.get("table_title", "Specifications"),
                        "clause": meta.get("clause", ""),
                        "page_number": int(meta.get("page_number", 1)),
                        "columns": table_dict.get("columns", []),
                        "rows": table_dict.get("rows", []),
                        "markdown_repr": table_dict.get("markdown", doc)
                    })
            return tables
        except Exception as e:
            logger.error(f"Failed to fetch tables: {e}")
            return []


vector_store_service = VectorStoreService()
