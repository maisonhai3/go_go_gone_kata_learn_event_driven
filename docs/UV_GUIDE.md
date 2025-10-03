# UV Package Manager Guide

## 🚀 What is uv?

[uv](https://docs.astral.sh/uv/) is a blazingly fast Python package and project manager written in Rust. It's **10-100x faster** than pip and provides an all-in-one solution for managing Python projects.

### Why uv?

- ⚡ **Extremely Fast** - 10-100x faster than pip
- 🔒 **Reproducible** - Uses lockfiles for exact dependency resolution
- 🎯 **All-in-One** - Replaces pip, pip-tools, pipx, poetry, pyenv, virtualenv
- 🐍 **Python Version Management** - Install and manage multiple Python versions
- 📦 **Virtual Environment Automation** - Automatically creates and manages venvs
- 🔄 **Cross-Platform** - Consistent behavior across all platforms

## 📦 Installation

### Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Using pipx
```bash
pipx install uv
```

### Verify Installation
```bash
uv --version
```

## 🏗️ Project Setup

This project is already configured with uv! Here's what's included:

### Core Files

1. **`pyproject.toml`** - Project configuration
   - Project metadata (name, version, description)
   - Dependencies list
   - Build system configuration
   - Package structure definition

2. **`uv.lock`** - Lockfile for reproducibility
   - Exact versions of all dependencies (direct + transitive)
   - Cross-platform compatibility
   - Ensures identical environments everywhere

3. **`.python-version`** - Python version specification
   - Tells uv which Python version to use
   - Auto-selected when creating virtual environments

## 🎯 Common Commands

### Setup & Installation

```bash
# Install/sync all dependencies (creates .venv if needed)
uv sync

# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Upgrade a dependency
uv add --upgrade <package-name>

# Upgrade all dependencies
uv sync --upgrade
```

### Running Code

```bash
# Run a Python script in the virtual environment
uv run python run_redis.py

# Run a Python module
uv run python -m src.main_redis

# Run any command in the virtual environment
uv run <command>
```

### Virtual Environment Management

```bash
# Create a virtual environment (automatically done by uv sync)
uv venv

# Activate the virtual environment (if you want manual control)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# List installed packages
uv pip list

# Show package info
uv pip show <package-name>
```

### Locking & Syncing

```bash
# Update the lockfile without installing
uv lock

# Sync from lockfile (install exact versions)
uv sync

# Sync including dev dependencies
uv sync --all-extras

# Sync without dev dependencies
uv sync --no-dev
```

### Python Version Management

```bash
# List available Python versions
uv python list

# Install a specific Python version
uv python install 3.12

# Use a specific Python version for this project
echo "3.12" > .python-version
```

## 🔄 Migration from pip

If you're migrating from pip:

### Import from requirements.txt
```bash
uv add -r requirements.txt
```

### Export to requirements.txt (for backward compatibility)
```bash
uv pip freeze > requirements.txt
```

## 📚 Project-Specific Commands

For this event-driven architecture project:

### Setup
```bash
# 1. Start Redis
docker-compose up -d

# 2. Install dependencies with uv
uv sync
```

### Run Applications
```bash
# Run Redis-based implementation
uv run python run_redis.py

# Run in-memory implementation
uv run python run_inmemory.py

# Run persistence demo
uv run python run_demo_persistence.py

# Run replay demo
uv run python run_demo_replay.py
```

### Development Workflow
```bash
# Add a new dependency
uv add <package-name>

# After adding/removing dependencies, sync
uv sync

# Run your code
uv run python <script.py>
```

## 🎨 Benefits for This Project

### Before (pip + requirements.txt)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_redis.py
```

### After (uv)
```bash
uv sync                    # One command for everything!
uv run python run_redis.py # Automatically uses correct env
```

### Advantages:
1. **No manual venv management** - uv creates and manages `.venv` automatically
2. **Reproducible builds** - `uv.lock` ensures exact versions across all machines
3. **Faster installation** - Redis package installs in milliseconds, not seconds
4. **Better dependency resolution** - Handles conflicts automatically
5. **Cross-platform consistency** - Same behavior on Windows, macOS, Linux

## 🔐 Lockfile (`uv.lock`)

The `uv.lock` file:
- ✅ **Should be committed** to version control
- ✅ Ensures reproducible installations
- ✅ Contains exact versions of all dependencies (direct + transitive)
- ❌ **Should NOT be edited manually** - always use `uv` commands

### How it Works:
1. You run `uv add redis` → pyproject.toml gets `redis>=5.0.1`
2. uv resolves → uv.lock gets exact version `redis==6.4.0` (plus all transitive deps)
3. Others run `uv sync` → They get the exact same `redis==6.4.0`

## 📊 Comparison: uv vs pip vs poetry

| Feature | uv | pip | poetry |
|---------|-----|-----|--------|
| **Speed** | ⚡⚡⚡ 10-100x faster | 🐌 baseline | 🏃 faster than pip |
| **Lockfile** | ✅ uv.lock | ❌ | ✅ poetry.lock |
| **Virtual Env** | ✅ Automatic | ❌ Manual | ✅ Automatic |
| **Python Version Mgmt** | ✅ Built-in | ❌ | ❌ |
| **Cross-Platform** | ✅ Rust binary | ⚠️ Python-based | ⚠️ Python-based |
| **Build & Publish** | ✅ | ❌ | ✅ |
| **Learning Curve** | 🟢 Easy | 🟢 Easy | 🟡 Moderate |

## 🐛 Troubleshooting

### Virtual environment not found
```bash
# Recreate virtual environment
rm -rf .venv
uv sync
```

### Dependency conflicts
```bash
# See dependency tree
uv pip tree

# Force update lockfile
uv lock --upgrade
uv sync
```

### Wrong Python version
```bash
# Check current version
python --version

# Set desired version
echo "3.12" > .python-version

# Recreate venv with new version
rm -rf .venv
uv sync
```

### Cache issues
```bash
# Clear uv cache
uv cache clean
```

## 📖 Additional Resources

- [Official uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub Repository](https://github.com/astral-sh/uv)
- [Real Python: Managing Python Projects With uv](https://realpython.com/python-uv/)
- [uv vs pip Comparison](https://realpython.com/uv-vs-pip/)

## 🎯 Quick Reference Card

```bash
# Setup
uv sync                      # Install all dependencies

# Dependencies
uv add <pkg>                 # Add dependency
uv add --dev <pkg>          # Add dev dependency
uv remove <pkg>              # Remove dependency
uv add --upgrade <pkg>       # Upgrade dependency

# Running
uv run python <script.py>    # Run Python script
uv run <command>             # Run any command

# Environment
uv venv                      # Create venv
uv pip list                  # List packages
uv pip freeze                # Show versions

# Maintenance
uv lock                      # Update lockfile
uv sync --upgrade            # Upgrade all packages
uv cache clean               # Clear cache
```

---

**💡 Pro Tip**: Once you sync with `uv sync`, you can also activate the venv traditionally with `source .venv/bin/activate` if you prefer, but `uv run` is more convenient!
