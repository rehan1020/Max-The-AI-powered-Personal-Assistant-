"""App registry resolver.

Loads app_registry.yaml and resolves app names to launch commands.
Uses dynamic discovery via shutil.which() — no hardcoded paths.
"""

import difflib
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import yaml


class AppRegistry:
    """Cross-platform app registry resolver."""

    def __init__(self, registry_path: Path):
        """Initialize the app registry.

        Args:
            registry_path: Path to the app_registry.yaml file.
        """
        with open(registry_path) as f:
            self._registry = yaml.safe_load(f)
        self._os = platform.system().lower().replace("darwin", "macos")

    def resolve(self, name: str) -> Optional[list[str]]:
        """Resolve an app name to a launch command.

        Uses shutil.which() to verify commands exist before returning.

        Args:
            name: The friendly name of the app to launch.

        Returns:
            A list of command arguments, or None if the app is not found.
        """
        name = name.lower().strip()

        # Direct match
        if name in self._registry:
            return self._get_verified_command(name)

        # Alias match
        for key, entry in self._registry.items():
            if name in [a.lower() for a in entry.get("aliases", [])]:
                return self._get_verified_command(key)

        # Fuzzy match (tolerance = 0.6)
        candidates = list(self._registry.keys())
        matches = difflib.get_close_matches(name, candidates, n=1, cutoff=0.6)
        if matches:
            return self._get_verified_command(matches[0])

        return None

    def _get_verified_command(self, key: str) -> list[str]:
        """Get a verified command for a given app key.

        Tries to find an existing executable on the system via shutil.which().
        Falls back to the registry value even if not verified.
        """
        entry = self._registry[key]

        # Try OS-specific search names first (for Windows, these are candidate exe names)
        search_key = f"{self._os}_search"
        if search_key in entry:
            for candidate in entry[search_key]:
                found = shutil.which(candidate)
                if found:
                    return [found]

        # Try the primary OS command
        cmd = self._get_command(key)

        # For single-element commands, verify via shutil.which
        if len(cmd) == 1:
            found = shutil.which(cmd[0])
            if found:
                return [found]

        # Try OS-specific fallbacks
        fallback_key = f"{self._os}_fallback"
        if fallback_key in entry:
            for candidate in entry[fallback_key]:
                found = shutil.which(candidate)
                if found:
                    return [found]

        # Return original command even if not verified (os.startfile may handle it)
        return cmd

    def _get_command(self, key: str) -> list[str]:
        """Get the command for a given app key."""
        entry = self._registry[key]
        if self._os in entry:
            return entry[self._os]
        if "linux" in entry:
            return entry["linux"]
        return [key]

    def try_launch(self, name: str) -> bool:
        """Try to launch an app by name.

        Args:
            name: The friendly name of the app to launch.

        Returns:
            True if launch succeeded, False otherwise.
        """
        cmd = self.resolve(name)
        if cmd:
            try:
                subprocess.Popen(cmd)
                return True
            except FileNotFoundError:
                pass

        try:
            subprocess.Popen([name])
            return True
        except FileNotFoundError:
            pass

        return False

    def get_all_apps(self) -> list[str]:
        """Get a list of all registered app names."""
        return list(self._registry.keys())
