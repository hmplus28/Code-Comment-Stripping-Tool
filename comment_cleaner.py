import os
import fnmatch
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class CommentSyntax:
    line_markers: List[str]
    block_markers: List[Tuple[str, str]]
    supports_nested_blocks: bool = False

SYNTAX_BY_EXT = {
    ".c": CommentSyntax(["//"], [("/*", "*/")]),
    ".h": CommentSyntax(["//"], [("/*", "*/")]),
    ".cpp": CommentSyntax(["//"], [("/*", "*/")]),
    ".hpp": CommentSyntax(["//"], [("/*", "*/")]),
    ".cc": CommentSyntax(["//"], [("/*", "*/")]),
    ".hh": CommentSyntax(["//"], [("/*", "*/")]),
    ".java": CommentSyntax(["//"], [("/*", "*/")]),
    ".kt": CommentSyntax(["//"], [("/*", "*/")]),
    ".cs": CommentSyntax(["//"], [("/*", "*/")]),
    ".js": CommentSyntax(["//"], [("/*", "*/")]),
    ".mjs": CommentSyntax(["//"], [("/*", "*/")]),
    ".ts": CommentSyntax(["//"], [("/*", "*/")]),
    ".jsx": CommentSyntax(["//"], [("/*", "*/")]),
    ".tsx": CommentSyntax(["//"], [("/*", "*/")]),
    ".go": CommentSyntax(["//"], [("/*", "*/")]),
    ".rs": CommentSyntax(["//"], [("/*", "*/")]),
    ".swift": CommentSyntax(["//"], [("/*", "*/")]),
    ".php": CommentSyntax(["//", "#"], [("/*", "*/")]),
    ".py": CommentSyntax(["#"], []),
    ".rb": CommentSyntax(["#"], []),
    ".sh": CommentSyntax(["#"], []),
    ".bash": CommentSyntax(["#"], []),
    ".zsh": CommentSyntax(["#"], []),
    ".yaml": CommentSyntax(["#"], []),
    ".yml": CommentSyntax(["#"], []),
    ".toml": CommentSyntax(["#"], []),
    ".ini": CommentSyntax([";", "#"], []),
    ".cfg": CommentSyntax([";", "#"], []),
    ".sql": CommentSyntax(["--"], [("/*", "*/")]),
    ".css": CommentSyntax([], [("/*", "*/")]),
    ".scss": CommentSyntax(["//"], [("/*", "*/")]),
    ".less": CommentSyntax(["//"], [("/*", "*/")]),
    ".html": CommentSyntax([], [("<!--", "-->")]),
    ".htm": CommentSyntax([], [("<!--", "-->")]),
    ".xml": CommentSyntax([], [("<!--", "-->")]),
    ".vue": CommentSyntax(["//"], [("/*", "*/"), ("<!--", "-->")]),
    ".lua": CommentSyntax(["--"], [("--[[", "]]")], supports_nested_blocks=True),
    ".hs": CommentSyntax(["--"], [("{-", "-}")], supports_nested_blocks=True),
}

GENERIC_FALLBACK = CommentSyntax(["//", "#", "--", ";"], [("/*", "*/"), ("<!--", "-->")])

TEXT_EXT_HINTS = set(SYNTAX_BY_EXT.keys()) | {
    ".md", ".txt", ".json", ".env", ".properties", ".gradle", ".make", ".mk", ".dockerfile"
}

def is_probably_text(path: str) -> bool:
    _, ext = os.path.splitext(path.lower())
    if ext in TEXT_EXT_HINTS:
        return True
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
        return b"\x00" not in chunk
    except Exception:
        return False

def read_text(path: str) -> Optional[str]:
    for encoding in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None

def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)

def normalize_newlines(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")

def pick_syntax(path: str) -> CommentSyntax:
    _, ext = os.path.splitext(path.lower())
    return SYNTAX_BY_EXT.get(ext, GENERIC_FALLBACK)

class CommentStripper:
    def __init__(self, text: str, syntax: CommentSyntax, allow_backtick: bool = True, is_js_like: bool = False):
        self.s = normalize_newlines(text)
        self.n = len(self.s)
        self.i = 0
        self.out = []
        self.syntax = syntax
        self.allow_backtick = allow_backtick
        self.is_js_like = is_js_like
        self.in_squote = self.in_dquote = self.in_btick = self.in_triple = self.in_block = False
        self.triple_delim = self.block_end = ""
        self.block_nest_level = 0 if syntax.supports_nested_blocks else None
        self.escape = False
        self.block_starts = [start for start, _ in syntax.block_markers]
        self.block_map = dict(syntax.block_markers)
        self.line_markers = syntax.line_markers[:]

    def startswith_any(self, markers: List[str]) -> Optional[str]:
        for m in sorted(markers, key=len, reverse=True):
            if self.s.startswith(m, self.i):
                return m
        return None

    def strip(self) -> str:
        while self.i < self.n:
            ch = self.s[self.i]

            if self.in_block:
                if self.syntax.supports_nested_blocks:
                    start = self.startswith_any(self.block_starts)
                    if start:
                        self.block_nest_level += 1
                        self.i += len(start)
                        continue
                    if self.s.startswith(self.block_end, self.i):
                        self.block_nest_level -= 1
                        self.i += len(self.block_end)
                        if self.block_nest_level <= 0:
                            self.in_block = False
                            self.block_end = ""
                        continue
                else:
                    if self.s.startswith(self.block_end, self.i):
                        self.i += len(self.block_end)
                        self.in_block = False
                        self.block_end = ""
                        continue
                self.i += 1
                continue

            if self.in_triple:
                if self.s.startswith(self.triple_delim, self.i) and not self.escape:
                    self.out.append(self.triple_delim)
                    self.i += len(self.triple_delim)
                    self.in_triple = False
                    self.triple_delim = ""
                    self.escape = False
                    continue
                ch = self.s[self.i]
                self.out.append(ch)
                self.escape = (ch == "\\") and not self.escape
                self.i += 1
                continue

            if self.in_squote or self.in_dquote or (self.allow_backtick and self.in_btick):
                self.out.append(ch)
                if ch == "\\" and not self.escape:
                    self.escape = True
                else:
                    self.escape = False
                    if not self.escape:
                        if self.in_squote and ch == "'":     self.in_squote = False
                        elif self.in_dquote and ch == '"':   self.in_dquote = False
                        elif self.allow_backtick and self.in_btick and ch == "`":
                            self.in_btick = False
                self.i += 1
                continue

            if self.s.startswith(("'''", '"""'), self.i):
                self.triple_delim = self.s[self.i:self.i+3]
                self.in_triple = True
                self.out.append(self.triple_delim)
                self.i += 3
                self.escape = False
                continue

            bs = self.startswith_any(self.block_starts)
            if bs:
                self.in_block = True
                self.block_end = self.block_map[bs]
                self.i += len(bs)
                if self.syntax.supports_nested_blocks:
                    self.block_nest_level = 1
                continue

            lm = self.startswith_any(self.line_markers)
            if lm:
                self.i += len(lm)
                while self.i < self.n and self.s[self.i] != "\n":
                    self.i += 1
                continue

            if ch == "'":
                self.in_squote = True
                self.out.append(ch)
                self.i += 1
                self.escape = False
                continue
            if ch == '"':
                self.in_dquote = True
                self.out.append(ch)
                self.i += 1
                self.escape = False
                continue
            if self.allow_backtick and ch == "`":
                self.in_btick = True
                self.out.append(ch)
                self.i += 1
                self.escape = False
                continue

            self.out.append(ch)
            self.i += 1

        return "".join(self.out)

def strip_comments_for_file(path: str, content: str) -> str:
    syntax = pick_syntax(path)
    ext = os.path.splitext(path.lower())[1]
    allow_backtick = ext in {".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue"}
    is_js_like = ext in {".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue"}
    stripper = CommentStripper(content, syntax, allow_backtick, is_js_like)
    return stripper.strip()

def matches_any_pattern(rel_path: str, patterns: List[str]) -> bool:
    rel = rel_path.replace("\\", "/")
    for pat in patterns:
        p = pat.strip().replace("\\", "/")
        if not p: continue
        if fnmatch.fnmatch(rel, p):
            return True
        if rel == p or rel.startswith(p.rstrip("/") + "/"):
            return True
    return False

@dataclass
class RunStats:
    scanned: int = 0
    skipped: int = 0
    changed: int = 0
    unchanged: int = 0
    errors: int = 0
    bytes_before: int = 0
    bytes_after: int = 0
    changed_files: List[str] = None

    def __post_init__(self):
        self.changed_files = []

def process_directory(
    root_dir: str,
    exclude_patterns: List[str],
    dry_run: bool,
    make_backup: bool,
    only_known_ext: bool,
    log_func: Callable[[str], None]
) -> RunStats:
    stats = RunStats()
    root_dir = os.path.abspath(root_dir)

    for base, dirs, files in os.walk(root_dir):
        rel_base = os.path.relpath(base, root_dir)
        if rel_base == ".":
            rel_base = ""

        if rel_base and matches_any_pattern(rel_base + "/", exclude_patterns):
            dirs[:] = []
            continue

        dirs[:] = [
            d for d in dirs
            if not matches_any_pattern((rel_base + "/" + d).lstrip("/"), exclude_patterns)
        ]

        for name in files:
            if name.lower().endswith(".bak"):
                stats.skipped += 1
                continue

            full = os.path.join(base, name)
            rel = os.path.relpath(full, root_dir).replace("\\", "/")

            if matches_any_pattern(rel, exclude_patterns):
                stats.skipped += 1
                continue

            if not is_probably_text(full):
                stats.skipped += 1
                continue

            _, ext = os.path.splitext(full.lower())
            if only_known_ext and ext not in SYNTAX_BY_EXT:
                stats.skipped += 1
                continue

            text = read_text(full)
            if text is None:
                stats.skipped += 1
                continue

            stats.scanned += 1
            before = text

            try:
                after = strip_comments_for_file(full, before)
            except Exception as e:
                logging.error(f"Error processing {rel}: {e}")
                stats.errors += 1
                log_func(f"Error processing {rel}: {e}")
                continue

            if after != before:
                stats.changed += 1
                stats.changed_files.append(rel)

                b_before = len(before.encode("utf-8", "ignore"))
                b_after = len(after.encode("utf-8", "ignore"))
                stats.bytes_before += b_before
                stats.bytes_after += b_after

                removed_bytes = b_before - b_after
                removed_chars = len(before) - len(after)
                removed_lines_approx = before.count("\n") - after.count("\n")

                status = "would be changed (Dry Run)" if dry_run else "changed"
                log_func(f"  → {rel}  ({status})")
                log_func(f"      removed approx: {removed_chars:,} chars  |  ~{removed_lines_approx} lines  |  {removed_bytes:,} bytes")


                if dry_run:
                    removed_sample = []
                    before_lines = before.splitlines(keepends=False)
                    after_lines = after.splitlines(keepends=False)

                    i = 0
                    syntax = pick_syntax(full)
                    comment_starters = syntax.line_markers + [start for start, _ in syntax.block_markers]

                    while i < len(before_lines) and len(removed_sample) < 15:
                        orig_line = before_lines[i].rstrip()
                        if i >= len(after_lines) or orig_line != after_lines[i].rstrip():
                            stripped = orig_line.strip()
                            if len(stripped) > 3:

                                starts_with_comment = any(
                                    orig_line.lstrip().startswith(m) for m in comment_starters
                                )
                                if starts_with_comment or "TODO" in stripped.upper() or "FIXME" in stripped.upper():
                                    removed_sample.append(orig_line)
                        i += 1

                    if removed_sample:
                        log_func("      Sample removed comment lines (preview):")
                        for idx, line in enumerate(removed_sample, 1):
                            display = line.replace("\t", "  ").rstrip()
                            log_func(f"        {idx:2d} | {display}")
                    else:
                        log_func("      (No obvious comment lines detected – possibly only whitespace changes)")

                if not dry_run:
                    try:
                        if make_backup:
                            bak_path = full + ".bak"
                            if not os.path.exists(bak_path):
                                write_text(bak_path, before)
                        write_text(full, after)
                    except Exception as e:
                        logging.error(f"Error saving {rel}: {e}")
                        stats.errors += 1
                        log_func(f"Error saving {rel}: {e}")
            else:
                stats.unchanged += 1

    return stats

class CommentCleanerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comment Cleaner")
        self.geometry("960x720")
        self.resizable(True, True)

        self.dir_var = tk.StringVar()
        self.dry_var = tk.BooleanVar(value=True)
        self.bak_var = tk.BooleanVar(value=True)
        self.known_ext_var = tk.BooleanVar(value=True)

        self._build_ui()
        self._add_help_section()

    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill=tk.BOTH, expand=True)

        # Directory
        f1 = ttk.Frame(main)
        f1.pack(fill="x", pady=(0, 10))
        ttk.Label(f1, text="Directory:").pack(side="left")
        ttk.Entry(f1, textvariable=self.dir_var).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(f1, text="Browse", command=self._pick_directory).pack(side="left")

        # Options
        f2 = ttk.LabelFrame(main, text=" Options ", padding=10)
        f2.pack(fill="x", pady=8)

        ttk.Checkbutton(
            f2, text="Dry Run (simulate only – no files modified)",
            variable=self.dry_var
        ).pack(anchor="w")
        ttk.Checkbutton(
            f2, text="Create .bak backup files before modifying",
            variable=self.bak_var
        ).pack(anchor="w")
        ttk.Checkbutton(
            f2, text="Process only known programming file extensions",
            variable=self.known_ext_var
        ).pack(anchor="w")

        # Exclusions
        ttk.Label(main, text="Exclude patterns (one per line) – examples:").pack(anchor="w", pady=(12, 2))
        ttk.Label(
            main,
            text="  node_modules/   dist/   **/*.min.js   **/*.map   .git/   *.bak",
            foreground="gray"
        ).pack(anchor="w")

        excl_frame = ttk.Frame(main)
        excl_frame.pack(fill="both", expand=False, pady=(4, 12))
        self.exclude_text = scrolledtext.ScrolledText(excl_frame, height=6, wrap="word")
        self.exclude_text.pack(fill="both", expand=True)
        self.exclude_text.insert("1.0", "node_modules/\ndist/\nbuild/\n**/*.min.js\n**/*.map\n**/*.bak\n.git/\n")

        # Buttons
        f_btn = ttk.Frame(main)
        f_btn.pack(fill="x", pady=10)
        ttk.Button(f_btn, text="Run", command=self._start_processing).pack(side="left", padx=6)
        ttk.Button(f_btn, text="Clear Log", command=lambda: self.log_text.delete("1.0", "end")).pack(side="left")

        # Log
        ttk.Label(main, text="Operation Log:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(main, height=18, state="normal", wrap="word")
        self.log_text.pack(fill="both", expand=True, pady=(4, 0))

    def _add_help_section(self):
        help_frame = ttk.LabelFrame(self, text=" Help / Quick Guide ", padding=10)
        help_frame.pack(fill="x", pady=8, padx=14)

        help_text = (
            "Dry Run (default = on):\n"
            "  Scans files and shows which comment lines would be removed – no actual changes.\n\n"
            "Create .bak backups:\n"
            "  Creates a backup copy (filename.bak) before modifying any file.\n\n"
            "Only known code extensions:\n"
            "  Only processes files like .js .py .ts .java etc. – skips .txt .md .json etc.\n\n"
            "Notes:\n"
            "  • .bak files are automatically skipped\n"
            "  • In Dry Run mode you will see sample comment lines that would be deleted\n"
            "  • Uncheck Dry Run to actually remove the comments\n"
        )

        tk.Label(help_frame, text=help_text, justify="left", anchor="w", font=("Helvetica", 10)).pack(fill="x")

    def _pick_directory(self):
        d = filedialog.askdirectory(title="Select Project Folder")
        if d:
            self.dir_var.set(d)

    def _get_excludes(self) -> List[str]:
        content = self.exclude_text.get("1.0", "end").strip()
        return [line.strip() for line in content.splitlines() if line.strip()]

    def _log(self, msg: str):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.update_idletasks()

    def _start_processing(self):
        root = self.dir_var.get().strip()
        if not root or not os.path.isdir(root):
            messagebox.showerror("Error", "Please select a valid directory.")
            return

        excludes = self._get_excludes()
        dry = self.dry_var.get()
        backup = self.bak_var.get()
        only_known = self.known_ext_var.get()

        self.log_text.delete("1.0", "end")
        self._log("Starting processing...")
        self._log(f"Root:               {root}")
        self._log(f"Dry Run:            {'Yes (preview only)' if dry else 'No – will modify files'}")
        self._log(f"Backups (.bak):     {'Yes' if backup else 'No'}")
        self._log(f"Only code files:    {'Yes' if only_known else 'No'}")
        self._log(f"Exclude patterns:   {len(excludes)}")
        self._log("-" * 70)

        try:
            stats = process_directory(
                root_dir=root,
                exclude_patterns=excludes,
                dry_run=dry,
                make_backup=backup,
                only_known_ext=only_known,
                log_func=self._log
            )
        except Exception as e:
            messagebox.showerror("Critical Error", str(e))
            self._log(f"Critical error: {e}")
            return

        self._log("-" * 70)
        self._log(f"Scanned files:          {stats.scanned:,}")
        self._log(f"Would change / changed: {stats.changed:,}")
        self._log(f"Unchanged:              {stats.unchanged:,}")
        self._log(f"Skipped:                {stats.skipped:,}")
        self._log(f"Errors:                 {stats.errors:,}")

        if stats.changed:
            saved = stats.bytes_before - stats.bytes_after
            self._log(f"Approx. bytes saved:    {saved:,} bytes")
            self._log("\nAffected files:")
            for p in stats.changed_files[:400]:
                self._log(f"  • {p}")
            if len(stats.changed_files) > 400:
                self._log(f"  ... and {len(stats.changed_files)-400} more")

        mode = "Preview (Dry Run)" if dry else "Actual modifications"
        messagebox.showinfo("Finished", f"Done.\nMode: {mode}\n{stats.changed} file(s) affected.")

if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = CommentCleanerApp()
    app.mainloop()
