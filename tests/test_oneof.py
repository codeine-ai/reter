"""
Test for cls-oo (oneOf enumeration) rule
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from reter import Reter


def test_oneof():
    """Test oneOf enumeration"""
    print("\n" + "=" * 60)
    print("TEST: OneOf Enumeration (cls-oo)")
    print("=" * 60)

    reasoner = Reter()

    # Define a concept using oneOf (instance_set)
    # Grammar: node can be SOPEN instance_list SCLOSE (instance_set)
    # So: Weekday ≡ {Monday, Tuesday, Wednesday, Thursday, Friday}
    ontology = """
    Weekday ≡ᑦ ｛Monday， Tuesday， Wednesday， Thursday， Friday｝
    Weekday ⊑ᑦ TimeUnit
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check if all members are instances of Weekday
    weekday_instances = reasoner.get_instances('Weekday')
    print(f"\nWeekday instances: {weekday_instances}")

    assert 'Monday' in weekday_instances, "Monday should be a Weekday"
    assert 'Tuesday' in weekday_instances, "Tuesday should be a Weekday"
    assert 'Wednesday' in weekday_instances, "Wednesday should be a Weekday"
    assert 'Thursday' in weekday_instances, "Thursday should be a Weekday"
    assert 'Friday' in weekday_instances, "Friday should be a Weekday"

    print("✓ Test passed: OneOf enumeration works (cls-oo)")


if __name__ == '__main__':
    test_oneof()
