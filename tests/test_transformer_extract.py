#!/usr/bin/env python3
"""
Minimal test case extracted from transformer.py to reproduce the parsing bug.
"""

import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reter import Reter


# Extracted from transformer.py lines 2312-2600 (simplified)
TRANSFORMER_EXTRACT = '''class NestStep:
    """Create nested/tree structure from flat data."""

    def __init__(self, parent: str, child: str, root=None, max_depth=10, children_key="children"):
        self.parent = parent
        self.child = child
        self.root = root
        self.max_depth = max_depth
        self.children_key = children_key

    def execute(self, data, ctx=None):
        """Execute nesting."""
        try:
            if hasattr(data, 'to_pylist'):
                data = data.to_pylist()
            return data
        except Exception as e:
            return str(e)


class RenderTableStep:
    """Render data as formatted table."""

    def __init__(self, format="markdown", columns=None, title=None, totals=False,
                 sort=None, group_by=None, max_rows=None):
        self.format = format
        self.columns = columns or []
        self.title = title
        self.totals = totals
        self.sort = sort
        self.group_by = group_by
        self.max_rows = max_rows

    def execute(self, data, ctx=None):
        """Render as table."""
        try:
            if hasattr(data, 'to_pylist'):
                data = data.to_pylist()
            if not data:
                return {"table": "", "format": self.format, "row_count": 0}
            return {"table": "table", "format": self.format, "row_count": len(data)}
        except Exception as e:
            return str(e)

    def _render_markdown(self, data, cols):
        """Render as Markdown table."""
        lines = []
        if self.title:
            lines.append(f"## {self.title}")
        return "\\n".join(lines)

    def _render_html(self, data, cols):
        """Render as HTML table."""
        lines = ['<table>']
        if self.title:
            lines.append(f'<caption>{self.title}</caption>')
        lines.append('</table>')
        return "\\n".join(lines)

    def _render_csv(self, data, cols):
        """Render as CSV."""
        lines = []
        return "\\n".join(lines)

    def _render_ascii(self, data, cols):
        """Render as ASCII table."""
        headers = []
        widths = [len(h) for h in headers]
        lines = []
        sep = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
        if self.title:
            lines.append(self.title)
            lines.append('=' * len(sep))
        lines.append(sep)
        lines.append('|' + '|'.join(f' {h:<{w}} ' for h, w in zip(headers, widths)) + '|')
        lines.append(sep)
        lines.append(sep)
        return "\\n".join(lines)


class RenderChartStep:
    """Render data as chart."""

    def __init__(self, chart_type="bar", x=None, y=None, series=None, title=None,
                 format="mermaid", colors=None, stacked=False, horizontal=False):
        self.chart_type = chart_type
        self.x = x
        self.y = y
        self.series = series
        self.title = title
        self.format = format
        self.colors = colors
        self.stacked = stacked
        self.horizontal = horizontal

    def execute(self, data, ctx=None):
        """Render as chart."""
        try:
            if hasattr(data, 'to_pylist'):
                data = data.to_pylist()
            if not data:
                return {"chart": "", "format": self.format, "type": self.chart_type}
            return {"chart": "chart", "format": self.format, "type": self.chart_type}
        except Exception as e:
            return str(e)
'''


class TestTransformerExtract(unittest.TestCase):
    """Test parsing of extracted transformer.py code."""

    def test_three_classes_parsed_correctly(self):
        """Test that all three classes are parsed as separate top-level classes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, newline='\n') as f:
            f.write(TRANSFORMER_EXTRACT)
            temp_path = f.name

        try:
            reasoner = Reter()
            wme_count, errors = reasoner.load_python_file(temp_path)

            classes = reasoner.pattern(
                ("?x", "type", "py:Class"),
                ("?x", "name", "?name"),
                ("?x", "qualifiedName", "?qname")
            ).to_list()

            class_names = {c["?name"] for c in classes}

            # Should have exactly 3 classes
            self.assertEqual(
                class_names,
                {"NestStep", "RenderTableStep", "RenderChartStep"},
                f"Expected 3 classes, got: {class_names}"
            )

            # None should be nested
            for c in classes:
                parts = c["?qname"].split(".")
                # The qualified name should be module.ClassName, not module.Class.NestedClass
                self.assertEqual(
                    len(parts),
                    2,  # module.ClassName
                    f"{c['?name']} should not be nested, got qname: {c['?qname']}"
                )
        finally:
            os.unlink(temp_path)

    def test_init_parameters_not_accumulated(self):
        """Test that __init__ parameters are not accumulated across classes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, newline='\n') as f:
            f.write(TRANSFORMER_EXTRACT)
            temp_path = f.name

        try:
            reasoner = Reter()
            wme_count, errors = reasoner.load_python_file(temp_path)

            # Check each class's __init__ parameter count
            expected = {
                "NestStep": 5,  # parent, child, root, max_depth, children_key
                "RenderTableStep": 7,  # format, columns, title, totals, sort, group_by, max_rows
                "RenderChartStep": 9,  # chart_type, x, y, series, title, format, colors, stacked, horizontal
            }

            for class_name, expected_count in expected.items():
                params = reasoner.pattern(
                    ("?class", "type", "py:Class"),
                    ("?class", "name", class_name),
                    ("?class", "hasMethod", "?method"),
                    ("?method", "name", "__init__"),
                    ("?method", "hasParameter", "?param"),
                    ("?param", "name", "?param_name")
                ).to_list()

                param_names = [p["?param_name"] for p in params if p["?param_name"] != "self"]

                self.assertEqual(
                    len(param_names),
                    expected_count,
                    f"{class_name}.__init__ should have {expected_count} params, "
                    f"got {len(param_names)}: {param_names}"
                )
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
