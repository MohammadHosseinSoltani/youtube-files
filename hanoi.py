"""
Tower of Hanoi GUI – Ultimate Enterprise Edition
Features:
- Golden Ratio (Phi) proportions for flawless visual aesthetics.
- Advanced UI/UX: Drop shadows, hover effects, neon/pastel palette, status bar.
- Performance: Asynchronous window-resize debouncing (no lag/flicker).
- Full internationalisation (i18n) support (English/Persian) with BiDi shaping.
- Pause/Resume, safe thread cancellation, and keyboard shortcuts.
- Comprehensive logging and docstrings.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font as tkfont
from typing import List, Tuple, Optional, Dict
import logging

# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------
LOG_LEVEL = logging.DEBUG  # Set to INFO to reduce terminal output
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class HanoiGUI:
    """
    A professional, optimized graphical user interface for the Tower of Hanoi puzzle.
    Features manual play and an animated auto-solver with pause/resume functionalities.
    """

    # --- Architectural & Aesthetic Constants ---
    PHI = 1.61803398875  # The Golden Ratio

    # --- Modern UI Color Palette ---
    BG_COLOR_MAIN = '#1E1E2E'        # Deep space background
    BG_COLOR_CONTROLS = '#181825'    # Darker control panel
    STATUS_BG = '#11111B'            # Darkest status bar
    TEXT_COLOR = '#CDD6F4'           # Soft white text
    
    BUTTON_BG = '#89B4FA'            # Soft Blue
    BUTTON_FG = '#11111B'            # Dark text for contrast
    BUTTON_ACTIVE_BG = '#B4BEFE'     # Lighter blue on hover/click
    BUTTON_DISABLED_BG = '#45475A'   # Grayed out state
    
    TOWER_BASE_COLOR = '#313244'
    TOWER_POLE_COLOR = '#45475A'
    SHADOW_COLOR = '#11111B'         # Drop shadow color
    
    DEFAULT_DISK_OUTLINE = '#181825'
    SELECTED_DISK_OUTLINE = '#F38BA8'
    SELECTED_TOWER_HIGHLIGHT = '#A6E3A1'
    WIN_GLOW_COLOR = '#F9E2AF'       # Golden glow for victory

    # Vibrant, harmonious disk colors
    DISK_COLORS = [
        '#F38BA8', '#FAB387', '#F9E2AF', '#A6E3A1',
        '#94E2D5', '#89DCEB', '#89B4FA', '#B4BEFE',
        '#CBA6F7', '#F5C2E7'
    ]

    # Dynamically split canvas into 3 equal parts
    TOWER_X_RATIOS = [1/6, 1/2, 5/6]

    # --- Game Logic Constants ---
    NUM_TOWERS = 3
    MIN_DISKS = 3
    MAX_DISKS = 10

    # Tower indices for code clarity
    FROM_PEG = 0
    AUX_PEG = 1
    TO_PEG = 2

    # ----------------------------------------------------------------------
    # Internationalisation (i18n) Dictionary
    # ----------------------------------------------------------------------
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        'en': {
            'disk_label': 'Disks:',
            'speed_label': 'Speed:',
            'reset_button': 'Reset',
            'solve_button': 'Auto Solve',
            'stop_button': 'Stop',
            'pause_button': 'Pause',
            'resume_button': 'Resume',
            'tower_0': 'A',
            'tower_1': 'B',
            'tower_2': 'C',
            'paused_text': '⏸ PAUSED',
            'moves_pattern': 'Moves: {moves} / Min: {min_moves}',
            'invalid_move_warning': 'Cannot place a larger disk on a smaller one.',
            'confirm_reset': 'Reset current game and start auto-solve?',
            'win_optimal': 'Optimal! Solved in {moves} moves!',
            'win_normal': 'Solved in {moves} moves.',
            'toggle_lang_text': 'فارسی',
            'help_button': 'Help',
            'help_title': 'How to Play',
            'help_text': (
                "Tower of Hanoi\n\n"
                "Goal: Move the entire stack to peg C.\n\n"
                "Rules:\n"
                "• Only one disk may be moved at a time.\n"
                "• Each move takes the top disk from one peg and places it onto another.\n"
                "• A larger disk may never be placed on top of a smaller disk.\n\n"
                "Minimum moves: 2^N − 1"
            ),
            'close_button': 'Close',
            'status_ready': 'Ready. Select a tower to move a disk.',
            'status_selected': 'Tower selected. Click target tower to place disk.',
            'status_solving': 'Auto-solving in progress...',
            'status_paused': 'Auto-solve paused.',
            'status_won': 'Puzzle solved successfully!'
        },
        'fa': {
            'disk_label': 'دیسک‌ها:',
            'speed_label': 'سرعت:',
            'reset_button': 'بازنشانی',
            'solve_button': 'حل خودکار',
            'stop_button': 'توقف',
            'pause_button': 'مکث',
            'resume_button': 'ادامه',
            'tower_0': 'آ',
            'tower_1': 'ب',
            'tower_2': 'پ',
            'paused_text': '⏸ مکث',
            'moves_pattern': 'حرکات: {moves} / حداقل: {min_moves}',
            'invalid_move_warning': 'قرار دادن دیسک بزرگتر روی دیسک کوچکتر مجاز نیست.',
            'confirm_reset': 'بازی فعلی بازنشانی و حل خودکار آغاز شود؟',
            'win_optimal': 'عالی! در {moves} حرکت حل شد!',
            'win_normal': 'در {moves} حرکت حل شد.',
            'toggle_lang_text': 'English',
            'help_button': 'راهنما',
            'help_title': 'راهنمای بازی',
            'help_text': (
                "برج هانوی\n\n"
                "هدف: انتقال کل پشته به میله پ.\n\n"
                "قوانین:\n"
                "• در هر حرکت فقط یک دیسک جابجا می‌شود.\n"
                "• دیسک بزرگتر هرگز روی دیسک کوچکتر قرار نمی‌گیرد.\n\n"
                "حداقل حرکات: ۲ به توان N منهای ۱"
            ),
            'close_button': 'بستن',
            'status_ready': 'آماده. برای جابجایی یک میله را انتخاب کنید.',
            'status_selected': 'میله انتخاب شد. روی میله مقصد کلیک کنید.',
            'status_solving': 'در حال حل خودکار...',
            'status_paused': 'حل خودکار متوقف شد.',
            'status_won': 'معما با موفقیت حل شد!'
        }
    }

    PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

    def __init__(self, root: tk.Tk):
        logger.debug("Initializing HanoiGUI")
        self.root = root
        self.lang: str = 'en'
        self._bidi_warning_logged = False
        
        # Ensure window sizes respect the Golden Ratio (Width / Height ≈ 1.618)
        self.root.title("Tower of Hanoi")
        self.root.geometry("971x600")
        self.root.minsize(809, 500) 
        self.root.configure(bg=self.BG_COLOR_MAIN)

        # Base Game State variables
        self.num_disks: int = self.MIN_DISKS
        self.towers: List[List[int]] = [[], [], []]
        self.selected_tower: Optional[int] = None
        self.moves: int = 0
        self.min_moves: int = 0
        self.is_won: bool = False

        # Auto-Solver State variables
        self.is_solving: bool = False
        self.is_paused: bool = False
        self.stop_solve_flag: bool = False
        self.move_sequence: List[Tuple[int, int]] = []
        self.solve_delay: int = 500
        self.solve_after_id: Optional[str] = None

        # Tracking for UI Debouncing and overriding states
        self._resize_timer: Optional[str] = None
        self._managed_buttons: List[tk.Button] = []
        self.help_popup: Optional[tk.Toplevel] = None
        self._base_font = self._choose_font()
        
        # Graceful Exit and Keyboard Shortcuts
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.bind("<Escape>", lambda e: self._on_closing())
        self.root.bind("r", lambda e: self.reset_game() if not self.is_solving else None)

        self.setup_ui()
        self.reset_game()
        logger.info("HanoiGUI initialized successfully.")

    # ----------------------------------------------------------------------
    # Core Utilities & I18N
    # ----------------------------------------------------------------------
    def _on_closing(self):
        """Safely clean up background tasks/loops before exiting application."""
        logger.info("Application shutdown requested. Cleaning up timers...")
        self.stop_solve_flag = True
        if self.solve_after_id:
            self.root.after_cancel(self.solve_after_id)
        if self._resize_timer:
            self.root.after_cancel(self._resize_timer)
        self.root.destroy()

    def _choose_font(self) -> str:
        """Selects the best available font supporting BiDi and modern look."""
        available = set(tkfont.families(self.root))
        for name in ('DejaVu Sans', 'Noto Naskh Arabic', 'Segoe UI', 'Arial'):
            if name in available:
                logger.debug(f"Selected font: {name}")
                return name
        return 'TkDefaultFont'

    def _shape_fa(self, text: str) -> str:
        """Applies BiDi shaping for Persian script text rendering in Tkinter."""
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except ImportError:
            if not self._bidi_warning_logged:
                logger.warning("arabic_reshaper or python-bidi not installed. RTL shaping will fail.")
                self._bidi_warning_logged = True
            return text

    def _(self, key: str, **kwargs: object) -> str:
        """Fetches and formats a translated string by language key."""
        text = self.TRANSLATIONS[self.lang].get(key, self.TRANSLATIONS['en'].get(key, key))
        if kwargs:
            text = text.format(**kwargs)
        if self.lang == 'fa':
            text = self._shape_fa(text)
        return text

    def _num(self, n: int) -> str:
        """Converts integer digits to Persian digits if 'fa' is active."""
        if self.lang == 'fa':
            return str(n).translate(self.PERSIAN_DIGITS)
        return str(n)

    # ----------------------------------------------------------------------
    # UI Setup
    # ----------------------------------------------------------------------
    def setup_ui(self):
        """Builds all UI components: Buttons, Sliders, Status Bar, and Canvas."""
        logger.debug("Setting up UI components.")

        # --- 1. Control Panel (Top) ---
        control_frame = tk.Frame(self.root, bg=self.BG_COLOR_CONTROLS, height=75)
        control_frame.pack(fill=tk.X, side=tk.TOP)
        control_frame.pack_propagate(False)

        button_font = (self._base_font, 10, "bold")
        
        def make_btn(parent, text, command):
            """Factory for creating consistently styled, hover-enabled buttons."""
            btn = tk.Button(
                parent, text=text, command=command, font=button_font,
                bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                activebackground=self.BUTTON_ACTIVE_BG, activeforeground=self.BUTTON_FG,
                disabledforeground='#6C7086', relief=tk.FLAT, padx=12, pady=4, 
                cursor="hand2", borderwidth=0
            )
            # Hover effect bindings
            def on_enter(e):
                if btn['state'] != 'disabled': btn.config(bg=self.BUTTON_ACTIVE_BG)
            def on_leave(e):
                if btn['state'] != 'disabled': btn.config(bg=self.BUTTON_BG)
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            self._managed_buttons.append(btn) # Track for disable-state overriding
            return btn
        
        # Disk Selector
        self.disk_label = tk.Label(control_frame, text=self._('disk_label'), bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, font=(self._base_font, 12, 'bold'))
        self.disk_label.pack(side=tk.LEFT, padx=(20, 5), pady=20)
        
        self.disk_var = tk.IntVar(value=self.num_disks)
        self.disk_spinbox = ttk.Spinbox(
            control_frame, from_=self.MIN_DISKS, to=self.MAX_DISKS,
            textvariable=self.disk_var, width=3, font=(self._base_font, 12, 'bold'),
            command=self.on_disk_change_manual, state='readonly'
        )
        self.disk_spinbox.pack(side=tk.LEFT, padx=5)

        # Primary Controls
        self.reset_btn = make_btn(control_frame, self._('reset_button'), self.reset_game)
        self.reset_btn.pack(side=tk.LEFT, padx=15)

        self.solve_btn = make_btn(control_frame, self._('solve_button'), self.auto_solve)
        self.solve_btn.pack(side=tk.LEFT, padx=5)

        self.pause_resume_btn = make_btn(control_frame, self._('pause_button'), self.pause_solve)
        self.stop_btn = make_btn(control_frame, self._('stop_button'), self.interrupt_solve)

        # Speed Slider
        self.speed_label = tk.Label(control_frame, text=self._('speed_label'), bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, font=(self._base_font, 12, 'bold'))
        self.speed_label.pack(side=tk.LEFT, padx=(20, 5))
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Horizontal.TScale", background=self.BG_COLOR_CONTROLS)
        self.speed_slider = ttk.Scale(control_frame, from_=50, to=1000, orient=tk.HORIZONTAL, command=self.set_solve_delay, length=120, style="Horizontal.TScale")
        self.speed_slider.set(550)
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        # Right-aligned utility buttons
        self.help_btn = make_btn(control_frame, self._('help_button'), self.show_help)
        self.help_btn.pack(side=tk.RIGHT, padx=20)

        persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
        self.lang_toggle_btn = make_btn(control_frame, self._shape_fa(persian_label), self.toggle_language)
        self.lang_toggle_btn.pack(side=tk.RIGHT, padx=5)

        self.move_label = tk.Label(control_frame, text="", bg=self.BG_COLOR_CONTROLS, fg=self.WIN_GLOW_COLOR, font=(self._base_font, 13, 'bold'))
        self.move_label.pack(side=tk.RIGHT, padx=20)

        # --- 2. Main Game Canvas ---
        self.canvas = tk.Canvas(self.root, bg=self.BG_COLOR_MAIN, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        # --- 3. Interactive Status Bar (Bottom) ---
        self.status_bar = tk.Label(self.root, text="", bg=self.STATUS_BG, fg="#A6ADC8", font=(self._base_font, 10), anchor="w", padx=15, pady=4)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _apply_button_states(self):
        """Forces custom coloring on buttons when disabled by tkinter."""
        for btn in self._managed_buttons:
            if btn['state'] == 'disabled':
                btn.config(bg=self.BUTTON_DISABLED_BG)
            else:
                btn.config(bg=self.BUTTON_BG)

    def set_status(self, key: str):
        """Updates the lower status bar with translated text."""
        self.status_bar.config(text=self._(key))
        logger.debug(f"Status changed to: {key}")

    # ----------------------------------------------------------------------
    # Event Handlers & User Interaction
    # ----------------------------------------------------------------------
    def on_canvas_resize(self, event):
        """Debounces resize events to prevent canvas flickering and CPU spikes."""
        if self._resize_timer:
            self.root.after_cancel(self._resize_timer)
        # Redraw 40ms after user STOPS dragging the window
        self._resize_timer = self.root.after(40, self.draw_towers)

    def toggle_language(self):
        """Switches between 'en' and 'fa' and reloads all UI strings."""
        self.lang = 'fa' if self.lang == 'en' else 'en'
        logger.info(f"Language toggled to {self.lang}")
        
        # Destroy help popup to ensure it re-translates when opened again
        if self.help_popup:
            self.help_popup.destroy()
            self.help_popup = None
            
        self.refresh_language()

    def refresh_language(self):
        """Updates text of all active UI elements to the current language."""
        self.disk_label.config(text=self._('disk_label'))
        self.speed_label.config(text=self._('speed_label'))
        self.reset_btn.config(text=self._('reset_button'))
        self.solve_btn.config(text=self._('solve_button'))
        self.help_btn.config(text=self._('help_button'))
        self.pause_resume_btn.config(text=self._('resume_button') if self.is_paused else self._('pause_button'))
        self.stop_btn.config(text=self._('stop_button'))

        if self.lang == 'en':
            self.lang_toggle_btn.config(text=self._shape_fa(self.TRANSLATIONS['en']['toggle_lang_text']))
        else:
            self.lang_toggle_btn.config(text=self._('toggle_lang_text'))

        self.update_move_label()
        
        # Restore current state logic to status bar
        if self.is_won: 
            self.set_status('status_won')
        elif self.is_solving and self.is_paused: 
            self.set_status('status_paused')
        elif self.is_solving: 
            self.set_status('status_solving')
        elif self.selected_tower is not None: 
            self.set_status('status_selected')
        else: 
            self.set_status('status_ready')
        
        self.draw_towers()

    def on_disk_change_manual(self):
        """Fires when the user manually changes the disk count."""
        new_count = self.disk_var.get()
        if not self.is_solving and new_count != self.num_disks:
            logger.info(f"Disk count changed to {new_count}. Resetting game.")
            self.reset_game()

    def set_solve_delay(self, value: str):
        """Inverts slider value so moving right increases speed (decreases delay)."""
        self.solve_delay = 1050 - int(float(value))
        logger.debug(f"Solve delay set to {self.solve_delay}ms")

    def on_canvas_click(self, event: tk.Event):
        """Handles manual puzzle play based on user clicks on the canvas."""
        if self.is_solving or self.is_won:
            logger.debug("Click ignored (game is solving or won).")
            return

        w = self.canvas.winfo_width()
        column_width = w / self.NUM_TOWERS
        
        # Calculate which of the 3 columns was clicked
        clicked_idx = min(max(0, int(event.x // column_width)), self.NUM_TOWERS - 1)
        logger.debug(f"User clicked tower index {clicked_idx}")

        if self.selected_tower is None:
            # First click: Pick up a disk
            if self.towers[clicked_idx]:
                self.selected_tower = clicked_idx
                self.set_status('status_selected')
        else:
            # Second click: Attempt to place a disk
            if self.selected_tower == clicked_idx:
                # Cancel selection
                self.selected_tower = None
                self.set_status('status_ready')
            else:
                self.move_disk(self.selected_tower, clicked_idx)
        
        self.draw_towers()

    def move_disk(self, from_idx: int, to_idx: int):
        """Executes a logical disk move and checks for game win state."""
        disk_to_move = self.towers[from_idx][-1]

        # Rule Check: Cannot place larger disk on smaller disk
        if self.towers[to_idx] and self.towers[to_idx][-1] < disk_to_move:
            logger.warning(f"Invalid move blocked: Disk {disk_to_move} onto {self.towers[to_idx][-1]}")
            messagebox.showwarning("Invalid Move", self._('invalid_move_warning'), parent=self.root)
        else:
            # Valid move execution
            self.towers[from_idx].pop()
            self.towers[to_idx].append(disk_to_move)
            self.moves += 1
            logger.info(f"Moved disk from {from_idx} to {to_idx}. Move count: {self.moves}")
            
            self.update_move_label()
            
            # Check win condition
            if len(self.towers[self.TO_PEG]) == self.num_disks:
                logger.info("Puzzle Solved by User!")
                self.selected_tower = None
                self.is_won = True
                self.set_status('status_won')
                self.draw_towers()
                self.show_win_message()
                return

        self.selected_tower = None
        self.set_status('status_ready')
        self.draw_towers()

    def show_win_message(self):
        """Displays a popup summarizing the win state."""
        msg = self._('win_optimal' if self.moves == self.min_moves else 'win_normal', moves=self._num(self.moves))
        # Use short delay to ensure canvas draws final disk before popup halts thread
        self.root.after(100, lambda: messagebox.showinfo("You Win!", msg, parent=self.root))

    # ----------------------------------------------------------------------
    # Auto-Solver Logistics
    # ----------------------------------------------------------------------
    def auto_solve(self):
        """Initiates the recursive auto-solve algorithm animation."""
        if self.is_solving: return
        if self.moves > 0 and not messagebox.askyesno("Confirm", self._('confirm_reset'), parent=self.root):
            return

        logger.info("Starting Auto-Solver...")
        self.reset_game()
        self.is_solving = True
        self.set_status('status_solving')
        self._set_ui_state(False)

        self.move_sequence = []
        self._generate_moves(self.num_disks, self.FROM_PEG, self.TO_PEG, self.AUX_PEG)
        logger.debug(f"Generated {len(self.move_sequence)} moves. Starting execution.")
        
        self.solve_after_id = self.root.after(300, self._execute_next_move)

    def pause_solve(self):
        """Suspends the auto-solve animation."""
        if self.is_solving and not self.is_paused:
            logger.info("Auto-Solve paused.")
            self.is_paused = True
            
            if self.solve_after_id:
                self.root.after_cancel(self.solve_after_id)
                self.solve_after_id = None
                
            self._set_ui_state(False, paused=True)
            self.set_status('status_paused')
            self.draw_towers()

    def resume_solve(self):
        """Resumes a paused auto-solve animation."""
        if self.is_solving and self.is_paused:
            logger.info("Auto-Solve resumed.")
            self.is_paused = False
            self._set_ui_state(False)
            self.set_status('status_solving')
            self.draw_towers()
            self._execute_next_move()

    def interrupt_solve(self):
        """Hard stops the auto-solver and clears remaining queue."""
        logger.info("Auto-Solve interrupted by user.")
        self.stop_solve_flag = True
        self.is_paused = False
        
        if self.solve_after_id:
            self.root.after_cancel(self.solve_after_id)
            self.solve_after_id = None
            
        self.move_sequence = []
        self.finish_auto_solve(interrupted=True)
        self.set_status('status_ready')

    def _generate_moves(self, n: int, src: int, tgt: int, aux: int):
        """Standard recursive algorithm to solve Tower of Hanoi."""
        if n == 0: return
        self._generate_moves(n - 1, src, aux, tgt)
        self.move_sequence.append((src, tgt))
        self._generate_moves(n - 1, aux, tgt, src)

    def _execute_next_move(self):
        """Pops the next move from the sequence and animates it via timer."""
        if self.stop_solve_flag or not self.move_sequence:
            self.finish_auto_solve(interrupted=self.stop_solve_flag)
            return
        if self.is_paused:
            return

        from_idx, to_idx = self.move_sequence.pop(0)
        self.towers[to_idx].append(self.towers[from_idx].pop())
        self.moves += 1
        
        self.update_move_label()
        self.draw_towers()

        if not self.is_paused and not self.stop_solve_flag:
            self.solve_after_id = self.root.after(self.solve_delay, self._execute_next_move)

    def finish_auto_solve(self, interrupted: bool = False):
        """Cleans up internal state after solver completion or interruption."""
        logger.info(f"Auto-solve finishing. Interrupted: {interrupted}")
        self.is_solving = False
        self.is_paused = False
        self.stop_solve_flag = False
        self.solve_after_id = None
        self._set_ui_state(True)
        
        if not interrupted and len(self.towers[self.TO_PEG]) == self.num_disks:
            self.is_won = True
            self.set_status('status_won')
            self.draw_towers()
            self.show_win_message()

    # ----------------------------------------------------------------------
    # Core Resets & Updates
    # ----------------------------------------------------------------------
    def reset_game(self):
        """Resets towers, move counters, and state flags back to start."""
        if self.is_solving:
            self.interrupt_solve()
            
        # Temporarily detach command to avoid circular event firing
        self.disk_spinbox.config(command='')
        
        self.num_disks = self.disk_var.get()
        self.min_moves = (2 ** self.num_disks) - 1
        logger.info(f"Resetting game. Disks: {self.num_disks}, Min Moves: {self.min_moves}")
        
        self.towers = [list(range(self.num_disks, 0, -1)), [], []]
        self.selected_tower = None
        self.moves = 0
        self.is_won = False
        
        self.update_move_label()
        self._set_ui_state(True)
        self.set_status('status_ready')
        self.disk_spinbox.config(command=self.on_disk_change_manual)
        
        self.draw_towers()

    def update_move_label(self):
        """Updates the top right label showing total vs minimum moves."""
        self.move_label.config(text=self._('moves_pattern', moves=self._num(self.moves), min_moves=self._num(self.min_moves)))

    def _set_ui_state(self, enabled: bool, paused: bool = False):
        """Toggles primary control visibility based on auto-solve state."""
        state = 'normal' if enabled else 'disabled'
        self.reset_btn.config(state=state)
        self.solve_btn.config(state=state)
        self.disk_spinbox.config(state=state)
        self.help_btn.config(state=state)

        if enabled:
            # Hide solve controls
            self.stop_btn.pack_forget()
            self.pause_resume_btn.pack_forget()
        else:
            # Show solve controls
            self.stop_btn.pack_forget()
            self.pause_resume_btn.pack_forget()
            
            if paused:
                self.pause_resume_btn.config(text=self._('resume_button'), command=self.resume_solve)
            else:
                self.pause_resume_btn.config(text=self._('pause_button'), command=self.pause_solve)
            
            # Repack carefully to maintain UI order
            self.pause_resume_btn.pack(side=tk.LEFT, padx=5, after=self.solve_btn)
            self.stop_btn.pack(side=tk.LEFT, padx=5, after=self.pause_resume_btn)
            
        self._apply_button_states()

    # ----------------------------------------------------------------------
    # Advanced UI Rendering (Golden Ratio & Effects)
    # ----------------------------------------------------------------------
    def draw_towers(self):
        """
        Draws the game board.
        Applies architectural Golden Ratio scaling to dynamically adapt to window sizes.
        Includes 3D shadow layering and conditional glow states.
        """
        self.canvas.delete('all')
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        if w <= 10 or h <= 10:
            logger.debug("Canvas dimensions too small for drawing, aborted.")
            return

        tower_x_positions = [w * ratio for ratio in self.TOWER_X_RATIOS]
        base_y = h * 0.85
        
        # --- Apply Golden Ratio (PHI) limits for aesthetic perfection ---
        section_width = w / self.NUM_TOWERS
        max_disk_width = section_width / 1.3  # Buffer between sections
        pole_height = max_disk_width * self.PHI
        
        # Scale back if window gets too short horizontally
        if pole_height > h * 0.65:
            pole_height = h * 0.65
            max_disk_width = pole_height / self.PHI
            
        base_width = max_disk_width * 1.15
        pole_width = max(6, base_width * 0.04)

        disk_height = min(28, pole_height / (self.num_disks + 1))
        min_disk_width = max_disk_width / (self.num_disks + 1) if self.num_disks > 0 else max_disk_width / 3

        # 1. Draw the Architecture (Bases and Poles with Shadows)
        for idx, x in enumerate(tower_x_positions):
            # Base Shadow & Base
            self.canvas.create_rectangle(x - base_width/2 + 3, base_y + 3, x + base_width/2 + 3, base_y + 18 + 3, fill=self.SHADOW_COLOR, outline='')
            self.canvas.create_rectangle(x - base_width/2, base_y, x + base_width/2, base_y + 18, fill=self.TOWER_BASE_COLOR, outline='', width=0, tags=f"base_{idx}")
            
            # Pole Shadow & Pole
            self.canvas.create_rectangle(x - pole_width/2 + 2, base_y - pole_height + 2, x + pole_width/2 + 2, base_y + 2, fill=self.SHADOW_COLOR, outline='')
            self.canvas.create_rectangle(x - pole_width/2, base_y - pole_height, x + pole_width/2, base_y, fill=self.TOWER_POLE_COLOR, outline='', width=0)

            # Highlight Selection Box
            if self.selected_tower == idx:
                self.canvas.create_rectangle(x - base_width/2 - 6, base_y - 6, x + base_width/2 + 6, base_y + 24, outline=self.SELECTED_TOWER_HIGHLIGHT, width=3, tags="highlight")

        # 2. Draw Disks (Calculated sizes and layers)
        for t_idx, tower in enumerate(self.towers):
            x = tower_x_positions[t_idx]
            for i, disk_size in enumerate(tower):
                
                # Dynamic width scaling
                d_width = min_disk_width + (max_disk_width - min_disk_width) * ((disk_size - 1) / max(1, self.num_disks - 1))
                y = base_y - (i + 1) * disk_height
                
                # Pick looping color
                color = self.DISK_COLORS[(disk_size - 1) % len(self.DISK_COLORS)]
                is_selected = (self.selected_tower == t_idx and i == len(tower) - 1)
                
                # Determine Border state
                outline_col = self.DEFAULT_DISK_OUTLINE
                outline_w = 1
                if self.is_won:
                    outline_col = self.WIN_GLOW_COLOR
                    outline_w = 3
                elif is_selected:
                    outline_col = self.SELECTED_DISK_OUTLINE
                    outline_w = 3

                # Drop Shadow for 3D stacking effect
                self.canvas.create_rectangle(x - d_width/2 + 4, y + 4, x + d_width/2 + 4, y + disk_height + 2, fill=self.SHADOW_COLOR, outline='')
                
                # Main Disk
                self.canvas.create_rectangle(x - d_width/2, y, x + d_width/2, y + disk_height - 2, fill=color, outline=outline_col, width=outline_w)
                
                # Disk Label text
                self.canvas.create_text(x, y + disk_height/2 - 2, text=str(disk_size), fill='#181825', font=(self._base_font, max(8, int(disk_height * 0.45)), 'bold'))

        # 3. Draw Tower Identifier Labels (A, B, C)
        for i, x in enumerate(tower_x_positions):
            self.canvas.create_text(x, base_y + 40, text=self._(f'tower_{i}'), fill=self.TEXT_COLOR, font=(self._base_font, 18, 'bold'))

        # 4. Draw Pause State Overlay Frame
        if self.is_solving and self.is_paused:
            pause_text = self._('paused_text')
            
            # Semi-transparent screen overlay
            self.canvas.create_rectangle(0, 0, w, h, fill=self.BG_COLOR_MAIN, stipple='gray50', outline='')
            self.canvas.create_text(w/2, h/3, text=pause_text, fill=self.WIN_GLOW_COLOR, font=(self._base_font, 36, 'bold'))

    # ----------------------------------------------------------------------
    # Help Modal Pop-up
    # ----------------------------------------------------------------------
    def show_help(self):
        """Summons an instructional top-level modal."""
        if self.help_popup and tk.Toplevel.winfo_exists(self.help_popup):
            # Bring to front if already open
            self.help_popup.lift()
            self.help_popup.focus_force()
            return

        logger.info("Opening Help Dialog.")
        self.help_popup = tk.Toplevel(self.root)
        self.help_popup.title(self._('help_title'))
        self.help_popup.transient(self.root)
        self.help_popup.resizable(False, False)
        self.help_popup.configure(bg=self.BG_COLOR_CONTROLS)
        
        # Geometrically center the pop-up relative to the parent application
        hw, hh = 450, 300
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (hw // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (hh // 2)
        self.help_popup.geometry(f"{hw}x{hh}+{x}+{y}")

        # Text Justification depending on language script (RTL / LTR)
        justify = 'right' if self.lang == 'fa' else 'left'
        
        tk.Label(
            self.help_popup, text=self._('help_text'), font=(self._base_font, 11),
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR, justify=justify, wraplength=400, padx=20, pady=25
        ).pack()

        tk.Button(
            self.help_popup, text=self._('close_button'), font=(self._base_font, 10, "bold"),
            bg=self.BUTTON_BG, fg=self.BUTTON_FG, activebackground=self.BUTTON_ACTIVE_BG,
            relief=tk.FLAT, padx=16, pady=6, cursor="hand2", borderwidth=0, command=self.help_popup.destroy
        ).pack(pady=(0, 20))


if __name__ == '__main__':
    logger.info("--- Booting Tower of Hanoi Application ---")
    root = tk.Tk()
    app = HanoiGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted via Keyboard (Ctrl+C). Shutting down safely.")
        app._on_closing()
