#!/usr/bin/env python3
"""
Debug C++ DL Parser Integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

from reter_core import owl_rete_cpp

def test_subsumption():
    """Test subsumption"""
    print("\n=== Test: Subsumption ===")
    net = owl_rete_cpp.ReteNetwork()
    dl_text = "Person ⊑ᑦ Animal"
    print(f"Input: {repr(dl_text)}")
    count = net.load_ontology_from_string(dl_text)
    print(f"Result: {count} WMEs")

def test_instance():
    """Test instance assertion"""
    print("\n=== Test: Instance Assertion ===")
    net = owl_rete_cpp.ReteNetwork()
    dl_text = "Person（john）"
    print(f"Input: {repr(dl_text)}")
    count = net.load_ontology_from_string(dl_text)
    print(f"Result: {count} WMEs")

def test_role():
    """Test role assertion"""
    print("\n=== Test: Role Assertion ===")
    net = owl_rete_cpp.ReteNetwork()
    dl_text = "hasFriend（john，mary）"
    print(f"Input: {repr(dl_text)}")
    count = net.load_ontology_from_string(dl_text)
    print(f"Result: {count} WMEs")

if __name__ == "__main__":
    try:
        test_subsumption()
        test_instance()
        test_role()
    except Exception as e:
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()
