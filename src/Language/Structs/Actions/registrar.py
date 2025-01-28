import importlib
import pkgutil
from typing import List


class ActionRegistrar:
    def __init__(self):
        self.plugins_dir = "language.structs.actions.action_plugins"  # Python package format
        self.imported_modules: List[str] = []
        self.discover_actions()

    def discover_actions(self) -> None:
        """Dynamically find and import all modules in the plugins directory."""
        # Discover and import modules in the package
        try:
            package = importlib.import_module(self.plugins_dir)  # Import the package itself first
            package_path = package.__path__  # Get the package path for pkgutil to scan

            # Use pkgutil to iterate through modules in the package
            for _, module_name, is_pkg in pkgutil.iter_modules(package_path):
                if not is_pkg:
                    module_path = f"{self.plugins_dir}.{module_name}"
                    print(module_path)
                    importlib.import_module(module_path)  # Import the module dynamically
                    self.imported_modules.append(module_path)

        except ModuleNotFoundError:
            raise ValueError(f"Package '{self.plugins_dir}' does not exist or is not a valid package.")

    def get_imported_modules(self) -> List[str]:
        """Return a list of all imported modules."""
        return self.imported_modules
