# LSP-pawnforge

<p align="center">
  <strong>Sublime Text helper package for PawnForge (AMX Mod X Pawn Language Server).</strong>
</p>

<p align="center">
  <a href="https://github.com/NiceFeatures/LSP-pawnforge/releases">
    <img alt="GitHub Release" src="https://img.shields.io/github/v/release/NiceFeatures/LSP-pawnforge?style=for-the-badge&color=22c55e">
  </a>
  <img alt="License" src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge">
  <img alt="Sublime Text 3 & 4" src="https://img.shields.io/badge/Sublime%20Text-3%20|%204-orange?style=for-the-badge">
</p>



### 🖱️ Optional: Enable Ctrl + Click for Go to Definition
By default in Sublime Text, `Ctrl + Click` adds multi-cursors, while **`F12`** goes to definition out of the box.

If you prefer **`Ctrl + Click`** to jump to definitions (like in VS Code), create or open:
`Preferences > Package Settings > LSP > Mouse Bindings` (or `Packages/User/Default (Windows).sublime-mousemap`):

```json
[
  {
    "button": "button1",
    "count": 1,
    "modifiers": ["ctrl"],
    "press_command": "drag_select",
    "command": "lsp_symbol_definition",
    "context": [
      {
        "key": "selector",
        "operator": "equal",
        "operand": "source.pawn, source.amxx, source.amxxpawn"
      }
    ]
  }
]
```

---

## 🌟 Overview

**`LSP-pawnforge`** integrates the **[PawnForge Language Server](https://github.com/NiceFeatures/pawnforge-lsp)** into **Sublime Text** using the official **[LSP](https://packagecontrol.io/packages/LSP)** package.

It brings enterprise-grade Pawn language intelligence to Sublime Text scripters with **zero manual configuration**:
- ⚡ **Auto-downloads the native language server binary** (`pawnforge-lsp.exe` / `pawnforge-lsp-linux`) on first launch (no Node.js required!).
- 📦 **Built-in syntax highlighting** for `.sma` and `.inc` files (`Pawn.sublime-syntax`).

---

## ✨ Features

- **Instant Autocomplete:** AMX Mod X 1.8.2 / 1.9 / 1.10 and ReAPI native functions with parameter hints and inline documentation.
- **Go to Definition (`F12`):** Instant $O(1)$ navigation to functions, stocks, variables, and macros.
- **Find all References (`Shift+F12`):** Project-wide search across `.inc` and `.sma` files with smart definition exclusion.
- **Hover Information:** Hover over any symbol to inspect its prototype, parameters, tags, and documentation.
- **Smart String Callback Navigation:** Jump to callbacks in `set_task(1.0, "@Callback")`.
- **Workspace Symbols (`Ctrl+T`):** Fuzzy symbol lookup across the entire workspace.
- **Document Highlight:** Highlights all occurrences of the selected identifier.
- **Code Folding:** Native code folding for `#if/#endif`, functions, and blocks.

---

## 🚀 Installation

### Prerequisites
1. In Sublime Text, open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).
2. Type `Package Control: Install Package` and press Enter.
3. Search for **`LSP`** and install it.

---

### Installing LSP-pawnforge

#### Option A: Package Control (Recommended)
1. Open the Command Palette (`Ctrl+Shift+P`).
2. Run `Package Control: Install Package`.
3. Search for **`LSP-pawnforge`** and press Enter.

#### Option B: Manual Installation (Git Clone)
Clone this repository directly into your Sublime Text `Packages` directory:

**Windows:**
```powershell
cd "$env:APPDATA\Sublime Text\Packages"
# (or for Sublime Text 3: "$env:APPDATA\Sublime Text 3\Packages")
git clone https://github.com/NiceFeatures/LSP-pawnforge.git
```

**Linux:**
```bash
cd ~/.config/sublime-text/Packages
git clone https://github.com/NiceFeatures/LSP-pawnforge.git
```

Restart Sublime Text and open any `.sma` or `.inc` file!

---

## ⚙️ Configuration

### Opening Settings
You can open the PawnForge configuration at any time:
- **Menu:** `Preferences` ➔ `Package Settings` ➔ `LSP` ➔ `Servers` ➔ `LSP-pawnforge` ➔ `Settings`
- **Command Palette (`Ctrl+Shift+P`):** Type **`Preferences: LSP-pawnforge Settings`** and press Enter.

This opens the default settings on the left (read-only reference) and your user settings on the right (`Packages/User/LSP-pawnforge.sublime-settings`).

---

### 1. Include Paths Configuration

To add your AMX Mod X `include` folders (e.g. `amxmodx.inc`, `cstrike.inc`, ReAPI):

#### User Global Settings (`Packages/User/LSP-pawnforge.sublime-settings`)
```json
{
  "settings": {
    "includePaths": [
      "include",
      "C:/HLDS/cstrike/addons/amxmodx/scripting/include"
    ]
  }
}
```

#### Per-Project Settings (`your-project.sublime-project`)
If you work with different server directories per project, define them inside your project file:
```json
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    "LSP": {
      "pawnforge": {
        "settings": {
          "includePaths": [
            "${project_path}/include",
            "C:/HLDS/cstrike/addons/amxmodx/scripting/include"
          ]
        }
      }
    }
  }
}
```

---

### 2. Available Settings Reference

| Setting | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `includePaths` | `array` | `["include"]` | List of paths to search for `.inc` files (workspace-relative or absolute). |
| `globalIncludePaths` | `array` | `[]` | Additional include directories applied globally across all projects. |
| `compiler.executablePath` | `string` | `""` | Path to `amxxpc.exe` compiler binary. |
| `compiler.includePaths` | `array` | `[]` | Include paths specifically passed to the compiler. |
| `compiler.options` | `array` | `[]` | Extra CLI options passed to compiler (e.g. `["-O2"]`). |
| `compiler.outputPath` | `string` | `""` | Directory where compiled `.amxx` binaries should be saved. |
| `language.reparseInterval` | `number` | `300` | Debounce delay in milliseconds before reparsing the file upon typing. |
| `language.webApiLinks` | `boolean` | `false` | Enable clickable links to AMX Mod X Web API docs in hover tooltips. |

---

## 📜 License
This project is licensed under the [GNU General Public License v3.0](LICENSE.txt).
