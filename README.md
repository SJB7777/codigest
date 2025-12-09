# Codigest: Codebase Context Manager

Codigest is a CLI tool designed to extract, structure, and track the context of your codebase.

While optimized for creating contexts for LLMs, it serves as a powerful utility for developers to grasp project structures, generate snapshots for documentation, and track local changes without polluting the main Git history.

## Core Philosophy

* **Read-Only & Safe**: Codigest never modifies your source code. It only reads, summarizes, and formats.
* **Human-Readable**: All outputs (XML snapshots, diffs, trees) are designed to be legible by developers first, machines second.
* **Session-Based Tracking**: It maintains an internal "anchor" separate from your Git commits. This allows you to track "work-in-progress" changes or specific refactoring sessions independently.
* **Lightweight**: Zero external database, zero daemon. It runs entirely on standard libraries and the file system.

## Key Features

### 1. Project Snapshot (Scan)
Generates a single, structured XML file containing the project tree and file contents.
* **Use Case (Dev):** Quickly sharing code context for peer review, onboarding new team members, or creating a backup before a risky change.
* **Use Case (LLM):** Providing the full codebase context to an AI for initial analysis.

### 2. Incremental Diff (Diff)
Tracks changes between the last snapshot and the current working tree using an internal anchor.
* **Use Case (Dev):** Checking "What have I changed since I started this specific task?" without relying on Git staging area or commit history.
* **Use Case (LLM):** Sending only the modified parts to the AI to save tokens and maintain focus.

### 3. Smart Filtering
Respects `.gitignore` by default and allows additional exclusion rules via configuration. It automatically handles binary files and reduces noise (e.g., lock files).

## Installation

Requires **Python 3.14+** (for PEP 750 Tag Strings support).

```bash
# Install via uv (Recommended)
git clone https://github.com/SJB7777/codigest.git
cd codigest
uv tool install .
````

## Usage Workflow

### Initialize

Sets up the `.codigest` directory and captures the initial baseline.

```bash
codigest init
```

### Scan (Capture Context)

Scans the codebase and saves the snapshot to `.codigest/snapshot.xml`. This updates the internal anchor.

```bash
codigest scan --message "Refactoring authentication module"
```

### Diff (Check Changes)

Shows what has changed since the last `scan`. This is useful for tracking progress within a specific development session.

```bash
codigest diff
```

### Tree (Visualize)

Prints the directory structure to the console, respecting ignore rules.

```bash
codigest tree
```

## Configuration

You can customize the behavior in `.codigest/config.toml`.

```toml
[project]
description = "My Project Context"

[filter]
# Only scan these extensions
extensions = [".py", ".ts", ".rs", ".md", ".json"]

# Additional ignore patterns (on top of .gitignore)
exclude_patterns = [
    "*.lock",
    "tests/data/",
    "legacy_code/"
]

[output]
format = "xml"
```

## Technical Details

Codigest uses a mechanism called **Context Anchoring**.
When you run `scan`, it creates a lightweight copy of the tracked files in `.codigest/anchor`. When you run `diff`, it compares your current working directory against this anchor.

This allows you to verify changes relative to your "logical session" rather than your Git commit history, keeping your main repository clean while allowing granular tracking for debugging or assistance.

## License

MIT License