from collections import defaultdict


def reciprocal_rank_fusion(retriever_results, k=60):
    """
    Combine results from multiple retrievers using Reciprocal Rank Fusion (RRF).

    Args:
        retriever_results: List of lists of Documents
        k: RRF constant (default = 60)

    Returns:
        List[Document] sorted by fused score
    """

    scores = defaultdict(float)
    unique_docs = {}

    for docs in retriever_results:
        for rank, doc in enumerate(docs):

            # Unique document ID
            doc_id = (
                doc.metadata.get("source", "")
                + "_"
                + str(doc.metadata.get("chunk_id", rank))
            )

            unique_docs[doc_id] = doc

            scores[doc_id] += 1 / (k + rank + 1)

    ranked_docs = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        unique_docs[doc_id]
        for doc_id, _ in ranked_docs
    ]
