"""
Command Registry Pattern implementation.
Decouples command logic from the CLI/Shell interface.
"""
from typing import Callable

class CommandInfo:
    def __init__(self, func: Callable, name: str, desc: str, aliases: list[str]):
        self.func = func
        self.name = name
        self.desc = desc
        self.aliases = aliases

class CommandRegistry:
    def __init__(self):
        self.commands: dict[str, CommandInfo] = {}
        self.alias_map: dict[str, str] = {}

    def register(self, name: str, desc: str = "", aliases: list[str] | None = None):
        """Decorator to register a function as a command."""
        if aliases is None:
            aliases = []
        
        def decorator(func):
            cmd = CommandInfo(func, name, desc, aliases)
            self.commands[name] = cmd
            for alias in aliases:
                self.alias_map[alias] = name
            return func
        return decorator

    def get_command(self, name: str) -> CommandInfo | None:
        """Retrieves command info by name or alias."""
        return self.commands.get(name) or self.commands.get(self.alias_map.get(name))

    def get_help_text(self) -> str:
        """Generates help text dynamically."""
        lines = ["\n🛠️  Available Commands:"]
        for name in sorted(self.commands.keys()):
            cmd = self.commands[name]
            alias_str = f"({', '.join(cmd.aliases)})" if cmd.aliases else ""
            lines.append(f"  {name:<10} {alias_str:<12} : {cmd.desc}")
        return "\n".join(lines)

registry = CommandRegistry()