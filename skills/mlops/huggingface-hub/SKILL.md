---
name: huggingface-hub
description: "HuggingFace hf CLI: search/download/upload models, datasets."
version: 1.0.0
author: Hugging Face
license: MIT
tags: [huggingface, hf, models, datasets, hub, mlops]
platforms: [linux, macos, windows]
---

# Hugging Face CLI (`hf`) Reference Guide

The `hf` command is the modern command-line interface for interacting with the Hugging Face Hub, providing tools to manage repositories, models, datasets, and Spaces.

> **IMPORTANT:** The `hf` command replaces the now deprecated `huggingface-cli` command.

## Quick Start
*   **Installation:** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **Help:** Use `hf --help` to view all available functions and real-world examples.
*   **Authentication:** Recommended via `HF_TOKEN` environment variable or the `--token` flag.

---

## Core Commands

### General Operations
*   `hf download REPO_ID [FILENAME]`: Download files from the Hub.
    * `hf download unsloth/Qwen3-14B-128K-GGUF Qwen3-14B-128K-Q4_K_M --local-dir ~/models/my-model`
    * Do NOT use `--local-dir-use-symlinks=false` — this flag does not exist in `hf download`. Use `--local-dir <path>` only.
    * Omit filename to download the entire repo.
*   `hf upload REPO_ID`: Upload files/folders (recommended for single-commit).
*   `hf upload-large-folder REPO_ID LOCAL_PATH`: Recommended for resumable uploads of large directories.
*   **Sync:** `hf sync`: Sync files between a local directory and a bucket.
    * `hf sync hf://buckets/NAME/path ./local_dir` (download)
    * `hf sync ./local_dir hf://buckets/NAME/path` (upload)
*   `hf env` / `hf version`: View environment and version details.

### Authentication (`hf auth`)
*   `login` / `logout`: Manage sessions using tokens from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
*   `list` / `switch`: Manage and toggle between multiple stored access tokens.
*   `whoami`: Identify the currently logged-in account.

### Repository Management (`hf repos`)
*   `create` / `delete`: Create or permanently remove repositories.
*   `duplicate`: Clone a model, dataset, or Space to a new ID.
*   `move`: Transfer a repository between namespaces.
*   `branch` / `tag`: Manage Git-like references.
*   `delete-files`: Remove specific files using patterns.

---

## Specialized Hub Interactions

### Datasets & Models
*   **Datasets:** `hf datasets list`, `info`, and `parquet` (list parquet URLs).
*   **SQL Queries:** `hf datasets sql SQL` — Execute raw SQL via DuckDB against dataset parquet URLs.
*   **Models:** `hf models list` and `info`.
*   **Papers:** `hf papers list` — View daily papers.

### Discussions & Pull Requests (`hf discussions`)
*   Manage the lifecycle of Hub contributions: `list`, `create`, `info`, `comment`, `close`, `reopen`, and `rename`.
*   `diff`: View changes in a PR.
*   `merge`: Finalize pull requests.

### Infrastructure & Compute
*   **Endpoints:** Deploy and manage Inference Endpoints (`deploy`, `pause`, `resume`, `scale-to-zero`, `catalog`).
*   **Jobs:** Run compute tasks on HF infrastructure. Includes `hf jobs uv` for running Python scripts with inline dependencies and `stats` for resource monitoring.
*   **Spaces:** Manage interactive apps. Includes `dev-mode` and `hot-reload` for Python files without full restarts.

### Storage & Automation
*   **Buckets:** Full S3-like bucket management (`create`, `cp`, `mv`, `rm`, `sync`).
*   **Cache:** Manage local storage with `list`, `prune` (remove detached revisions), and `verify` (checksum checks).
*   **Webhooks:** Automate workflows by managing Hub webhooks (`create`, `watch`, `enable`/`disable`).
*   **Collections:** Organize Hub items into collections (`add-item`, `update`, `list`).

---

## Advanced Usage & Tips

### ⚠️ Two Different `hf` Binaries — CRITICAL

There are **two completely different** `hf` CLI tools:

| Tool | Install | Has `sync`? | Has `download`? |
|------|---------|-------------|-----------------|
| `hf` (Rust-based) | `pipx install hf` or `curl -LsSf https://hf.co/cli/install.sh \| bash` | ✅ Yes | ✅ Yes |
| `huggingface_hub` CLI | `pip install huggingface_hub` | ❌ No | ✅ Yes |

**The pip `huggingface_hub` package provides `~/.local/bin/hf` which LACKS `sync`, `upload-large-folder`, and bucket commands.** If `hf sync` gives "unrecognized arguments", you have the wrong binary.

**Fix:** Install via pipx: `pipx install hf` — the binary is at `~/.local/share/pipx/venvs/hf/bin/hf`. Ensure this path is first in `$PATH` or call it directly.

**Check which one you have:**
```bash
which hf                    # Shows active binary
hf --help | grep sync       # If missing, wrong binary
pip show hf                 # If installed via pip, that's the wrong one
pipx list | grep hf         # Should show hf if pipx-installed
```

### Global Flags
*   `--format json`: Produces machine-readable output for automation.
*   `-q` / `--quiet`: Limits output to IDs only.

### Extensions & Skills
*   **Extensions:** Extend CLI functionality via GitHub repositories using `hf extensions install REPO_ID`.
*   **Skills:** Manage AI assistant skills with `hf skills add`.
