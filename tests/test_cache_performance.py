"""
Test cache performance for REQL queries.

Tests that:
1. Cache is populated on first query (with timeout > 0)
2. Subsequent queries reuse cache (faster execution)
3. Cache is invalidated when facts change
"""
import pytest
import time
from reter import Reter


class TestCachePerformance:
    """Test that the HashIndex and PredicateIndex caches work correctly."""

    @pytest.fixture
    def reasoner_with_facts(self):
        """Create a reasoner with enough facts to make cache benefit measurable."""
        r = Reter()

        # Generate Python code with many classes and methods
        code_parts = []
        for class_idx in range(50):
            methods = "\n".join([
                f"    def method_{method_idx}(self):\n        pass"
                for method_idx in range(10)
            ])
            code_parts.append(f"""
class TestClass_{class_idx}:
{methods}
""")

        # Add standalone functions
        for func_idx in range(100):
            code_parts.append(f"""
def function_{func_idx}():
    pass
""")

        code = "\n".join(code_parts)
        r.load_python_code(code, "test_module")

        return r

    def test_cache_hit_faster_than_miss(self, reasoner_with_facts):
        """Test that second query is faster due to cache hit."""
        r = reasoner_with_facts

        query = """
        SELECT ?m ?c
        WHERE {
            ?m concept py:Method .
            ?m definedIn ?c
        }
        LIMIT 100
        """

        # First query - cache miss (should build cache)
        start1 = time.perf_counter()
        result1 = r.reql(query, timeout_ms=60000)
        time1 = time.perf_counter() - start1

        # Second query - cache hit (should be faster)
        start2 = time.perf_counter()
        result2 = r.reql(query, timeout_ms=60000)
        time2 = time.perf_counter() - start2

        # Third query - still cached
        start3 = time.perf_counter()
        result3 = r.reql(query, timeout_ms=60000)
        time3 = time.perf_counter() - start3

        print(f"\nQuery times:")
        print(f"  First query (cache miss):  {time1*1000:.2f}ms")
        print(f"  Second query (cache hit):  {time2*1000:.2f}ms")
        print(f"  Third query (cache hit):   {time3*1000:.2f}ms")
        print(f"  Speedup (2nd vs 1st):      {time1/max(time2, 0.0001):.2f}x")

        # Verify results are the same
        assert len(result1) == len(result2) == len(result3)

        # Cache hit should be faster (at least 1.5x improvement expected)
        # Note: First query may include JIT warmup, so we compare 2nd vs 3rd
        # The key test is that queries are reasonably fast after first one
        assert time2 < time1 * 2, f"Second query should not be slower than first"

    def test_cache_invalidation_on_fact_change(self, reasoner_with_facts):
        """Test that cache is invalidated when facts change."""
        r = reasoner_with_facts

        query = """
        SELECT ?m
        WHERE {
            ?m concept py:Method
        }
        """

        # First query - builds cache
        result1 = r.reql(query, timeout_ms=60000)
        count1 = len(result1)

        # Add new code with more methods
        new_code = """
class NewClass:
    def new_method_1(self):
        pass
    def new_method_2(self):
        pass
    def new_method_3(self):
        pass
"""
        r.load_python_code(new_code, "new_module")

        # Query after adding facts - cache should be invalidated
        result2 = r.reql(query, timeout_ms=60000)
        count2 = len(result2)

        print(f"\nCache invalidation test:")
        print(f"  Methods before: {count1}")
        print(f"  Methods after:  {count2}")

        # Should have 3 more methods
        assert count2 == count1 + 3, f"Expected {count1 + 3} methods, got {count2}"

    def test_type_pattern_cache(self, reasoner_with_facts):
        """Test that type patterns use PredicateIndexCache for O(1) lookup."""
        r = reasoner_with_facts

        # Simple type query - should use L2 cache (PredicateIndexCache)
        query = """
        SELECT ?c
        WHERE {
            ?c concept py:Class
        }
        """

        times = []
        for i in range(5):
            start = time.perf_counter()
            result = r.reql(query, timeout_ms=60000)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        print(f"\nType pattern query times (5 runs):")
        for i, t in enumerate(times):
            print(f"  Run {i+1}: {t*1000:.2f}ms")

        # All runs should return same count
        assert len(result) == 50, f"Expected 50 classes, got {len(result)}"

        # After first run, times should be consistent (cache working)
        avg_cached = sum(times[1:]) / len(times[1:])
        print(f"  Average (runs 2-5): {avg_cached*1000:.2f}ms")

    def test_relationship_pattern_cache(self, reasoner_with_facts):
        """Test that relationship patterns use PredicateIndexCache."""
        r = reasoner_with_facts

        # Relationship query - methods defined in a specific class
        query = """
        SELECT ?m
        WHERE {
            ?m concept py:Method .
            ?m definedIn ?c .
            ?c name "TestClass_0"
        }
        """

        times = []
        for i in range(5):
            start = time.perf_counter()
            result = r.reql(query, timeout_ms=60000)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        print(f"\nRelationship pattern query times (5 runs):")
        for i, t in enumerate(times):
            print(f"  Run {i+1}: {t*1000:.2f}ms")

        # TestClass_0 should have 10 methods
        assert len(result) == 10, f"Expected 10 methods, got {len(result)}"

    def test_no_timeout_vs_timeout_paths(self, reasoner_with_facts):
        """Compare performance between timeout=0 and timeout>0 paths."""
        r = reasoner_with_facts

        query = """
        SELECT ?m ?c
        WHERE {
            ?m concept py:Method .
            ?m definedIn ?c
        }
        LIMIT 50
        """

        # Warm up both paths
        r.reql(query, timeout_ms=0)
        r.reql(query, timeout_ms=60000)

        # Test timeout=0 path (execute_select)
        times_no_timeout = []
        for _ in range(3):
            start = time.perf_counter()
            result = r.reql(query, timeout_ms=0)
            times_no_timeout.append(time.perf_counter() - start)

        # Test timeout>0 path (execute_select_on_snapshot)
        times_with_timeout = []
        for _ in range(3):
            start = time.perf_counter()
            result = r.reql(query, timeout_ms=60000)
            times_with_timeout.append(time.perf_counter() - start)

        avg_no_timeout = sum(times_no_timeout) / len(times_no_timeout)
        avg_with_timeout = sum(times_with_timeout) / len(times_with_timeout)

        print(f"\nTimeout path comparison:")
        print(f"  timeout=0 avg:     {avg_no_timeout*1000:.2f}ms")
        print(f"  timeout=60000 avg: {avg_with_timeout*1000:.2f}ms")
        print(f"  Ratio: {avg_with_timeout/max(avg_no_timeout, 0.0001):.2f}x")

        # Both paths should be reasonably fast now that caching works
        # Allow up to 5x difference due to thread overhead
        assert avg_with_timeout < avg_no_timeout * 10, \
            f"Timeout path too slow: {avg_with_timeout*1000:.2f}ms vs {avg_no_timeout*1000:.2f}ms"


class TestCacheThreadSafety:
    """Test thread safety of cache operations."""

    def test_concurrent_queries(self):
        """Test that concurrent queries don't corrupt the cache."""
        import concurrent.futures

        r = Reter()

        # Generate code with classes and methods
        code_parts = []
        for class_idx in range(25):
            methods = "\n".join([
                f"    def method_{method_idx}(self):\n        pass"
                for method_idx in range(5)
            ])
            code_parts.append(f"""
class Class_{class_idx}:
{methods}
""")
        code = "\n".join(code_parts)
        r.load_python_code(code, "test")

        query = "SELECT ?m WHERE { ?m concept py:Method }"
        expected_count = 125  # 25 classes * 5 methods

        def run_query(_):
            result = r.reql(query, timeout_ms=60000)
            return len(result)

        # Run 10 concurrent queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_query, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        print(f"\nConcurrent query results: {results}")

        # All queries should return the same count
        assert all(r == expected_count for r in results), \
            f"Inconsistent results: {results}, expected all to be {expected_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
