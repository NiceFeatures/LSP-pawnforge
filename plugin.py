from pathlib import Path
import os
import shutil
import stat
import sublime
import sublime_plugin
import urllib.request
import ssl

from LSP.plugin import (
    ClientResponse,
    LspPlugin,
    OnPreStartContext,
    PluginStartError,
)

PACKAGE_NAME = "LSP-pawnforge"
SERVER_VERSION = "1.0.1"


class PawnForge(LspPlugin):

    @classmethod
    def get_binary_name(cls) -> str:
        return "pawnforge-lsp.exe" if os.name == "nt" else "pawnforge-lsp-linux"

    @classmethod
    def get_server_path(cls) -> str:
        binary_name = cls.get_binary_name()

        # 1. Check if user has pawnforge-lsp in system PATH
        path_binary = shutil.which(binary_name)
        if path_binary and os.path.isfile(path_binary):
            return path_binary

        # 2. Check local package storage directory ($DATA/Package Storage/LSP-pawnforge/bin)
        try:
            local_binary = cls.plugin_storage_path / "bin" / binary_name
            if local_binary.is_file():
                return str(local_binary)
        except Exception:
            pass

        # 3. Check desktop build directory (local developer fallback)
        home = os.path.expanduser("~")
        desktop_binary = os.path.join(home, "Desktop", "pawnforge-lsp", "bin", binary_name)
        if os.path.isfile(desktop_binary):
            return desktop_binary

        return ""

    @classmethod
    def needs_installation_or_update(cls) -> bool:
        server_path = cls.get_server_path()
        if not server_path:
            return True
        # For managed installation in plugin_storage_path, check version
        version_file = cls.plugin_storage_path / "bin" / "VERSION"
        managed_binary = cls.plugin_storage_path / "bin" / cls.get_binary_name()
        if managed_binary.is_file():
            if not version_file.is_file():
                return True
            try:
                if version_file.read_text(encoding="utf-8").strip() != SERVER_VERSION:
                    return True
            except Exception:
                return True
        return False

    @classmethod
    def install_server(cls) -> None:
        bin_dir = cls.plugin_storage_path / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        binary_name = cls.get_binary_name()
        destination = bin_dir / binary_name
        version_file = bin_dir / "VERSION"

        url = f"https://github.com/NiceFeatures/pawnforge-lsp/releases/download/v{SERVER_VERSION}/{binary_name}"

        sublime.status_message(f"[{PACKAGE_NAME}] Downloading {binary_name} v{SERVER_VERSION}...")
        print(f"[{PACKAGE_NAME}] Downloading {binary_name} from {url} to {destination}...")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={"User-Agent": "Sublime-LSP-pawnforge"})
        with urllib.request.urlopen(req, context=ctx) as response, open(destination, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

        if os.name != "nt":
            st = os.stat(destination)
            os.chmod(destination, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        version_file.write_text(SERVER_VERSION, encoding="utf-8")

        sublime.status_message(f"[{PACKAGE_NAME}] Server v{SERVER_VERSION} installed successfully!")
        print(f"[{PACKAGE_NAME}] Server installed successfully at {destination}")

    @classmethod
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        if cls.needs_installation_or_update():
            try:
                cls.install_server()
            except Exception as e:
                print(f"[{PACKAGE_NAME}] Installation/Update failed: {e}")

        server_path = cls.get_server_path()
        if not server_path:
            raise PluginStartError(f"[{PACKAGE_NAME}] Server binary not found and installation failed.")

        print(f"[{PACKAGE_NAME}] Starting language server using: {server_path}")
        context.variables["server_path"] = str(server_path)
        context.configuration.command = [
            str(server_path) if arg == "${server_path}" else arg
            for arg in context.configuration.command
        ]

        # Inject settings into initialization_options so the server has them immediately
        try:
            settings_dict = context.configuration.settings.copy()
            window = context.view.window() or sublime.active_window()
            vars_dict = window.extract_variables() if window else {}
            init_opts = context.configuration.initialization_options.get_resolved(vars_dict) or {}
            if not isinstance(init_opts, dict):
                init_opts = {}
            init_opts["settings"] = settings_dict
            init_opts["includePaths"] = settings_dict.get("includePaths", [])
            init_opts["compiler"] = settings_dict.get("compiler", {})
            context.configuration.initialization_options.set(init_opts)
            print(f"[{PACKAGE_NAME}] Injected include paths: {settings_dict.get('includePaths', [])}")
        except Exception as e:
            print(f"[{PACKAGE_NAME}] Failed to inject init_options: {e}")

    def on_pre_send_response_async(self, response: ClientResponse) -> None:
        if response.get("method") == "workspace/configuration":
            session = self.weaksession()
            if not session:
                return
            result = response.get("result")
            if isinstance(result, list):
                for i, item in enumerate(result):
                    if item is None or item == {}:
                        result[i] = session.config.settings.copy()


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


def plugin_loaded() -> None:
    PawnForge.register()


def plugin_unloaded() -> None:
    PawnForge.unregister()
