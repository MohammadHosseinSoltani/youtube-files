"""
Multiplication Practice GUI – a simple arithmetic quiz with i18n (en/fa) and help.
Features:
- Randomly generates multiplication problems (factors 1‑MAX_FACTOR, default 12).
- User enters an answer and receives immediate feedback.
- Tracks correct, incorrect, and total attempts.
- Language toggle between English and Persian.
- Persian text is reshaped with arabic_reshaper / python-bidi for correct Tkinter rendering.
- Help pop‑up explains the purpose and usage.
- Consistent styling and clean shutdown.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font as tkfont
import random
from typing import Dict, Optional
import logging

# ------------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------------
LOG_LEVEL = logging.DEBUG
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class MultiplicationGUI:
    """
    A Tkinter‑based multiplication practice application.
    Generates random multiplication problems, lets the user answer,
    and tracks score. Supports English and Persian localisation.
    """

    # --- UI & Styling Constants ---
    BG_COLOR_MAIN = '#34495E'
    BG_COLOR_CONTROLS = '#2C3E50'
    TEXT_COLOR = 'white'
    BUTTON_BG = '#3D5060'
    BUTTON_ACTIVE_BG = '#4A6274'
    BUTTON_FG = 'white'
    BUTTON_ACTIVE_FG = 'white'
    ENTRY_BG = '#ECF0F1'
    ENTRY_FG = '#2C3E50'
    FEEDBACK_CORRECT = '#2ECC71'
    FEEDBACK_WRONG = '#E74C3C'

    # --- Game Constants ---
    MIN_FACTOR = 2          # minimum factor value (inclusive)
    MAX_FACTOR = 12         # maximum factor value (inclusive)

    # ----------------------------------------------------------------------
    # Internationalisation (i18n) Data
    # ----------------------------------------------------------------------
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        'en': {
            'title': 'Multiplication Practice',
            'factor_range_label': 'Range:',
            'question_pattern': '{a} × {b} = ?',
            'answer_label': 'Your answer:',
            'check_button': 'Check',
            'next_button': 'Next',
            'help_button': 'Help',
            'toggle_lang_text': 'فارسی',
            'help_title': 'How to Play',
            'help_text': (
                "Multiplication Practice\n\n"
                "A random multiplication problem is shown.\n"
                "Type your answer and press 'Check' or Enter.\n"
                "You'll see if you were right and your score.\n"
                "Press 'Next' for a new problem.\n\n"
                "The language can be switched at any time."
            ),
            'close_button': 'Close',
            'correct_feedback': '✓ Correct!',
            'wrong_feedback': '✗ Wrong.',
            'score_pattern': 'Score: {correct}/{total}',
            'empty_answer_warning': 'Please enter an answer.',
            'invalid_input_warning': 'Please enter a valid number.',
        },
        'fa': {
            'title': 'تمرین ضرب',
            'factor_range_label': 'بازه:',
            'question_pattern': '{a} × {b} = ؟',
            'answer_label': 'پاسخ شما:',
            'check_button': 'بررسی',
            'next_button': 'بعدی',
            'help_button': 'راهنما',
            'toggle_lang_text': 'English',
            'help_title': 'راهنما',
            'help_text': (
                "تمرین ضرب\n\n"
                "یک مسئله ضرب تصادفی نشان داده می‌شود.\n"
                "پاسخ خود را وارد کرده و 'بررسی' را بزنید.\n"
                "نتیجه و امتیاز شما نمایش داده می‌شود.\n"
                "با زدن 'بعدی' مسئله جدید دریافت کنید.\n\n"
                "زبان را می‌توانید در هر زمان تغییر دهید."
            ),
            'close_button': 'بستن',
            'correct_feedback': '✓ درست!',
            'wrong_feedback': '✗ نادرست.',
            'score_pattern': 'امتیاز: {correct}/{total}',
            'empty_answer_warning': 'لطفاً پاسخ را وارد کنید.',
            'invalid_input_warning': 'لطفاً یک عدد معتبر وارد کنید.',
        }
    }

    PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

    def __init__(self, root: tk.Tk):
        logger.debug("Initializing MultiplicationGUI")
        self.root = root
        self.lang: str = 'en'
        self.root.title(self._('title'))
        self.root.geometry("600x450")
        self.root.minsize(500, 380)

        # Quiz state
        self.current_a: int = 0
        self.current_b: int = 0
        self.correct: int = 0
        self.total: int = 0

        # Help pop‑up reference
        self.help_popup: Optional[tk.Toplevel] = None

        # Font that supports Arabic
        self._base_font = self._choose_font()

        self.setup_ui()
        self.new_problem()
        logger.info("MultiplicationGUI initialized successfully")

    # ----------------------------------------------------------------------
    # i18n Helpers
    # ----------------------------------------------------------------------
    def _choose_font(self) -> str:
        """Return a font family that is available and supports Arabic."""
        available = set(tkfont.families(self.root))
        preferred = ('DejaVu Sans', 'Noto Naskh Arabic', 'Arial')
        for name in preferred:
            if name in available:
                return name
        return 'TkDefaultFont'

    def _shape_fa(self, text: str) -> str:
        """Shape Persian text using arabic_reshaper and python-bidi."""
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except ImportError:
            if not getattr(self, '_bidi_warning_logged', False):
                logger.warning(
                    "arabic_reshaper / python-bidi not installed – "
                    "Persian text may appear unshaped or in wrong order."
                )
                self._bidi_warning_logged = True
            return text

    def _(self, key: str, **kwargs: object) -> str:
        """Return the translated string for the current language."""
        try:
            text = self.TRANSLATIONS[self.lang][key]
        except KeyError:
            text = self.TRANSLATIONS['en'].get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        if self.lang == 'fa':
            text = self._shape_fa(text)
        return text

    def _num(self, n: int) -> str:
        """Convert integer to string, with Persian digits if fa."""
        if self.lang == 'fa':
            return str(n).translate(self.PERSIAN_DIGITS)
        return str(n)

    def toggle_language(self):
        """Switch between 'en' and 'fa' and refresh UI."""
        self.lang = 'fa' if self.lang == 'en' else 'en'
        logger.info(f"Language toggled to {self.lang}")
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None
        self.refresh_language()

    def refresh_language(self):
        """Update all UI strings to the current language."""
        self.root.title(self._('title'))
        self.factor_range_lbl.config(text=self._('factor_range_label'))
        self.answer_label.config(text=self._('answer_label'))
        self.check_btn.config(text=self._('check_button'))
        self.next_btn.config(text=self._('next_button'))
        self.help_btn.config(text=self._('help_button'))
        if self.lang == 'en':
            persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
            self.lang_toggle_btn.config(text=self._shape_fa(persian_label))
        else:
            self.lang_toggle_btn.config(text=self._('toggle_lang_text'))
        self.update_question()
        self.update_score_label()
        self.update_feedback_label()

    # ----------------------------------------------------------------------
    # UI Setup
    # ----------------------------------------------------------------------
    def setup_ui(self):
        """Build the interface."""
        logger.debug("Setting up UI")

        # Control frame at top
        ctrl = tk.Frame(self.root, bg=self.BG_COLOR_CONTROLS, height=60)
        ctrl.pack(fill=tk.X)
        ctrl.pack_propagate(False)

        btn_font = (self._base_font, 10)

        def make_btn(parent, text, command):
            return tk.Button(
                parent, text=text, command=command,
                font=btn_font,
                bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                activebackground=self.BUTTON_ACTIVE_BG,
                activeforeground=self.BUTTON_ACTIVE_FG,
                relief=tk.FLAT, padx=8, pady=2,
                highlightthickness=0, borderwidth=0
            )

        # Factor range label (max factor)
        self.factor_range_lbl = tk.Label(ctrl, text=self._('factor_range_label'),
                                         bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                         font=(self._base_font, 12))
        self.factor_range_lbl.pack(side=tk.LEFT, padx=10)
        self.factor_var = tk.IntVar(value=self.MAX_FACTOR)
        self.factor_spinbox = ttk.Spinbox(
            ctrl, from_=2, to=20, textvariable=self.factor_var,
            width=3, font=(self._base_font, 12),
            command=self.on_factor_change, state='readonly'
        )
        self.factor_spinbox.pack(side=tk.LEFT, padx=5)

        # Help button
        self.help_btn = make_btn(ctrl, self._('help_button'), self.show_help)
        self.help_btn.pack(side=tk.LEFT, padx=10)

        # Language toggle
        persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
        self.lang_toggle_btn = make_btn(ctrl, self._shape_fa(persian_label),
                                        self.toggle_language)
        self.lang_toggle_btn.config(padx=12)
        self.lang_toggle_btn.pack(side=tk.LEFT, padx=10)

        # Score label (right side)
        self.score_label = tk.Label(ctrl, text="",
                                    bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                    font=(self._base_font, 14, 'bold'))
        self.score_label.pack(side=tk.RIGHT, padx=20)
        self.update_score_label()

        # Main area
        main = tk.Frame(self.root, bg=self.BG_COLOR_MAIN)
        main.pack(fill=tk.BOTH, expand=True)

        # Problem display (large font)
        self.question_label = tk.Label(main, text="",
                                       bg=self.BG_COLOR_MAIN, fg=self.TEXT_COLOR,
                                       font=(self._base_font, 32, 'bold'))
        self.question_label.pack(pady=(40, 20))

        # Answer entry
        answer_frame = tk.Frame(main, bg=self.BG_COLOR_MAIN)
        answer_frame.pack(pady=5)
        self.answer_label = tk.Label(answer_frame, text=self._('answer_label'),
                                     bg=self.BG_COLOR_MAIN, fg=self.TEXT_COLOR,
                                     font=(self._base_font, 14))
        self.answer_label.pack(side=tk.LEFT, padx=(0, 10))

        self.answer_entry = tk.Entry(answer_frame, width=8,
                                     font=(self._base_font, 20),
                                     bg=self.ENTRY_BG, fg=self.ENTRY_FG,
                                     justify='center', relief=tk.FLAT,
                                     highlightthickness=1, highlightcolor='#95A5A6')
        self.answer_entry.pack(side=tk.LEFT)
        self.answer_entry.bind('<Return>', lambda e: self.check_answer())
        self.answer_entry.focus_set()

        # Feedback label
        self.feedback_label = tk.Label(main, text="",
                                       bg=self.BG_COLOR_MAIN, fg=self.FEEDBACK_CORRECT,
                                       font=(self._base_font, 16, 'bold'))
        self.feedback_label.pack(pady=10)

        # Buttons frame
        btn_frame = tk.Frame(main, bg=self.BG_COLOR_MAIN)
        btn_frame.pack(pady=20)

        self.check_btn = make_btn(btn_frame, self._('check_button'), self.check_answer)
        self.check_btn.pack(side=tk.LEFT, padx=10)

        self.next_btn = make_btn(btn_frame, self._('next_button'), self.new_problem)
        self.next_btn.pack(side=tk.LEFT, padx=10)

        logger.debug("UI setup complete")

    # ----------------------------------------------------------------------
    # Help pop‑up
    # ----------------------------------------------------------------------
    def show_help(self):
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
            font=(self._base_font, 12),
            bg=self.BG_COLOR_MAIN, fg=self.TEXT_COLOR,
            justify=justify, wraplength=350, padx=20, pady=20
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
            command=popup.destroy
        )
        close_btn.pack(pady=(0, 20))

        self.help_popup = popup
        popup.protocol("WM_DELETE_WINDOW", self._on_help_popup_close)

    def _on_help_popup_close(self):
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None

    # ----------------------------------------------------------------------
    # Game logic
    # ----------------------------------------------------------------------
    def on_factor_change(self):
        """Reset score when max factor changes and generate new problem."""
        self.correct = 0
        self.total = 0
        self.update_score_label()
        self.new_problem()

    def new_problem(self):
        """Generate a new multiplication problem."""
        max_val = self.factor_var.get()
        self.current_a = random.randint(self.MIN_FACTOR, max_val)
        self.current_b = random.randint(self.MIN_FACTOR, max_val)
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")
        self.update_question()
        self.answer_entry.focus_set()
        logger.debug(f"New problem: {self.current_a} × {self.current_b}")

    def update_question(self):
        text = self._('question_pattern',
                      a=self._num(self.current_a),
                      b=self._num(self.current_b))
        self.question_label.config(text=text)

    def check_answer(self):
        """Validate the user's answer and update score/feedback."""
        answer_str = self.answer_entry.get().strip()
        if not answer_str:
            messagebox.showwarning(
                "Empty Answer", self._('empty_answer_warning'), parent=self.root
            )
            return

        # Convert Persian digits back if needed (handled by int conversion? no, we need to convert)
        if self.lang == 'fa':
            # map Persian digits to ASCII
            trans_back = {ord(c): str(i) for i, c in enumerate('۰۱۲۳۴۵۶۷۸۹')}
            answer_str = answer_str.translate(trans_back)

        try:
            answer = int(answer_str)
        except ValueError:
            messagebox.showwarning(
                "Invalid Input", self._('invalid_input_warning'), parent=self.root
            )
            return

        correct_answer = self.current_a * self.current_b
        self.total += 1
        if answer == correct_answer:
            self.correct += 1
            self.feedback_label.config(
                text=self._('correct_feedback'), fg=self.FEEDBACK_CORRECT
            )
            logger.info(f"Correct: {self.current_a}×{self.current_b}={answer}")
        else:
            self.feedback_label.config(
                text=self._('wrong_feedback') + f" ({correct_answer})",
                fg=self.FEEDBACK_WRONG
            )
            logger.info(f"Wrong: {self.current_a}×{self.current_b} answered {answer} (correct {correct_answer})")

        self.update_score_label()
        self.answer_entry.delete(0, tk.END)
        # Optionally auto‑generate new problem after check, or require "Next"
        # For a smoother flow, we could go to next problem. I'll keep it manual.
        self.answer_entry.focus_set()

    def update_score_label(self):
        text = self._('score_pattern',
                      correct=self._num(self.correct),
                      total=self._num(self.total))
        self.score_label.config(text=text)

    def update_feedback_label(self):
        # Reset feedback text when language changes; just clear if not showing feedback currently
        current = self.feedback_label.cget('text')
        if not current:
            self.feedback_label.config(text="")


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
if __name__ == '__main__':
    logger.info("Starting Multiplication Practice GUI")
    root = tk.Tk()
    app = MultiplicationGUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        root.destroy()
