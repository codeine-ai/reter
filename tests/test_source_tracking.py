"""
Comprehensive pytest tests for source tracking functionality.

Tests various orderings of add, remove, serialize, and deserialize operations
to ensure source tracking works correctly in all scenarios.
"""
import pytest
import os
import tempfile
from pathlib import Path
from reter_core.owl_rete_cpp import ReteNetwork, Fact


@pytest.fixture
def temp_file():
    """Provide a temporary file for serialization tests."""
    fd, path = tempfile.mkstemp(suffix='.reter')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def sample_facts():
    """Provide sample facts for testing."""
    return [
        (Fact({"type": "Class", "id": "Person"}), "ontology"),
        (Fact({"type": "Class", "id": "Animal"}), "ontology"),
        (Fact({"type": "SubClassOf", "sub": "Person", "super": "Animal"}), "ontology"),
        (Fact({"type": "Individual", "id": "Alice"}), "data"),
        (Fact({"type": "Individual", "id": "Bob"}), "data"),
        (Fact({"type": "Type", "individual": "Alice", "class": "Person"}), "data"),
        (Fact({"type": "Rule", "id": "rule1"}), "rules"),
        (Fact({"type": "Rule", "id": "rule2"}), "rules"),
    ]


class TestBasicSourceTracking:
    """Test basic source tracking functionality."""

    def test_add_with_source(self):
        """Test adding facts with source tracking."""
        net = ReteNetwork()
        fact = Fact({"type": "Class", "id": "Person"})

        fact_id = net.add_fact_with_source(fact, "source1")
        # After WME ID refactoring, fact_id is now a signature (content-based)
        assert fact_id is not None and len(fact_id) > 0
        assert len(net.get_all_facts()) == 1

    def test_remove_source(self):
        """Test removing all facts from a source."""
        net = ReteNetwork()

        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "C"}), "s2")

        assert len(net.get_all_facts()) == 3

        net.remove_source("s1")
        assert len(net.get_all_facts()) == 1

    def test_remove_nonexistent_source(self):
        """Test that removing non-existent source doesn't error."""
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")

        # Should not raise an error
        net.remove_source("nonexistent")
        assert len(net.get_all_facts()) == 1

    def test_multiple_sources(self, sample_facts):
        """Test tracking facts from multiple sources."""
        net = ReteNetwork()

        for fact, source in sample_facts:
            net.add_fact_with_source(fact, source)

        assert len(net.get_all_facts()) == 8

        # Remove each source and verify count
        net.remove_source("ontology")
        assert len(net.get_all_facts()) == 5

        net.remove_source("data")
        assert len(net.get_all_facts()) == 2

        net.remove_source("rules")
        assert len(net.get_all_facts()) == 0


class TestSerializationBasic:
    """Test basic serialization with source tracking."""

    def test_save_load_preserves_facts(self, temp_file, sample_facts):
        """Test that save/load preserves all facts."""
        net = ReteNetwork()
        for fact, source in sample_facts:
            net.add_fact_with_source(fact, source)

        net.save(temp_file)

        net2 = ReteNetwork()
        net2.load(temp_file)

        assert len(net2.get_all_facts()) == len(sample_facts)

    def test_save_load_preserves_source_tracking(self, temp_file):
        """Test that save/load preserves source tracking."""
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "C"}), "s2")

        net.save(temp_file)

        net2 = ReteNetwork()
        net2.load(temp_file)

        # Source tracking should work after load
        net2.remove_source("s1")
        assert len(net2.get_all_facts()) == 1

        net2.remove_source("s2")
        assert len(net2.get_all_facts()) == 0


class TestOperationOrdering:
    """Test various orderings of add, remove, save, load operations."""

    def test_add_save_load_remove(self, temp_file):
        """Test: Add → Save → Load → Remove"""
        # Add facts
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s2")

        # Save
        net.save(temp_file)

        # Load into new network
        net2 = ReteNetwork()
        net2.load(temp_file)

        # Remove
        net2.remove_source("s1")
        assert len(net2.get_all_facts()) == 1

    def test_add_remove_save_load(self, temp_file):
        """Test: Add → Remove → Save → Load"""
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s2")
        net.add_fact_with_source(Fact({"type": "Class", "id": "C"}), "s3")

        # Remove one source
        net.remove_source("s2")
        assert len(net.get_all_facts()) == 2

        # Save
        net.save(temp_file)

        # Load and verify
        net2 = ReteNetwork()
        net2.load(temp_file)
        assert len(net2.get_all_facts()) == 2

        # Source tracking should still work
        net2.remove_source("s1")
        assert len(net2.get_all_facts()) == 1

    def test_save_empty_load_add_remove(self, temp_file):
        """Test: Save Empty → Load → Add → Remove"""
        # Save empty network
        net = ReteNetwork()
        net.save(temp_file)

        # Load and add
        net2 = ReteNetwork()
        net2.load(temp_file)
        net2.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")

        assert len(net2.get_all_facts()) == 1

        # Remove should work
        net2.remove_source("s1")
        assert len(net2.get_all_facts()) == 0

    def test_multiple_save_load_cycles(self, temp_file):
        """Test: Add → Save → Load → Add → Save → Load"""
        # First cycle
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")
        net.save(temp_file)

        # Load and add more
        net2 = ReteNetwork()
        net2.load(temp_file)
        net2.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s2")
        net2.save(temp_file)

        # Load again and verify
        net3 = ReteNetwork()
        net3.load(temp_file)
        assert len(net3.get_all_facts()) == 2

        # Both sources should be tracked
        net3.remove_source("s1")
        assert len(net3.get_all_facts()) == 1
        net3.remove_source("s2")
        assert len(net3.get_all_facts()) == 0

    def test_interleaved_operations(self, temp_file):
        """Test: Add → Save → Load → Add → Remove → Save → Load → Remove"""
        # Initial add and save
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s2")
        net.save(temp_file)

        # Load, add, remove, save
        net2 = ReteNetwork()
        net2.load(temp_file)
        net2.add_fact_with_source(Fact({"type": "Class", "id": "C"}), "s3")
        net2.remove_source("s2")
        assert len(net2.get_all_facts()) == 2  # A and C
        net2.save(temp_file)

        # Load and verify final state
        net3 = ReteNetwork()
        net3.load(temp_file)
        assert len(net3.get_all_facts()) == 2

        # Verify source tracking
        net3.remove_source("s1")
        assert len(net3.get_all_facts()) == 1
        net3.remove_source("s3")
        assert len(net3.get_all_facts()) == 0


class TestComplexScenarios:
    """Test complex scenarios with multiple operations."""

    def test_same_fact_different_sources(self):
        """Test adding the same fact from different sources."""
        net = ReteNetwork()

        # Add same fact twice (should deduplicate based on signature)
        fact1 = Fact({"type": "Class", "id": "Person"})
        fact2 = Fact({"type": "Class", "id": "Person"})

        id1 = net.add_fact_with_source(fact1, "s1")
        id2 = net.add_fact_with_source(fact2, "s2")

        # Should be deduplicated (same signature)
        assert len(net.get_all_facts()) == 1
        # After WME ID refactoring, fact_id is now a signature (content-based)
        # First add returns fact signature, second returns empty string (duplicate)
        assert id1 is not None and len(id1) > 0
        assert id2 == ""

        # The fact is tracked under the first source (s1)
        # Removing s2 won't remove it (it was never added under s2)
        net.remove_source("s2")
        assert len(net.get_all_facts()) == 1

        # Removing s1 will remove it
        net.remove_source("s1")
        assert len(net.get_all_facts()) == 0

    def test_cascade_add_remove_save_load(self, temp_file):
        """Test cascading operations across save/load boundaries."""
        operations = []

        # Round 1: Add and save
        net = ReteNetwork()
        for i in range(5):
            net.add_fact_with_source(
                Fact({"type": "Class", "id": f"C{i}"}),
                f"source_{i % 3}"
            )
        operations.append(("add", 5))
        net.save(temp_file)

        # Round 2: Load, remove, add, save
        net = ReteNetwork()
        net.load(temp_file)
        net.remove_source("source_0")
        operations.append(("remove_source_0", -2))  # C0, C3
        net.add_fact_with_source(Fact({"type": "Class", "id": "C5"}), "source_3")
        operations.append(("add", 1))
        net.save(temp_file)

        # Round 3: Load and verify
        net = ReteNetwork()
        net.load(temp_file)
        expected = 5 - 2 + 1  # 4 facts
        assert len(net.get_all_facts()) == expected

    def test_remove_all_sources_sequentially(self, sample_facts, temp_file):
        """Test removing all sources one by one with saves in between."""
        net = ReteNetwork()
        for fact, source in sample_facts:
            net.add_fact_with_source(fact, source)

        sources = ["ontology", "data", "rules"]

        for source in sources:
            net.remove_source(source)
            net.save(temp_file)

            # Load and verify
            net2 = ReteNetwork()
            net2.load(temp_file)

            # Calculate expected count
            remaining_sources = [s for s in sources if s not in sources[:sources.index(source) + 1]]
            expected = sum(1 for _, s in sample_facts if s in remaining_sources)
            assert len(net2.get_all_facts()) == expected

            # Continue with original network
            net = net2

    def test_mixed_tracked_and_untracked_facts(self):
        """Test mixing facts with and without source tracking."""
        net = ReteNetwork()

        # Add with source
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")

        # Add without source (using regular add_fact)
        net.add_fact(Fact({"type": "Class", "id": "B"}))

        # Add with different source
        net.add_fact_with_source(Fact({"type": "Class", "id": "C"}), "s2")

        assert len(net.get_all_facts()) == 3

        # Remove s1 - should only remove A
        net.remove_source("s1")
        assert len(net.get_all_facts()) == 2

        # Remove s2 - should only remove C
        net.remove_source("s2")
        assert len(net.get_all_facts()) == 1  # B remains

    def test_stress_many_sources(self, temp_file):
        """Test with many sources and facts."""
        net = ReteNetwork()

        num_sources = 50
        facts_per_source = 10

        # Add many facts across many sources
        for s_idx in range(num_sources):
            for f_idx in range(facts_per_source):
                net.add_fact_with_source(
                    Fact({"type": "Class", "id": f"C_{s_idx}_{f_idx}"}),
                    f"source_{s_idx}"
                )

        total = num_sources * facts_per_source
        assert len(net.get_all_facts()) == total

        # Save and load
        net.save(temp_file)
        net2 = ReteNetwork()
        net2.load(temp_file)
        assert len(net2.get_all_facts()) == total

        # Remove every other source
        for s_idx in range(0, num_sources, 2):
            net2.remove_source(f"source_{s_idx}")

        expected = (num_sources // 2) * facts_per_source
        if num_sources % 2 == 1:
            expected += facts_per_source
        assert len(net2.get_all_facts()) == expected

    def test_alternating_add_remove_save_load(self, temp_file):
        """Test: (Add → Remove → Save → Load) × N"""
        net = ReteNetwork()

        for iteration in range(5):
            # Add facts
            for i in range(3):
                net.add_fact_with_source(
                    Fact({"type": "Class", "id": f"C_{iteration}_{i}"}),
                    f"source_{iteration}"
                )

            # Remove previous iteration's source (if exists)
            if iteration > 0:
                net.remove_source(f"source_{iteration - 1}")

            # Save
            net.save(temp_file)

            # Load into new network
            net = ReteNetwork()
            net.load(temp_file)

            # Verify we only have current iteration's facts
            expected = 3  # Current iteration only
            assert len(net.get_all_facts()) == expected

    def test_empty_network_serialization_cycle(self, temp_file):
        """Test: Empty → Save → Load → Add → Remove → Save → Load"""
        # Save empty
        net = ReteNetwork()
        net.save(temp_file)

        # Load empty
        net = ReteNetwork()
        net.load(temp_file)
        assert len(net.get_all_facts()) == 0

        # Add facts
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s2")
        assert len(net.get_all_facts()) == 2

        # Remove one
        net.remove_source("s1")
        assert len(net.get_all_facts()) == 1

        # Save
        net.save(temp_file)

        # Load and verify
        net = ReteNetwork()
        net.load(temp_file)
        assert len(net.get_all_facts()) == 1

        # Source tracking should work
        net.remove_source("s2")
        assert len(net.get_all_facts()) == 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_source_id(self):
        """Test adding with empty source ID."""
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "")
        assert len(net.get_all_facts()) == 1

        # Should be able to remove with empty source
        net.remove_source("")
        assert len(net.get_all_facts()) == 0

    def test_special_characters_in_source_id(self):
        """Test source IDs with special characters."""
        net = ReteNetwork()

        special_sources = [
            "source/with/slashes",
            "source\\with\\backslashes",
            "source.with.dots",
            "source-with-dashes",
            "source_with_underscores",
            "source with spaces",
            "source@with#special$chars",
        ]

        for idx, source in enumerate(special_sources):
            net.add_fact_with_source(
                Fact({"type": "Class", "id": f"C{idx}"}),
                source
            )

        assert len(net.get_all_facts()) == len(special_sources)

        # Remove each one
        for source in special_sources:
            net.remove_source(source)

        assert len(net.get_all_facts()) == 0

    def test_very_long_source_id(self):
        """Test with very long source IDs."""
        net = ReteNetwork()
        long_source = "s" * 10000

        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), long_source)
        assert len(net.get_all_facts()) == 1

        net.remove_source(long_source)
        assert len(net.get_all_facts()) == 0

    def test_unicode_in_source_id(self):
        """Test source IDs with Unicode characters."""
        net = ReteNetwork()

        unicode_sources = [
            "源代码",  # Chinese
            "مصدر",    # Arabic
            "исходник",  # Russian
            "🎯🎨🎭",  # Emojis
        ]

        for idx, source in enumerate(unicode_sources):
            net.add_fact_with_source(
                Fact({"type": "Class", "id": f"C{idx}"}),
                source
            )

        assert len(net.get_all_facts()) == len(unicode_sources)

        for source in unicode_sources:
            net.remove_source(source)

        assert len(net.get_all_facts()) == 0

    def test_remove_source_twice(self):
        """Test removing the same source twice."""
        net = ReteNetwork()
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")

        net.remove_source("s1")
        assert len(net.get_all_facts()) == 0

        # Second remove should be safe
        net.remove_source("s1")
        assert len(net.get_all_facts()) == 0

    def test_rapid_add_remove_cycles(self):
        """Test rapid cycles of add and remove."""
        net = ReteNetwork()

        for cycle in range(100):
            # Add
            net.add_fact_with_source(
                Fact({"type": "Class", "id": f"C{cycle}"}),
                f"s{cycle}"
            )
            assert len(net.get_all_facts()) == 1

            # Remove
            net.remove_source(f"s{cycle}")
            assert len(net.get_all_facts()) == 0


class TestConcurrentSourceOperations:
    """Test scenarios with multiple sources being manipulated."""

    def test_add_to_existing_source(self):
        """Test adding more facts to an existing source."""
        net = ReteNetwork()

        # Add initial fact
        net.add_fact_with_source(Fact({"type": "Class", "id": "A"}), "s1")

        # Add more to same source
        net.add_fact_with_source(Fact({"type": "Class", "id": "B"}), "s1")
        net.add_fact_with_source(Fact({"type": "Class", "id": "C"}), "s1")

        assert len(net.get_all_facts()) == 3

        # Removing source should remove all
        net.remove_source("s1")
        assert len(net.get_all_facts()) == 0

    def test_partial_source_removal_pattern(self, temp_file):
        """Test pattern: Add many sources, remove some, save, load, verify."""
        net = ReteNetwork()

        # Add 10 sources with 3 facts each
        for s in range(10):
            for f in range(3):
                net.add_fact_with_source(
                    Fact({"type": "Class", "id": f"C_{s}_{f}"}),
                    f"source_{s}"
                )

        assert len(net.get_all_facts()) == 30

        # Remove sources 0, 2, 4, 6, 8 (every other)
        for s in range(0, 10, 2):
            net.remove_source(f"source_{s}")

        assert len(net.get_all_facts()) == 15

        # Save and load
        net.save(temp_file)
        net2 = ReteNetwork()
        net2.load(temp_file)
        assert len(net2.get_all_facts()) == 15

        # Remove odd sources
        for s in range(1, 10, 2):
            net2.remove_source(f"source_{s}")

        assert len(net2.get_all_facts()) == 0


class TestSourceTrackingWithQueries:
    """Test source tracking interaction with queries."""

    def test_query_after_source_removal(self):
        """Test that queries work correctly after removing sources."""
        net = ReteNetwork()

        # Add facts from different sources
        net.add_fact_with_source(
            Fact({"type": "Class", "id": "Person"}), "ontology"
        )
        net.add_fact_with_source(
            Fact({"type": "Individual", "id": "Alice"}), "data"
        )

        # Remove one source
        net.remove_source("data")

        # Query should only return remaining facts
        facts = net.get_all_facts()
        assert len(facts) == 1
        assert facts[0]["id"] == "Person"

    def test_source_removal_invalidates_cache(self, temp_file):
        """Test that source removal properly invalidates caches."""
        net = ReteNetwork()

        # Add facts
        for i in range(100):
            net.add_fact_with_source(
                Fact({"type": "Class", "id": f"C{i}"}),
                "source1"
            )

        # Trigger cache population
        _ = net.get_all_facts()

        # Remove source (should invalidate cache)
        net.remove_source("source1")

        # Query should reflect removal
        assert len(net.get_all_facts()) == 0

        # Save and load to verify
        net.save(temp_file)
        net2 = ReteNetwork()
        net2.load(temp_file)
        assert len(net2.get_all_facts()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
