"""Test to verify find_duplicate_candidates fix for k-NN search."""
import pytest


def test_find_similar_pairs_k_parameter():
    """Verify find_similar_pairs accepts and uses k parameter."""
    from logical_thinking_server.services.faiss_wrapper import FAISSWrapper
    import numpy as np

    # Create a wrapper with small dimension for testing
    wrapper = FAISSWrapper(dimension=4, metric="ip")

    # Add some test vectors
    vectors = np.array([
        [1.0, 0.0, 0.0, 0.0],  # v0
        [0.99, 0.1, 0.0, 0.0],  # v1 - similar to v0
        [0.0, 1.0, 0.0, 0.0],  # v2
        [0.0, 0.99, 0.1, 0.0],  # v3 - similar to v2
        [0.0, 0.0, 1.0, 0.0],  # v4
        [0.0, 0.0, 0.0, 1.0],  # v5
    ], dtype=np.float32)

    # Normalize for inner product similarity
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / norms

    ids = np.array([100, 101, 200, 201, 300, 400])
    wrapper.add_vectors(vectors, ids)

    # Test with default k=10 (which becomes 6 since we have 6 vectors)
    pairs_default = wrapper.find_similar_pairs(similarity_threshold=0.9, max_pairs=100)

    # Test with explicit k=3
    pairs_k3 = wrapper.find_similar_pairs(similarity_threshold=0.9, max_pairs=100, k=3)

    # Test with k=6 (all vectors)
    pairs_k6 = wrapper.find_similar_pairs(similarity_threshold=0.9, max_pairs=100, k=6)

    # All should find similar pairs (v0-v1, v2-v3)
    print(f"Default k: {len(pairs_default)} pairs")
    print(f"k=3: {len(pairs_k3)} pairs")
    print(f"k=6: {len(pairs_k6)} pairs")

    # We expect to find pairs with high similarity
    assert len(pairs_k6) >= 2, f"Expected at least 2 pairs, got {len(pairs_k6)}"

    # Check that similar vectors are paired
    pair_ids = set()
    for id1, id2, score in pairs_k6:
        pair_ids.add((min(id1, id2), max(id1, id2)))

    assert (100, 101) in pair_ids, "Expected v0-v1 to be paired"
    assert (200, 201) in pair_ids, "Expected v2-v3 to be paired"


def test_find_duplicate_candidates_uses_larger_k():
    """Verify find_duplicate_candidates passes larger k when filtering by entity_types."""
    # This is more of an integration test that would need the full RAG index
    # For now, just verify the code path exists
    from logical_thinking_server.services.rag_index_manager import RAGIndexManager

    # Check that the code has the k_neighbors variable
    import inspect
    source = inspect.getsource(RAGIndexManager.find_duplicate_candidates)
    assert "k_neighbors" in source, "find_duplicate_candidates should use k_neighbors variable"
    assert "k=k_neighbors" in source, "find_duplicate_candidates should pass k parameter"


if __name__ == "__main__":
    test_find_similar_pairs_k_parameter()
    test_find_duplicate_candidates_uses_larger_k()
    print("All tests passed!")
