# 🔐 Password Strength Analyzer

> **Cybersecurity Education & Ethical Hacking Training Tool**

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Educational](https://img.shields.io/badge/Purpose-Educational-orange)](README.md)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](README.md)

A **professional, fully-featured** password analysis and custom wordlist generation tool built for cybersecurity students, ethical hackers, digital forensics practitioners, and red-team lab environments.

---

## ⚠️ Disclaimer

This tool is strictly intended for:

- ✅ Cybersecurity learning and research
- ✅ Ethical hacking training
- ✅ Digital forensics practice
- ✅ Red-team lab environments
- ✅ Academic / portfolio projects

**Never use this software to access systems or accounts without explicit written permission. The authors accept no liability for misuse.**

---

## ✨ Features

### 🔍 Password Analyzer
| Feature | Description |
|---|---|
| Score (0–4) | zxcvbn-powered realistic strength rating |
| Entropy | Shannon bit-entropy with character-pool detection |
| Crack Time | Estimated crack time across 4 attack scenarios |
| Character Stats | Uppercase / lowercase / digits / symbols / unicode count |
| Pattern Detection | Keyboard walks, repeated chars, sequential runs, years |
| Leet-speak Detection | Identifies `p4ssw0rd`-style substitutions |
| Personal Info | Flags tokens from user-supplied personal context |
| Actionable Feedback | Specific issues AND concrete recommendations |

### 📋 Wordlist Generator
Generates realistic password candidates from:
- Personal information (name, nickname, birthday, pet, partner, company…)
- Capitalisation variants (lower / UPPER / Title / camelCase / SNAKE_CASE)
- Leet-speak substitutions (a→4, e→3, i→1, o→0, s→5, t→7…)
- Common suffixes (123, @, #, !, 2025, 2026…)
- Token pair combinations
- Popular base words + personal tokens

### 💾 Export
- Export wordlists to `.txt` (one word per line)
- Configurable output folder, filename, and encoding
- Metadata header in exported file
- Word count / file size / generation time summary

### 🖥️ Dual Interface
- **GUI** – Modern dark-theme Tkinter application (4 tabs, live feedback)
- **CLI** – Rich-powered terminal interface with coloured output and JSON export

---

## 🏗️ Architecture

```
Password-Strength-Analyzer/
│
├── main.py          # Entry point (GUI or CLI dispatch)
├── cli.py           # argparse + Rich CLI
├── gui.py           # Tkinter dark-theme GUI (4 tabs)
├── analyzer.py      # Core password analysis engine
├── entropy.py       # Shannon entropy & crack-time calculation
├── generator.py     # Custom wordlist generation engine
├── export.py        # Wordlist export to TXT
├── validators.py    # Input validation helpers
├── utils.py         # Logging, timing, text helpers
├── config.py        # Central configuration & constants
│
├── output/          # Generated wordlist files
├── logs/            # Application logs
├── tests/           # pytest unit tests
│   ├── test_analyzer.py
│   ├── test_entropy.py
│   ├── test_generator.py
│   ├── test_export.py
│   └── test_validators.py
│
├── requirements.txt
├── LICENSE
├── README.md
└── .gitignore
```

---

## 🚀 Installation

### Prerequisites
- Python **3.12+**
- `pip`

### Clone & Install

```bash
git clone https://github.com/your-username/Password-Strength-Analyzer.git
cd Password-Strength-Analyzer
pip install -r requirements.txt
```

> **Windows users:** Tkinter is bundled with the official Python installer.  
> **Linux users:** `sudo apt install python3-tk` if tkinter is missing.

---

## 💻 Usage

### GUI (default)

```bash
python main.py
```

Opens the full dark-theme graphical interface.

### CLI – Password Analysis

```bash
# Interactive (hidden password prompt)
python main.py analyze

# Pass password directly (use in scripts)
python main.py analyze -p "MyP@ssw0rd!"

# Include personal tokens for context-aware analysis
python main.py analyze -p "alice1990" --user-info "alice,1990"

# Save full JSON report
python main.py analyze -p "hunter2" --json-out report.json
```

### CLI – Wordlist Generation

```bash
# Interactive questionnaire
python main.py generate

# Generate and immediately export
python main.py generate --output custom_wordlist

# Specify encoding
python main.py generate --output wordlist --encoding utf-16
```

### CLI – Export

```bash
# Re-export / rename an existing wordlist
python main.py export --input output/wordlist.txt --output renamed_list
```

### Help

```bash
python main.py --help
python main.py analyze --help
python main.py generate --help
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
# With coverage report
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 📊 Example CLI Output

```
╔══════════════════════════════════════════════════════╗
║  Password Strength Analyzer  v1.0.0                 ║
╚══════════════════════════════════════════════════════╝

╭─ Password Rating ──────────────────────────────────╮
│  Very Weak  █░░░░  (score 0/4)                     │
╰────────────────────────────────────────────────────╯

 Property            Value
 ─────────────────── ──────────────────────────────
 Length              8
 Uppercase           0
 Lowercase           8
 Digits              0
 Symbols             0
 Entropy (bits)      37.60
 Crack time (fast)   less than a second

Issues found:
  ❌ Missing uppercase letters
  ❌ Missing numbers
  ❌ Missing symbols
  ❌ Contains a keyboard pattern ('qwerty')

Recommendations:
  ✔ Add at least one uppercase letter (A-Z)
  ✔ Include at least one digit (0-9)
  ✔ Add symbols like ! @ # $ % & *
  ✔ Use a password manager to generate complex passwords
```

---

## ⚙️ Configuration

All tuneable constants are in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `MIN_LENGTH` | 8 | Minimum acceptable password length |
| `RECOMMENDED_LENGTH` | 16 | Recommended length for strong passwords |
| `MAX_WORDLIST_SIZE` | 500,000 | Hard cap on wordlist generation |
| `ENTROPY_FAIR` | 60 bits | Threshold for "fair" entropy rating |
| `ENTROPY_STRONG` | 128 bits | Threshold for "strong" entropy rating |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Write tests for your changes
4. Ensure all tests pass: `pytest tests/`
5. Commit with a clear message: `git commit -m "feat: add amazing feature"`
6. Push and open a Pull Request

Please follow PEP-8 and add type hints to all new functions.

---

## ❓ FAQ

**Q: Does this tool store passwords?**  
A: No. Passwords are analysed in memory and never written to disk.

**Q: Can I use this on a production system to test real user passwords?**  
A: Only with proper authorisation (e.g., security audit with signed permission).

**Q: Why does a "strong-looking" password still score low?**  
A: zxcvbn uses pattern analysis, not just character-class rules. A password like `P@ssw0rd` contains common patterns and scores low despite meeting character requirements.

**Q: The wordlist generator produced fewer words than expected.**  
A: More profile fields = more combinations. Try adding more personal tokens. The generator caps output at 500,000 entries by default (configurable in `config.py`).

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

*Built for education. Use responsibly.*
