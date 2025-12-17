#!/usr/bin/env python3
"""Test the C++ RETE implementation through DLReasoner with OWL RL rules using DL syntax"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reter import Reter


def test_basic():
    """Test 1: Basic subsumption reasoning"""
    reasoner = Reter()

    # Add subsumption facts using DL syntax: Cat ⊑ᑦ Mammal, Mammal ⊑ᑦ Animal
    # This uses the same syntax as test_reasoner.py which is known to work
    ontology = """
    Cat ⊑ᑦ Mammal
    Mammal ⊑ᑦ Animal
    Cat（Felix）
    """
    reasoner.load_ontology(ontology)

    # Check that Felix is inferred to be an Animal (via Cat ⊑ Mammal ⊑ Animal)
    animals = reasoner.get_instances('Animal')

    assert 'Felix' in animals, f"Felix should be an Animal via transitive subsumption. Animals: {animals}"


def test_instances():
    """Test 2: Instance reasoning with subsumption"""
    reasoner = Reter()

    # Add instance and subsumption using DL syntax
    ontology = """
        Cat（felix）
        Cat ⊑ᑦ Animal
    """
    reasoner.load_ontology(ontology)

    # Should infer felix : Animal
    animals = reasoner.get_instances('Animal')

    assert 'felix' in animals, f"Did not infer felix : Animal. Animals: {animals}"


def test_property_reasoning():
    """Test 3: Property reasoning (transitive property)"""
    reasoner = Reter()

    # Define transitive property using role chain (matches test_reasoner.py::test_transitive_property)
    # ancestorOf ∘ ancestorOf ⊑ᴿ ancestorOf means ancestorOf is transitive
    ontology = """
        ancestorOf ∘ ancestorOf ⊑ᴿ ancestorOf
        ancestorOf（Alice，Bob）
        ancestorOf（Bob，Charlie）
    """
    reasoner.load_ontology(ontology)

    # Should infer Alice ancestorOf Charlie (transitive)
    ancestor_facts = reasoner.get_role_assertions(role='ancestorOf')

    assert ('Alice', 'ancestorOf', 'Charlie') in ancestor_facts, f"Did not infer transitive property. Facts: {ancestor_facts}"


def test_deduplication():
    """Test 4: Fact deduplication"""
    reasoner = Reter()

    # Add the same fact multiple times
    ontology1 = "Dog ⊑ᑦ Animal"
    reasoner.load_ontology(ontology1)

    # Get initial fact count
    initial_count = reasoner.network.fact_count()

    # Try to add it again - should be deduplicated
    ontology2 = "Dog ⊑ᑦ Animal"
    reasoner.load_ontology(ontology2)

    final_count = reasoner.network.fact_count()

    # Count should not increase (deduplication)
    assert final_count == initial_count, f"Deduplication failed: initial={initial_count}, final={final_count}"
