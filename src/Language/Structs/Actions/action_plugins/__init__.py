# action_plugins_dir/__init__.py
import importlib
import pathlib

__all__ = []  # We'll populate it dynamically

package_dir = pathlib.Path(__file__).parent

for py_file in package_dir.glob("*.py"):
    if py_file.name == "__init__.py":
        continue
    module_name = py_file.stem  # e.g. "plugin1"
    module_path = f"{__name__}.{module_name}"
    # Dynamically import the module
    imported_module = importlib.import_module(module_path)
