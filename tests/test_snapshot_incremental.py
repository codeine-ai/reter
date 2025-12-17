"""
Test snapshot behavior with incremental updates.

Compares two scenarios:
A) Load ontologies + 2 files, remove 1, add 3rd, save snapshot (no snapshot load in between)
B) Load ontologies + 2 files, save snapshot, load snapshot, remove 1, add 3rd, save snapshot

If the network is working correctly with incremental updates, both scenarios
should produce similar snapshot sizes. If scenario B produces a much larger
snapshot, it indicates a problem with reasoning after snapshot restore.

KNOWN ISSUE: After snapshot load, adding new facts causes reasoning to blow up.
Instead of incremental updates, the inference engine re-processes everything,
causing exponential growth in derived facts:
- Scenario A (no snapshot load): 727 facts, 437KB
- Scenario B (with snapshot load): 1165 facts, 5.8MB (13x larger!)
"""

import sys
import os
import pytest
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

# Ontology paths
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
OO_ONTOLOGY_PATH = os.path.join(PROJECT_ROOT, "reter-logical-thinking-server", "resources", "oo_ontology.reol")
PY_ONTOLOGY_PATH = os.path.join(PROJECT_ROOT, "reter-logical-thinking-server", "resources", "python", "py_ontology.reol")


def create_reasoner_with_ontologies() -> Reter:
    """Create a Reter instance with oo_ontology and py_ontology loaded."""
    reasoner = Reter(variant="ai")  # Use AI variant which supports comments

    # Load oo_ontology first (base object-oriented concepts)
    with open(OO_ONTOLOGY_PATH, 'r', encoding='utf-8') as f:
        oo_ontology = f.read()
    reasoner.load_ontology(oo_ontology, source="oo_ontology")

    # Load py_ontology (Python-specific concepts, depends on oo_ontology)
    with open(PY_ONTOLOGY_PATH, 'r', encoding='utf-8') as f:
        py_ontology = f.read()
    reasoner.load_ontology(py_ontology, source="py_ontology")

    return reasoner


# Sample Python files for testing
PYTHON_FILE_1 = """
class Animal:
    \"\"\"Base class for all animals.\"\"\"

    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."

    def move(self) -> str:
        return "moving"


class Dog(Animal):
    \"\"\"A dog is an animal that barks.\"\"\"

    def speak(self) -> str:
        return "Woof!"

    def fetch(self, item: str) -> str:
        return f"Fetching {item}"
"""

PYTHON_FILE_2 = """
class Vehicle:
    \"\"\"Base class for all vehicles.\"\"\"

    def __init__(self, brand: str, model: str):
        self.brand = brand
        self.model = model

    def start(self) -> bool:
        return True

    def stop(self) -> bool:
        return True


class Car(Vehicle):
    \"\"\"A car is a vehicle with wheels.\"\"\"

    def __init__(self, brand: str, model: str, doors: int = 4):
        super().__init__(brand, model)
        self.doors = doors

    def honk(self) -> str:
        return "Beep!"

    def drive(self, destination: str) -> str:
        return f"Driving to {destination}"
"""

PYTHON_FILE_3 = """
class Shape:
    \"\"\"Base class for geometric shapes.\"\"\"

    def __init__(self):
        pass

    def area(self) -> float:
        raise NotImplementedError()

    def perimeter(self) -> float:
        raise NotImplementedError()


class Circle(Shape):
    \"\"\"A circle shape.\"\"\"

    def __init__(self, radius: float):
        super().__init__()
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    \"\"\"A rectangle shape.\"\"\"

    def __init__(self, width: float, height: float):
        super().__init__()
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)
"""


def get_wme_count(reasoner) -> int:
    """Get total WME count from network using REQL query."""
    # Query all facts with py:Class concept as a proxy for loaded content
    result = reasoner.reql("""
        SELECT ?entity
        WHERE {
            ?entity concept "py:Class"
        }
    """)
    return result.num_rows


def count_sources(reasoner) -> int:
    """Count number of sources loaded."""
    sources = reasoner.network.get_all_sources()
    return len(sources)


def test_snapshot_incremental_comparison():
    """
    Compare snapshot sizes between:
    A) Load 2 files, remove 1, add 3rd, save
    B) Load 2 files, save, load, remove 1, add 3rd, save

    Both should produce similar snapshot sizes if incremental updates
    work correctly after snapshot restore.
    """
    print("\n" + "=" * 70)
    print("TEST: Snapshot Incremental Update Comparison")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        snapshot_a = os.path.join(tmpdir, "scenario_a.reter")
        snapshot_b_intermediate = os.path.join(tmpdir, "scenario_b_intermediate.reter")
        snapshot_b_final = os.path.join(tmpdir, "scenario_b_final.reter")

        # ==========================================
        # SCENARIO A: Direct incremental (no snapshot load)
        # Load 2 files -> remove 1 -> add 3rd -> save
        # ==========================================
        print("\n--- SCENARIO A: Direct incremental (baseline) ---")

        reasoner_a = create_reasoner_with_ontologies()
        print("  Loaded oo_ontology and py_ontology")

        # Step 1: Load file 1
        wme_count_1a, errors_1a = reasoner_a.load_python_code(
            PYTHON_FILE_1, "file1.py", "file1", "source:file1"
        )
        print(f"  Loaded file1.py: {wme_count_1a} WMEs, {len(errors_1a)} errors")
        assert len(errors_1a) == 0, f"File 1 parse errors: {errors_1a}"

        # Step 2: Load file 2
        wme_count_2a, errors_2a = reasoner_a.load_python_code(
            PYTHON_FILE_2, "file2.py", "file2", "source:file2"
        )
        print(f"  Loaded file2.py: {wme_count_2a} WMEs, {len(errors_2a)} errors")
        assert len(errors_2a) == 0, f"File 2 parse errors: {errors_2a}"

        classes_after_2_files = get_wme_count(reasoner_a)
        sources_after_2_files = count_sources(reasoner_a)
        print(f"  After loading 2 files: {classes_after_2_files} classes, {sources_after_2_files} sources")

        # Step 3: Remove file 1
        print(f"  Removing source:file1...")
        reasoner_a.remove_source("source:file1")

        classes_after_remove = get_wme_count(reasoner_a)
        sources_after_remove = count_sources(reasoner_a)
        print(f"  After removing file1: {classes_after_remove} classes, {sources_after_remove} sources")

        # Check template rules before file3 in Scenario A
        prod_stats_a_before_file3 = reasoner_a.network.get_production_stats()
        template_rules_a_before = [r for r in prod_stats_a_before_file3.keys()
                                   if '-template-meta' not in r and
                                   (r.startswith('prp-') or r.startswith('cax-') or r.startswith('eq-'))]
        print(f"  Production stats before file3: {len(prod_stats_a_before_file3)} rules")
        print(f"  Template-instantiated rules before file3: {len(template_rules_a_before)}")

        # Step 4: Add file 3
        wme_count_3a, errors_3a = reasoner_a.load_python_code(
            PYTHON_FILE_3, "file3.py", "file3", "source:file3"
        )
        print(f"  Loaded file3.py: {wme_count_3a} WMEs, {len(errors_3a)} errors")
        assert len(errors_3a) == 0, f"File 3 parse errors: {errors_3a}"

        classes_final_a = get_wme_count(reasoner_a)
        sources_final_a = count_sources(reasoner_a)
        print(f"  Final state A: {classes_final_a} classes, {sources_final_a} sources")

        # Check template rules AFTER file3 in Scenario A
        prod_stats_a_after_file3 = reasoner_a.network.get_production_stats()
        template_rules_a_after = [r for r in prod_stats_a_after_file3.keys()
                                  if '-template-meta' not in r and
                                  (r.startswith('prp-') or r.startswith('cax-') or r.startswith('eq-'))]
        print(f"  Production stats after file3: {len(prod_stats_a_after_file3)} rules")
        print(f"  Template-instantiated rules after file3: {len(template_rules_a_after)}")

        # Step 5: Save snapshot A
        reasoner_a.network.save(snapshot_a)
        size_a = os.path.getsize(snapshot_a)
        print(f"  Snapshot A saved: {size_a:,} bytes")

        # ==========================================
        # SCENARIO B: With snapshot load in between
        # Load 2 files -> save -> load -> remove 1 -> add 3rd -> save
        # ==========================================
        print("\n--- SCENARIO B: With snapshot load in between ---")

        reasoner_b = create_reasoner_with_ontologies()
        print("  Loaded oo_ontology and py_ontology")

        # Step 1: Load file 1
        wme_count_1b, errors_1b = reasoner_b.load_python_code(
            PYTHON_FILE_1, "file1.py", "file1", "source:file1"
        )
        print(f"  Loaded file1.py: {wme_count_1b} WMEs, {len(errors_1b)} errors")
        assert len(errors_1b) == 0, f"File 1 parse errors: {errors_1b}"

        # Step 2: Load file 2
        wme_count_2b, errors_2b = reasoner_b.load_python_code(
            PYTHON_FILE_2, "file2.py", "file2", "source:file2"
        )
        print(f"  Loaded file2.py: {wme_count_2b} WMEs, {len(errors_2b)} errors")
        assert len(errors_2b) == 0, f"File 2 parse errors: {errors_2b}"

        classes_b_initial = get_wme_count(reasoner_b)
        sources_b_initial = count_sources(reasoner_b)
        print(f"  After loading 2 files: {classes_b_initial} classes, {sources_b_initial} sources")

        # Step 3: Save intermediate snapshot
        # Check production stats before save
        prod_stats_before_save = reasoner_b.network.get_production_stats()
        print(f"  Production stats before save: {len(prod_stats_before_save)} rules")
        # Count template-instantiated rules (non-meta)
        template_rules_before = [r for r in prod_stats_before_save.keys()
                                 if '-template-meta' not in r and
                                 (r.startswith('prp-') or r.startswith('cax-') or r.startswith('eq-'))]
        print(f"  Template-instantiated rules before save: {len(template_rules_before)}")

        reasoner_b.network.save(snapshot_b_intermediate)
        size_b_intermediate = os.path.getsize(snapshot_b_intermediate)
        print(f"  Intermediate snapshot saved: {size_b_intermediate:,} bytes")

        # Step 4: Load snapshot (creates new reasoner to simulate fresh load)
        print(f"  Loading snapshot...")
        reasoner_b2 = Reter()
        success = reasoner_b2.network.load(snapshot_b_intermediate)
        assert success, "Failed to load intermediate snapshot"

        classes_after_load = get_wme_count(reasoner_b2)
        sources_after_load = count_sources(reasoner_b2)
        print(f"  After loading snapshot: {classes_after_load} classes, {sources_after_load} sources")

        # Check production stats after load
        prod_stats_after_load = reasoner_b2.network.get_production_stats()
        print(f"  Production stats after load: {len(prod_stats_after_load)} rules")
        template_rules_after = [r for r in prod_stats_after_load.keys()
                                if '-template-meta' not in r and
                                (r.startswith('prp-') or r.startswith('cax-') or r.startswith('eq-'))]
        print(f"  Template-instantiated rules after load: {len(template_rules_after)}")
        print(f"  Template rule names after load: {sorted(template_rules_after)[:5]}...")

        # Check for equivalent_property facts (should be none!)
        try:
            eq_props = reasoner_b2.reql('SELECT ?ep ?p1 ?p2 WHERE { ?ep type "equivalent_property" . ?ep property1 ?p1 . ?ep property2 ?p2 }')
            print(f"  equivalent_property facts after load: {eq_props.num_rows}")
        except Exception as e:
            print(f"  Error querying equivalent_property: {e}")

        # Check total fact count and sample facts
        fact_count = reasoner_b2.network.fact_count()
        print(f"  Total facts after load: {fact_count}")

        # Check if template meta-rules exist as productions
        meta_rules = [r for r in prod_stats_after_load.keys() if 'template-meta' in r]
        print(f"  Template meta-rules: {len(meta_rules)}")

        # DEBUG: Check for any type="equivalent_property" facts BEFORE remove
        try:
            any_eq = reasoner_b2.reql('SELECT ?x ?a ?v WHERE { ?x type "equivalent_property" }')
            print(f"  DEBUG: Facts with type=equivalent_property BEFORE remove: {any_eq.num_rows}")
        except Exception as e:
            print(f"  DEBUG error: {e}")

        # Step 5: Remove file 1
        print(f"  Removing source:file1...")
        reasoner_b2.remove_source("source:file1")

        classes_b_after_remove = get_wme_count(reasoner_b2)
        sources_b_after_remove = count_sources(reasoner_b2)
        print(f"  After removing file1: {classes_b_after_remove} classes, {sources_b_after_remove} sources")

        # Step 6: Add file 3
        wme_count_3b, errors_3b = reasoner_b2.load_python_code(
            PYTHON_FILE_3, "file3.py", "file3", "source:file3"
        )
        print(f"  Loaded file3.py: {wme_count_3b} WMEs, {len(errors_3b)} errors")
        assert len(errors_3b) == 0, f"File 3 parse errors: {errors_3b}"

        classes_final_b = get_wme_count(reasoner_b2)
        sources_final_b = count_sources(reasoner_b2)
        print(f"  Final state B: {classes_final_b} classes, {sources_final_b} sources")

        # Check production stats after file3 load (should NOT have new template rules!)
        prod_stats_after_file3 = reasoner_b2.network.get_production_stats()
        print(f"  Production stats after file3: {len(prod_stats_after_file3)} rules")
        template_rules_after_file3 = [r for r in prod_stats_after_file3.keys()
                                      if '-template-meta' not in r and
                                      (r.startswith('prp-') or r.startswith('cax-') or r.startswith('eq-'))]
        print(f"  Template-instantiated rules after file3: {len(template_rules_after_file3)}")

        # Find new rules that weren't there after load
        new_rules = set(template_rules_after_file3) - set(template_rules_after)
        print(f"  NEW template rules after file3: {len(new_rules)}")
        if new_rules:
            print(f"  Sample new rules: {sorted(new_rules)[:10]}")

        # Check equivalent_property facts after file3
        try:
            eq_props = reasoner_b2.reql('SELECT ?ep ?p1 ?p2 WHERE { ?ep type "equivalent_property" . ?ep property1 ?p1 . ?ep property2 ?p2 }')
            print(f"  equivalent_property facts after file3: {eq_props.num_rows}")
            if eq_props.num_rows > 0:
                for i in range(min(5, eq_props.num_rows)):
                    print(f"    {eq_props.column('?ep')[i].as_py()} property1={eq_props.column('?p1')[i].as_py()} property2={eq_props.column('?p2')[i].as_py()}")
        except Exception as e:
            print(f"  Error querying equivalent_property: {e}")

        # Step 7: Save final snapshot B
        reasoner_b2.network.save(snapshot_b_final)
        size_b_final = os.path.getsize(snapshot_b_final)
        print(f"  Snapshot B saved: {size_b_final:,} bytes")

        # ==========================================
        # COMPARISON
        # ==========================================
        print("\n" + "=" * 70)
        print("COMPARISON RESULTS:")
        print("=" * 70)

        print(f"\nFinal class counts:")
        print(f"  Scenario A: {classes_final_a} classes")
        print(f"  Scenario B: {classes_final_b} classes")

        print(f"\nFinal source counts:")
        print(f"  Scenario A: {sources_final_a} sources")
        print(f"  Scenario B: {sources_final_b} sources")

        print(f"\nSnapshot sizes:")
        print(f"  Scenario A: {size_a:,} bytes")
        print(f"  Scenario B: {size_b_final:,} bytes")
        print(f"  Difference: {size_b_final - size_a:,} bytes ({100 * (size_b_final - size_a) / size_a:.1f}%)")

        # Allow some tolerance (10%) for serialization overhead
        size_ratio = size_b_final / size_a
        print(f"  Size ratio (B/A): {size_ratio:.2f}")

        # Assert that both scenarios end up with same class and source counts
        assert classes_final_a == classes_final_b, \
            f"Class count mismatch: A={classes_final_a}, B={classes_final_b}"

        assert sources_final_a == sources_final_b, \
            f"Source count mismatch: A={sources_final_a}, B={sources_final_b}"

        # Assert that snapshot sizes are within reasonable tolerance
        # If B is significantly larger, it indicates stale WMEs in the RETE network
        assert size_ratio < 1.2, \
            f"Snapshot B is {size_ratio:.1f}x larger than A - indicates stale WMEs after snapshot restore + source removal"

        print("\n" + "=" * 70)
        print("TEST PASSED: Snapshots have similar sizes")
        print("=" * 70)


def test_snapshot_source_tracking_preserved():
    """
    Test that source tracking is preserved across snapshot save/load.
    """
    print("\n" + "=" * 70)
    print("TEST: Source Tracking Preservation")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        snapshot_path = os.path.join(tmpdir, "sources.reter")

        # Create and save
        reasoner1 = create_reasoner_with_ontologies()
        print("  Loaded oo_ontology and py_ontology")
        reasoner1.load_python_code(PYTHON_FILE_1, "file1.py", "file1", "source:file1")
        reasoner1.load_python_code(PYTHON_FILE_2, "file2.py", "file2", "source:file2")

        sources_before = reasoner1.network.get_all_sources()
        print(f"Sources before save: {sources_before}")

        reasoner1.network.save(snapshot_path)

        # Load into new reasoner
        reasoner2 = Reter()
        success = reasoner2.network.load(snapshot_path)
        assert success, "Failed to load snapshot"

        sources_after = reasoner2.network.get_all_sources()
        print(f"Sources after load: {sources_after}")

        assert set(sources_before) == set(sources_after), \
            f"Source tracking not preserved: before={sources_before}, after={sources_after}"

        # Verify we can still remove sources by their IDs
        print(f"Removing source:file1 after snapshot load...")
        reasoner2.remove_source("source:file1")

        sources_final = reasoner2.network.get_all_sources()
        print(f"Sources after remove: {sources_final}")

        assert "source:file1" not in sources_final, "source:file1 should be removed"
        assert "source:file2" in sources_final, "source:file2 should still exist"

        print("\nTEST PASSED: Source tracking preserved across snapshot")


def test_multiple_remove_add_cycles():
    """
    Test multiple cycles of remove/add with snapshot loads.
    """
    print("\n" + "=" * 70)
    print("TEST: Multiple Remove/Add Cycles")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        snapshot_path = os.path.join(tmpdir, "cycle.reter")

        # Initial: create new reasoner with ontologies, load file1, save
        reasoner = create_reasoner_with_ontologies()
        print("  Loaded oo_ontology and py_ontology")
        reasoner.load_python_code(PYTHON_FILE_1, "file1.py", "file1", "source:file1")
        reasoner.network.save(snapshot_path)
        initial_size = os.path.getsize(snapshot_path)
        print(f"Initial snapshot: {initial_size:,} bytes")

        # Cycle 1: create fresh reasoner (no ontologies - snapshot has them), load snapshot, add file2, save
        reasoner = Reter()  # Fresh - snapshot already includes ontologies
        reasoner.network.load(snapshot_path)
        reasoner.load_python_code(PYTHON_FILE_2, "file2.py", "file2", "source:file2")
        reasoner.network.save(snapshot_path)
        cycle1_size = os.path.getsize(snapshot_path)
        print(f"After cycle 1 (add file2): {cycle1_size:,} bytes")

        # Cycle 2: create fresh reasoner, load snapshot, remove file1, add file3, save
        reasoner = Reter()  # Fresh - snapshot already includes ontologies
        reasoner.network.load(snapshot_path)
        reasoner.remove_source("source:file1")
        reasoner.load_python_code(PYTHON_FILE_3, "file3.py", "file3", "source:file3")
        reasoner.network.save(snapshot_path)
        cycle2_size = os.path.getsize(snapshot_path)
        print(f"After cycle 2 (remove file1, add file3): {cycle2_size:,} bytes")

        # Cycle 3: create fresh reasoner, load snapshot, remove file2, add file1 back, save
        reasoner = Reter()  # Fresh - snapshot already includes ontologies
        reasoner.network.load(snapshot_path)
        reasoner.remove_source("source:file2")
        reasoner.load_python_code(PYTHON_FILE_1, "file1.py", "file1", "source:file1")
        reasoner.network.save(snapshot_path)
        cycle3_size = os.path.getsize(snapshot_path)
        print(f"After cycle 3 (remove file2, add file1): {cycle3_size:,} bytes")

        # Final sources should be file1 and file3
        sources = reasoner.network.get_all_sources()
        print(f"Final sources: {sources}")

        assert "source:file1" in sources, "source:file1 should exist"
        assert "source:file3" in sources, "source:file3 should exist"
        assert "source:file2" not in sources, "source:file2 should be removed"

        # Check for size bloat (each cycle shouldn't accumulate stale data)
        print(f"\nSize progression: {initial_size:,} -> {cycle1_size:,} -> {cycle2_size:,} -> {cycle3_size:,}")

        # Cycle 3 should be similar to cycle 2 (file1 and file3 vs file2 and file3)
        size_ratio = cycle3_size / cycle2_size
        print(f"Cycle3/Cycle2 ratio: {size_ratio:.2f}")

        assert size_ratio < 1.5, \
            f"Size grew too much across cycles ({size_ratio:.1f}x) - indicates accumulating stale data"

        print("\nTEST PASSED: Multiple cycles don't accumulate excessive data")


def test_snapshot_content_comparison():
    """
    Detailed comparison of snapshot contents between scenarios A and B.
    This helps identify exactly what differs.
    """
    print("\n" + "=" * 70)
    print("TEST: Detailed Snapshot Content Comparison")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        snapshot_a = os.path.join(tmpdir, "scenario_a.reter")
        snapshot_b = os.path.join(tmpdir, "scenario_b.reter")

        # SCENARIO A: Direct incremental (with ontologies)
        reasoner_a = create_reasoner_with_ontologies()
        print("  Scenario A: Loaded oo_ontology and py_ontology")
        reasoner_a.load_python_code(PYTHON_FILE_1, "file1.py", "file1", "source:file1")
        reasoner_a.load_python_code(PYTHON_FILE_2, "file2.py", "file2", "source:file2")
        reasoner_a.remove_source("source:file1")
        reasoner_a.load_python_code(PYTHON_FILE_3, "file3.py", "file3", "source:file3")
        reasoner_a.network.save(snapshot_a)

        # SCENARIO B: With snapshot load (with ontologies initially)
        reasoner_b = create_reasoner_with_ontologies()
        print("  Scenario B: Loaded oo_ontology and py_ontology")
        reasoner_b.load_python_code(PYTHON_FILE_1, "file1.py", "file1", "source:file1")
        reasoner_b.load_python_code(PYTHON_FILE_2, "file2.py", "file2", "source:file2")
        intermediate_snapshot = os.path.join(tmpdir, "intermediate.reter")
        reasoner_b.network.save(intermediate_snapshot)

        # Load from snapshot (fresh Reter - snapshot includes ontologies)
        reasoner_b2 = Reter()
        reasoner_b2.network.load(intermediate_snapshot)
        reasoner_b2.remove_source("source:file1")
        reasoner_b2.load_python_code(PYTHON_FILE_3, "file3.py", "file3", "source:file3")
        reasoner_b2.network.save(snapshot_b)

        # Compare sizes
        size_a = os.path.getsize(snapshot_a)
        size_b = os.path.getsize(snapshot_b)
        print(f"\nSnapshot sizes: A={size_a:,} bytes, B={size_b:,} bytes, diff={size_b-size_a:,} bytes")

        # Load both and compare internal counts
        print("\n--- Loading and comparing snapshots ---")

        # Load A
        check_a = Reter()
        check_a.network.load(snapshot_a)
        fact_count_a = check_a.network.fact_count()
        sources_a = sorted(check_a.network.get_all_sources())

        # Load B
        check_b = Reter()
        check_b.network.load(snapshot_b)
        fact_count_b = check_b.network.fact_count()
        sources_b = sorted(check_b.network.get_all_sources())

        print(f"\nFact counts (network.fact_count()): A={fact_count_a}, B={fact_count_b}")

        # Also get WME count if available
        try:
            wme_count_a = check_a.network.wme_count() if hasattr(check_a.network, 'wme_count') else "N/A"
            wme_count_b = check_b.network.wme_count() if hasattr(check_b.network, 'wme_count') else "N/A"
            print(f"WME counts: A={wme_count_a}, B={wme_count_b}")
        except:
            pass

        # Get token count if available
        try:
            token_count_a = check_a.network.token_count() if hasattr(check_a.network, 'token_count') else "N/A"
            token_count_b = check_b.network.token_count() if hasattr(check_b.network, 'token_count') else "N/A"
            print(f"Token counts: A={token_count_a}, B={token_count_b}")
        except:
            pass

        # Get internal metrics
        print("\n--- Internal Metrics ---")
        try:
            metrics_a = check_a.network.get_metrics()
            metrics_b = check_b.network.get_metrics()
            print(f"Metrics A: {metrics_a}")
            print(f"Metrics B: {metrics_b}")
        except Exception as e:
            print(f"  Error getting metrics: {e}")

        # Get production stats
        print("\n--- Production Stats ---")
        try:
            prod_stats_a = check_a.network.get_production_stats()
            prod_stats_b = check_b.network.get_production_stats()
            print(f"Production stats A: {prod_stats_a}")
            print(f"Production stats B: {prod_stats_b}")
        except Exception as e:
            print(f"  Error getting production stats: {e}")

        print(f"\nSources A: {sources_a}")
        print(f"Sources B: {sources_b}")

        # Compare facts per source using REQL
        print("\n--- Facts per source comparison ---")
        for source in set(sources_a) | set(sources_b):
            # Query facts by source using the source tracking
            try:
                result_a = check_a.reql(f'SELECT ?f WHERE {{ ?f _source "{source}" }}')
                result_b = check_b.reql(f'SELECT ?f WHERE {{ ?f _source "{source}" }}')
                facts_a_count = result_a.num_rows
                facts_b_count = result_b.num_rows
            except:
                facts_a_count = "N/A"
                facts_b_count = "N/A"
            if facts_a_count != facts_b_count:
                print(f"  {source}: A={facts_a_count} facts, B={facts_b_count} facts - MISMATCH!")
            else:
                print(f"  {source}: {facts_a_count} facts (match)")

        # Query for classes to compare semantic content
        classes_a = check_a.reql("SELECT ?c WHERE { ?c concept \"py:Class\" }").num_rows
        classes_b = check_b.reql("SELECT ?c WHERE { ?c concept \"py:Class\" }").num_rows
        print(f"\npy:Class count: A={classes_a}, B={classes_b}")

        methods_a = check_a.reql("SELECT ?m WHERE { ?m concept \"py:Method\" }").num_rows
        methods_b = check_b.reql("SELECT ?m WHERE { ?m concept \"py:Method\" }").num_rows
        print(f"py:Method count: A={methods_a}, B={methods_b}")

        # Analyze what's extra in B
        print("\n--- Analyzing extra content in B ---")
        print(f"Extra facts in B: {fact_count_b - fact_count_a}")

        # Query different fact types to see what's bloated
        fact_types = [
            ("py:Class", "classes"),
            ("py:Method", "methods"),
            ("py:Function", "functions"),
            ("py:Parameter", "parameters"),
            ("py:Module", "modules"),
            ("oo:Class", "oo:Class"),
            ("oo:Method", "oo:Method"),
            ("oo:Function", "oo:Function"),
        ]

        print("\nFact type comparison:")
        for concept, label in fact_types:
            try:
                count_a = check_a.reql(f'SELECT ?x WHERE {{ ?x concept "{concept}" }}').num_rows
                count_b = check_b.reql(f'SELECT ?x WHERE {{ ?x concept "{concept}" }}').num_rows
                diff = count_b - count_a
                marker = " <-- BLOAT" if diff > 0 else ""
                print(f"  {label}: A={count_a}, B={count_b}, diff={diff}{marker}")
            except Exception as e:
                print(f"  {label}: error - {e}")

        # Check for specific relationship bloat
        relationships = [
            ("?x type ?y", "type assertions"),
            ("?x subClassOf ?y", "subClassOf"),
            ("?x inheritsFrom ?y", "inheritsFrom"),
            ("?x calls ?y", "calls"),
            ("?x definedIn ?y", "definedIn"),
        ]

        print("\nRelationship comparison:")
        for pattern, label in relationships:
            try:
                count_a = check_a.reql(f'SELECT ?x ?y WHERE {{ {pattern} }}').num_rows
                count_b = check_b.reql(f'SELECT ?x ?y WHERE {{ {pattern} }}').num_rows
                diff = count_b - count_a
                marker = " <-- BLOAT" if diff > 0 else ""
                print(f"  {label}: A={count_a}, B={count_b}, diff={diff}{marker}")
            except Exception as e:
                print(f"  {label}: error - {e}")

        # Get all unique predicates/attributes in both networks
        print("\n--- All predicates comparison ---")
        try:
            # Query all facts and group by predicate
            all_facts_a = check_a.reql('SELECT ?s ?p ?o WHERE { ?s ?p ?o }')
            all_facts_b = check_b.reql('SELECT ?s ?p ?o WHERE { ?s ?p ?o }')

            # Count by predicate
            pred_counts_a = {}
            for i in range(all_facts_a.num_rows):
                p = all_facts_a.column('?p')[i].as_py()
                pred_counts_a[p] = pred_counts_a.get(p, 0) + 1

            pred_counts_b = {}
            for i in range(all_facts_b.num_rows):
                p = all_facts_b.column('?p')[i].as_py()
                pred_counts_b[p] = pred_counts_b.get(p, 0) + 1

            all_preds = sorted(set(pred_counts_a.keys()) | set(pred_counts_b.keys()))
            print(f"  Total unique predicates: A={len(pred_counts_a)}, B={len(pred_counts_b)}")

            print("\n  Predicate counts (showing differences):")
            for p in all_preds:
                count_a = pred_counts_a.get(p, 0)
                count_b = pred_counts_b.get(p, 0)
                diff = count_b - count_a
                if diff != 0:
                    marker = " <-- BLOAT" if diff > 0 else " <-- LESS"
                    print(f"    {p}: A={count_a}, B={count_b}, diff={diff}{marker}")

            # Show predicates only in B
            only_in_b = set(pred_counts_b.keys()) - set(pred_counts_a.keys())
            if only_in_b:
                print(f"\n  Predicates ONLY in B ({len(only_in_b)}):")
                for p in sorted(only_in_b):
                    print(f"    {p}: {pred_counts_b[p]} facts")

            # Sample facts from bloated predicates
            print("\n--- Sample extra facts in B ---")
            # Find the most bloated predicate
            bloated = [(p, pred_counts_b.get(p, 0) - pred_counts_a.get(p, 0))
                       for p in all_preds if pred_counts_b.get(p, 0) > pred_counts_a.get(p, 0)]
            bloated.sort(key=lambda x: -x[1])

            if bloated:
                top_bloated = bloated[0][0]
                print(f"  Most bloated predicate: {top_bloated}")
                # Sample facts with this predicate
                sample = check_b.reql(f'SELECT ?s ?o WHERE {{ ?s {top_bloated} ?o }}')
                print(f"  Sample facts (first 10):")
                for i in range(min(10, sample.num_rows)):
                    s = sample.column('?s')[i].as_py()
                    o = sample.column('?o')[i].as_py()
                    print(f"    {s} {top_bloated} {o}")

        except Exception as e:
            import traceback
            print(f"  Error analyzing predicates: {e}")
            traceback.print_exc()

        print("\n" + "=" * 70)
        if fact_count_a == fact_count_b:
            print("Content is identical - size difference is from serialization metadata")
        else:
            print(f"CONTENT DIFFERS: B has {fact_count_b - fact_count_a} extra facts")
        print("=" * 70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
