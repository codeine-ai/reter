# RETER

High-performance Description Logic reasoner with C++ RETE engine.

## Installation

With uv (no clone needed):
```bash
uv pip install git+https://github.com/reter-ai/reter.git --find-links https://raw.githubusercontent.com/reter-ai/reter/main/reter_core/index.html
```

Or clone and install:
```bash
git clone https://github.com/reter-ai/reter.git && uv pip install ./reter --find-links ./reter/reter_core/
```

With pip:
```bash
git clone https://github.com/reter-ai/reter.git
cd reter
pip install . --find-links ./reter_core/
```

## Quick Start

```python
from reter import Reter

# Create reasoner
r = Reter()

# Load ontology
r.load_ontology("""
Person ⊑ᑦ Animal
Student ⊑ᑦ Person
Person（John）
Student（Alice）
""")

# Query instances
people = r.instances_of("Person")
for p in people:
    print(p["?x"])

# REQL queries
result = r.reql("SELECT ?x WHERE { ?x type Person }")
print(result.to_pandas())
```

## Features

- Fast OWL 2 RL reasoning
- Description Logic parser with Unicode and ASCII syntax
- SWRL rule support
- Query interface with pandas/Arrow export
- Source tracking for incremental ontology loading
- Multi-language code analysis (Python, JavaScript, C#, C++)

## Documentation

- [Grammar Reference](docs/01_grammar.md) - Description Logic syntax
- [API Reference](docs/02_api_reference.md) - Python API documentation
- [REQL Queries](docs/03_reql.md) - SPARQL-like query language
- [Syntax Variants](docs/04_syntax_variants.md) - Unicode vs ASCII syntax

## Tests
```
set PYTHONPATH=%CD%\src && python -m pytest tests/ -v --tb=short -m "not slow"
```

## License

**reter** (this package) is licensed under the [MIT License](LICENSE).

**reter-core** (the C++ engine, distributed as binary wheels) is proprietary software owned by Reter Code.AI. It is distributed in binary form only and may only be used as a dependency of the reter package. See [LICENSE](LICENSE) for details.
