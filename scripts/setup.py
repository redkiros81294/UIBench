"""
UIBench setup script.

Interactive setup that lets users choose their deployment mode:
  - fullstack: frontend + backend + core
  - cli: core + CLI only
  - core: core engine only

The script will prune unused components and install dependencies.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    import click
except ImportError:
    print("Error: click is required for setup. Install with: pip install click")
    sys.exit(1)

# Components that can be removed
OPTIONAL_COMPONENTS = {
    "frontend": {
        "paths": [ROOT / "frontend"],
        "description": "SvelteKit frontend (web UI)",
        "required_for": ["fullstack"],
    },
    "backend": {
        "paths": [ROOT / "backend"],
        "description": "FastAPI backend service",
        "required_for": ["fullstack"],
    },
    "docker": {
        "paths": [ROOT / "docker", ROOT / "docker-compose.yml"],
        "description": "Docker Compose deployment files",
        "required_for": ["fullstack"],
    },
    "tests": {
        "paths": [ROOT / "tests"],
        "description": "Project-level integration tests",
        "required_for": ["fullstack"],
    },
    "docs": {
        "paths": [
            ROOT / "ARCHITECTURE.md",
            ROOT / "CONTRIBUTING.md",
            ROOT / "CHANGELOG.md",
            ROOT / "PDF_PLAN.md",
        ],
        "description": "Project documentation markdown files",
        "required_for": ["fullstack"],
    },
    "github": {
        "paths": [ROOT / ".github"],
        "description": "GitHub Actions CI/CD workflows",
        "required_for": ["fullstack"],
    },
    "vscode": {
        "paths": [ROOT / ".vscode"],
        "description": "VSCode workspace settings",
        "required_for": [],
    },
}

# Dependencies for each mode
DEPENDENCIES = {
    "fullstack": [
        "requirements.txt",
        "cli",
    ],
    "cli": [
        "requirements.txt",
        "cli",
    ],
    "core": [
        "requirements.txt",
    ],
}


def print_header(text: str) -> None:
    click.echo(click.style(f"\n{text}", fg="cyan", bold=True))


def print_success(text: str) -> None:
    click.echo(click.style(f"✓ {text}", fg="green"))


def print_warning(text: str) -> None:
    click.echo(click.style(f"⚠ {text}", fg="yellow"))


def print_error(text: str) -> None:
    click.echo(click.style(f"✗ {text}", fg="red", bold=True))


def remove_paths(paths: list[Path]) -> None:
    for path in paths:
        if not path.exists():
            continue
        try:
            if path.is_dir():
                shutil.rmtree(path)
                print_success(f"Removed directory: {path.relative_to(ROOT)}")
            else:
                path.unlink()
                print_success(f"Removed file: {path.relative_to(ROOT)}")
        except Exception as exc:
            print_error(f"Failed to remove {path}: {exc}")


def setup_virtualenv() -> None:
    print_header("Setting up virtual environment...")
    venv_path = ROOT / ".venv"
    if venv_path.exists():
        print_warning("Virtual environment already exists")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print_success("Virtual environment created")
        
        # Determine pip path
        if platform.system() == "Windows":
            pip = venv_path / "Scripts" / "pip.exe"
        else:
            pip = venv_path / "bin" / "pip"
        
        subprocess.run([str(pip), "install", "--upgrade", "pip"], check=True)
        print_success("pip upgraded")
    except Exception as exc:
        print_error(f"Failed to setup virtual environment: {exc}")


def install_dependencies(mode: str) -> None:
    print_header(f"Installing dependencies for '{mode}' mode...")
    
    req_files = DEPENDENCIES.get(mode, ["requirements.txt"])
    
    if platform.system() == "Windows":
        pip = ROOT / ".venv" / "Scripts" / "pip.exe"
    else:
        pip = ROOT / ".venv" / "bin" / "pip"
    
    for req_file in req_files:
        req_path = ROOT / req_file
        if not req_path.exists():
            print_warning(f"Requirements file not found: {req_file}")
            continue
        
        try:
            if req_file == "cli":
                # Install CLI package in editable mode with optional deps
                subprocess.run(
                    [str(pip), "install", "-e", str(ROOT / "cli")],
                    check=True,
                )
                print_success(f"Installed CLI package from {req_file}")
            else:
                subprocess.run(
                    [str(pip), "install", "-r", str(req_path)],
                    check=True,
                )
                print_success(f"Installed dependencies from {req_file}")
        except Exception as exc:
            print_error(f"Failed to install {req_file}: {exc}")


def setup_mode(mode: str) -> None:
    print_header(f"Configuring for mode: {mode}")
    
    # Determine what to keep/remove
    if mode == "fullstack":
        print_success("Keeping all components")
        return
    
    remove_targets = []
    for component, config in OPTIONAL_COMPONENTS.items():
        if mode not in config["required_for"]:
            remove_targets.extend(config["paths"])
    
    if remove_targets:
        print_header("Removing unused components...")
        remove_paths(remove_targets)
    else:
        print_success("No components to remove")


def main() -> None:
    print_header("UIBench Setup")
    click.echo("This script will help you set up UIBench for your needs.\n")
    
    # Check if click is available
    try:
        import click  # noqa: F401
    except ImportError:
        print_error("click is required for setup. Install with: pip install click")
        sys.exit(1)
    
    # Ask for mode
    click.echo("Select deployment mode:")
    click.echo("  1. fullstack - Frontend + Backend + Core (web UI + API + engine)")
    click.echo("  2. cli       - Core + CLI only (lightweight command-line tool)")
    click.echo("  3. core      - Core engine only (library for integration)")
    click.echo()
    
    choice = click.prompt("Enter choice", type=click.IntRange(1, 3), default=2)
    modes = {1: "fullstack", 2: "cli", 3: "core"}
    mode = modes[choice]
    
    # Ask about virtual environment
    click.echo()
    create_venv = click.confirm("Create virtual environment?", default=True)
    
    # Ask about dependency installation
    click.echo()
    install_deps = click.confirm("Install dependencies now?", default=True)
    
    # Execute setup
    setup_mode(mode)
    
    if create_venv:
        setup_virtualenv()
    
    if install_deps:
        install_dependencies(mode)
    
    print_header("Setup complete!")
    print_success(f"Mode: {mode}")
    
    if mode == "cli":
        click.echo("\nNext steps:")
        click.echo("  1. Activate virtual environment:")
        if platform.system() == "Windows":
            click.echo("     .venv\\Scripts\\activate")
        else:
            click.echo("     source .venv/bin/activate")
        click.echo("  2. Run CLI: uibench --help")
        click.echo("  3. Evaluate a URL: uibench evaluate https://example.com")
        click.echo("  4. Batch evaluate: uibench batch urls.txt")
        click.echo("  5. Generate PDF: uibench evaluate https://example.com --output pdf --save report.pdf")
    elif mode == "core":
        click.echo("\nNext steps:")
        click.echo("  1. Activate virtual environment:")
        if platform.system() == "Windows":
            click.echo("     .venv\\Scripts\\activate")
        else:
            click.echo("     source .venv/bin/activate")
        click.echo("  2. Import core in your Python code:")
        click.echo("     from core.engine import RegistryPageEvaluator")
    else:
        click.echo("\nNext steps:")
        click.echo("  1. Configure .env files for frontend and backend")
        click.echo("  2. Start with Docker: docker compose up --build")
        click.echo("  3. Or start services individually:")
        click.echo("     - Backend: cd backend && uvicorn app.main:app --reload")
        click.echo("     - Frontend: cd frontend && pnpm dev")


if __name__ == "__main__":
    main()
