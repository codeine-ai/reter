#!/usr/bin/env python3
"""
Test if parser reports errors
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter import owl_rete_cpp

test_cases = [
    "≡ᑦ（Human，Person，Individual）",
    "Alice ﹦ Bob",
    "Alice ≠ Bob",
    "¬≡ᑦ（Male，Female）",
]

for stmt in test_cases:
    print(f"\nTesting: {stmt}")
    net = owl_rete_cpp.ReteNetwork()
    # This should trigger parser and show any parse errors on stderr
    net.load_ontology_from_string(stmt)
    facts = net.get_all_facts()
    print(f"Facts created: {len(facts)}")
