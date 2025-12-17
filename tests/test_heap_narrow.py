"""
Narrow down which operation causes heap corruption
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

from reter import Reter

try:
    print("Step 1: Creating reasoner...")
    reasoner = Reter()
    print("  OK")

    print("Step 2: Loading ontology...")
    reasoner.load_ontology("""
        Person（Alice）
        Person（Bob）
        knows（Alice， Bob）
        knows ≡ᴿ knows⁻
    """)
    print("  OK")

    print("Step 3: Running reasoning...")
    
    print("  OK")

    print("Step 4: Querying results...")
    facts = reasoner.query(
        type="role_assertion",
        subject="Bob",
        role="knows",
        object="Alice"
    )
    print(f"  OK - Found {len(facts)} facts")

    print("Step 5: Explicit del reasoner...")
    del reasoner
    print("  OK")

    print("\nStep 6: Creating second reasoner...")
    reasoner2 = Reter()
    print("  OK")

    print("SUCCESS: All steps completed!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
