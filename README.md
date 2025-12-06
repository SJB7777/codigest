# Codigest

> *Digest your codebase for LLM context with Vibe Coding flow.*

## Prerequisites

Before you begin, ensure you have **git** and **uv** installed on your system.

  * **Git:** [Install Git](https://git-scm.com/downloads)
  * **uv:** [Install uv](https://github.com/astral-sh/uv)

To install `uv` quickly:

### MacOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### PowerShell (Windows):

```bash
winget install --id astral-sh.uv
```

> **⚠️ Note:** After installing uv on Windows, you must **restart your terminal** (or VS Code) for the command to be recognized.

-----

## 🚀 Quick Start: Install & Run Anywhere

Follow these steps to install this tool globally so you can run it from any directory on your computer.

### 1\. Clone the Repository

First, download the source code to your local machine.

```bash
git clone https://github.com/SJB7777/codigest.git
cd codigest
```

### 2\. Install via uv Tool

Run the following command to build and install the tool globally.

```bash
# The --force flag ensures it overwrites any existing installation
uv tool install . --force
```

> **🎉 Ready\!** Once this command finishes, the `codigest` command is globally active. You can now use it from **any folder**.

-----

## 📖 Usage Guide

Once installed, you can use `codigest` to instantly prepare your codebase for LLMs.

### 1\. Generate Context

Navigate to your project directory and run:

```bash
cd your/project/path
codigest
```

This will scan your current directory and generate a file named **`codigest_context.txt`**.

### 2\. How to Use with LLMs

1.  Open the generated `codigest_context.txt` file.
2.  **Upload** or **Copy & Paste** the content into your AI tool (ChatGPT, Claude, Gemini, etc.).
3.  Start your session with full context of your project structure and code.

### ✨ Features

  * **Respects `.gitignore`:** Automatically skips files and folders ignored by git.
  * **Filters Binaries:** Skips non-text files (images, executables) to keep the context clean.
  * **Tree Structure:** Includes a visual directory tree at the top of the context file.

### Options

To see all available options and flags:

```bash
codigest --help
```

-----

## 🛠️ Developer Setup (Manual Virtual Environment)

If you want to modify the code or run it in an isolated local environment, follow these steps.

### 1\. Create a Virtual Environment

Initialize a new virtual environment using `uv`.

```bash
uv venv
```

### 2\. Activate the Environment

  * **macOS / Linux:**
    ```bash
    source .venv/bin/activate
    ```
  * **Windows:**
    ```powershell
    .venv\Scripts\activate
    ```

### 3\. Install Dependencies

Sync the project dependencies into your virtual environment.

```bash
uv sync
```

### 4\. Run Locally

You can now run the script within this specific environment.

```bash
codigest