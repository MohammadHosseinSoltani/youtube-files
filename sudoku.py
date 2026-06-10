#!/usr/bin/env python3
"""
Sudoku GUI – complete version with Pause/Resume, i18n (en/fa), Help/About, and solver.
Features:
- Full internationalisation (English / Persian) for all UI texts except the title bar.
- Title bar kept in English for maximum OS compatibility.
- Arabic‑text shaping via arabic_reshaper + python‑bidi (optional).
- Standard tk.Button for consistent font rendering.
- Three difficulty levels (Easy, Medium, Hard) with appropriate clue counts.
- Auto‑solver with adjustable speed, pause / resume, and stop.
- Hint function (fills one empty cell correctly).
- Timer with pause support; stops when puzzle is solved.
- Undo/Redo for player moves.
- Validation check with visual feedback.
- Cell highlighting on selection.
- Keyboard input (digits 1‑9, Delete/Backspace to clear).
- Help pop‑up with localised rules.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Tuple, Optional, Dict, Set
import logging
import random
import copy
import time

# ------------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------------
LOG_LEVEL = logging.INFO
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SudokuGUI:
    """
    A graphical Sudoku game with manual play and auto‑solver.
    Supports English and Persian localisation. The window title is always English.
    """

    # --- UI & Styling Constants ---
    BG_COLOR_MAIN = '#2C3E50'
    BG_COLOR_CONTROLS = '#34495E'
    TEXT_COLOR = 'white'
    BUTTON_BG = '#3D5060'
    BUTTON_ACTIVE_BG = '#4A6274'
    BUTTON_FG = 'white'
    BUTTON_ACTIVE_FG = 'white'

    CELL_BG_DEFAULT = '#ECF0F1'
    CELL_BG_FIXED = '#BDC3C7'
    CELL_BG_SELECTED = '#3498DB'
    CELL_BG_SAME_NUM = '#AED6F1'
    CELL_BG_ERROR = '#E74C3C'
    CELL_BG_CORRECT = '#2ECC71'

    GRID_COLOR_THIN = '#95A5A6'
    GRID_COLOR_THICK = '#2C3E50'

    GRID_SIZE = 9
    SUBGRID_SIZE = 3
    CELL_SIZE = 50

    # ----------------------------------------------------------------------
    # Internationalisation (i18n) Data
    # ----------------------------------------------------------------------
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        'en': {
            'title': 'Sudoku',
            'difficulty_label': 'Difficulty:',
            'easy': 'Easy',
            'medium': 'Medium',
            'hard': 'Hard',
            'new_game_button': 'New Game',
            'solve_button': 'Auto Solve',
            'stop_button': 'Stop',
            'pause_button': 'Pause',
            'resume_button': 'Resume',
            'hint_button': 'Hint',
            'undo_button': 'Undo',
            'redo_button': 'Redo',
            'check_button': 'Check',
            'clear_button': 'Clear',
            'timer_label': 'Time: {time}',
            'paused_text': '⏸ PAUSED',
            'toggle_lang_text': 'فارسی',
            'help_button': 'Help',
            'help_title': 'How to Play Sudoku',
            'help_text': (
                "Sudoku Rules\n\n"
                "Goal:\n"
                "Fill the 9×9 grid so that each row, column, and 3×3 box contains the digits 1-9 exactly once.\n\n"
                "How to play:\n"
                "• Click a cell to select it\n"
                "• Type a number (1-9) to fill the cell\n"
                "• Press Delete or 0 to clear a cell\n"
                "• Use Hint for help with one cell\n"
                "• Use Check to validate your solution\n"
                "• Use Undo/Redo to navigate your moves\n\n"
                "Difficulty levels:\n"
                "• Easy: 40-45 clues\n"
                "• Medium: 30-35 clues\n"
                "• Hard: 25-28 clues"
            ),
            'close_button': 'Close',
            'win_message': 'Congratulations! You solved the puzzle in {time}!',
            'invalid_solution': 'The solution is not correct. Keep trying!',
            'no_solution': 'This puzzle has no solution.',
            'hint_complete': 'Puzzle is already complete!',
            'no_undo': 'Nothing to undo.',
            'no_redo': 'Nothing to redo.',
            'confirm_new_game': 'Start a new game? Current progress will be lost.',
            'speed_label': 'Speed:',
        },
        'fa': {
            'title': 'سودوکو',
            'difficulty_label': 'سختی:',
            'easy': 'آسان',
            'medium': 'متوسط',
            'hard': 'سخت',
            'new_game_button': 'بازی جدید',
            'solve_button': 'حل خودکار',
            'stop_button': 'توقف',
            'pause_button': 'مکث',
            'resume_button': 'ادامه',
            'hint_button': 'راهنما',
            'undo_button': 'بازگشت',
            'redo_button': 'جلو',
            'check_button': 'بررسی',
            'clear_button': 'پاک کردن',
            'timer_label': 'زمان: {time}',
            'paused_text': '⏸ مکث',
            'toggle_lang_text': 'English',
            'help_button': 'راهنما',
            'help_title': 'راهنمای بازی سودوکو',
            'help_text': (
                "قوانین سودوکو\n\n"
                "هدف:\n"
                "پر کردن جدول ۹×۹ به گونه‌ای که هر سطر، ستون و مربع ۳×۳\n"
                "شامل اعداد ۱ تا ۹ دقیقاً یک بار باشد.\n\n"
                "نحوه بازی:\n"
                "• روی خانه کلیک کنید تا انتخاب شود\n"
                "• عددی (۱-۹) تایپ کنید\n"
                "• Delete یا ۰ برای پاک کردن\n"
                "• از راهنما برای کمک استفاده کنید\n"
                "• از بررسی برای اعتبارسنجی استفاده کنید\n"
                "• از بازگشت/جلو برای مرور حرکات استفاده کنید\n\n"
                "سطوح سختی:\n"
                "• آسان: ۴۰-۴۵ سرنخ\n"
                "• متوسط: ۳۰-۳۵ سرنخ\n"
                "• سخت: ۲۵-۲۸ سرنخ"
            ),
            'close_button': 'بستن',
            'win_message': 'تبریک! پازل را در {time} حل کردید!',
            'invalid_solution': 'جواب صحیح نیست. ادامه دهید!',
            'no_solution': 'این پازل جواب ندارد.',
            'hint_complete': 'پازل کامل شده است!',
            'no_undo': 'چیزی برای بازگشت نیست.',
            'no_redo': 'چیزی برای جلو رفتن نیست.',
            'confirm_new_game': 'بازی جدید شروع شود؟ پیشرفت فعلی از دست می‌رود.',
            'speed_label': 'سرعت:',
        }
    }

    PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

    def __init__(self, root: tk.Tk):
        logger.debug("Initializing SudokuGUI")
        self.root = root
        self.lang: str = 'en'
        # Title bar stays in English for cross‑OS compatibility
        self.root.title("Sudoku")
        self.root.geometry("650x750")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG_COLOR_MAIN)

        # Game State
        self.board: List[List[int]] = [[0]*9 for _ in range(9)]
        self.solution: List[List[int]] = [[0]*9 for _ in range(9)]
        self.fixed_cells: Set[Tuple[int, int]] = set()
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.difficulty: str = 'medium'

        # History for undo/redo
        self.history: List[Tuple[int, int, int, int]] = []  # (row, col, old_val, new_val)
        self.history_index: int = -1

        # Timer
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        self.timer_running: bool = False
        self.timer_id: Optional[str] = None
        self.paused: bool = False   # game paused (stops timer)

        # Auto‑solver state
        self.is_solving: bool = False
        self.is_paused: bool = False   # solver paused
        self.stop_solve_flag: bool = False
        self.solve_delay: int = 100    # ms between steps
        self.solve_after_id: Optional[str] = None
        self.solve_cells: List[Tuple[int, int, int]] = []  # (row, col, value)

        # Help popup reference
        self.help_popup: Optional[tk.Toplevel] = None

        # Font
        self._base_font = self._choose_font()

        self.setup_ui()
        self.new_game()
        logger.info("SudokuGUI initialized successfully")

    # ----------------------------------------------------------------------
    # i18n Helpers
    # ----------------------------------------------------------------------
    def _choose_font(self) -> str:
        """Return a font family that supports Arabic."""
        from tkinter import font as tkfont
        available = set(tkfont.families(self.root))
        preferred = ('DejaVu Sans', 'Noto Naskh Arabic', 'Arial')
        for name in preferred:
            if name in available:
                return name
        return 'TkDefaultFont'

    def _shape_fa(self, text: str) -> str:
        """Shape Persian text using arabic_reshaper and python‑bidi."""
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except ImportError:
            if not getattr(self, '_bidi_warning_logged', False):
                logger.warning("arabic_reshaper / python-bidi not installed")
                self._bidi_warning_logged = True
            return text

    def _(self, key: str, **kwargs: object) -> str:
        """Return translated string for current language."""
        try:
            text = self.TRANSLATIONS[self.lang][key]
        except KeyError:
            logger.warning(f"Missing translation key '{key}' for language '{self.lang}'")
            text = self.TRANSLATIONS['en'].get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        if self.lang == 'fa':
            text = self._shape_fa(text)
        return text

    def _num(self, n: int) -> str:
        """Convert integer to string with Persian digits if fa."""
        if self.lang == 'fa':
            return str(n).translate(self.PERSIAN_DIGITS)
        return str(n)

    def _time_str(self, seconds: float) -> str:
        """Format time as M:SS (or with Persian digits)."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        if self.lang == 'fa':
            return f"{self._num(mins)}:{self._num(secs):0>2}"
        return f"{mins}:{secs:02d}"

    def toggle_language(self):
        """Switch between en and fa."""
        self.lang = 'fa' if self.lang == 'en' else 'en'
        logger.info(f"Language toggled to {self.lang}")
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None
        self.refresh_language()

    def refresh_language(self):
        """Update all UI texts after a language change (title left unchanged)."""
        # Note: we do NOT change self.root.title() – it stays "Sudoku"
        self.difficulty_label.config(text=self._('difficulty_label'))
        self.easy_radio.config(text=self._('easy'))
        self.medium_radio.config(text=self._('medium'))
        self.hard_radio.config(text=self._('hard'))
        self.new_game_btn.config(text=self._('new_game_button'))
        self.solve_btn.config(text=self._('solve_button'))
        self.hint_btn.config(text=self._('hint_button'))
        self.undo_btn.config(text=self._('undo_button'))
        self.redo_btn.config(text=self._('redo_button'))
        self.check_btn.config(text=self._('check_button'))
        self.clear_btn.config(text=self._('clear_button'))
        self.help_btn.config(text=self._('help_button'))
        self.speed_label.config(text=self._('speed_label'))

        # Update pause/resume button according to current paused state
        self._update_pause_resume_btn()

        if self.lang == 'en':
            persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
            self.lang_toggle_btn.config(text=self._shape_fa(persian_label))
        else:
            self.lang_toggle_btn.config(text=self._('toggle_lang_text'))

        self.update_timer_label()
        self.draw_board()

    # ----------------------------------------------------------------------
    # UI Setup
    # ----------------------------------------------------------------------
    def setup_ui(self):
        """Create all UI widgets."""
        logger.debug("Setting up UI")

        # Top control frame
        control_frame = tk.Frame(self.root, bg=self.BG_COLOR_CONTROLS, height=100)
        control_frame.pack(fill=tk.X)
        control_frame.pack_propagate(False)

        button_font = (self._base_font, 10)

        def make_btn(parent, text, command):
            return tk.Button(
                parent, text=text, command=command,
                font=button_font,
                bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                activebackground=self.BUTTON_ACTIVE_BG,
                activeforeground=self.BUTTON_ACTIVE_FG,
                relief=tk.FLAT, padx=8, pady=2,
                highlightthickness=0, borderwidth=0
            )

        # Row 1: Difficulty selector
        row1 = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        row1.pack(pady=5)

        self.difficulty_label = tk.Label(
            row1, text=self._('difficulty_label'),
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            font=(self._base_font, 11)
        )
        self.difficulty_label.pack(side=tk.LEFT, padx=5)

        self.difficulty_var = tk.StringVar(value='medium')
        radio_font = (self._base_font, 10)
        self.easy_radio = tk.Radiobutton(
            row1, text=self._('easy'), variable=self.difficulty_var,
            value='easy', bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            selectcolor=self.BUTTON_BG, font=radio_font,
            activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR
        )
        self.easy_radio.pack(side=tk.LEFT, padx=5)

        self.medium_radio = tk.Radiobutton(
            row1, text=self._('medium'), variable=self.difficulty_var,
            value='medium', bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            selectcolor=self.BUTTON_BG, font=radio_font,
            activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR
        )
        self.medium_radio.pack(side=tk.LEFT, padx=5)

        self.hard_radio = tk.Radiobutton(
            row1, text=self._('hard'), variable=self.difficulty_var,
            value='hard', bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            selectcolor=self.BUTTON_BG, font=radio_font,
            activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR
        )
        self.hard_radio.pack(side=tk.LEFT, padx=5)

        # Row 2: Main action buttons
        row2 = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        row2.pack(pady=5)

        self.new_game_btn = make_btn(row2, self._('new_game_button'), self.confirm_new_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=3)

        self.solve_btn = make_btn(row2, self._('solve_button'), self.auto_solve)
        self.solve_btn.pack(side=tk.LEFT, padx=3)

        # Stop button (packed only when solver is running)
        self.stop_btn = make_btn(row2, self._('stop_button'), self.interrupt_solve)

        # Pause/Resume button (text updated according to state)
        self.pause_resume_btn = make_btn(row2, self._('pause_button'), self.toggle_pause_solve)
        self.pause_resume_btn.pack(side=tk.LEFT, padx=3)

        self.hint_btn = make_btn(row2, self._('hint_button'), self.give_hint)
        self.hint_btn.pack(side=tk.LEFT, padx=3)

        self.check_btn = make_btn(row2, self._('check_button'), self.check_solution)
        self.check_btn.pack(side=tk.LEFT, padx=3)

        # Row 3: Undo/Redo, Clear, Speed, Language, Help
        row3 = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        row3.pack(pady=5)

        self.undo_btn = make_btn(row3, self._('undo_button'), self.undo)
        self.undo_btn.pack(side=tk.LEFT, padx=3)

        self.redo_btn = make_btn(row3, self._('redo_button'), self.redo)
        self.redo_btn.pack(side=tk.LEFT, padx=3)

        self.clear_btn = make_btn(row3, self._('clear_button'), self.clear_cell)
        self.clear_btn.pack(side=tk.LEFT, padx=3)

        # Speed slider
        self.speed_label = tk.Label(
            row3, text=self._('speed_label'),
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            font=(self._base_font, 10)
        )
        self.speed_label.pack(side=tk.LEFT, padx=5)

        self.speed_slider = ttk.Scale(
            row3, from_=10, to=500, orient=tk.HORIZONTAL,
            command=self.set_solve_delay, length=80
        )
        self.speed_slider.set(100)   # initial delay 100 ms
        self.speed_slider.pack(side=tk.LEFT, padx=3)

        self.lang_toggle_btn = make_btn(
            row3,
            self._shape_fa(self.TRANSLATIONS['en']['toggle_lang_text']),
            self.toggle_language
        )
        self.lang_toggle_btn.pack(side=tk.LEFT, padx=5)

        self.help_btn = make_btn(row3, self._('help_button'), self.show_help)
        self.help_btn.pack(side=tk.LEFT, padx=3)

        # Timer label
        self.timer_label = tk.Label(
            control_frame, text=self._('timer_label', time='0:00'),
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            font=(self._base_font, 12, 'bold')
        )
        self.timer_label.pack(pady=5)

        # Canvas for the board
        canvas_size = self.CELL_SIZE * self.GRID_SIZE + 20
        self.canvas = tk.Canvas(
            self.root, width=canvas_size, height=canvas_size,
            bg=self.BG_COLOR_MAIN, highlightthickness=0
        )
        self.canvas.pack(pady=10)

        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.root.bind('<Key>', self.on_key_press)

        logger.debug("UI setup complete")

    # ----------------------------------------------------------------------
    # Help popup
    # ----------------------------------------------------------------------
    def show_help(self):
        """Show help popup."""
        if self.help_popup is not None and tk.Toplevel.winfo_exists(self.help_popup):
            self.help_popup.lift()
            self.help_popup.focus_force()
            return

        popup = tk.Toplevel(self.root)
        popup.title("How to Play")
        popup.transient(self.root)
        popup.resizable(False, False)
        popup.configure(bg=self.BG_COLOR_MAIN)

        help_text = self._('help_text')
        justify = 'right' if self.lang == 'fa' else 'left'
        label = tk.Label(
            popup, text=help_text,
            font=(self._base_font, 11),
            bg=self.BG_COLOR_MAIN, fg=self.TEXT_COLOR,
            justify=justify, wraplength=450,
            padx=20, pady=20
        )
        label.pack()

        close_btn = tk.Button(
            popup, text=self._('close_button'),
            font=(self._base_font, 10),
            bg=self.BUTTON_BG, fg=self.BUTTON_FG,
            activebackground=self.BUTTON_ACTIVE_BG,
            activeforeground=self.BUTTON_ACTIVE_FG,
            relief=tk.FLAT, padx=8, pady=2,
            highlightthickness=0, borderwidth=0,
            command=self._on_help_popup_close
        )
        close_btn.pack(pady=(0, 20))

        self.help_popup = popup
        popup.protocol("WM_DELETE_WINDOW", self._on_help_popup_close)

    def _on_help_popup_close(self):
        """Callback when help popup is closed."""
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None

    # ----------------------------------------------------------------------
    # Game Logic
    # ----------------------------------------------------------------------
    def confirm_new_game(self):
        """Confirm before starting new game if in progress."""
        if self.is_solving:
            self.interrupt_solve()

        if any(self.board[r][c] != 0 for r in range(9) for c in range(9) if (r, c) not in self.fixed_cells):
            if not messagebox.askyesno("Sudoku", self._('confirm_new_game'), parent=self.root):
                return

        self.difficulty = self.difficulty_var.get()
        self.new_game()

    def new_game(self):
        """Start a new game."""
        logger.info(f"Starting new game with difficulty: {self.difficulty}")
        self._stop_timer()

        # Generate solution
        self.solution = self._generate_solution()

        # Create puzzle by removing cells
        clues_map = {'easy': (40, 45), 'medium': (30, 35), 'hard': (25, 28)}
        min_clues, max_clues = clues_map[self.difficulty]
        num_clues = random.randint(min_clues, max_clues)

        self.board = [row[:] for row in self.solution]
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)

        removed = 0
        for r, c in cells:
            if removed >= 81 - num_clues:
                break
            self.board[r][c] = 0
            removed += 1

        self.fixed_cells = {(r, c) for r in range(9) for c in range(9) if self.board[r][c] != 0}
        self.selected_cell = None
        self.history = []
        self.history_index = -1

        # Reset timer and start
        self.paused = False
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.timer_running = True
        self._update_timer()

        self._set_ui_state(True)
        self.draw_board()
        logger.info(f"New game started with {num_clues} clues")

    def _generate_solution(self) -> List[List[int]]:
        """Generate a valid Sudoku solution."""
        board = [[0]*9 for _ in range(9)]
        self._fill_board(board)
        return board

    def _fill_board(self, board: List[List[int]]) -> bool:
        """Fill board using backtracking."""
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if self._is_valid(board, r, c, num):
                            board[r][c] = num
                            if self._fill_board(board):
                                return True
                            board[r][c] = 0
                    return False
        return True

    def _is_valid(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid."""
        if num in board[row]:
            return False
        if num in [board[r][col] for r in range(9)]:
            return False
        box_r, box_c = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if board[r][c] == num:
                    return False
        return True

    def _is_complete(self) -> bool:
        """Check if board is completely filled."""
        return all(self.board[r][c] != 0 for r in range(9) for c in range(9))

    def _is_correct(self) -> bool:
        """Check if current board matches solution."""
        return self.board == self.solution

    # ----------------------------------------------------------------------
    # User Interaction
    # ----------------------------------------------------------------------
    def on_canvas_click(self, event: tk.Event):
        """Handle canvas click to select cell."""
        if self.is_solving or self.paused:
            return

        offset = 10
        x, y = event.x - offset, event.y - offset
        if x < 0 or y < 0:
            return

        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if 0 <= row < 9 and 0 <= col < 9:
            if (row, col) not in self.fixed_cells:
                self.selected_cell = (row, col)
                logger.debug(f"Selected cell ({row}, {col})")
                self.draw_board()

    def on_key_press(self, event: tk.Event):
        """Handle keyboard input."""
        if self.is_solving or self.paused or self.selected_cell is None:
            return

        row, col = self.selected_cell
        if (row, col) in self.fixed_cells:
            return

        key = event.char
        if key in '123456789':
            num = int(key)
            old_val = self.board[row][col]
            if old_val != num:
                self.board[row][col] = num
                self._add_to_history(row, col, old_val, num)
                logger.debug(f"Set cell ({row}, {col}) to {num}")
                self.draw_board()

                if self._is_complete():
                    self.check_solution(auto=True)

        elif key in ('0', '\x7f', '\x08'):  # 0, Delete, Backspace
            self.clear_cell()

    def clear_cell(self):
        """Clear selected cell."""
        if self.selected_cell is None or self.is_solving or self.paused:
            return

        row, col = self.selected_cell
        if (row, col) in self.fixed_cells:
            return

        old_val = self.board[row][col]
        if old_val != 0:
            self.board[row][col] = 0
            self._add_to_history(row, col, old_val, 0)
            self.draw_board()

    # ----------------------------------------------------------------------
    # Undo/Redo
    # ----------------------------------------------------------------------
    def _add_to_history(self, r, c, old, new):
        """Add move to history list."""
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append((r, c, old, new))
        self.history_index += 1

    def undo(self):
        """Undo the last move."""
        if self.is_solving or self.paused:
            return
        if self.history_index < 0:
            messagebox.showinfo("Sudoku", self._('no_undo'))
            return
        r, c, old, new = self.history[self.history_index]
        self.board[r][c] = old
        self.history_index -= 1
        self.draw_board()

    def redo(self):
        """Redo the previously undone move."""
        if self.is_solving or self.paused:
            return
        if self.history_index >= len(self.history) - 1:
            messagebox.showinfo("Sudoku", self._('no_redo'))
            return
        self.history_index += 1
        r, c, old, new = self.history[self.history_index]
        self.board[r][c] = new
        self.draw_board()

    # ----------------------------------------------------------------------
    # Timer
    # ----------------------------------------------------------------------
    def _stop_timer(self):
        """Cancel the timer loop and reset running flag."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_running = False

    def _update_timer(self):
        """Recurring timer update."""
        if self.timer_running and not self.paused:
            now = time.time()
            self.elapsed_time = now - self.start_time
            self.update_timer_label()
            self.timer_id = self.root.after(200, self._update_timer)

    def update_timer_label(self):
        """Refresh the timer label."""
        self.timer_label.config(
            text=self._('timer_label', time=self._time_str(self.elapsed_time))
        )

    def pause_game(self):
        """Pause the game (timer and input)."""
        self.paused = True
        if self.is_solving:
            self.is_paused = True
        self._update_pause_resume_btn()
        self.draw_board()

    def resume_game(self):
        """Resume the game."""
        self.paused = False
        if self.is_solving and self.is_paused:
            self.is_paused = False
            self._step_solver()
        self._update_pause_resume_btn()
        self.draw_board()

    def toggle_pause_resume(self):
        """Toggle pause/resume for both manual game and solver."""
        if self.paused:
            self.resume_game()
        else:
            self.pause_game()

    def _update_pause_resume_btn(self):
        """Update the text on the pause/resume button."""
        if self.paused:
            self.pause_resume_btn.config(text=self._('resume_button'))
        else:
            self.pause_resume_btn.config(text=self._('pause_button'))

    # ----------------------------------------------------------------------
    # Solver
    # ----------------------------------------------------------------------
    def set_solve_delay(self, val):
        """Callback for speed slider; val is string of float, e.g. '100.0'."""
        self.solve_delay = int(float(val))

    def interrupt_solve(self):
        """Stop the solver."""
        self.stop_solve_flag = True
        if self.solve_after_id:
            self.root.after_cancel(self.solve_after_id)
            self.solve_after_id = None
        self.is_solving = False
        self.is_paused = False
        self.paused = False
        self._update_pause_resume_btn()
        self._set_ui_state(True)
        self.draw_board()

    def auto_solve(self):
        """Start the automatic solver."""
        if self.is_solving:
            return
        # Generate solver steps
        board_copy = copy.deepcopy(self.board)
        self.solve_cells = []
        if not self._collect_solver_steps(board_copy):
            messagebox.showinfo("Sudoku", self._('no_solution'))
            return
        self.is_solving = True
        self.stop_solve_flag = False
        self.is_paused = False
        self._set_ui_state(False)
        self._update_pause_resume_btn()
        self._step_solver()

    def _collect_solver_steps(self, board: List[List[int]]) -> bool:
        """
        Backtracking that fills a copy of the board and records the cells that were empty.
        Returns True if a solution exists; the steps are stored as (row, col, value).
        """
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if self._is_valid(board, r, c, num):
                            board[r][c] = num
                            self.solve_cells.append((r, c, num))
                            if self._collect_solver_steps(board):
                                return True
                            board[r][c] = 0
                            self.solve_cells.pop()
                    return False
        return True

    def _step_solver(self):
        """Perform one step of the solver if not stopped or paused."""
        if self.stop_solve_flag:
            self.interrupt_solve()
            return
        if self.paused:
            return
        if not self.solve_cells:
            self.is_solving = False
            self._set_ui_state(True)
            self._update_pause_resume_btn()
            return
        r, c, val = self.solve_cells.pop(0)
        self.board[r][c] = val
        self.draw_board()
        self.solve_after_id = self.root.after(self.solve_delay, self._step_solver)

    def toggle_pause_solve(self):
        """Pause/Resume the solver (also pauses manual game timer)."""
        self.toggle_pause_resume()

    # ----------------------------------------------------------------------
    # Hint
    # ----------------------------------------------------------------------
    def give_hint(self):
        """Fill one empty cell correctly."""
        if self.is_solving:
            return
        if self._is_complete():
            messagebox.showinfo("Sudoku", self._('hint_complete'))
            return
        # Find all empty cells and choose one randomly
        empty = [(r, c) for r in range(9) for c in range(9) if self.board[r][c] == 0]
        if not empty:
            return
        r, c = random.choice(empty)
        correct = self.solution[r][c]
        old_val = self.board[r][c]
        self.board[r][c] = correct
        self._add_to_history(r, c, old_val, correct)
        self.draw_board()
        if self._is_complete():
            self.check_solution(auto=True)

    # ----------------------------------------------------------------------
    # Check solution
    # ----------------------------------------------------------------------
    def check_solution(self, auto=False):
        """Check if the puzzle is complete and correct."""
        if not self._is_complete():
            if not auto:
                messagebox.showinfo("Sudoku", self._('invalid_solution'))
            return
        if self._is_correct():
            self._stop_timer()
            time_str = self._time_str(self.elapsed_time)
            messagebox.showinfo("Sudoku", self._('win_message', time=time_str))
        else:
            if not auto:
                messagebox.showinfo("Sudoku", self._('invalid_solution'))

    # ----------------------------------------------------------------------
    # Drawing
    # ----------------------------------------------------------------------
    def draw_board(self):
        """Draw grid and numbers."""
        self.canvas.delete('all')
        offset = 10
        # Grid lines
        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            color = self.GRID_COLOR_THICK if i % 3 == 0 else self.GRID_COLOR_THIN
            # vertical
            self.canvas.create_line(
                offset + i * self.CELL_SIZE, offset,
                offset + i * self.CELL_SIZE, offset + 9 * self.CELL_SIZE,
                fill=color, width=width
            )
            # horizontal
            self.canvas.create_line(
                offset, offset + i * self.CELL_SIZE,
                offset + 9 * self.CELL_SIZE, offset + i * self.CELL_SIZE,
                fill=color, width=width
            )

        # Cells
        for r in range(9):
            for c in range(9):
                x1 = offset + c * self.CELL_SIZE
                y1 = offset + r * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                fill = self.CELL_BG_DEFAULT
                if (r, c) == self.selected_cell:
                    fill = self.CELL_BG_SELECTED
                elif (r, c) in self.fixed_cells:
                    fill = self.CELL_BG_FIXED
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline='')

                val = self.board[r][c]
                if val != 0:
                    display_val = self._num(val)
                    self.canvas.create_text(
                        x1 + self.CELL_SIZE // 2, y1 + self.CELL_SIZE // 2,
                        text=display_val, font=(self._base_font, 18, 'bold')
                    )

        # Dark overlay when paused
        if self.paused:
            self.canvas.create_rectangle(
                offset, offset,
                offset + 9 * self.CELL_SIZE, offset + 9 * self.CELL_SIZE,
                fill='gray', stipple='gray50', outline=''
            )

    # ----------------------------------------------------------------------
    # Utility
    # ----------------------------------------------------------------------
    def _set_ui_state(self, normal=True):
        """Enable/disable buttons during solver."""
        state = tk.NORMAL if normal else tk.DISABLED
        for btn in (self.new_game_btn, self.solve_btn, self.hint_btn,
                    self.undo_btn, self.redo_btn, self.check_btn,
                    self.clear_btn, self.help_btn, self.lang_toggle_btn):
            btn.config(state=state)
        if not normal:
            self.stop_btn.pack(side=tk.LEFT, padx=3, before=self.pause_resume_btn)
        else:
            self.stop_btn.pack_forget()
            self.paused = False
            self._update_pause_resume_btn()


# ----------------------------------------------------------------------
# Main launcher
# ----------------------------------------------------------------------
if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = SudokuGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        pass
