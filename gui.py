"""
gui.py - Modern dark-theme Tkinter GUI
========================================
Four tabs: Password Analyzer | Wordlist Generator | Export | Settings
"""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from config import (
    APP_NAME, APP_VERSION,
    GUI_BG, GUI_FG, GUI_ACCENT, GUI_ENTRY_BG, GUI_ENTRY_FG,
    GUI_BUTTON_BG, GUI_BUTTON_FG, GUI_TAB_BG,
    GUI_FONT, GUI_FONT_BOLD, GUI_FONT_LARGE,
    GUI_WIDTH, GUI_HEIGHT,
    SCORE_COLORS_GUI, OUTPUT_DIR,
)
from utils import get_logger

log = get_logger(__name__)


# ─── Themed widget helpers ────────────────────────────────────────────────────

def _entry(parent: tk.Widget, **kw) -> tk.Entry:
    return tk.Entry(
        parent,
        bg=GUI_ENTRY_BG, fg=GUI_ENTRY_FG,
        insertbackground=GUI_FG,
        relief="flat", bd=4,
        font=GUI_FONT,
        **kw,
    )


def _label(parent: tk.Widget, text: str, **kw) -> tk.Label:
    return tk.Label(
        parent,
        text=text,
        bg=GUI_BG, fg=GUI_FG,
        font=GUI_FONT,
        **kw,
    )


def _button(parent: tk.Widget, text: str, command, **kw) -> tk.Button:
    btn = tk.Button(
        parent,
        text=text,
        bg=GUI_BUTTON_BG, fg=GUI_BUTTON_FG,
        activebackground=GUI_ACCENT,
        activeforeground=GUI_BUTTON_FG,
        relief="flat", bd=0,
        padx=14, pady=6,
        font=GUI_FONT_BOLD,
        cursor="hand2",
        command=command,
        **kw,
    )
    return btn


def _frame(parent: tk.Widget, **kw) -> tk.Frame:
    return tk.Frame(parent, bg=GUI_BG, **kw)


def _scrolled_text(parent: tk.Widget, height: int = 12) -> scrolledtext.ScrolledText:
    return scrolledtext.ScrolledText(
        parent,
        bg=GUI_ENTRY_BG, fg=GUI_FG,
        insertbackground=GUI_FG,
        font=("Consolas", 10),
        relief="flat", bd=4,
        wrap=tk.WORD,
        height=height,
    )


# ─── Password Analyzer Tab ────────────────────────────────────────────────────

class AnalyzerTab(tk.Frame):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master, bg=GUI_BG)
        self._build()

    def _build(self) -> None:
        # ── Input row ─────────────────────────────────────────────────────────
        inp_frame = _frame(self)
        inp_frame.pack(fill="x", padx=20, pady=(20, 6))

        _label(inp_frame, "Password:", font=GUI_FONT_BOLD).pack(side="left")
        self.pw_var = tk.StringVar()
        self.pw_entry = _entry(inp_frame, textvariable=self.pw_var, width=42, show="•")
        self.pw_entry.pack(side="left", padx=(8, 4))
        self.pw_entry.bind("<Return>", lambda _: self._analyze())

        self.show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            inp_frame, text="Show", variable=self.show_var,
            command=self._toggle_show,
            bg=GUI_BG, fg=GUI_FG, selectcolor=GUI_ENTRY_BG,
            activebackground=GUI_BG, font=GUI_FONT,
        ).pack(side="left", padx=4)

        _button(inp_frame, "Analyze", self._analyze).pack(side="left", padx=6)
        _button(inp_frame, "Clear", self._clear, bg="#444466", fg=GUI_FG).pack(side="left")

        # ── User info row ─────────────────────────────────────────────────────
        ui_frame = _frame(self)
        ui_frame.pack(fill="x", padx=20, pady=(0, 8))
        _label(ui_frame, "Personal tokens (comma-sep):").pack(side="left")
        self.ui_var = tk.StringVar()
        _entry(ui_frame, textvariable=self.ui_var, width=40).pack(side="left", padx=(8, 0))

        # ── Strength meter ────────────────────────────────────────────────────
        meter_frame = _frame(self)
        meter_frame.pack(fill="x", padx=20, pady=4)
        self.score_label = tk.Label(
            meter_frame, text="Strength:  —",
            bg=GUI_BG, fg=GUI_FG, font=GUI_FONT_LARGE,
        )
        self.score_label.pack(side="left")

        self.meter_bar = ttk.Progressbar(meter_frame, length=260, maximum=4, mode="determinate")
        self.meter_bar.pack(side="left", padx=16)

        # ── Live entropy label ────────────────────────────────────────────────
        self.entropy_label = _label(self, "Entropy: —  |  Length: 0  |  Charset: —")
        self.entropy_label.pack(anchor="w", padx=20)

        # ── Crack time ────────────────────────────────────────────────────────
        self.crack_label = _label(self, "Crack time (fast GPU): —")
        self.crack_label.pack(anchor="w", padx=20, pady=(0, 6))

        # ── Separator ────────────────────────────────────────────────────────
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=4)

        # ── Stats + Results pane ──────────────────────────────────────────────
        pane = _frame(self)
        pane.pack(fill="both", expand=True, padx=20, pady=6)

        # Left: stats grid
        stats_frame = _frame(pane)
        stats_frame.pack(side="left", fill="y", padx=(0, 16))
        _label(stats_frame, "Character Statistics", font=GUI_FONT_BOLD).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self._stat_vars: dict[str, tk.StringVar] = {}
        stat_rows = [
            ("Length", "length"), ("Uppercase", "uppercase"),
            ("Lowercase", "lowercase"), ("Digits", "digits"),
            ("Symbols", "symbols"), ("Unicode", "unicode_ch"),
        ]
        for i, (lbl, key) in enumerate(stat_rows, start=1):
            _label(stats_frame, f"{lbl}:").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="—")
            self._stat_vars[key] = var
            _label(stats_frame, "").configure()
            tk.Label(
                stats_frame, textvariable=var,
                bg=GUI_BG, fg=GUI_ACCENT, font=GUI_FONT_BOLD,
            ).grid(row=i, column=1, sticky="e", padx=8)

        # Right: issues + suggestions
        right = _frame(pane)
        right.pack(side="left", fill="both", expand=True)

        _label(right, "Issues & Recommendations:", font=GUI_FONT_BOLD).pack(anchor="w")
        self.result_text = _scrolled_text(right, height=16)
        self.result_text.pack(fill="both", expand=True, pady=4)

        # Pattern row
        self.pattern_label = _label(self, "Patterns detected: —")
        self.pattern_label.pack(anchor="w", padx=20, pady=(4, 12))

        # ── Status bar ────────────────────────────────────────────────────────
        self.status = _label(self, "Ready.", fg="#888888")
        self.status.pack(anchor="w", padx=20)

        # Live typing feedback
        self.pw_var.trace_add("write", self._on_type)

    # ── Internal methods ──────────────────────────────────────────────────────

    def _toggle_show(self) -> None:
        self.pw_entry.config(show="" if self.show_var.get() else "•")

    def _on_type(self, *_) -> None:
        """Provide instant feedback as the user types."""
        pw = self.pw_var.get()
        if not pw:
            self._reset_display()
            return
        # Quick sync check (lightweight)
        from entropy import calculate_entropy
        ent = calculate_entropy(pw)
        self.entropy_label.config(
            text=f"Entropy: {ent.bits:.1f} bits  |  Length: {len(pw)}  |  Charset: {ent.charset_size}"
        )

    def _analyze(self) -> None:
        pw = self.pw_var.get()
        if not pw:
            messagebox.showwarning("Input Required", "Please enter a password to analyze.")
            return
        user_tokens = [t.strip() for t in self.ui_var.get().split(",") if t.strip()]
        self.status.config(text="Analyzing…")
        self.update()

        def _run() -> None:
            from analyzer import analyze
            result = analyze(pw, user_tokens)
            self.after(0, lambda: self._display_result(result))

        threading.Thread(target=_run, daemon=True).start()

    def _display_result(self, result) -> None:
        from config import SCORE_COLORS_GUI
        color = SCORE_COLORS_GUI[result.score]

        self.score_label.config(
            text=f"Strength:  {result.label}",
            fg=color,
        )
        self.meter_bar["value"] = result.score + 1

        s = result.stats
        for key, var in self._stat_vars.items():
            var.set(str(getattr(s, key, "—")))

        self.entropy_label.config(
            text=(
                f"Entropy: {result.entropy.bits:.2f} bits  |  "
                f"Length: {s.length}  |  Charset: {result.entropy.charset_size}"
            )
        )
        self.crack_label.config(text=f"Crack time (fast GPU): {result.crack_time_display}")

        # Issues + suggestions
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")

        if result.issues:
            self.result_text.insert("end", "── Issues ──────────────────────\n", "heading")
            for issue in result.issues:
                self.result_text.insert("end", f"  {issue}\n")
            self.result_text.insert("end", "\n")

        if result.suggestions:
            self.result_text.insert("end", "── Recommendations ──────────────\n", "heading")
            for sug in result.suggestions:
                self.result_text.insert("end", f"  {sug}\n")

        self.result_text.tag_configure("heading", foreground=GUI_ACCENT, font=GUI_FONT_BOLD)
        self.result_text.config(state="disabled")

        # Patterns
        if result.patterns_found:
            self.pattern_label.config(
                text="Patterns: " + "  •  ".join(result.patterns_found),
                fg="#e67e22",
            )
        else:
            self.pattern_label.config(text="Patterns detected: none ✓", fg="#2ecc71")

        self.status.config(text=f"Analysis complete – {result.label}")

    def _clear(self) -> None:
        self.pw_var.set("")
        self.ui_var.set("")
        self._reset_display()

    def _reset_display(self) -> None:
        self.score_label.config(text="Strength:  —", fg=GUI_FG)
        self.meter_bar["value"] = 0
        self.entropy_label.config(text="Entropy: —  |  Length: 0  |  Charset: —")
        self.crack_label.config(text="Crack time (fast GPU): —")
        self.pattern_label.config(text="Patterns detected: —", fg=GUI_FG)
        for var in self._stat_vars.values():
            var.set("—")
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")
        self.status.config(text="Ready.")


# ─── Wordlist Generator Tab ───────────────────────────────────────────────────

class GeneratorTab(tk.Frame):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master, bg=GUI_BG)
        self._wordlist: list[str] = []
        self._build()

    # noinspection DuplicatedCode
    def _build(self) -> None:
        # Scrollable canvas for the form
        canvas = tk.Canvas(self, bg=GUI_BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = _frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # Mouse wheel
        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_wheel)

        # ── Title ─────────────────────────────────────────────────────────────
        _label(inner, "Custom Wordlist Generator", font=GUI_FONT_LARGE).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(16, 10))

        # ── Form fields ───────────────────────────────────────────────────────
        fields = [
            ("First Name",       "first_name"),
            ("Last Name",        "last_name"),
            ("Nickname",         "nickname"),
            ("Username",         "username"),
            ("Birthday (DD/MM/YYYY)", "birthday"),
            ("Birth Year",       "birth_year"),
            ("Pet Name",         "pet_name"),
            ("Partner Name",     "partner_name"),
            ("Parents Names",    "parents_names"),
            ("Company",          "company"),
            ("School",           "school"),
            ("College",          "college"),
            ("Phone Prefix",     "phone_prefix"),
            ("Favourite Team",   "favourite_team"),
            ("Favourite Movie",  "favourite_movie"),
            ("Favourite Game",   "favourite_game"),
            ("Vehicle",          "vehicle"),
            ("City",             "city"),
            ("State",            "state"),
            ("Country",          "country"),
            ("Custom Keywords",  "custom_keywords"),
        ]

        self._field_vars: dict[str, tk.StringVar] = {}

        for i, (label, key) in enumerate(fields):
            row = (i // 2) + 1
            col_l = (i % 2) * 2
            col_e = col_l + 1

            _label(inner, f"{label}:").grid(
                row=row, column=col_l, sticky="e", padx=(20, 4), pady=4)
            var = tk.StringVar()
            self._field_vars[key] = var
            _entry(inner, textvariable=var, width=28).grid(
                row=row, column=col_e, sticky="w", padx=(0, 20), pady=4)

        last_row = (len(fields) // 2) + 2

        # ── Progress ──────────────────────────────────────────────────────────
        self.progress = ttk.Progressbar(inner, length=460, maximum=100, mode="determinate")
        self.progress.grid(row=last_row, column=0, columnspan=4, padx=20, pady=(14, 4))

        self.prog_label = _label(inner, "")
        self.prog_label.grid(row=last_row + 1, column=0, columnspan=4, padx=20)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = _frame(inner)
        btn_frame.grid(row=last_row + 2, column=0, columnspan=4, pady=10)

        _button(btn_frame, "Generate Wordlist", self._generate).pack(side="left", padx=6)
        _button(btn_frame, "Reset", self._reset, bg="#444466", fg=GUI_FG).pack(side="left", padx=6)

        # ── Preview log ───────────────────────────────────────────────────────
        _label(inner, "Preview (first 200 words):", font=GUI_FONT_BOLD).grid(
            row=last_row + 3, column=0, columnspan=4, sticky="w", padx=20, pady=(10, 2))
        self.preview = _scrolled_text(inner, height=10)
        self.preview.grid(row=last_row + 4, column=0, columnspan=4,
                          sticky="ew", padx=20, pady=(0, 16))

    def _build_profile(self):
        from generator import UserProfile
        d = {k: v.get().strip() for k, v in self._field_vars.items()}
        kw_raw = d.pop("custom_keywords", "")
        profile = UserProfile(**d)
        profile.custom_keywords = [k.strip() for k in kw_raw.split(",") if k.strip()]
        return profile

    def _generate(self) -> None:
        from validators import validate_profile

        profile = self._build_profile()
        errors  = validate_profile(profile.__dict__)
        if errors:
            messagebox.showerror("Validation Errors", "\n".join(errors))
            return

        tokens = profile.base_tokens()
        if not tokens:
            messagebox.showwarning(
                "No Data", "Please fill in at least one field to generate a wordlist.")
            return

        self.progress["value"] = 0
        self.prog_label.config(text="Starting…")
        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.config(state="disabled")
        self._wordlist = []

        def _run() -> None:
            from generator import generate_wordlist

            def cb(current: int, total: int) -> None:
                pct = int(min(current / max(total, 1) * 100, 100))
                self.after(0, lambda p=pct, c=current: self._update_progress(p, c))

            wl = generate_wordlist(profile, progress_cb=cb)
            self.after(0, lambda: self._generation_done(wl))

        threading.Thread(target=_run, daemon=True).start()

    def _update_progress(self, pct: int, count: int) -> None:
        self.progress["value"] = pct
        self.prog_label.config(text=f"Generated {count:,} words…")

    def _generation_done(self, wordlist: list[str]) -> None:
        self._wordlist = wordlist
        self.progress["value"] = 100
        self.prog_label.config(text=f"✔ Done – {len(wordlist):,} unique words generated.")

        # Preview
        preview_words = wordlist[:200]
        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("end", "\n".join(preview_words))
        if len(wordlist) > 200:
            self.preview.insert("end", f"\n… and {len(wordlist) - 200:,} more words.")
        self.preview.config(state="disabled")

    def _reset(self) -> None:
        for var in self._field_vars.values():
            var.set("")
        self.progress["value"] = 0
        self.prog_label.config(text="")
        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.config(state="disabled")
        self._wordlist = []

    def get_wordlist(self) -> list[str]:
        return self._wordlist


# ─── Export Tab ───────────────────────────────────────────────────────────────

class ExportTab(tk.Frame):
    def __init__(self, master: tk.Widget, generator_tab: GeneratorTab) -> None:
        super().__init__(master, bg=GUI_BG)
        self._gen_tab = generator_tab
        self._build()

    def _build(self) -> None:
        _label(self, "Export Wordlist", font=GUI_FONT_LARGE).pack(anchor="w", padx=20, pady=(16, 10))

        # Filename
        row1 = _frame(self)
        row1.pack(fill="x", padx=20, pady=4)
        _label(row1, "Filename:").pack(side="left")
        self.fn_var = tk.StringVar(value="wordlist")
        _entry(row1, textvariable=self.fn_var, width=30).pack(side="left", padx=8)

        # Output folder
        row2 = _frame(self)
        row2.pack(fill="x", padx=20, pady=4)
        _label(row2, "Output folder:").pack(side="left")
        self.dir_var = tk.StringVar(value=str(OUTPUT_DIR))
        _entry(row2, textvariable=self.dir_var, width=40).pack(side="left", padx=8)
        _button(row2, "Browse…", self._browse, bg="#444466", fg=GUI_FG).pack(side="left")

        # Encoding
        row3 = _frame(self)
        row3.pack(fill="x", padx=20, pady=4)
        _label(row3, "Encoding:").pack(side="left")
        self.enc_var = tk.StringVar(value="utf-8")
        enc_combo = ttk.Combobox(row3, textvariable=self.enc_var, width=14,
                                 values=["utf-8", "utf-16", "ascii", "latin-1"])
        enc_combo.pack(side="left", padx=8)

        # Export button
        _button(self, "Export Wordlist", self._export).pack(anchor="w", padx=20, pady=12)

        # Result log
        _label(self, "Export Log:", font=GUI_FONT_BOLD).pack(anchor="w", padx=20)
        self.log_text = _scrolled_text(self, height=12)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(4, 20))

    def _browse(self) -> None:
        d = filedialog.askdirectory(title="Select output folder", initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _export(self) -> None:
        wordlist = self._gen_tab.get_wordlist()
        if not wordlist:
            messagebox.showwarning(
                "No Wordlist", "Generate a wordlist first in the Wordlist Generator tab.")
            return

        from export import export_wordlist

        try:
            res = export_wordlist(
                wordlist,
                filename   = self.fn_var.get() or "wordlist",
                output_dir = Path(self.dir_var.get()),
                encoding   = self.enc_var.get(),
            )
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export Failed", str(exc))
            return

        msg = (
            f"✔ Export successful\n"
            f"   Path     : {res.path}\n"
            f"   Words    : {res.word_count:,}\n"
            f"   Size     : {res.file_size_human}\n"
            f"   Encoding : {res.encoding}\n"
            f"   Time     : {res.elapsed_seconds:.3f}s\n"
        )
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        messagebox.showinfo("Export Complete", f"Saved to:\n{res.path}")


# ─── Settings Tab ─────────────────────────────────────────────────────────────

class SettingsTab(tk.Frame):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master, bg=GUI_BG)
        self._build()

    def _build(self) -> None:
        _label(self, "Settings", font=GUI_FONT_LARGE).pack(anchor="w", padx=20, pady=(16, 10))

        # About
        about_text = (
            f"  {APP_NAME}  v{APP_VERSION}\n\n"
            "  ⚠ DISCLAIMER\n"
            "  This tool is strictly for:\n"
            "    • Cybersecurity learning\n"
            "    • Ethical hacking training\n"
            "    • Digital forensics practice\n"
            "    • Red-team lab environments\n"
            "    • Academic / portfolio projects\n\n"
            "  Never use this tool for unauthorised access to any system.\n"
            "  The authors accept no liability for misuse.\n"
        )
        box = _scrolled_text(self, height=10)
        box.pack(fill="x", padx=20, pady=8)
        box.insert("end", about_text)
        box.config(state="disabled")

        # Open output folder button
        _button(self, "Open Output Folder", lambda: self._open_folder(OUTPUT_DIR)).pack(
            anchor="w", padx=20, pady=6)

        # Open log file button
        from config import LOG_FILE
        _button(self, "Open Log File", lambda: self._open_file(LOG_FILE),
                bg="#444466", fg=GUI_FG).pack(anchor="w", padx=20, pady=4)

    @staticmethod
    def _open_folder(path: Path) -> None:
        import subprocess, sys
        path.mkdir(exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    @staticmethod
    def _open_file(path: Path) -> None:
        import subprocess, sys
        if not path.exists():
            messagebox.showinfo("Log File", "Log file not yet created.")
            return
        if sys.platform == "win32":
            subprocess.Popen(["notepad", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])


# ─── Main Application Window ──────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME}  v{APP_VERSION}")
        self.geometry(f"{GUI_WIDTH}x{GUI_HEIGHT}")
        self.minsize(900, 600)
        self.configure(bg=GUI_BG)
        self._apply_style()
        self._build()

    def _apply_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",       background=GUI_TAB_BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=GUI_ENTRY_BG, foreground=GUI_FG,
                        font=GUI_FONT_BOLD, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", GUI_ACCENT)],
                  foreground=[("selected", GUI_BUTTON_FG)])
        style.configure("TProgressbar",
                        troughcolor=GUI_ENTRY_BG,
                        background=GUI_ACCENT,
                        borderwidth=0, thickness=14)
        style.configure("TScrollbar",
                        troughcolor=GUI_ENTRY_BG,
                        background=GUI_ACCENT)
        style.configure("TCombobox",
                        fieldbackground=GUI_ENTRY_BG,
                        background=GUI_ENTRY_BG,
                        foreground=GUI_FG,
                        selectbackground=GUI_ACCENT)

    def _build(self) -> None:
        # Title bar
        header = _frame(self)
        header.pack(fill="x")
        tk.Label(
            header,
            text=f"  🔐  {APP_NAME}",
            bg=GUI_TAB_BG, fg=GUI_ACCENT,
            font=("Consolas", 15, "bold"),
            pady=10,
        ).pack(side="left")
        tk.Label(
            header,
            text=f"v{APP_VERSION}  |  Cybersecurity Education Tool",
            bg=GUI_TAB_BG, fg="#888888",
            font=GUI_FONT,
        ).pack(side="right", padx=16)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.analyzer_tab  = AnalyzerTab(nb)
        self.generator_tab = GeneratorTab(nb)
        self.export_tab    = ExportTab(nb, self.generator_tab)
        self.settings_tab  = SettingsTab(nb)

        nb.add(self.analyzer_tab,  text="  🔍 Password Analyzer  ")
        nb.add(self.generator_tab, text="  📋 Wordlist Generator  ")
        nb.add(self.export_tab,    text="  💾 Export  ")
        nb.add(self.settings_tab,  text="  ⚙ Settings  ")


def run_gui() -> None:
    app = App()
    app.mainloop()
