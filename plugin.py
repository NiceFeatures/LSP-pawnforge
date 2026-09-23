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
        # 1. Check if user has pawnforge-lsp in system PATH
        binary_name = "pawnforge-lsp.exe" if sublime.platform() == "windows" else "pawnforge-lsp"
        path_binary = shutil.which(binary_name)
        if path_binary and os.path.isfile(path_binary):
            return path_binary

        # 2. Check local package storage directory
        storage_dir = cls.storage_path()
        local_binary = os.path.join(storage_dir, "bin", cls.get_binary_name())
        if os.path.isfile(local_binary):
            return local_binary

        return ""

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        server_path = cls.get_server_path()
        return not bool(server_path)

    @classmethod
    def install_or_update(cls) -> None:
        storage_dir = cls.storage_path()
        bin_dir = os.path.join(storage_dir, "bin")
        os.makedirs(bin_dir, exist_ok=True)

        binary_name = cls.get_binary_name()
        destination = os.path.join(bin_dir, binary_name)

        url = f"https://github.com/NiceFeatures/pawnforge-lsp/releases/download/v{SERVER_VERSION}/{binary_name}"

        sublime.status_message(f"[{PACKAGE_NAME}] Downloading {binary_name}...")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={"User-Agent": "Sublime-LSP-pawnforge"})
        with urllib.request.urlopen(req, context=ctx) as response, open(destination, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

        # Grant executable permissions on Linux/macOS
        if sublime.platform() != "windows":
            st = os.stat(destination)
            os.chmod(destination, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        sublime.status_message(f"[{PACKAGE_NAME}] Server installed successfully!")

    @classmethod
    def on_pre_start(cls, window, initiating_view, workspace_folders, configuration):
        server_path = cls.get_server_path()
        if not server_path:
            cls.install_or_update()
            server_path = cls.get_server_path()

        if server_path:
            cmd = configuration.command
            new_cmd = [server_path if arg == "${server_path}" else arg for arg in cmd]
            configuration.command = new_cmd


def plugin_loaded():
    register_plugin(PawnForge)


def plugin_unloaded():
    unregister_plugin(PawnForge)
