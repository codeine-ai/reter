#!/usr/bin/env python
"""
Generate codebase_analysis.reter snapshot by analyzing the reter source code.

This script analyzes the reter Python codebase and saves the network state
as a snapshot file that can be used for testing.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reter import Reter


def main():
    """Generate the codebase snapshot"""
    print("Creating Reter instance...")
    reasoner = Reter()

    # Get the src/reter directory
    reter_src = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "src",
        "reter"
    )

    if not os.path.exists(reter_src):
        print(f"ERROR: Source directory not found: {reter_src}")
        sys.exit(1)

    print(f"Analyzing Python codebase in: {reter_src}")

    # Load the Python codebase
    def progress(processed, total, msg):
        if processed % 5 == 0 or processed == total:
            print(f"  Progress: {processed}/{total} - {msg}")

    total_wmes = reasoner.load_python_directory(
        reter_src,
        recursive=True,
        progress_callback=progress
    )

    print(f"\n✅ Loaded {total_wmes} WMEs from Python codebase")

    # Get some statistics
    methods_result = reasoner.reql("""
        SELECT (COUNT(?method) AS ?count)
        WHERE {
            ?method concept "py:Method"
        }
    """)
    method_count = methods_result.column('?count')[0].as_py() if methods_result.num_rows > 0 else 0

    classes_result = reasoner.reql("""
        SELECT (COUNT(?class) AS ?count)
        WHERE {
            ?class concept "py:Class"
        }
    """)
    class_count = classes_result.column('?count')[0].as_py() if classes_result.num_rows > 0 else 0

    modules_result = reasoner.reql("""
        SELECT (COUNT(?module) AS ?count)
        WHERE {
            ?module concept "py:Module"
        }
    """)
    module_count = modules_result.column('?count')[0].as_py() if modules_result.num_rows > 0 else 0

    print(f"\n📊 Statistics:")
    print(f"  Modules: {module_count}")
    print(f"  Classes: {class_count}")
    print(f"  Methods: {method_count}")

    # Save the snapshot
    snapshot_path = os.path.join(
        os.path.dirname(__file__),
        "codebase_analysis.reter"
    )

    print(f"\n💾 Saving snapshot to: {snapshot_path}")
    success = reasoner.network.save(snapshot_path)

    if success:
        file_size = os.path.getsize(snapshot_path)
        print(f"✅ Snapshot saved successfully ({file_size:,} bytes)")
    else:
        print("❌ Failed to save snapshot")
        sys.exit(1)

    # Verify the snapshot can be loaded
    print("\n🔍 Verifying snapshot...")
    test_reasoner = Reter()
    if test_reasoner.network.load(snapshot_path):
        print("✅ Snapshot verified - loads successfully")
    else:
        print("❌ Snapshot verification failed")
        sys.exit(1)

    print("\n🎉 Codebase snapshot generation complete!")


if __name__ == "__main__":
    main()
