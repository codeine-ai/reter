"""
Test script for node sharing metrics (OPS5 Innovation - Phase 2)

This script tests the NetworkMetrics tracking system that measures
how effectively RETE shares nodes across multiple productions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reter_core.owl_rete_cpp import ReteNetwork, Fact

def make_fact(**kwargs):
    """Helper to create a Fact from keyword arguments"""
    fact = Fact()
    for key, value in kwargs.items():
        fact.set(key, value)
    return fact

def test_node_sharing_metrics():
    """Test that node sharing metrics are tracked correctly"""

    print("="*70)
    print("Testing Node Sharing Metrics (OPS5 Innovation)")
    print("="*70)
    print()

    # Create a RETE network
    # With lazy registration, rules are activated when facts arrive
    # Add some facts to trigger rule activation and node creation
    network = ReteNetwork()

    print("Network created - adding facts to trigger rule activation...")

    # Add facts that will trigger multiple OWL RL rules and demonstrate node sharing
    # These facts will activate property templates and create RETE network nodes
    network.add_fact(make_fact(type="symmetric", property="knows"))
    network.add_fact(make_fact(type="transitive", property="knows"))
    network.add_fact(make_fact(type="role_assertion", subject="Alice", role="knows", object="Bob"))
    network.add_fact(make_fact(type="role_assertion", subject="Bob", role="knows", object="Charlie"))

    network.add_fact(make_fact(type="sub_property", sub="hasParent", super="hasAncestor"))
    network.add_fact(make_fact(type="role_assertion", subject="Bob", role="hasParent", object="Alice"))

    network.add_fact(make_fact(type="functional", property="hasBirthMother"))
    network.add_fact(make_fact(type="role_assertion", subject="Bob", role="hasBirthMother", object="Mary"))

    print("Facts added - rules activated via lazy registration")
    print()

    # Print the metrics
    print("Network Construction Complete!")
    print()
    network.print_metrics()
    print()

    # Get metrics and verify
    metrics = network.get_metrics()

    print("Verification:")
    print(f"  Virtual alpha nodes: {metrics['virtual_alpha_nodes']}")
    print(f"  Real alpha nodes: {metrics['real_alpha_nodes']}")
    print(f"  Alpha sharing ratio: {metrics['alpha_sharing_ratio']:.2f}:1")
    print()
    print(f"  Virtual join nodes: {metrics['virtual_join_nodes']}")
    print(f"  Real join nodes: {metrics['real_join_nodes']}")
    print(f"  Join sharing ratio: {metrics['join_sharing_ratio']:.2f}:1")
    print()
    print(f"  Virtual beta nodes: {metrics['virtual_beta_nodes']}")
    print(f"  Real beta nodes: {metrics['real_beta_nodes']}")
    print(f"  Beta sharing ratio: {metrics['beta_sharing_ratio']:.2f}:1")
    print()
    print(f"  Overall sharing ratio: {metrics['overall_sharing_ratio']:.2f}:1")
    print(f"  Est. memory saved: {metrics['estimated_memory_saved_bytes']} bytes")
    print()

    # Verify that sharing is happening
    assert metrics['virtual_alpha_nodes'] > metrics['real_alpha_nodes'], \
        "Alpha nodes should be shared!"
    assert metrics['alpha_sharing_ratio'] > 1.0, \
        "Alpha sharing ratio should be > 1.0!"

    print("✅ All metrics verified successfully!")
    print()
    print("Analysis:")
    reduction = (1.0 - 1.0/metrics['overall_sharing_ratio']) * 100.0
    print(f"  Overall node reduction: {reduction:.1f}%")
    print(f"  Virtual nodes requested: {metrics['virtual_alpha_nodes'] + metrics['virtual_join_nodes'] + metrics['virtual_beta_nodes']}")
    print(f"  Real nodes created: {metrics['real_alpha_nodes'] + metrics['real_join_nodes'] + metrics['real_beta_nodes']}")
    print(f"  Nodes saved by sharing: {(metrics['virtual_alpha_nodes'] - metrics['real_alpha_nodes']) + (metrics['virtual_join_nodes'] - metrics['real_join_nodes']) + (metrics['virtual_beta_nodes'] - metrics['real_beta_nodes'])}")
    print()

if __name__ == "__main__":
    test_node_sharing_metrics()
