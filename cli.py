"""
cli.py - Rich CLI interface
=============================
Provides subcommands: analyze, generate, export.
Run via:  python main.py analyze | generate | export | --help
"""

import argparse
import getpass
import json
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn,
)
from rich.table import Table
from rich.text import Text

from analyzer import analyze
from config import APP_NAME, APP_VERSION, SCORE_COLORS_GUI, OUTPUT_DIR
from export import export_wordlist
from generator import UserProfile, generate_wordlist
from validators import validate_password, validate_profile

console = Console()

BANNER = f"""
[bold cyan]╔══════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]  [bold white]{APP_NAME}[/bold white]  [dim]v{APP_VERSION}[/dim]  [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [dim]Cybersecurity Education & Ethical Hacking Training[/dim]  [bold cyan]║[/bold cyan]
[bold cyan]╚══════════════════════════════════════════════════════╝[/bold cyan]
"""

# Colour mapping for zxcvbn score
_RICH_SCORE_COLORS = {
    0: "bold red",
    1: "red",
    2: "yellow",
    3: "green",
    4: "bold green",
}


# ─── Analyze sub-command ──────────────────────────────────────────────────────

def cmd_analyze(args: argparse.Namespace) -> None:
    """Interactive or flag-based password analysis."""
    console.print(BANNER)

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("  Enter password to analyze (hidden): ")

    ok, err = validate_password(password)
    if not ok:
        console.print(f"[red]Error:[/red] {err}")
        sys.exit(1)

    user_info: list[str] = []
    if args.user_info:
        user_info = [t.strip() for t in args.user_info.split(",") if t.strip()]

    with console.status("[cyan]Analyzing password…[/cyan]"):
        result = analyze(password, user_info)

    # ── Score panel ──────────────────────────────────────────────────────────
    color = _RICH_SCORE_COLORS[result.score]
    score_bar = "█" * (result.score + 1) + "░" * (4 - result.score)
    console.print(Panel(
        f"[{color}]{result.label}[/{color}]  [{color}]{score_bar}[/{color}]  "
        f"[dim](score {result.score}/4)[/dim]",
        title="[bold]Password Rating[/bold]",
        border_style="cyan",
    ))

    # ── Stats table ──────────────────────────────────────────────────────────
    t = Table(title="Password Statistics", box=box.ROUNDED, border_style="cyan", show_header=True)
    t.add_column("Property",   style="bold white",  no_wrap=True)
    t.add_column("Value",      style="cyan")

    s = result.stats
    t.add_row("Length",          str(s.length))
    t.add_row("Uppercase",       str(s.uppercase))
    t.add_row("Lowercase",       str(s.lowercase))
    t.add_row("Digits",          str(s.digits))
    t.add_row("Symbols",         str(s.symbols))
    t.add_row("Unicode chars",   str(s.unicode_ch))
    t.add_row("Entropy (bits)",  f"{result.entropy.bits:.2f}")
    t.add_row("Charset size",    str(result.entropy.charset_size))
    t.add_row("Crack time (fast GPU)", result.crack_time_display)
    console.print(t)

    # ── Crack times ──────────────────────────────────────────────────────────
    ct = Table(title="Estimated Crack Times", box=box.SIMPLE, border_style="dim")
    ct.add_column("Scenario",  style="white")
    ct.add_column("Time",      style="yellow")
    for scenario, timestr in result.entropy.crack_times.items():
        ct.add_row(scenario, timestr)
    console.print(ct)

    # ── Patterns ─────────────────────────────────────────────────────────────
    if result.patterns_found:
        pf = Table(title="Detected Patterns", box=box.SIMPLE, border_style="yellow")
        pf.add_column("Pattern", style="yellow")
        for p in result.patterns_found:
            pf.add_row(p)
        console.print(pf)

    # ── Issues ───────────────────────────────────────────────────────────────
    if result.issues:
        console.print("\n[bold red]Issues found:[/bold red]")
        for issue in result.issues:
            console.print(f"  {issue}")

    # ── Suggestions ──────────────────────────────────────────────────────────
    if result.suggestions:
        console.print("\n[bold green]Recommendations:[/bold green]")
        for sug in result.suggestions:
            console.print(f"  {sug}")

    # ── JSON output ──────────────────────────────────────────────────────────
    if args.json_out:
        data = {
            "score":       result.score,
            "label":       result.label,
            "entropy":     result.entropy.bits,
            "crack_time":  result.crack_time_display,
            "issues":      result.issues,
            "suggestions": result.suggestions,
            "patterns":    result.patterns_found,
            "stats": {
                "length":    result.stats.length,
                "uppercase": result.stats.uppercase,
                "lowercase": result.stats.lowercase,
                "digits":    result.stats.digits,
                "symbols":   result.stats.symbols,
            },
        }
        out_path = Path(args.json_out)
        out_path.write_text(json.dumps(data, indent=2))
        console.print(f"\n[dim]JSON saved to:[/dim] {out_path}")


# ─── Generate sub-command ─────────────────────────────────────────────────────

def cmd_generate(args: argparse.Namespace) -> None:
    """Interactive wordlist generation from profile questions."""
    console.print(BANNER)
    console.print("[bold cyan]Wordlist Generator[/bold cyan] – answer the prompts (press Enter to skip):\n")

    def ask(prompt: str) -> str:
        return console.input(f"  [dim]{prompt}:[/dim] ").strip()

    profile = UserProfile(
        first_name      = ask("First name"),
        last_name       = ask("Last name"),
        nickname        = ask("Nickname"),
        username        = ask("Username"),
        birthday        = ask("Birthday (DD/MM/YYYY)"),
        birth_year      = ask("Birth year (YYYY)"),
        pet_name        = ask("Pet name"),
        partner_name    = ask("Partner name"),
        parents_names   = ask("Parents names (comma-separated)"),
        company         = ask("Company / employer"),
        school          = ask("School"),
        college         = ask("College / university"),
        phone_prefix    = ask("Phone prefix (first 4-6 digits)"),
        favourite_team  = ask("Favourite sports team"),
        favourite_movie = ask("Favourite movie"),
        favourite_game  = ask("Favourite video game"),
        vehicle         = ask("Vehicle (brand/model)"),
        city            = ask("City"),
        state           = ask("State / province"),
        country         = ask("Country"),
    )

    kw_str = ask("Custom keywords (comma-separated)")
    profile.custom_keywords = [k.strip() for k in kw_str.split(",") if k.strip()]

    errors = validate_profile(profile.__dict__)
    if errors:
        console.print("\n[red]Validation errors:[/red]")
        for e in errors:
            console.print(f"  ❌ {e}")
        sys.exit(1)

    tokens = profile.base_tokens()
    if not tokens:
        console.print("[red]No usable information provided. Please enter at least one field.[/red]")
        sys.exit(1)

    console.print(f"\n[dim]Extracted {len(tokens)} base tokens.[/dim]")

    # Generate with progress bar
    wordlist: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Generating…"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as prog:
        task = prog.add_task("generating", total=100)

        def cb(current: int, total: int) -> None:
            pct = int(min(current / max(total, 1) * 100, 100))
            prog.update(task, completed=pct)

        wordlist = generate_wordlist(profile, progress_cb=cb)
        prog.update(task, completed=100)

    console.print(f"\n[green]✔ Generated {len(wordlist):,} unique passwords.[/green]")

    # Store for possible export
    args._wordlist = wordlist
    args._profile  = profile

    # Optionally export immediately
    if args.output:
        _do_export(wordlist, args.output, args.encoding)
    else:
        save = console.input("\n[cyan]Export to file now? (y/N):[/cyan] ").strip().lower()
        if save in ("y", "yes"):
            fname = console.input("  Filename (no extension): ").strip() or "wordlist"
            _do_export(wordlist, fname, args.encoding)


# ─── Export helper ────────────────────────────────────────────────────────────

def _do_export(wordlist: list[str], filename: str, encoding: str = "utf-8") -> None:
    from export import export_wordlist as _ew
    try:
        res = _ew(wordlist, filename=filename, encoding=encoding)
        console.print(
            f"\n[green]✔ Exported:[/green] {res.path}\n"
            f"   Words: {res.word_count:,}  |  Size: {res.file_size_human}"
            f"  |  Time: {res.elapsed_seconds:.3f}s"
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Export failed:[/red] {exc}")
        sys.exit(1)


def cmd_export(args: argparse.Namespace) -> None:
    """Export a previously saved wordlist or re-generate and export."""
    console.print(BANNER)
    if args.input:
        src = Path(args.input)
        if not src.exists():
            console.print(f"[red]File not found:[/red] {src}")
            sys.exit(1)
        words = src.read_text(encoding="utf-8", errors="replace").splitlines()
        words = [w for w in words if w and not w.startswith("#")]
        console.print(f"[dim]Loaded {len(words):,} words from {src}[/dim]")
        _do_export(words, args.output or src.stem + "_exported", args.encoding)
    else:
        console.print("[yellow]No --input specified. Run 'generate' first.[/yellow]")
        sys.exit(1)


# ─── CLI entry point ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description=f"{APP_NAME} v{APP_VERSION} – Cybersecurity Educational Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py analyze
  python main.py analyze -p "MyPassw0rd!" --json-out result.json
  python main.py generate
  python main.py generate --output wordlist --encoding utf-8
  python main.py export --input wordlist.txt --output renamed
        """,
    )
    parser.add_argument("--version", action="version", version=APP_VERSION)

    sub = parser.add_subparsers(dest="command", required=True)

    # ── analyze ──────────────────────────────────────────────────────────────
    p_analyze = sub.add_parser("analyze", help="Analyze a password")
    p_analyze.add_argument("-p", "--password", help="Password to analyze (omit for hidden prompt)")
    p_analyze.add_argument("--user-info", metavar="TOKENS",
                           help="Comma-separated personal tokens for context (e.g. 'John,1990')")
    p_analyze.add_argument("--json-out", metavar="FILE", help="Save JSON report to FILE")
    p_analyze.set_defaults(func=cmd_analyze)

    # ── generate ─────────────────────────────────────────────────────────────
    p_gen = sub.add_parser("generate", help="Generate a custom wordlist")
    p_gen.add_argument("-o", "--output", metavar="FILENAME",
                       help="Output filename (without extension)")
    p_gen.add_argument("--encoding", default="utf-8", metavar="ENC",
                       help="File encoding (default: utf-8)")
    p_gen.set_defaults(func=cmd_generate)

    # ── export ───────────────────────────────────────────────────────────────
    p_exp = sub.add_parser("export", help="Export a wordlist file")
    p_exp.add_argument("-i", "--input", metavar="FILE",
                       help="Existing wordlist .txt to re-export / rename")
    p_exp.add_argument("-o", "--output", metavar="FILENAME",
                       help="Output filename (without extension)")
    p_exp.add_argument("--encoding", default="utf-8", metavar="ENC")
    p_exp.set_defaults(func=cmd_export)

    return parser


def run_cli() -> None:
    parser = build_parser()
    args   = parser.parse_args()
    args.func(args)
