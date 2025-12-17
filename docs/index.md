# RETER Documentation

High-performance OWL 2 RL reasoner for Python.

## Documentation

| Document | Description |
|----------|-------------|
| [Grammar Reference](01_grammar.md) | Description Logic syntax and operators |
| [API Reference](02_api_reference.md) | Python API documentation |
| [REQL Queries](03_reql.md) | SPARQL-like query language |
| [Syntax Variants](04_syntax_variants.md) | Unicode vs ASCII syntax |

## Quick Start

```python
from reter import Reter

# Create reasoner
r = Reter()

# Load ontology
r.load_ontology("""
Person ⊑ᑦ Animal
Person（john）
Person（mary）
hasParent（john，mary）
""")

# Query
results = r.pattern(("?x", "type", "Person"))
for binding in results:
    print(binding["?x"])

# Convert to pandas
df = results.to_pandas()
```

## Installation

```bash
pip install reter
pip install reter_core --extra-index-url https://codeine-ai.github.io/reter/reter_core/
```

## Supported Platforms

- Windows x64 (Python 3.9-3.14)
- Linux x64 (Python 3.9-3.14)
- macOS arm64/x86_64 (Python 3.9-3.14)

## License

- **reter**: MIT License
- **reter_core**: Proprietary (binary-only distribution)
