#!/usr/bin/env python3
"""
Tic-Tac-Toe GUI – improved version with Undo/Redo, i18n (en/fa), AI opponent, and Help/About.
Changes (including bug fixes):
- Full i18n (English & Persian) with a language toggle button.
- Persian text rendering using arabic_reshaper + python-bidi when language is 'fa'.
- Standard tk.Button (not ttk) for reliable font rendering in both scripts.
- Undo/Redo with correct score tracking and proper replay of player+AI pairs.
- AI opponent with three difficulty levels (Easy, Medium, Hard – minimax).
- Medium AI now correctly blocks the opponent (fixes bug where it never blocked).
- Pending AI timer cancelled when mode / new game changes (prevents spurious AI moves).
- Window title now translated when language changes.
- Message box titles are localised.
- Help pop‑up reference correctly cleaned up on window close.
- i18n fallback returns un‑shaped English text when a translation key is missing.
- Hover effect: cursor changes and cell highlight.
- Responsive grid that scales with the window.
- Graceful shutdown on Ctrl+C.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple, Optional, Dict
import logging
import random

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


class TicTacToeGUI:
    """
    A graphical Tic-Tac-Toe game with AI opponent, undo/redo, and bilingual support.
    Features manual play against AI or two-player mode with move history.
    Supports English and Persian localisation.
    """

    # --- UI & Styling Constants ---
    BG_COLOR_MAIN = '#1E272E'
    BG_COLOR_CONTROLS = '#2C3A47'
    BG_COLOR_CANVAS = '#34495E'
    TEXT_COLOR = 'white'
    BUTTON_BG = '#3D5060'
    BUTTON_ACTIVE_BG = '#4A6274'
    BUTTON_FG = 'white'
    BUTTON_ACTIVE_FG = 'white'
    
    GRID_COLOR = '#95A5A6'
    X_COLOR = '#E74C3C'
    O_COLOR = '#3498DB'
    WIN_LINE_COLOR = '#F1C40F'
    HOVER_COLOR = '#2ECC71'
    
    CELL_PADDING = 20
    LINE_WIDTH = 4
    SYMBOL_WIDTH = 8

    # --- Game Constants ---
    EMPTY = ' '
    PLAYER_X = 'X'
    PLAYER_O = 'O'
    
    # ----------------------------------------------------------------------
    # Internationalisation (i18n) Data
    # ----------------------------------------------------------------------
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        'en': {
            'title': 'Tic-Tac-Toe',
            'mode_label': 'Mode:',
            'mode_pvp': 'Player vs Player',
            'mode_pvc': 'Player vs AI',
            'difficulty_label': 'AI Difficulty:',
            'difficulty_easy': 'Easy',
            'difficulty_medium': 'Medium',
            'difficulty_hard': 'Hard',
            'new_game_button': 'New Game',
            'undo_button': 'Undo',
            'redo_button': 'Redo',
            'reset_scores_button': 'Reset Scores',
            'help_button': 'Help',
            'toggle_lang_text': 'فارسی',
            'score_x': 'X Wins: {score}',
            'score_o': 'O Wins: {score}',
            'score_draw': 'Draws: {score}',
            'status_turn': "{player}'s Turn",
            'status_win': '{player} Wins!',
            'status_draw': "It's a Draw!",
            'status_thinking': 'AI is thinking...',
            'confirm_new_game': 'Start a new game? Current game will be lost.',
            'confirm_reset_scores': 'Reset all scores to zero?',
            'confirm_title': 'Confirm',
            'help_title': 'How to Play',
            'help_text': (
                "Tic-Tac-Toe\n\n"
                "A classic two-player game played on a 3×3 grid.\n\n"
                "Goal:\n"
                "Be the first to get three of your marks (X or O) in a row – "
                "horizontally, vertically, or diagonally.\n\n"
                "How to Play:\n"
                "• Players take turns placing their mark in an empty cell.\n"
                "• Click on any empty cell to place your mark.\n"
                "• The game ends when one player gets three in a row or all cells are filled.\n\n"
                "Game Modes:\n"
                "• Player vs Player: Two human players take turns.\n"
                "• Player vs AI: Play against the computer.\n\n"
                "AI Difficulty:\n"
                "• Easy: AI makes random moves.\n"
                "• Medium: AI blocks obvious wins and takes winning moves.\n"
                "• Hard: AI uses optimal strategy (minimax algorithm).\n\n"
                "Features:\n"
                "• Undo/Redo: Take back or replay moves during the game.\n"
                "• Score Tracking: Wins and draws are tracked across games."
            ),
            'close_button': 'Close',
        },
        'fa': {
            'title': 'دوز',
            'mode_label': 'حالت:',
            'mode_pvp': 'بازیکن در مقابل بازیکن',
            'mode_pvc': 'بازیکن در مقابل هوش مصنوعی',
            'difficulty_label': 'سختی هوش مصنوعی:',
            'difficulty_easy': 'آسان',
            'difficulty_medium': 'متوسط',
            'difficulty_hard': 'سخت',
            'new_game_button': 'بازی جدید',
            'undo_button': 'بازگشت',
            'redo_button': 'جلو',
            'reset_scores_button': 'صفر کردن امتیازها',
            'help_button': 'راهنما',
            'toggle_lang_text': 'English',
            'score_x': 'برد X: {score}',
            'score_o': 'برد O: {score}',
            'score_draw': 'مساوی: {score}',
            'status_turn': 'نوبت {player}',
            'status_win': '{player} برنده شد!',
            'status_draw': 'مساوی!',
            'status_thinking': 'هوش مصنوعی در حال فکر کردن...',
            'confirm_new_game': 'بازی جدید شروع شود؟ بازی فعلی از دست می‌رود.',
            'confirm_reset_scores': 'همه امتیازها صفر شوند؟',
            'confirm_title': 'تأیید',
            'help_title': 'راهنمای بازی',
            'help_text': (
                "دوز (Tic-Tac-Toe)\n\n"
                "یک بازی کلاسیک دو نفره که روی یک شبکه ۳×۳ انجام می‌شود.\n\n"
                "هدف:\n"
                "اولین نفری باشید که سه علامت خود (X یا O) را در یک ردیف "
                "قرار می‌دهید – افقی، عمودی یا مورب.\n\n"
                "نحوه بازی:\n"
                "• بازیکنان به نوبت علامت خود را در یک خانه خالی قرار می‌دهند.\n"
                "• روی هر خانه خالی کلیک کنید تا علامت خود را بگذارید.\n"
                "• بازی زمانی تمام می‌شود که یک بازیکن سه علامت در یک ردیف "
                "داشته باشد یا همه خانه‌ها پر شوند.\n\n"
                "حالت‌های بازی:\n"
                "• بازیکن در مقابل بازیکن: دو بازیکن انسانی به نوبت بازی می‌کنند.\n"
                "• بازیکن در مقابل هوش مصنوعی: با کامپیوتر بازی کنید.\n\n"
                "سختی هوش مصنوعی:\n"
                "• آسان: هوش مصنوعی حرکات تصادفی انجام می‌دهد.\n"
                "• متوسط: هوش مصنوعی برد‌های واضح را مسدود و حرکات برنده را انجام می‌دهد.\n"
                "• سخت: هوش مصنوعی از استراتژی بهینه استفاده می‌کند.\n\n"
                "امکانات:\n"
                "• بازگشت/جلو: حرکات را در طول بازی برگردانید یا تکرار کنید.\n"
                "• ردیابی امتیاز: برد‌ها و مساوی‌ها در بازی‌ها ثبت می‌شوند."
            ),
            'close_button': 'بستن',
        }
    }

    PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

    def __init__(self, root: tk.Tk):
        logger.debug("Initializing TicTacToeGUI")
        self.root = root
        self.lang: str = 'en'
        self.root.title(self._('title'))   # initial localised title
        self.root.geometry("600x700")
        self.root.minsize(500, 600)
        self.root.configure(bg=self.BG_COLOR_MAIN)

        # Game State
        self.board: List[List[str]] = [[self.EMPTY] * 3 for _ in range(3)]
        self.current_player: str = self.PLAYER_X
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.winning_line: Optional[List[Tuple[int, int]]] = None
        
        # Move History for Undo/Redo
        self.move_history: List[Tuple[int, int]] = []
        self.redo_stack: List[Tuple[int, int]] = []
        
        # Game Mode & AI
        self.mode_var = tk.StringVar(value='pvc')   # 'pvp' or 'pvc'
        self.difficulty_var = tk.StringVar(value='medium')
        self.ai_thinking: bool = False
        self._ai_after_id: Optional[str] = None     # to cancel pending AI moves
        
        # Scores
        self.scores = {self.PLAYER_X: 0, self.PLAYER_O: 0, 'draw': 0}
        
        # UI State
        self.hover_cell: Optional[Tuple[int, int]] = None
        self.help_popup: Optional[tk.Toplevel] = None
        
        # Font
        self._base_font = self._choose_font()
        
        self.setup_ui()
        self.draw_board()
        logger.info("TicTacToeGUI initialized successfully")

    # ----------------------------------------------------------------------
    # i18n Helpers
    # ----------------------------------------------------------------------
    def _choose_font(self) -> str:
        """Return a font family that supports Arabic."""
        from tkinter import font as tkfont
        available = set(tkfont.families(self.root))
        preferred = ('DejaVu Sans', 'Noto Naskh Arabic', 'Arial', 'Segoe UI')
        for name in preferred:
            if name in available:
                return name
        return 'TkDefaultFont'

    def _shape_fa(self, text: str) -> str:
        """Shape Persian text for proper rendering. Requires arabic_reshaper and python-bidi."""
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except ImportError:
            if not getattr(self, '_bidi_warning_logged', False):
                logger.warning("arabic_reshaper/python-bidi not installed")
                self._bidi_warning_logged = True
            return text

    def _(self, key: str, **kwargs: object) -> str:
        """Get translated string for current language. Falls back to unshaped English if key missing."""
        try:
            text = self.TRANSLATIONS[self.lang][key]
        except KeyError:
            logger.warning(f"Missing translation key '{key}' for language '{self.lang}'")
            text = self.TRANSLATIONS['en'].get(key, key)
            if kwargs:
                text = text.format(**kwargs)
            return text   # no shaping for fallback

        if kwargs:
            text = text.format(**kwargs)
        if self.lang == 'fa':
            text = self._shape_fa(text)
        return text

    def _num(self, n: int) -> str:
        """Convert integer to string with appropriate digits."""
        if self.lang == 'fa':
            return str(n).translate(self.PERSIAN_DIGITS)
        return str(n)

    def toggle_language(self):
        """Switch between en and fa."""
        self.lang = 'fa' if self.lang == 'en' else 'en'
        logger.info(f"Language toggled to {self.lang}")
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None
        self.refresh_language()

    def refresh_language(self):
        """Update all UI texts after a language change."""
        self.root.title(self._('title'))
        self.mode_label.config(text=self._('mode_label'))
        self.mode_pvp_radio.config(text=self._('mode_pvp'))
        self.mode_pvc_radio.config(text=self._('mode_pvc'))
        self.difficulty_label.config(text=self._('difficulty_label'))
        self.diff_easy_radio.config(text=self._('difficulty_easy'))
        self.diff_medium_radio.config(text=self._('difficulty_medium'))
        self.diff_hard_radio.config(text=self._('difficulty_hard'))
        self.new_game_btn.config(text=self._('new_game_button'))
        self.undo_btn.config(text=self._('undo_button'))
        self.redo_btn.config(text=self._('redo_button'))
        self.reset_scores_btn.config(text=self._('reset_scores_button'))
        self.help_btn.config(text=self._('help_button'))
        
        if self.lang == 'en':
            persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
            self.lang_toggle_btn.config(text=self._shape_fa(persian_label))
        else:
            self.lang_toggle_btn.config(text=self._('toggle_lang_text'))
        
        self.update_status()
        self.update_scores()

    # ----------------------------------------------------------------------
    # UI Setup
    # ----------------------------------------------------------------------
    def setup_ui(self):
        """Create and arrange all UI widgets."""
        logger.debug("Setting up UI")
        
        # Top control frame
        control_frame = tk.Frame(self.root, bg=self.BG_COLOR_CONTROLS, height=120)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        button_font = (self._base_font, 10)
        label_font = (self._base_font, 10)
        
        def make_btn(parent, text, command):
            return tk.Button(
                parent, text=text, command=command,
                font=button_font,
                bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                activebackground=self.BUTTON_ACTIVE_BG,
                activeforeground=self.BUTTON_ACTIVE_FG,
                relief=tk.FLAT, padx=10, pady=4,
                highlightthickness=0, borderwidth=0
            )
        
        # Row 1: Mode selection
        row1 = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        row1.pack(fill=tk.X, pady=5)
        
        self.mode_label = tk.Label(row1, text=self._('mode_label'),
                                   bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                   font=label_font)
        self.mode_label.pack(side=tk.LEFT, padx=5)
        
        self.mode_pvp_radio = tk.Radiobutton(
            row1, text=self._('mode_pvp'), variable=self.mode_var, value='pvp',
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, selectcolor=self.BUTTON_BG,
            font=label_font, activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR, command=self.on_mode_change
        )
        self.mode_pvp_radio.pack(side=tk.LEFT, padx=5)
        
        self.mode_pvc_radio = tk.Radiobutton(
            row1, text=self._('mode_pvc'), variable=self.mode_var, value='pvc',
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, selectcolor=self.BUTTON_BG,
            font=label_font, activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR, command=self.on_mode_change
        )
        self.mode_pvc_radio.pack(side=tk.LEFT, padx=5)
        
        # Row 2: Difficulty selection
        row2 = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        row2.pack(fill=tk.X, pady=5)
        
        self.difficulty_label = tk.Label(row2, text=self._('difficulty_label'),
                                        bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                        font=label_font)
        self.difficulty_label.pack(side=tk.LEFT, padx=5)
        
        self.diff_easy_radio = tk.Radiobutton(
            row2, text=self._('difficulty_easy'), variable=self.difficulty_var, value='easy',
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, selectcolor=self.BUTTON_BG,
            font=label_font, activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR
        )
        self.diff_easy_radio.pack(side=tk.LEFT, padx=5)
        
        self.diff_medium_radio = tk.Radiobutton(
            row2, text=self._('difficulty_medium'), variable=self.difficulty_var, value='medium',
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, selectcolor=self.BUTTON_BG,
            font=label_font, activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR
        )
        self.diff_medium_radio.pack(side=tk.LEFT, padx=5)
        
        self.diff_hard_radio = tk.Radiobutton(
            row2, text=self._('difficulty_hard'), variable=self.difficulty_var, value='hard',
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, selectcolor=self.BUTTON_BG,
            font=label_font, activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR
        )
        self.diff_hard_radio.pack(side=tk.LEFT, padx=5)
        
        # Row 3: Action buttons
        row3 = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        row3.pack(fill=tk.X, pady=5)
        
        self.new_game_btn = make_btn(row3, self._('new_game_button'), self.new_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        self.undo_btn = make_btn(row3, self._('undo_button'), self.undo_move)
        self.undo_btn.pack(side=tk.LEFT, padx=5)
        
        self.redo_btn = make_btn(row3, self._('redo_button'), self.redo_move)
        self.redo_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_scores_btn = make_btn(row3, self._('reset_scores_button'), self.reset_scores)
        self.reset_scores_btn.pack(side=tk.LEFT, padx=5)
        
        self.help_btn = make_btn(row3, self._('help_button'), self.show_help)
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
        persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
        self.lang_toggle_btn = make_btn(row3, self._shape_fa(persian_label), self.toggle_language)
        self.lang_toggle_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            self.root, text="", bg=self.BG_COLOR_MAIN,
            fg=self.TEXT_COLOR, font=(self._base_font, 14, 'bold')
        )
        self.status_label.pack(pady=10)
        
        # Score frame
        score_frame = tk.Frame(self.root, bg=self.BG_COLOR_MAIN)
        score_frame.pack(pady=5)
        
        self.score_x_label = tk.Label(
            score_frame, text="", bg=self.BG_COLOR_MAIN,
            fg=self.X_COLOR, font=(self._base_font, 12, 'bold')
        )
        self.score_x_label.pack(side=tk.LEFT, padx=15)
        
        self.score_o_label = tk.Label(
            score_frame, text="", bg=self.BG_COLOR_MAIN,
            fg=self.O_COLOR, font=(self._base_font, 12, 'bold')
        )
        self.score_o_label.pack(side=tk.LEFT, padx=15)
        
        self.score_draw_label = tk.Label(
            score_frame, text="", bg=self.BG_COLOR_MAIN,
            fg=self.TEXT_COLOR, font=(self._base_font, 12, 'bold')
        )
        self.score_draw_label.pack(side=tk.LEFT, padx=15)
        
        # Canvas for game board
        self.canvas = tk.Canvas(self.root, bg=self.BG_COLOR_CANVAS, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        self.canvas.bind('<Leave>', self.on_canvas_leave)
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        
        self.root.update_idletasks()
        self.update_status()
        self.update_scores()
        self.update_button_states()
        logger.debug("UI setup complete")

    # ----------------------------------------------------------------------
    # Help Pop-up
    # ----------------------------------------------------------------------
    def show_help(self):
        """Open the help window."""
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
            justify=justify, wraplength=480,
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
            command=self._on_help_popup_close   # use the cleanup callback
        )
        close_btn.pack(pady=(0, 20))
        
        self.help_popup = popup
        popup.protocol("WM_DELETE_WINDOW", self._on_help_popup_close)

    def _on_help_popup_close(self):
        """Callback when help window is closed – destroys the popup and clears reference."""
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None

    # ----------------------------------------------------------------------
    # Game Logic
    # ----------------------------------------------------------------------
    def cancel_ai(self):
        """Cancel any pending AI move timer."""
        if self._ai_after_id:
            self.root.after_cancel(self._ai_after_id)
            self._ai_after_id = None

    def new_game(self):
        """Start a new game."""
        if not self.game_over and self.move_history:
            if not messagebox.askyesno(
                self._('confirm_title'), self._('confirm_new_game'), parent=self.root
            ):
                return
        self.cancel_ai()
        logger.info("Starting new game")
        self.board = [[self.EMPTY] * 3 for _ in range(3)]
        self.current_player = self.PLAYER_X
        self.game_over = False
        self.winner = None
        self.winning_line = None
        self.move_history = []
        self.redo_stack = []
        self.hover_cell = None
        self.ai_thinking = False
        
        self.update_status()
        self.update_button_states()
        self.draw_board()

    def on_mode_change(self):
        """Handle mode change."""
        logger.info(f"Mode changed to {self.mode_var.get()}")
        self.new_game()

    def make_move(self, row: int, col: int) -> bool:
        """Make a move at the specified position."""
        if self.game_over or self.board[row][col] != self.EMPTY or self.ai_thinking:
            return False
        
        logger.debug(f"Making move: {self.current_player} at ({row}, {col})")
        self.board[row][col] = self.current_player
        self.move_history.append((row, col))
        self.redo_stack.clear()  # new move invalidates redo history
        
        self.draw_board()
        
        if self.check_winner():
            self.game_over = True
            self.winner = self.current_player
            self.scores[self.current_player] += 1
            logger.info(f"Game over: {self.winner} wins")
            self.update_status()
            self.update_scores()
            self.update_button_states()
            self.draw_board()
            return True
        
        if self.is_board_full():
            self.game_over = True
            self.scores['draw'] += 1
            logger.info("Game over: Draw")
            self.update_status()
            self.update_scores()
            self.update_button_states()
            return True
        
        self.current_player = self.PLAYER_O if self.current_player == self.PLAYER_X else self.PLAYER_X
        self.update_status()
        self.update_button_states()
        
        # Trigger AI move if in AI mode and it's O's turn
        if self.mode_var.get() == 'pvc' and self.current_player == self.PLAYER_O:
            self.ai_thinking = True
            self.update_status()
            self.cancel_ai()
            self._ai_after_id = self.root.after(500, self.ai_move)
        
        return True

    def undo_move(self):
        """Undo the last move(s). Correctly adjusts scores and cancels pending AI."""
        if not self.move_history or self.ai_thinking:
            return

        self.cancel_ai()  # prevent any scheduled AI move

        # Remember if we are undoing a game-ending state
        was_game_over = self.game_over
        previous_winner = self.winner
        was_draw = was_game_over and previous_winner is None

        # In AI mode, undoes both player and AI if possible
        moves_to_undo = 2 if self.mode_var.get() == 'pvc' and len(self.move_history) >= 2 else 1

        for _ in range(moves_to_undo):
            if not self.move_history:
                break
            row, col = self.move_history.pop()
            # Store in redo stack in the order they will be redone (original order)
            # Currently we append as we pop, so order in redo_stack will be
            #   [ai_move, player_move] for two moves → player is on top (correct).
            self.redo_stack.append((row, col))
            self.board[row][col] = self.EMPTY
            # Toggle player back to the one who made the move we just undid
            self.current_player = self.PLAYER_O if self.current_player == self.PLAYER_X else self.PLAYER_X

        # After undoing, game is definitely not over
        self.game_over = False
        self.winner = None
        self.winning_line = None

        # Adjust scores if we undid a terminal move
        if was_game_over:
            if was_draw:
                self.scores['draw'] = max(0, self.scores['draw'] - 1)
            elif previous_winner is not None:
                self.scores[previous_winner] = max(0, self.scores[previous_winner] - 1)

        self.update_status()
        self.update_scores()
        self.update_button_states()
        self.draw_board()

    def _apply_single_redo(self) -> bool:
        """Redo a single move from the redo stack. Returns True if successful."""
        if not self.redo_stack:
            return False
        row, col = self.redo_stack.pop()
        self.board[row][col] = self.current_player
        self.move_history.append((row, col))
        if self.check_winner():
            self.game_over = True
            self.winner = self.current_player
            self.scores[self.current_player] += 1
        elif self.is_board_full():
            self.game_over = True
            self.scores['draw'] += 1
        else:
            self.current_player = self.PLAYER_O if self.current_player == self.PLAYER_X else self.PLAYER_X
        return True

    def redo_move(self):
        """Redo previously undone move(s). In AI mode, replays the full player+AI pair."""
        if not self.redo_stack or self.ai_thinking:
            return

        self.cancel_ai()

        # Redo first move (must be the player's move if we undid a pair)
        if not self._apply_single_redo():
            return

        # In AI mode, if the game is not over and there is still a redo entry, it must be the AI's move.
        # Replay it directly without triggering the AI engine.
        if (self.mode_var.get() == 'pvc' and not self.game_over 
                and self.redo_stack and not self.ai_thinking):
            if not self._apply_single_redo():
                return

        # After redoing, if we're back to normal play and it's AI's turn, trigger AI
        if (self.mode_var.get() == 'pvc' and not self.game_over 
                and self.current_player == self.PLAYER_O and not self.redo_stack):
            self.ai_thinking = True
            self._ai_after_id = self.root.after(500, self.ai_move)

        self.update_status()
        self.update_scores()
        self.update_button_states()
        self.draw_board()

    def reset_scores(self):
        """Reset score counters."""
        if not messagebox.askyesno(
            self._('confirm_title'), self._('confirm_reset_scores'), parent=self.root
        ):
            return
        self.scores = {self.PLAYER_X: 0, self.PLAYER_O: 0, 'draw': 0}
        self.update_scores()

    # ----------------- Drawing & Event Handling -----------------
    def draw_board(self):
        """Draw grid, symbols, winning line (if any), and hover effect."""
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 3 or h < 3:
            return
        cell_w, cell_h = w / 3, h / 3
        
        # Grid lines
        for i in range(1, 3):
            self.canvas.create_line(i * cell_w, 0, i * cell_w, h, fill=self.GRID_COLOR, width=self.LINE_WIDTH)
            self.canvas.create_line(0, i * cell_h, w, i * cell_h, fill=self.GRID_COLOR, width=self.LINE_WIDTH)
        
        # Symbols and hover highlight
        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                x0, y0 = c * cell_w, r * cell_h
                x1, y1 = x0 + cell_w, y0 + cell_h
                if val == self.PLAYER_X:
                    self.canvas.create_line(x0 + self.CELL_PADDING, y0 + self.CELL_PADDING,
                                             x1 - self.CELL_PADDING, y1 - self.CELL_PADDING,
                                             fill=self.X_COLOR, width=self.SYMBOL_WIDTH)
                    self.canvas.create_line(x0 + self.CELL_PADDING, y1 - self.CELL_PADDING,
                                             x1 - self.CELL_PADDING, y0 + self.CELL_PADDING,
                                             fill=self.X_COLOR, width=self.SYMBOL_WIDTH)
                elif val == self.PLAYER_O:
                    self.canvas.create_oval(x0 + self.CELL_PADDING, y0 + self.CELL_PADDING,
                                             x1 - self.CELL_PADDING, y1 - self.CELL_PADDING,
                                             outline=self.O_COLOR, width=self.SYMBOL_WIDTH)
                # Hover effect
                if not self.game_over and (r, c) == self.hover_cell and val == self.EMPTY:
                    self.canvas.create_rectangle(x0, y0, x1, y1,
                                                 fill='', outline=self.HOVER_COLOR, width=2, dash=(4,4))
        
        # Winner line highlight
        if self.winning_line:
            (r1, c1), (r2, c2), (r3, c3) = self.winning_line
            self.canvas.create_line(
                (c1 + 0.5) * cell_w, (r1 + 0.5) * cell_h,
                (c3 + 0.5) * cell_w, (r3 + 0.5) * cell_h,
                fill=self.WIN_LINE_COLOR, width=6)

    def on_canvas_click(self, event):
        """Handle click on board. Bounds‑checked to avoid IndexError."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 3 or h < 3:
            return
        cell_w, cell_h = w / 3, h / 3
        col, row = int(event.x // cell_w), int(event.y // cell_h)
        if not (0 <= row < 3 and 0 <= col < 3):
            return
        self.make_move(row, col)

    def on_canvas_motion(self, event):
        """Track mouse to change cursor and highlight hovered cell."""
        if self.game_over or self.ai_thinking:
            self.canvas.config(cursor="")
            if self.hover_cell is not None:
                self.hover_cell = None
                self.draw_board()
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 3 or h < 3:
            return
        cell_w, cell_h = w / 3, h / 3
        col, row = int(event.x // cell_w), int(event.y // cell_h)
        if not (0 <= row < 3 and 0 <= col < 3):
            self.canvas.config(cursor="")
            if self.hover_cell is not None:
                self.hover_cell = None
                self.draw_board()
            return
        new_hover = (row, col)
        if self.board[row][col] == self.EMPTY:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")
        if new_hover != self.hover_cell:
            self.hover_cell = new_hover
            self.draw_board()

    def on_canvas_leave(self, event):
        self.canvas.config(cursor="")
        if self.hover_cell is not None:
            self.hover_cell = None
            self.draw_board()

    def on_canvas_resize(self, event):
        self.draw_board()

    # ----------------- Game helpers -----------------
    def check_winner(self):
        """Check if current player won and record line."""
        b = self.board
        lines = [
            [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
        ]
        for line in lines:
            if all(b[r][c] == self.current_player for r, c in line):
                self.winning_line = line
                return True
        return False

    def is_board_full(self):
        return all(cell != self.EMPTY for row in self.board for cell in row)

    def ai_move(self):
        """Simple AI with three difficulty levels."""
        self._ai_after_id = None
        self.ai_thinking = False
        diff = self.difficulty_var.get()
        move = None
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == self.EMPTY]
        if not empty:
            return
        if diff == 'easy':
            move = random.choice(empty)
        elif diff == 'medium':
            # Win if possible
            for r, c in empty:
                self.board[r][c] = self.current_player
                if self.check_static(self.current_player):   # correctly use static check
                    self.board[r][c] = self.EMPTY
                    move = (r, c)
                    break
                self.board[r][c] = self.EMPTY
            if not move:
                # Block opponent
                opp = self.PLAYER_X
                for r, c in empty:
                    self.board[r][c] = opp
                    if self.check_static(opp):     # check if opponent would win
                        self.board[r][c] = self.EMPTY
                        move = (r, c)
                        break
                    self.board[r][c] = self.EMPTY
            if not move:
                move = random.choice(empty)
        else:  # hard: minimax
            move = self.minimax_move()
        if move:
            self.make_move(*move)

    def minimax_move(self):
        """Return best move using minimax."""
        best_score, best_move = -2, None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == self.EMPTY:
                    self.board[r][c] = self.PLAYER_O
                    score = self.minimax(False)
                    self.board[r][c] = self.EMPTY
                    if score > best_score:
                        best_score, best_move = score, (r, c)
        if best_move is None:
            empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == self.EMPTY]
            if empty:
                best_move = random.choice(empty)
        return best_move

    def minimax(self, is_max):
        if self.check_static(self.PLAYER_O):
            return 1
        if self.check_static(self.PLAYER_X):
            return -1
        if self.is_board_full():
            return 0
        if is_max:
            best = -2
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == self.EMPTY:
                        self.board[r][c] = self.PLAYER_O
                        best = max(best, self.minimax(False))
                        self.board[r][c] = self.EMPTY
            return best
        else:
            best = 2
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == self.EMPTY:
                        self.board[r][c] = self.PLAYER_X
                        best = min(best, self.minimax(True))
                        self.board[r][c] = self.EMPTY
            return best

    def check_static(self, player):
        """Check if the given player has a win (without modifying self.current_player)."""
        b = self.board
        lines = [
            [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
        ]
        return any(all(b[r][c] == player for r, c in L) for L in lines)

    # ----------------- UI update helpers -----------------
    def update_status(self):
        if self.ai_thinking:
            text = self._('status_thinking')
        elif self.game_over:
            if self.winner:
                text = self._('status_win', player=self.winner)
            else:
                text = self._('status_draw')
        else:
            text = self._('status_turn', player=self.current_player)
        self.status_label.config(text=text)

    def update_scores(self):
        self.score_x_label.config(text=self._('score_x', score=self._num(self.scores[self.PLAYER_X])))
        self.score_o_label.config(text=self._('score_o', score=self._num(self.scores[self.PLAYER_O])))
        self.score_draw_label.config(text=self._('score_draw', score=self._num(self.scores['draw'])))

    def update_button_states(self):
        state_undo = tk.NORMAL if self.move_history and not self.ai_thinking else tk.DISABLED
        state_redo = tk.NORMAL if self.redo_stack and not self.ai_thinking else tk.DISABLED
        self.undo_btn.config(state=state_undo)
        self.redo_btn.config(state=state_redo)


# ---------- Entry point ----------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TicTacToeGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nExiting gracefully.")
