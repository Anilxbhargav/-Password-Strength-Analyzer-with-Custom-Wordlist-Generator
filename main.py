"""
main.py - Entry point for Password Strength Analyzer
======================================================
Dispatches to GUI (default) or CLI based on command-line arguments.

Usage:
    python main.py               # Launch GUI
    python main.py analyze       # CLI: analyze a password
    python main.py generate      # CLI: generate a wordlist
    python main.py export        # CLI: export a wordlist
    python main.py --help        # Show help
"""

import sys

# ─── Disclaimer printed at startup ────────────────────────────────────────────
DISCLAIMER = """
╔══════════════════════════════════════════════════════════════╗
║           Password Strength Analyzer  v1.0.0                ║
║         Cybersecurity Educational Tool                       ║
╠══════════════════════════════════════════════════════════════╣
║  ⚠  FOR EDUCATIONAL & AUTHORISED USE ONLY                   ║
║                                                              ║
║  This tool is designed for:                                  ║
║    • Cybersecurity learning & research                       ║
║    • Ethical hacking training                                ║
║    • Digital forensics practice                              ║
║    • Red-team lab environments                               ║
║    • Academic / portfolio projects                           ║
║                                                              ║
║  Never use this software to access systems without          ║
║  explicit written permission.                                ║
╚══════════════════════════════════════════════════════════════╝
"""

CLI_COMMANDS = {"analyze", "generate", "export"}


def main() -> None:
    # Detect whether the user wants the CLI or the GUI
    args = sys.argv[1:]

    # Any recognised CLI subcommand (or --help / --version) → CLI mode
    if args and (args[0] in CLI_COMMANDS or args[0].startswith("-")):
        print(DISCLAIMER)
        from cli import run_cli
        run_cli()
    else:
        # No subcommand → launch GUI
        print(DISCLAIMER)
        try:
            from gui import run_gui
            run_gui()
        except ImportError as exc:
            print(f"[ERROR] Could not launch GUI: {exc}")
            print("Tip: install tkinter (usually included with Python on most platforms).")
            sys.exit(1)


if __name__ == "__main__":
    main()
