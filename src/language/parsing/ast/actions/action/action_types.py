import os

from dataclasses import dataclass

from file_operations.exceptions.external.file_exceptions import (
    BadPluginNameError,
    PluginNotFoundError,
)


def find_action_plugins():
    plugins = []
    actions_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    plugin_dir = os.path.join(actions_folder, "action_plugins")
    for plugin_py in os.listdir(plugin_dir):
        if ".py" in plugin_py:
            plugin = plugin_py.split('.py')[0]
            plugins.append(plugin)
        elif os.path.isdir(os.path.join(plugin_dir, plugin_py)):
            plugins.append(plugin_py)
        else:
            raise BadPluginNameError(os.path.join(plugin_dir, plugin_py))
    return plugins

plugins = find_action_plugins()

@dataclass
class ActionType:
    plugin_name: str
    def __init__(self, name: str):
        for plugin in plugins:
            if plugin == name:
                self.plugin_name = plugin
                return
        raise PluginNotFoundError(filepath=name)
    def __repr__(self):
        return self.plugin_name
    def __str__(self):
        return self.plugin_name

