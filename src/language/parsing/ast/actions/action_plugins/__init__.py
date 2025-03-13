# action_plugins_dir/__init__.py
import importlib
import pathlib
import sys

from language.parsing.ast.actions.action.action import Action, ActionType
from shared.registry import RegistryType, register

__all__ = []  # We'll populate it dynamically

package_dir = pathlib.Path(__file__).parent

def import_modules_from_directory(directory: pathlib.Path, parent_module: str):
    """Recursively imports all Python modules from the given directory."""
    for path in directory.glob("**/*.py"):  # Recursively find all .py files
        if path.name == "__init__.py":
            continue
        modules = []  # Collect module names first

        # Convert path to a module name relative to the package
        relative_path = path.relative_to(package_dir)
        module_name = ".".join(relative_path.with_suffix("").parts)
        module_path = f"{parent_module}.{module_name}"
        modules.append((module_path, module_name))  # Store module paths

        try:
            # Import the module dynamically
            imported_module = importlib.import_module(module_path)
            setattr(sys.modules[parent_module], module_name, imported_module)  # Attach module to namespace
            __all__.append(module_name)  # Add to __all__

            # Find the Action subclass in this module
            for attr_name in dir(imported_module):
                attr = getattr(imported_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Action) and attr is not Action:
                    register(RegistryType.ACTION, item=attr.generate, key=ActionType(attr_name))
                    print(f'Registered {attr_name} as a language plugin')
        except Exception as e:
            print(f"⚠️ Failed to import {module_path}: {e}")
import_modules_from_directory(package_dir, __name__)
