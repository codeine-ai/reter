"""Test file for Extract Composite pattern detection."""

from abc import ABC, abstractmethod
from typing import List, Optional


# ===== Pattern Example 1: HTML/XML Tags (Should be flagged - HIGH) =====

class TagBase(ABC):
    """Base class for all tags."""

    @abstractmethod
    def render(self):
        pass


class FormTag(TagBase):
    """Form tag with child management - duplicate composite implementation."""

    def __init__(self, action="", method="POST"):
        self.action = action
        self.method = method
        self.children = []

    def add_child(self, child):
        """Add a child tag."""
        self.children.append(child)

    def remove_child(self, child):
        """Remove a child tag."""
        self.children.remove(child)

    def clear_children(self):
        """Clear all children."""
        self.children.clear()

    def render(self):
        """Render the form tag."""
        return f"<form action='{self.action}' method='{self.method}'>"


class DivTag(TagBase):
    """Div tag with child management - duplicate composite implementation."""

    def __init__(self, class_name=""):
        self.class_name = class_name
        self.children = []

    def add_child(self, child):
        """Add a child tag."""
        self.children.append(child)

    def remove_child(self, child):
        """Remove a child tag."""
        self.children.remove(child)

    def clear_children(self):
        """Clear all children."""
        self.children.clear()

    def render(self):
        """Render the div tag."""
        return f"<div class='{self.class_name}'>"


class SpanTag(TagBase):
    """Span tag with child management - duplicate composite implementation."""

    def __init__(self, id_val=""):
        self.id = id_val
        self.children = []

    def add_child(self, child):
        """Add a child tag."""
        self.children.append(child)

    def remove_child(self, child):
        """Remove a child tag."""
        self.children.remove(child)

    def clear_children(self):
        """Clear all children."""
        self.children.clear()

    def render(self):
        """Render the span tag."""
        return f"<span id='{self.id}'>"


class LabelTag(TagBase):
    """Label tag with child management - duplicate composite implementation."""

    def __init__(self, for_input=""):
        self.for_input = for_input
        self.children = []

    def add_child(self, child):
        """Add a child tag."""
        self.children.append(child)

    def remove_child(self, child):
        """Remove a child tag."""
        self.children.remove(child)

    def clear_children(self):
        """Clear all children."""
        self.children.clear()

    def render(self):
        """Render the label tag."""
        return f"<label for='{self.for_input}'>"


# ===== Pattern Example 2: UI Components (Should be flagged - MEDIUM) =====

class UIComponent:
    """Base UI component."""

    def draw(self):
        """Draw the component."""
        pass


class Panel(UIComponent):
    """Panel with child components - duplicate composite implementation."""

    def __init__(self, title=""):
        self.title = title
        self.components = []

    def add_component(self, component):
        """Add a child component."""
        self.components.append(component)

    def remove_component(self, component):
        """Remove a child component."""
        self.components.remove(component)

    def draw(self):
        """Draw the panel."""
        print(f"Drawing panel: {self.title}")


class Window(UIComponent):
    """Window with child components - duplicate composite implementation."""

    def __init__(self, title=""):
        self.title = title
        self.components = []

    def add_component(self, component):
        """Add a child component."""
        self.components.append(component)

    def remove_component(self, component):
        """Remove a child component."""
        self.components.remove(component)

    def draw(self):
        """Draw the window."""
        print(f"Drawing window: {self.title}")


class Container(UIComponent):
    """Container with child components - duplicate composite implementation."""

    def __init__(self, layout="vertical"):
        self.layout = layout
        self.components = []

    def add_component(self, component):
        """Add a child component."""
        self.components.append(component)

    def remove_component(self, component):
        """Remove a child component."""
        self.components.remove(component)

    def draw(self):
        """Draw the container."""
        print(f"Drawing container with {self.layout} layout")


# ===== Pattern Example 3: File System (Should be flagged - HIGH) =====

class FileSystemNode:
    """Base class for file system nodes."""

    def __init__(self, name):
        self.name = name

    def get_size(self):
        """Get the size of the node."""
        return 0


class Directory(FileSystemNode):
    """Directory with child nodes - duplicate composite implementation."""

    def __init__(self, name):
        super().__init__(name)
        self.nodes = []

    def add_node(self, node):
        """Add a child node."""
        self.nodes.append(node)

    def remove_node(self, node):
        """Remove a child node."""
        self.nodes.remove(node)

    def clear_nodes(self):
        """Clear all nodes."""
        self.nodes.clear()

    def get_size(self):
        """Get total size of directory."""
        return sum(node.get_size() for node in self.nodes)


class Folder(FileSystemNode):
    """Folder with child nodes - duplicate composite implementation."""

    def __init__(self, name):
        super().__init__(name)
        self.nodes = []

    def add_node(self, node):
        """Add a child node."""
        self.nodes.append(node)

    def remove_node(self, node):
        """Remove a child node."""
        self.nodes.remove(node)

    def clear_nodes(self):
        """Clear all nodes."""
        self.nodes.clear()

    def get_size(self):
        """Get total size of folder."""
        return sum(node.get_size() for node in self.nodes)


class VirtualDirectory(FileSystemNode):
    """Virtual directory with child nodes - duplicate composite implementation."""

    def __init__(self, name):
        super().__init__(name)
        self.nodes = []

    def add_node(self, node):
        """Add a child node."""
        self.nodes.append(node)

    def remove_node(self, node):
        """Remove a child node."""
        self.nodes.remove(node)

    def clear_nodes(self):
        """Clear all nodes."""
        self.nodes.clear()

    def get_size(self):
        """Get total size of virtual directory."""
        return sum(node.get_size() for node in self.nodes)


# ===== Example of Good Design (Already has extracted composite) =====

class CompositeNode:
    """Base composite with child management - good pattern."""

    def __init__(self):
        self.children = []

    def add_child(self, child):
        """Add a child node."""
        self.children.append(child)

    def remove_child(self, child):
        """Remove a child node."""
        self.children.remove(child)

    def clear_children(self):
        """Clear all children."""
        self.children.clear()


class TreeNode(CompositeNode):
    """Tree node using composite base - good pattern."""

    def __init__(self, value):
        super().__init__()
        self.value = value


class GraphNode(CompositeNode):
    """Graph node using composite base - good pattern."""

    def __init__(self, id_val):
        super().__init__()
        self.id = id_val


# ===== Simple Classes (Should NOT be flagged) =====

class SimpleNode:
    """Simple node without composite pattern."""

    def __init__(self, value):
        self.value = value


class LeafNode:
    """Leaf node without children."""

    def __init__(self, data):
        self.data = data


# ===== Unrelated Classes with Similar Composite (Should be flagged - MEDIUM) =====

class MenuItem:
    """Menu item with children - not in same hierarchy."""

    def __init__(self, label):
        self.label = label
        self.items = []

    def add_item(self, item):
        """Add a child item."""
        self.items.append(item)

    def remove_item(self, item):
        """Remove a child item."""
        self.items.remove(item)

    def clear_items(self):
        """Clear all items."""
        self.items.clear()


class TreeWidget:
    """Tree widget with children - not in same hierarchy."""

    def __init__(self, title):
        self.title = title
        self.items = []

    def add_item(self, item):
        """Add a child item."""
        self.items.append(item)

    def remove_item(self, item):
        """Remove a child item."""
        self.items.remove(item)

    def clear_items(self):
        """Clear all items."""
        self.items.clear()


# ===== Classes with Different Method Names (Should NOT be flagged) =====

class Node1:
    """Node with unique method names."""

    def __init__(self):
        self.subnodes = []

    def attach(self, node):
        """Attach a node."""
        self.subnodes.append(node)

    def detach(self, node):
        """Detach a node."""
        self.subnodes.remove(node)


class Node2:
    """Node with different method names."""

    def __init__(self):
        self.descendants = []

    def link(self, node):
        """Link a node."""
        self.descendants.append(node)

    def unlink(self, node):
        """Unlink a node."""
        self.descendants.remove(node)


# ===== Client Code Examples =====

def build_form():
    """Build a form with nested tags - shows duplication problem."""
    form = FormTag(action="/submit")
    form.add_child(DivTag("form-group"))

    label = LabelTag("username")
    label.add_child(SpanTag("required"))
    form.add_child(label)

    return form


def build_ui():
    """Build UI with nested components - shows duplication problem."""
    window = Window("Main Window")
    panel = Panel("Side Panel")
    container = Container("horizontal")

    window.add_component(panel)
    panel.add_component(container)

    return window


def build_filesystem():
    """Build file system tree - shows duplication problem."""
    root = Directory("/")
    home = Folder("home")
    virtual = VirtualDirectory("virtual")

    root.add_node(home)
    home.add_node(virtual)

    return root