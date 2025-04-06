"""
Plugin system for Wiseflow.

This module provides the base classes and utilities for the plugin system.
"""

from typing import Dict, List, Type, Any, Optional
import importlib
import os
import logging
import json
import inspect
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class PluginBase(ABC):
    """Base class for all plugins."""
    
    name: str = "base_plugin"
    description: str = "Base plugin class"
    version: str = "0.1.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin with optional configuration."""
        self.config = config or {}
        self.is_enabled = True
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful, False otherwise."""
        pass
    
    def enable(self) -> None:
        """Enable the plugin."""
        self.is_enabled = True
        logger.info(f"Plugin {self.name} enabled")
        
    def disable(self) -> None:
        """Disable the plugin."""
        self.is_enabled = False
        logger.info(f"Plugin {self.name} disabled")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the plugin configuration."""
        return self.config
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the plugin configuration."""
        self.config = config
        
    def __str__(self) -> str:
        """Return a string representation of the plugin."""
        return f"{self.name} (v{self.version}): {self.description}"


class PluginManager:
    """Manager for loading and managing plugins."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """Initialize the plugin manager."""
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, PluginBase] = {}
        
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory."""
        plugin_modules = []
        
        # Walk through the plugins directory
        for root, dirs, files in os.walk(self.plugins_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    # Convert file path to module path
                    rel_path = os.path.relpath(os.path.join(root, file), start=os.path.dirname(self.plugins_dir))
                    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")
                    plugin_modules.append(module_path)
        
        return plugin_modules
    
    def load_plugin(self, module_path: str) -> Optional[PluginBase]:
        """Load a plugin from a module path."""
        try:
            module = importlib.import_module(module_path)
            
            # Find plugin classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj is not PluginBase):
                    
                    # Create an instance of the plugin
                    plugin = obj()
                    self.plugins[plugin.name] = plugin
                    logger.info(f"Loaded plugin: {plugin}")
                    return plugin
                    
            logger.warning(f"No plugin class found in module: {module_path}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {module_path}: {e}")
            return None
    
    def load_all_plugins(self) -> Dict[str, PluginBase]:
        """Discover and load all available plugins."""
        plugin_modules = self.discover_plugins()
        
        for module_path in plugin_modules:
            self.load_plugin(module_path)
            
        return self.plugins
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a plugin by name."""
        return self.plugins.get(name)
    
    def initialize_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize a plugin with optional configuration."""
        plugin = self.get_plugin(name)
        if plugin:
            if config:
                plugin.set_config(config)
            return plugin.initialize()
        return False
    
    def initialize_all_plugins(self, configs: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, bool]:
        """Initialize all loaded plugins with optional configurations."""
        results = {}
        configs = configs or {}
        
        for name, plugin in self.plugins.items():
            config = configs.get(name)
            results[name] = self.initialize_plugin(name, config)
            
        return results
