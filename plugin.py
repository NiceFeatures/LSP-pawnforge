from LSP.plugin import AbstractPlugin
from LSP.plugin import register_plugin
from LSP.plugin import unregister_plugin
import os
import sys
import shutil
import stat
import sublime
import sublime_plugin
import urllib.request
import ssl

PACKAGE_NAME = "LSP-pawnforge"
SERVER_VERSION = "1.0.1"


class PawnForge(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return "pawnforge"

    @classmethod
    def get_binary_name(cls) -> str:
        return "pawnforge-lsp.exe" if sys.platform.startswith("win") else "pawnforge-lsp-linux"

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

            if not sys.platform.startswith("win"):
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

        # Inject settings into initialization_options so the server has them immediately
        try:
            settings_dict = configuration.settings.copy()
            init_opts = configuration.init_options.get_resolved(window.extract_variables()) or {}
            if not isinstance(init_opts, dict):
                init_opts = {}
            init_opts["settings"] = settings_dict
            init_opts["includePaths"] = settings_dict.get("includePaths", [])
            init_opts["compiler"] = settings_dict.get("compiler", {})
            configuration.init_options.set(init_opts)
            print(f"[{PACKAGE_NAME}] Injected include paths: {settings_dict.get('includePaths', [])}")
        except Exception as e:
            print(f"[{PACKAGE_NAME}] Failed to inject init_options: {e}")

    def on_workspace_configuration(self, params, configuration):
        if configuration is not None:
            return configuration
        session = self.weaksession()
        if session:
            return session.config.settings.copy()
        return None


class PawnBuildCommand(sublime_plugin.WindowCommand):
    """Compile AMX Mod X (.sma) plugins via amxxpc.exe with clickable errors."""

    def run(self):
        view = self.window.active_view()
        if not view:
            return

        # Auto-save file before compilation
        if view.is_dirty():
            view.run_command("save")

        file_path = view.file_name()
        if not file_path:
            sublime.error_message("[PawnForge] Please save the .sma file before compiling.")
            return

        # Load LSP-pawnforge settings
        s = sublime.load_settings("LSP-pawnforge.sublime-settings")
        user_settings = s.get("settings", {})

        # Find compiler executable
        compiler_exe = user_settings.get("compiler", {}).get("executablePath", "")
        file_dir = os.path.dirname(file_path)

        if not compiler_exe or not os.path.isfile(compiler_exe):
            # Try auto-detecting amxxpc.exe in common locations
            home = os.path.expanduser("~")
            candidates = [
                os.path.join(file_dir, "amxxpc.exe"),
                os.path.join(file_dir, "..", "amxxpc.exe"),
                os.path.join(home, "Desktop", "compiler", "amxxpc.exe"),
                r"C:\HLDS\cstrike\addons\amxmodx\scripting\amxxpc.exe",
                shutil.which("amxxpc.exe") or ""
            ]
            for cand in candidates:
                if cand and os.path.isfile(cand):
                    compiler_exe = cand
                    break

        if not compiler_exe or not os.path.isfile(compiler_exe):
            sublime.error_message(
                "[PawnForge] Compiler amxxpc.exe not found!\n\n"
                "Please configure 'compiler.executablePath' in:\n"
                "Preferences > Package Settings > LSP > Servers > LSP-pawnforge > Settings"
            )
            return

        # Collect include paths
        raw_includes = []
        raw_includes.extend(user_settings.get("includePaths", []))
        raw_includes.extend(user_settings.get("compiler", {}).get("includePaths", []))
        raw_includes.extend(user_settings.get("compiler", {}).get("globalIncludePaths", []))

        # Always include the local file directory and local 'include' folder
        raw_includes.append(file_dir)
        raw_includes.append(os.path.join(file_dir, "include"))

        # Unique include directories
        seen_dirs = set()
        unique_includes = []
        for inc in raw_includes:
            if not inc:
                continue
            norm = os.path.normpath(inc if os.path.isabs(inc) else os.path.join(file_dir, inc))
            if os.path.isdir(norm) and norm not in seen_dirs:
                seen_dirs.add(norm)
                unique_includes.append(norm)

        # Compiler output path
        custom_output = user_settings.get("compiler", {}).get("outputPath", "")
        if custom_output:
            if not os.path.isabs(custom_output):
                custom_output = os.path.join(file_dir, custom_output)
            os.makedirs(custom_output, exist_ok=True)
            output_amxx = os.path.join(custom_output, os.path.splitext(os.path.basename(file_path))[0] + ".amxx")
        else:
            output_amxx = os.path.splitext(file_path)[0] + ".amxx"

        # Compiler options
        raw_opts = user_settings.get("compiler", {}).get("options", [])
        options = [opt for opt in raw_opts if not opt.startswith("-O")]

        # Construct command line
        cmd = [compiler_exe, file_path, f"-o{output_amxx}"]
        for inc in unique_includes:
            cmd.append(f"-i{inc}")
        cmd.extend(options)

        print(f"[{PACKAGE_NAME}] Compiling via: {' '.join(cmd)}")

        # Run via Sublime's native exec command with file_regex for clickable error navigation (F4 / Shift+F4)
        self.window.run_command("exec", {
            "cmd": cmd,
            "working_dir": file_dir,
            "file_regex": r"^(.+?)\((\d+)\) : (fatal error|error|warning) \d+: (.*)$"
        })


def plugin_loaded():
    register_plugin(PawnForge)


def plugin_unloaded():
    unregister_plugin(PawnForge)
