from typing import List, Dict, Any

class RAGReranker:
    def __init__(self):
        pass

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Reranks retrieved candidate chunks using multi-feature relevance:
        - Term proximity & exact query phrase match
        - Specific travel constraint signals (family, budget, timings, fees)
        - Source authority weighting (official tourism > general FAQs)
        """
        if not candidates:
            return []

        q_lower = query.lower()
        query_words = set(q_lower.split())

        reranked = []
        for c in candidates:
            content_lower = c["content"].lower()
            title_lower = c.get("document_title", "").lower()
            
            # Base score from RRF
            base_score = c.get("rrf_score", 0.0) * 100.0

            # 1. Title match boost
            title_overlap = sum(1 for w in query_words if len(w) > 3 and w in title_lower)
            title_boost = title_overlap * 2.5

            # 2. Exact sub-phrase boost
            exact_boost = 3.0 if (len(q_lower) > 5 and q_lower in content_lower) else 0.0

            # 3. Source credibility boost
            source_boost = 0.0
            if c.get("source_type") == "official_tourism":
                source_boost = 1.5
            elif c.get("source_type") == "government_notice":
                source_boost = 2.0

            # 4. Contextual intent boost
            intent_boost = 0.0
            if any(term in q_lower for term in ["child", "kid", "family"]) and ("family" in content_lower or "child" in content_lower or "children" in content_lower):
                intent_boost += 2.0
            if any(term in q_lower for term in ["price", "ticket", "cost", "budget", "₹"]) and ("ticket" in content_lower or "entry" in content_lower or "₹" in content_lower or "fee" in content_lower):
                intent_boost += 2.0
            if any(term in q_lower for term in ["timing", "open", "hour", "close"]) and ("am" in content_lower or "pm" in content_lower or "timing" in content_lower or "open" in content_lower):
                intent_boost += 1.5

            final_score = base_score + title_boost + exact_boost + source_boost + intent_boost
            
            item = dict(c)
            item["rerank_score"] = round(final_score, 4)
            reranked.append(item)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]

reranker = RAGReranker()
