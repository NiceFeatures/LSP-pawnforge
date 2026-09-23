from LSP.plugin import AbstractPlugin
from LSP.plugin import register_plugin
from LSP.plugin import unregister_plugin
import os
import shutil
import stat
import sublime
import urllib.request
import ssl

PACKAGE_NAME = "LSP-pawnforge"
SERVER_VERSION = "1.0.0"


class PawnForge(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return "pawnforge"

    @classmethod
    def get_binary_name(cls) -> str:
        return "pawnforge-lsp.exe" if sublime.platform() == "windows" else "pawnforge-lsp-linux"

    @classmethod
    def get_server_path(cls) -> str:
        binary_name = cls.get_binary_name()

        # 1. Check if user has pawnforge-lsp in system PATH
        path_binary = shutil.which(binary_name)
        if path_binary and os.path.isfile(path_binary):
            return path_binary

        # 2. Check local package storage directory ($DATA/Package Storage/LSP-pawnforge/bin)
        try:
            storage_dir = os.path.join(cls.storage_path(), PACKAGE_NAME)
            local_binary = os.path.join(storage_dir, "bin", binary_name)
            if os.path.isfile(local_binary):
                return local_binary
        except Exception:
            pass

        # 3. Check desktop build directory (local developer fallback)
        home = os.path.expanduser("~")
        desktop_binary = os.path.join(home, "Desktop", "pawnforge-lsp", "bin", binary_name)
        if os.path.isfile(desktop_binary):
            return desktop_binary

        return ""

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        server_path = cls.get_server_path()
        return not bool(server_path)

    @classmethod
    def install_or_update(cls) -> None:
        try:
            storage_dir = os.path.join(cls.storage_path(), PACKAGE_NAME)
            bin_dir = os.path.join(storage_dir, "bin")
            os.makedirs(bin_dir, exist_ok=True)

            binary_name = cls.get_binary_name()
            destination = os.path.join(bin_dir, binary_name)

            url = f"https://github.com/NiceFeatures/pawnforge-lsp/releases/download/v{SERVER_VERSION}/{binary_name}"

            sublime.status_message(f"[{PACKAGE_NAME}] Downloading {binary_name}...")
            print(f"[{PACKAGE_NAME}] Downloading {binary_name} from {url} to {destination}...")

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(url, headers={"User-Agent": "Sublime-LSP-pawnforge"})
            with urllib.request.urlopen(req, context=ctx) as response, open(destination, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

            if sublime.platform() != "windows":
                st = os.stat(destination)
                os.chmod(destination, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

            sublime.status_message(f"[{PACKAGE_NAME}] Server installed successfully!")
            print(f"[{PACKAGE_NAME}] Server installed successfully at {destination}")
        except Exception as e:
            print(f"[{PACKAGE_NAME}] Installation failed: {e}")

    @classmethod
    def on_pre_start(cls, window, initiating_view, workspace_folders, configuration):
        server_path = cls.get_server_path()
        if not server_path:
            cls.install_or_update()
            server_path = cls.get_server_path()

        if server_path:
            print(f"[{PACKAGE_NAME}] Starting language server using: {server_path}")
            cmd = configuration.command
            new_cmd = [server_path if arg == "${server_path}" else arg for arg in cmd]
            configuration.command = new_cmd
        else:
            print(f"[{PACKAGE_NAME}] Error: Server binary not found!")


def plugin_loaded():
    register_plugin(PawnForge)


def plugin_unloaded():
    unregister_plugin(PawnForge)
