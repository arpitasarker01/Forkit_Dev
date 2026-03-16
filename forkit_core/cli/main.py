"""
forkit CLI — register, inspect, search, and trace AI model and agent passports.

Usage:
    forkit --help
    forkit register model config.yaml
    forkit register agent config.yaml
    forkit inspect <id>
    forkit list [--type model|agent] [--status active]
    forkit search <query>
    forkit lineage <id>
    forkit verify <id>
    forkit stats
    forkit registry rebuild-index
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml  # PyYAML

from ..registry import LocalRegistry
from ..schemas import AgentPassport, ModelPassport

app = typer.Typer(
    name="forkit",
    help="forkit-core — AI model and agent passport registry CLI",
    add_completion=True,
    rich_markup_mode="markdown",
)

register_app = typer.Typer(help="Register a model or agent passport.")
app.add_typer(register_app, name="register")

registry_app = typer.Typer(help="Registry maintenance commands.")
app.add_typer(registry_app, name="registry")

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _get_registry(registry_root: str | None) -> LocalRegistry:
    root = registry_root or "~/.forkit/registry"
    return LocalRegistry(root=root)


def _load_config(path: Path) -> dict:
    if not path.exists():
        typer.echo(f"[red]File not found: {path}[/red]", err=True)
        raise typer.Exit(code=1)
    text = path.read_text()
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def _print_json(data) -> None:
    typer.echo(json.dumps(data, indent=2, default=str))


def _short(id: str) -> str:
    return id[:12] + "..." if len(id) > 12 else id


# ------------------------------------------------------------------ #
# register model
# ------------------------------------------------------------------ #

@register_app.command("model")
def register_model(
    config: Path = typer.Argument(..., help="YAML or JSON config file for the ModelPassport"),
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r", help="Registry root path"),
    output_id: bool = typer.Option(False, "--id", help="Print only the registered ID"),
):
    """Register a new **model** passport from a YAML/JSON config file."""
    data = _load_config(config)
    passport = ModelPassport(**data)
    reg = _get_registry(registry_root)
    pid = reg.register_model(passport)

    if output_id:
        typer.echo(pid)
        return

    typer.echo(
        f"✓ Model passport registered\n"
        f"  ID      : {pid}\n"
        f"  Name    : {passport.name} v{passport.version}\n"
        f"  Status  : {passport.status}\n"
        f"  Creator : {passport.creator.name}"
    )


# ------------------------------------------------------------------ #
# register agent
# ------------------------------------------------------------------ #

@register_app.command("agent")
def register_agent(
    config: Path = typer.Argument(..., help="YAML or JSON config file for the AgentPassport"),
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r", help="Registry root path"),
    output_id: bool = typer.Option(False, "--id", help="Print only the registered ID"),
):
    """Register a new **agent** passport from a YAML/JSON config file."""
    data = _load_config(config)
    passport = AgentPassport(**data)
    reg = _get_registry(registry_root)
    pid = reg.register_agent(passport)

    if output_id:
        typer.echo(pid)
        return

    typer.echo(
        f"✓ Agent passport registered\n"
        f"  ID       : {pid}\n"
        f"  Name     : {passport.name} v{passport.version}\n"
        f"  Role     : {passport.role}\n"
        f"  Model ID : {_short(passport.model_id)}\n"
        f"  Status   : {passport.status}"
    )


# ------------------------------------------------------------------ #
# inspect
# ------------------------------------------------------------------ #

@app.command()
def inspect(
    passport_id: str = typer.Argument(..., help="Full passport ID (SHA-256 hex)"),
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r"),
    raw: bool = typer.Option(False, "--raw", help="Print raw JSON"),
):
    """Inspect a registered passport by ID."""
    reg = _get_registry(registry_root)
    passport = reg.get(passport_id)
    if passport is None:
        typer.echo(f"[red]Passport not found: {passport_id}[/red]", err=True)
        raise typer.Exit(code=1)

    if raw:
        _print_json(passport.to_dict())
        return

    d = passport.to_dict()
    typer.echo(f"\n{'─'*60}")
    typer.echo(f"  Type    : {d.get('passport_type', 'unknown').upper()}")
    typer.echo(f"  ID      : {d['id']}")
    typer.echo(f"  Name    : {d['name']} v{d['version']}")
    typer.echo(f"  Status  : {d['status']}")
    typer.echo(f"  Creator : {d.get('creator', {}).get('name')} / {d.get('creator', {}).get('organization')}")
    typer.echo(f"  Tags    : {', '.join(d.get('tags', [])) or '—'}")
    typer.echo(f"  Created : {d.get('created_at', '—')}")
    if d.get("passport_type") == "agent":
        typer.echo(f"  Model   : {_short(d.get('model_id', '—'))}")
        typer.echo(f"  Tools   : {len(d.get('tools', []))}")
    elif d.get("passport_type") == "model":
        typer.echo(f"  Arch    : {d.get('architecture', '—')}")
        typer.echo(f"  Params  : {d.get('parameter_count', '—')}")
        typer.echo(f"  License : {d.get('license', '—')}")
    typer.echo(f"{'─'*60}\n")


# ------------------------------------------------------------------ #
# list
# ------------------------------------------------------------------ #

@app.command("list")
def list_passports(
    passport_type: Optional[str] = typer.Option(None, "--type", "-t", help="model | agent"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="draft | active | deprecated | revoked"),
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List registered passports."""
    reg = _get_registry(registry_root)
    results = reg.list(passport_type=passport_type, status=status)

    if json_output:
        _print_json(results)
        return

    if not results:
        typer.echo("No passports found.")
        return

    header = f"{'TYPE':<8} {'ID':<14} {'NAME':<30} {'VERSION':<10} {'STATUS'}"
    typer.echo(f"\n{header}")
    typer.echo("─" * 80)
    for r in results:
        typer.echo(
            f"{r['passport_type']:<8} "
            f"{r['id'][:12]+'...':<14} "
            f"{r['name'][:28]:<30} "
            f"{r['version']:<10} "
            f"{r['status']}"
        )
    typer.echo(f"\n{len(results)} passport(s) found.\n")


# ------------------------------------------------------------------ #
# search
# ------------------------------------------------------------------ #

@app.command()
def search(
    query: str = typer.Argument(..., help="Search term (name, creator, org)"),
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Search passports by name or creator."""
    reg = _get_registry(registry_root)
    results = reg.search(query)

    if json_output:
        _print_json(results)
        return

    if not results:
        typer.echo(f"No passports matching '{query}'.")
        return

    for r in results:
        typer.echo(f"  [{r['passport_type']}] {r['name']} v{r['version']} — {r['id'][:12]}...")


# ------------------------------------------------------------------ #
# lineage
# ------------------------------------------------------------------ #

@app.command()
def lineage(
    passport_id: str = typer.Argument(..., help="Passport ID to trace"),
    direction: str = typer.Option("both", "--direction", "-d", help="ancestors | descendants | both"),
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Trace lineage ancestors and/or descendants of a passport."""
    reg = _get_registry(registry_root)
    graph = reg.lineage

    if passport_id not in graph._nodes:
        typer.echo(f"[red]Node not found in lineage graph: {passport_id}[/red]", err=True)
        raise typer.Exit(code=1)

    node = graph.get_node(passport_id)
    ancestors = graph.ancestors(passport_id) if direction in ("ancestors", "both") else []
    descendants = graph.descendants(passport_id) if direction in ("descendants", "both") else []

    if json_output:
        _print_json({
            "node": node.to_dict(),
            "ancestors": [n.to_dict() for n in ancestors],
            "descendants": [n.to_dict() for n in descendants],
        })
        return

    typer.echo(f"\n◉ {node.name} v{node.version} [{node.node_type}]")
    typer.echo(f"  ID: {node.id}")

    if ancestors:
        typer.echo(f"\n  ↑ Ancestors ({len(ancestors)})")
        for a in ancestors:
            typer.echo(f"    [{a.node_type}] {a.name} v{a.version} — {a.id[:12]}...")

    if descendants:
        typer.echo(f"\n  ↓ Descendants ({len(descendants)})")
        for d in descendants:
            typer.echo(f"    [{d.node_type}] {d.name} v{d.version} — {d.id[:12]}...")

    if not ancestors and not descendants:
        typer.echo("  (no lineage connections)")
    typer.echo()


# ------------------------------------------------------------------ #
# verify
# ------------------------------------------------------------------ #

@app.command()
def verify(
    passport_id: str = typer.Argument(...),
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r"),
):
    """Verify the integrity of a stored passport."""
    reg = _get_registry(registry_root)
    result = reg.verify_passport(passport_id)
    if result["valid"]:
        typer.echo(f"✓ Passport {passport_id[:12]}... is valid.")
    else:
        typer.echo(f"✗ Verification failed: {result['reason']}", err=True)
        raise typer.Exit(code=1)


# ------------------------------------------------------------------ #
# stats
# ------------------------------------------------------------------ #

@app.command()
def stats(
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Show registry statistics."""
    reg = _get_registry(registry_root)
    s = reg.stats()
    if json_output:
        _print_json(s)
        return
    typer.echo(f"\n  Registry : {s['registry_root']}")
    typer.echo(f"  Models   : {s['models']}")
    typer.echo(f"  Agents   : {s['agents']}")
    typer.echo(f"  Total    : {s['total']}")
    typer.echo(f"  Lineage  : {s['lineage_nodes']} nodes, {s['lineage_edges']} edges\n")


# ------------------------------------------------------------------ #
# registry maintenance
# ------------------------------------------------------------------ #

@registry_app.command("rebuild-index")
def rebuild_index(
    registry_root: Optional[str] = typer.Option(None, "--registry", "-r"),
):
    """Rebuild the SQLite index from JSON passport files."""
    reg = _get_registry(registry_root)
    count = reg.rebuild_index()
    typer.echo(f"✓ Index rebuilt. {count} passport(s) indexed.")


def main():
    app()


if __name__ == "__main__":
    main()
