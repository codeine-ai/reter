"""
Test incremental SWRL rule loading.

This test isolates the issue where SWRL rules loaded after facts
or in separate load_ontology() calls don't fire properly.

The expected behavior is that rules should fire regardless of
when they are loaded (before or after facts).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


class TestSimpleIncrementalRules:
    """Tests for simple (non-transitive) incremental SWRL rule loading."""

    def test_rule_and_fact_together(self):
        """BASELINE: Rule and fact loaded together should work."""
        r = Reter(variant="ai")

        r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
            hasParent(alice, bob)
        """)

        facts = r.pattern(('alice', 'hasAncestor', 'bob'))
        assert len(facts) > 0, "Rule should fire when loaded together with fact"

    def test_fact_first_then_rule(self):
        """Fact loaded first, then rule - should still work."""
        r = Reter(variant="ai")

        r.load_ontology("""
            hasParent(alice, bob)
        """)

        r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
        """)

        facts = r.pattern(('alice', 'hasAncestor', 'bob'))
        assert len(facts) > 0, "Rule loaded after fact should still fire"

    def test_rule_first_then_fact(self):
        """Rule loaded first, then fact - should fire when fact arrives."""
        r = Reter(variant="ai")

        r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
        """)

        r.load_ontology("""
            hasParent(alice, bob)
        """)

        facts = r.pattern(('alice', 'hasAncestor', 'bob'))
        assert len(facts) > 0, "Rule loaded before fact should fire when fact arrives"

    def test_namespaced_rule(self):
        """Test rule with namespace prefix."""
        r = Reter(variant="ai")

        r.load_ontology("""
            if py:calls(object x, object y) then py:callsTransitive(object x, object y)
        """)

        r.load_ontology("""
            py:calls(FuncA, FuncB)
        """)

        facts = r.pattern(('FuncA', 'py:callsTransitive', 'FuncB'))
        assert len(facts) > 0, "Rule with namespace should fire"


class TestTransitiveRules:
    """Tests for transitive (chained) inference rules."""

    def test_transitive_in_one_load(self):
        """BASELINE: Transitive rules should work when loaded together."""
        r = Reter(variant="ai")

        r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
            if hasAncestor(object x, object y) also hasAncestor(object y, object z) then hasAncestor(object x, object z)
            hasParent(alice, bob)
            hasParent(bob, charlie)
        """)

        direct_ab = r.pattern(('alice', 'hasAncestor', 'bob'))
        direct_bc = r.pattern(('bob', 'hasAncestor', 'charlie'))
        transitive = r.pattern(('alice', 'hasAncestor', 'charlie'))

        print(f"Direct alice->bob: {len(direct_ab)}")
        print(f"Direct bob->charlie: {len(direct_bc)}")
        print(f"Transitive alice->charlie: {len(transitive)}")

        assert len(direct_ab) > 0, "Direct hasAncestor alice->bob should be inferred"
        assert len(direct_bc) > 0, "Direct hasAncestor bob->charlie should be inferred"
        assert len(transitive) > 0, "Transitive hasAncestor alice->charlie should be inferred"

    def test_transitive_incremental_rules(self):
        """BUG TEST: Transitive rules loaded incrementally."""
        r = Reter(variant="ai")

        # Load first rule
        wme1 = r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
        """)
        print(f"After rule 1: {wme1} WMEs")

        # Load second rule (transitive)
        wme2 = r.load_ontology("""
            if hasAncestor(object x, object y) also hasAncestor(object y, object z) then hasAncestor(object x, object z)
        """)
        print(f"After rule 2: {wme2} WMEs")

        # Load facts
        wme3 = r.load_ontology("""
            hasParent(alice, bob)
            hasParent(bob, charlie)
        """)
        print(f"After facts: {wme3} WMEs")

        direct_ab = r.pattern(('alice', 'hasAncestor', 'bob'))
        direct_bc = r.pattern(('bob', 'hasAncestor', 'charlie'))
        transitive = r.pattern(('alice', 'hasAncestor', 'charlie'))

        print(f"Direct alice->bob: {len(direct_ab)}")
        print(f"Direct bob->charlie: {len(direct_bc)}")
        print(f"Transitive alice->charlie: {len(transitive)}")

        assert len(direct_ab) > 0, "Direct hasAncestor alice->bob should be inferred"
        assert len(direct_bc) > 0, "Direct hasAncestor bob->charlie should be inferred"
        assert len(transitive) > 0, "Transitive hasAncestor alice->charlie should be inferred"

    def test_transitive_facts_first(self):
        """BUG TEST: Facts loaded first, then transitive rules."""
        r = Reter(variant="ai")

        # Load facts first
        r.load_ontology("""
            hasParent(alice, bob)
            hasParent(bob, charlie)
        """)

        # Load rules after
        r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
            if hasAncestor(object x, object y) also hasAncestor(object y, object z) then hasAncestor(object x, object z)
        """)

        direct_ab = r.pattern(('alice', 'hasAncestor', 'bob'))
        transitive = r.pattern(('alice', 'hasAncestor', 'charlie'))

        print(f"Direct: {len(direct_ab)}, Transitive: {len(transitive)}")

        assert len(direct_ab) > 0, "Direct hasAncestor should be inferred"
        assert len(transitive) > 0, "Transitive hasAncestor should be inferred"


class TestPyOntologyRules:
    """Tests for py_ontology.reol bundled rules."""

    def test_py_calls_transitive_chain(self):
        """Test py:callsTransitive with a chain of calls."""
        r = Reter(variant="ai")

        # Load the transitive rule (like py_ontology.reol)
        r.load_ontology("""
            if py:calls(object x, object y) then py:callsTransitive(object x, object y)
            if py:callsTransitive(object x, object y) also py:callsTransitive(object y, object z) then py:callsTransitive(object x, object z)
        """)

        # Load call chain
        r.load_ontology("""
            py:calls(FuncA, FuncB)
            py:calls(FuncB, FuncC)
        """)

        direct_ab = r.pattern(('FuncA', 'py:callsTransitive', 'FuncB'))
        direct_bc = r.pattern(('FuncB', 'py:callsTransitive', 'FuncC'))
        transitive = r.pattern(('FuncA', 'py:callsTransitive', 'FuncC'))

        print(f"Direct A->B: {len(direct_ab)}")
        print(f"Direct B->C: {len(direct_bc)}")
        print(f"Transitive A->C: {len(transitive)}")

        assert len(direct_ab) > 0, "Direct py:callsTransitive A->B should be inferred"
        assert len(direct_bc) > 0, "Direct py:callsTransitive B->C should be inferred"
        assert len(transitive) > 0, "Transitive py:callsTransitive A->C should be inferred"


class TestGanttRules:
    """Tests for gantt rules similar to gantt_rules.reol."""

    def test_gantt_blocks_relationship(self):
        """Test that gantt:depends_on creates gantt:blocks."""
        r = Reter(variant="ai")

        r.load_ontology("""
            if gantt:depends_on(object a, object b) then gantt:blocks(object b, object a)
        """)

        r.load_ontology("""
            gantt:depends_on(TaskA, TaskB)
        """)

        facts = r.pattern(('TaskB', 'gantt:blocks', 'TaskA'))
        assert len(facts) > 0, "gantt:blocks should be inferred"

    def test_gantt_transitive_dependency(self):
        """Test transitive dependency inference."""
        r = Reter(variant="ai")

        # Load both rules together
        r.load_ontology("""
            if gantt:depends_on(object a, object b) then gantt:transitively_depends_on(object a, object b)
            if gantt:depends_on(object a, object b) also gantt:depends_on(object b, object c) then gantt:transitively_depends_on(object a, object c)
        """)

        r.load_ontology("""
            gantt:depends_on(TaskA, TaskB)
            gantt:depends_on(TaskB, TaskC)
        """)

        direct = r.pattern(('TaskA', 'gantt:transitively_depends_on', 'TaskB'))
        transitive = r.pattern(('TaskA', 'gantt:transitively_depends_on', 'TaskC'))

        print(f"Direct: {len(direct)}, Transitive: {len(transitive)}")

        assert len(direct) > 0, "Direct transitively_depends_on should be inferred"
        assert len(transitive) > 0, "Transitive transitively_depends_on should be inferred"


class TestDebugInfo:
    """Debug tests to understand RETER behavior."""

    def test_dump_all_facts(self):
        """Dump all facts to understand what's being inferred."""
        r = Reter(variant="ai")

        r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
            if hasAncestor(object x, object y) also hasAncestor(object y, object z) then hasAncestor(object x, object z)
            hasParent(alice, bob)
            hasParent(bob, charlie)
        """)

        # Get all hasAncestor facts using REQL query
        all_ancestor = r.reql("SELECT ?s ?o WHERE { ?s hasAncestor ?o }")
        print(f"\nAll hasAncestor facts ({len(all_ancestor)}):")
        for fact in all_ancestor:
            print(f"  {fact}")

        # Also check hasParent facts
        all_parent = r.reql("SELECT ?s ?o WHERE { ?s hasParent ?o }")
        print(f"\nAll hasParent facts ({len(all_parent)}):")
        for fact in all_parent:
            print(f"  {fact}")

    def test_rule_wme_count(self):
        """Check WME count when loading rules."""
        r = Reter(variant="ai")

        wme1 = r.load_ontology("""
            if hasParent(object x, object y) then hasAncestor(object x, object y)
        """)
        print(f"Simple rule WME count: {wme1}")

        wme2 = r.load_ontology("""
            if hasAncestor(object x, object y) also hasAncestor(object y, object z) then hasAncestor(object x, object z)
        """)
        print(f"Transitive rule WME count: {wme2}")

        wme3 = r.load_ontology("""
            hasParent(alice, bob)
        """)
        print(f"Fact WME count: {wme3}")

        # Rules return 1 WME each, facts return 1 WME
        # This shows rules ARE being registered


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
