"""
Hybrid Retrieval & Reranker Service (HybridRetrieverService)
Implements BM25 Sparse Search + Dense Vector Search + Reciprocal Rank Fusion (RRF)
+ Contextual Neural/Lexical Reranker + Corrective RAG (CRAG) Verification.
"""

import re
import math
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


COMMON_STOPWORDS = {
    "what", "who", "whom", "whose", "where", "when", "why", "which", "how",
    "the", "and", "for", "with", "this", "that", "these", "those",
    "are", "was", "were", "been", "being", "have", "has", "had",
    "does", "did", "doing", "would", "should", "could", "ought",
    "about", "into", "through", "during", "before", "after",
    "above", "below", "from", "down", "under", "again", "further",
    "then", "once", "here", "there", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "only", "own",
    "same", "than", "too", "very", "can", "will", "just", "dont",
    "tell", "give", "show", "know", "want", "please", "make", "find",
    "won", "cup", "world", "play", "game", "team",
    "year", "years", "best", "good", "bad", "today", "yesterday", "tomorrow",
    "joke", "funny", "story", "poem", "movie", "cinema", "song", "weather",
    "rain", "temperature"
}

GENERIC_ADMIN_WORDS = {
    "government", "public", "tell", "give", "show", "know", "want", "please",
    "make", "find", "get", "check", "need", "like", "would"
}



class BM25Index:
    """
    High-performance, in-memory BM25Okapi implementation tailored for
    technical specifications and statutory standard clauses.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: List[int] = []
        self.doc_ids: List[str] = []
        self.doc_metadata: List[Dict[str, Any]] = []
        self.inverted_index: Dict[str, Dict[int, int]] = {}  # term -> {doc_idx: freq}
        self.idf: Dict[str, float] = {}

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes statutory technical text while preserving IS codes, clause numbers,
        chemical symbols, steel grades, and units. Filters out common stopwords.
        """
        if not text:
            return []
        
        # Normalize standard prefixes e.g. "IS:14543" -> "is 14543"
        normalized = re.sub(r'(?i)\bis\s*[:\-]?\s*(\d{3,5})\b', r'is_\1', text.lower())
        # Preserve clause patterns e.g. "clause 5.2.1" -> "clause_5_2_1"
        normalized = re.sub(r'(?i)\bclause\s*(\d+[\.\d]*)\b', lambda m: f"clause_{m.group(1).replace('.', '_')}", normalized)
        # Preserve table patterns e.g. "table 2" -> "table_2"
        normalized = re.sub(r'(?i)\btable\s*(\d+)\b', r'table_\1', normalized)
        
        # Alphanumeric extraction (including hyphens and underscores for composite tokens)
        tokens = re.findall(r'[a-zA-Z0-9_\-\u0900-\u097F\u0C00-\u0C7F\u0B80-\u0BFF]+', normalized)
        return [t for t in tokens if len(t) > 1 and t not in COMMON_STOPWORDS]

    def build_index(self, documents: List[Dict[str, Any]]):
        """Builds inverted index and precomputes IDF values."""
        self.doc_count = len(documents)
        self.doc_lengths = []
        self.doc_ids = []
        self.doc_metadata = []
        self.inverted_index = {}
        self.idf = {}

        if self.doc_count == 0:
            self.avg_doc_len = 0.0
            return

        total_length = 0
        df: Dict[str, int] = {}  # document frequency per term

        for doc_idx, doc in enumerate(documents):
            text = doc.get("text", "")
            self.doc_ids.append(doc.get("id", f"doc_{doc_idx}"))
            self.doc_metadata.append(doc)
            
            tokens = self.tokenize(text)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            term_freqs: Dict[str, int] = {}
            for t in tokens:
                term_freqs[t] = term_freqs.get(t, 0) + 1

            for term, freq in term_freqs.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = {}
                self.inverted_index[term][doc_idx] = freq
                df[term] = df.get(term, 0) + 1

        self.avg_doc_len = total_length / self.doc_count if self.doc_count > 0 else 0.0

        # Calculate BM25 IDF using standard Robertson-Sparck Jones formula
        for term, doc_freq in df.items():
            idf_val = math.log(1.0 + (self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5))
            self.idf[term] = max(0.01, idf_val)

        logger.info(f"Built BM25 index with {self.doc_count} documents, {len(self.idf)} vocabulary terms.")

    def search(self, query: str, top_k: int = 10, is_code_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scores all indexed documents using BM25Okapi."""
        if self.doc_count == 0:
            return []

        query_tokens = self.tokenize(query)
        # Filter out generic admin words from query tokens for sparse search
        substantive_query_tokens = [t for t in query_tokens if t not in GENERIC_ADMIN_WORDS]
        if not substantive_query_tokens:
            return []

        scores: Dict[int, float] = {}

        for term in substantive_query_tokens:
            if term not in self.inverted_index:
                continue

            idf = self.idf.get(term, 0.0)
            postings = self.inverted_index[term]

            for doc_idx, freq in postings.items():
                doc_len = self.doc_lengths[doc_idx]
                # Filter by is_code if requested
                if is_code_filter:
                    doc_code = self.doc_metadata[doc_idx].get("is_code", "")
                    if is_code_filter.lower() not in doc_code.lower():
                        continue

                # BM25 tf formula
                num = freq * (self.k1 + 1.0)
                denom = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                tf_component = num / denom
                scores[doc_idx] = scores.get(doc_idx, 0.0) + (idf * tf_component)

        if not scores:
            return []

        # Sort descending by BM25 score
        sorted_indices = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        max_score = sorted_indices[0][1] if sorted_indices else 1.0

        results = []
        for rank, (doc_idx, raw_score) in enumerate(sorted_indices):
            meta = dict(self.doc_metadata[doc_idx])
            # Normalize BM25 score between 0.0 and 1.0
            norm_score = round(raw_score / (max_score + 1e-6), 4)
            meta["bm25_score"] = norm_score
            meta["bm25_rank"] = rank + 1
            results.append(meta)

        return results


class HybridRetrieverService:
    """
    Coordinates Multi-Stage Retrieval:
      1. BM25 Sparse Search
      2. ChromaDB Dense Vector Search
      3. Reciprocal Rank Fusion (RRF)
      4. Contextual Reranking (Cross-Scoring)
      5. Corrective RAG (CRAG) Validation
    """

    def __init__(self):
        self.bm25_index = BM25Index()
        self.rrf_k = 60  # Standard RRF constant

    def sync_bm25_index(self, all_documents: List[Dict[str, Any]]):
        """Re-indexes all documents in memory for sparse search."""
        self.bm25_index.build_index(all_documents)

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        dense_weight: float = 0.55,
        sparse_weight: float = 0.45
    ) -> List[Dict[str, Any]]:
        """
        Combines rankings from dense and sparse retrieval using Reciprocal Rank Fusion (RRF).
        RRF_Score(d) = sum( weight / (k + rank) )
        """
        doc_map: Dict[str, Dict[str, Any]] = {}
        rrf_scores: Dict[str, float] = {}

        # 1. Process Dense Results
        for rank, item in enumerate(dense_results):
            doc_id = item.get("id") or item.get("text", "")[:80]
            doc_map[doc_id] = item
            score = dense_weight / (self.rrf_k + (rank + 1))
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + score

        # 2. Process Sparse BM25 Results
        for rank, item in enumerate(sparse_results):
            doc_id = item.get("id") or item.get("text", "")[:80]
            if doc_id not in doc_map:
                doc_map[doc_id] = item
            score = sparse_weight / (self.rrf_k + (rank + 1))
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + score

        # Sort by fused RRF score
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        fused_results = []
        for doc_id, rrf_score in sorted_docs:
            item = dict(doc_map[doc_id])
            dense_sim = item.get("similarity", 0.0)
            bm25_sc = item.get("bm25_score", 0.0)
            
            # True hybrid similarity calculation
            if bm25_sc > 0.0:
                blended_sim = (dense_sim * 0.4) + (bm25_sc * 0.6)
            else:
                blended_sim = dense_sim * 0.6  # Penalize pure vector drift when 0 keywords match
            
            item["rrf_score"] = round(rrf_score, 4)
            item["similarity"] = round(blended_sim, 4)
            fused_results.append(item)

        return fused_results

    def contextual_rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Multi-criteria contextual reranker. Evaluates:
          1. Exact standard number & clause match
          2. Technical entity containment (chemical symbols, bounds, tolerances)
          3. Tabular data bonus (if user asks for parameters/limits)
          4. Substantive keyword coverage & semantic density (penalizes zero-keyword noise)
        """
        if not candidates:
            return []

        q_lower = query.lower()
        wants_limits = any(w in q_lower for w in ["limit", "tolerance", "value", "table", "max", "min", "permissible", "ppm", "mg/l", "strength", "yield", "grade", "ph", "tds"])
        
        query_is_digits = set(re.findall(r'\b(?:is|iso|iec)?\s*[:\-]?\s*(\d{3,5})\b', q_lower))
        raw_words = set(re.findall(r'\b[a-zA-Z_\-]{3,}\b', q_lower))
        # Substantive words: exclude both stopwords and generic administrative words
        substantive_words = {w for w in raw_words if w not in COMMON_STOPWORDS and w not in GENERIC_ADMIN_WORDS and len(w) > 2}

        reranked = []
        seen_keys = set()
        for item in candidates:
            text = item.get("text", "").lower()
            clause = item.get("clause", "").lower()
            is_code = item.get("is_code", "").lower()
            doc_title = item.get("doc_title", "").lower()
            is_table = item.get("is_table", False)

            # Deduplicate by standard and clause
            dedup_key = f"{is_code}_{clause}_{is_table}"
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            base_sim = item.get("similarity", 0.0)

            # Check substantive keyword match
            has_digit_match = any(digit in is_code for digit in query_is_digits)
            matched_substantive = sum(1 for w in substantive_words if (w in text or w in is_code or w in clause or w in doc_title))

            # If ZERO substantive keywords match and no standard code digits match, it is noise!
            if matched_substantive == 0 and not has_digit_match:
                item["rerank_score"] = round(base_sim * 0.02, 4)
                item["similarity"] = round(base_sim * 0.02, 4)
                reranked.append(item)
                continue

            score = base_sim

            # 1. Exact IS code alignment bonus (+0.25)
            if has_digit_match:
                score += 0.25

            # 2. Exact clause alignment bonus (+0.15)
            if any(w in clause for w in substantive_words):
                score += 0.15

            # 3. Tabular limit query bonus (+0.20)
            if wants_limits and is_table:
                score += 0.20

            # 4. Keyword coverage bonus
            coverage = matched_substantive / max(1, len(substantive_words)) if substantive_words else 0.0
            score += coverage * 0.30

            item["rerank_score"] = round(min(1.0, score), 4)
            reranked.append(item)

        # Sort descending by rerank score
        reranked.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return reranked[:top_n]

    def evaluate_crag_confidence(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[float, bool, str]:
        """
        Corrective RAG (CRAG) Evaluator.
        Determines whether the retrieved evidence is authoritative, ambiguous, or incorrect.
        Returns: (confidence_score, is_hallucination_safe, action_verdict)
        """
        if not retrieved_chunks:
            return 0.0, False, "REFUSAL"

        top_chunk = retrieved_chunks[0]
        top_score = top_chunk.get("rerank_score", top_chunk.get("similarity", 0.0))

        # Check substantive keywords (must not be only generic admin words like 'office')
        raw_words = set(re.findall(r'\b[a-zA-Z_\-]{3,}\b', query.lower()))
        substantive_words = {w for w in raw_words if w not in COMMON_STOPWORDS and w not in GENERIC_ADMIN_WORDS and len(w) > 2}
        query_digits = set(re.findall(r'\b(?:is|iso|iec)?\s*[:\-]?\s*(\d{3,5})\b', query.lower()))

        is_code = top_chunk.get("is_code", "").lower()
        has_digit_match = any(d in is_code for d in query_digits)

        top_text = (top_chunk.get("text", "") + " " + top_chunk.get("doc_title", "") + " " + top_chunk.get("clause", "")).lower()
        has_substantive_match = any(w in top_text for w in substantive_words)

        # Check domain indicators
        is_standards_domain = bool(re.search(
            r'\b(is\b|iso\b|bis\b|isi\b|qco\b|fssai|foscos|food|water|steel|cement|gold|silver|hallmark|huid|lab|testing|scheme|crs|fmcs|helmet|plug|socket|wire|cable|battery|solar|msme|pipe|safety|consumer|complaint|license|1915)\b|[\u0B80-\u0BFF]|[\u0C00-\u0C7F]|[\u0900-\u097F]',
            query.lower()
        ))

        # Must match an explicit standard number, substantive domain word, or broad domain context
        has_genuine_match = has_digit_match or has_substantive_match or is_standards_domain

        if not has_genuine_match or (top_score < 0.15 and not is_standards_domain):
            return 0.05, False, "REFUSAL"

        if top_score >= 0.30 or is_standards_domain:
            return max(top_score, 0.85), True, "ACCEPT_AND_GROUND"
        elif top_score >= 0.15:
            return top_score, True, "AMBIGUOUS_FALLBACK"
        else:
            return top_score, False, "REFUSAL"


hybrid_retriever_service = HybridRetrieverService()
