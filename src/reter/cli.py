"""
Command-line interface for RETER reasoner
"""
import sys
import argparse
from pathlib import Path
from reter.reasoner import Reter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="RETER - High-Performance OWL 2 RL Reasoner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load and reason over an ontology
  reter ontology.dl

  # Save reasoning results to binary file
  reter ontology.dl --save ontology.pb

  # Load from binary file (fast)
  reter --load ontology.pb

  # Query for all animals
  reter ontology.dl --query "?x type Animal"
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        type=Path,
        help='Input ontology file (.dl format)'
    )

    parser.add_argument(
        '--load',
        type=Path,
        help='Load from binary file instead of parsing'
    )

    parser.add_argument(
        '--save',
        type=Path,
        help='Save reasoning results to binary file'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Query pattern (e.g., "?x type Animal")'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show reasoning statistics'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='RETER 0.1.0'
    )

    args = parser.parse_args()

    if not args.input and not args.load:
        parser.print_help()
        return 1

    try:
        # Create reasoner
        reasoner = Reter()

        # Load ontology
        if args.load:
            print(f"Loading from binary file: {args.load}")
            reasoner.load_from_file(str(args.load))
        elif args.input:
            print(f"Loading ontology: {args.input}")
            content = args.input.read_text(encoding='utf-8')
            reasoner.load(content)

        # Show stats if requested
        if args.stats:
            reasoner.print_summary()

        # Save if requested
        if args.save:
            print(f"\nSaving to binary file: {args.save}")
            reasoner.save_to_file(str(args.save))
            print(f"✓ Saved successfully")

        # Query if requested
        if args.query:
            print(f"\nQuerying: {args.query}")
            # Parse simple query format
            parts = args.query.split()
            if len(parts) >= 3:
                pattern = [(parts[0], parts[1], parts[2])]
                results = reasoner.query(pattern)
                count = 0
                for result in results:
                    print(result)
                    count += 1
                print(f"\nFound {count} result(s)")
            else:
                print("Invalid query format. Use: ?var predicate object")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
