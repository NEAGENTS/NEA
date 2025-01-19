import ast
import inspect
import builtins
from typing import Set
import textwrap
from .utils import BASE_BUILTIN_MODULES

_BUILTIN_NAMES = set(vars(builtins))


class MethodChecker(ast.NodeVisitor):
    """
    Checks that a method:
    - Only uses defined names.
    - Contains no local imports (e.g. numpy is ok but local_script is not).
    """

    def __init__(self, class_attributes: Set[str], check_imports: bool = True):
        self.undefined_names = set()
        self.imports = {}
        self.from_imports = {}
        self.assigned_names = set()
        self.arg_names = set()
        self.class_attributes = class_attributes
        self.errors = []
        self.check_imports = check_imports

    def visit_arguments(self, node):
        """Collect function arguments"""
        self.arg_names = {arg.arg for arg in node.args}
        if node.kwarg:
            self.arg_names.add(node.kwarg.arg)
        if node.vararg:
            self.arg_names.add(node.vararg.arg)

    def visit_Import(self, node):
        for name in node.names:
            actual_name = name.asname or name.name
            self.imports[actual_name] = name.name

    def visit_ImportFrom(self, node):
        module = node.module or ""
        for name in node.names:
            actual_name = name.asname or name.name
            self.from_imports[actual_name] = (module, name.name)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned_names.add(target.id)
        self.generic_visit(node)

    def visit_With(self, node):
        """Track aliases in 'with' statements (the 'y' in 'with X as y')"""
        for item in node.items:
            if item.optional_vars:  # This is the 'y' in 'with X as y'
                if isinstance(item.optional_vars, ast.Name):
                    self.assigned_names.add(item.optional_vars.id)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        """Track exception aliases (the 'e' in 'except Exception as e')"""
        if node.name:  # This is the 'e' in 'except Exception as e'
            self.assigned_names.add(node.name)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Track annotated assignments."""
        if isinstance(node.target, ast.Name):
            self.assigned_names.add(node.target.id)
        if node.value:
            self.generic_visit(node)

    def visit_For(self, node):
        target = node.target
        if isinstance(target, ast.Name):
            self.assigned_names.add(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                if isinstance(elt, ast.Name):
                    self.assigned_names.add(elt.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if not (isinstance(node.value, ast.Name) and node.value.id == "self"):
            self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if not (
                node.id in _BUILTIN_NAMES
                or node.id in BASE_BUILTIN_MODULES
                or node.id in self.arg_names
                or node.id == "self"
                or node.id in self.class_attributes
                or node.id in self.imports
                or node.id in self.from_imports
                or node.id in self.assigned_names
            ):
                self.errors.append(f"Name '{node.id}' is undefined.")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if not (
                node.func.id in _BUILTIN_NAMES
                or node.func.id in BASE_BUILTIN_MODULES
                or node.func.id in self.arg_names
                or node.func.id == "self"
                or node.func.id in self.class_attributes
                or node.func.id in self.imports
                or node.func.id in self.from_imports
                or node.func.id in self.assigned_names
            ):
                self.errors.append(f"Name '{node.func.id}' is undefined.")
        self.generic_visit(node)


def validate_tool_attributes(cls, check_imports: bool = True) -> None:
    """
    Validates that a Tool class follows the proper patterns:
    - __init__ should take no arguments (args chosen at init are not traceable).
    - Class attributes should be simple types (strings, dicts).
    - Methods should only use defined imports and self-contained logic.

    Raises all errors encountered, otherwise returns None.
    """
    errors = []

    # Get the source code of the class and parse it to an AST
    source = textwrap.dedent(inspect.getsource(cls))
    tree = ast.parse(source)

    if not isinstance(tree.body[0], ast.ClassDef):
        raise ValueError("Source code must define a class")

    # Check that __init__ method takes no arguments
    if cls.__init__.__qualname__ != "Tool.__init__":
        sig = inspect.signature(cls.__init__)
        non_self_params = [arg_name for arg_name in sig.parameters if arg_name != "self"]
        if non_self_params:
            errors.append(
                f"Tool class '__init__' method has unexpected arguments: {non_self_params}. "
                "Ensure no arguments are specified, as values should be hardcoded."
            )

    class_node = tree.body[0]

    # Check class-level attributes (simplified)
    class_level_checker = ClassLevelChecker()
    class_level_checker.visit(class_node)

    if class_level_checker.complex_attributes:
        errors.append(
            f"Complex attributes found at the class level (use __init__ instead): "
            f"{', '.join(class_level_checker.complex_attributes)}"
        )

    # Validate methods within the class
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef):
            method_checker = MethodChecker(class_level_checker.class_attributes, check_imports)
            method_checker.visit(node)
            errors.extend([f"- {node.name}: {error}" for error in method_checker.errors])

    if errors:
        raise ValueError("Tool validation failed:\n" + "\n".join(errors))


class ClassLevelChecker(ast.NodeVisitor):
    """
    Checks the class-level structure for attributes and complex assignments.
    """
    def __init__(self):
        self.imported_names = set()
        self.complex_attributes = set()
        self.class_attributes = set()
        self.in_method = False

    def visit_FunctionDef(self, node):
        old_context = self.in_method
        self.in_method = True
        self.generic_visit(node)
        self.in_method = old_context

    def visit_Assign(self, node):
        if self.in_method:
            return

        # Track class attributes
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.class_attributes.add(target.id)

        # Check if assignment is more complex than simple literals
        if not all(isinstance(val, (ast.Str, ast.Num, ast.Constant, ast.Dict, ast.List, ast.Set))
                   for val in ast.walk(node.value)):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.complex_attributes.add(target.id)
