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

---

## 🌟 Overview

**`LSP-pawnforge`** integrates the **[PawnForge Language Server](https://github.com/NiceFeatures/pawnforge-lsp)** into **Sublime Text** using the official **[LSP](https://packagecontrol.io/packages/LSP)** package.

It brings enterprise-grade Pawn language intelligence to Sublime Text scripters with **zero manual configuration**:
- ⚡ **Auto-downloads the language server binary** (`pawnforge-lsp.exe` / `pawnforge-lsp-linux`) automatically.
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

Open `Preferences` -> `Package Settings` -> `LSP` -> `Servers` -> `LSP-pawnforge` to customize settings:

```json
{
  "settings": {
    "command": ["${server_path}", "--stdio"],
    "enabled": true
  }
}
```

If you prefer to use a custom or globally installed binary, specify its path in `command`:
```json
{
  "settings": {
    "command": ["C:\\path\\to\\my\\pawnforge-lsp.exe", "--stdio"]
  }
}
```

---

## 📄 License
This project is licensed under the [GNU General Public License v3.0](LICENSE.txt).
