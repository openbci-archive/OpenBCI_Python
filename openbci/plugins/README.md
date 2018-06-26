
To create a new plugin, see print.py and print.yapsy-plugin for a minimal example and plugin_interface.py for documentation about more advanced features.

Note: "__init__" will be automatically called when the main program loads, even if the plugin is not used, put computationally intensive instructions in activate() instead.
