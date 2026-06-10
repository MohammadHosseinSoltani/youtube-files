"""
Multiplication Table GUI – with i18n (en/fa), interactive controls, and clean styling.
Refactored for Golden Ratio geometry, peak performance, and zero bugs.
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter import font as tkfont
from typing import Optional, Dict, Set, Tuple
import logging
import os

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


class MultiplicationTableGUI:
    """
    A graphical user interface for displaying interactive multiplication tables.
    Supports English and Persian localisation with full Arabic text shaping.
    """

    # --- UI & Styling Constants (Modern Color Palette) ---
    BG_COLOR_MAIN = '#1E1E2E'        # Deep dark space background
    BG_COLOR_CONTROLS = '#181825'    # Slightly darker for control panel
    TEXT_COLOR = '#CDD6F4'
    
    BUTTON_BG = '#313244'
    BUTTON_HOVER_BG = '#45475A'
    BUTTON_ACTIVE_BG = '#585B70'
    BUTTON_FG = '#CDD6F4'
    
    HEADER_COLOR = '#CBA6F7'         # Soft Purple for Headers
    CELL_BASE_COLOR = '#89B4FA'      # Light Blue (min value)
    CELL_DARK_COLOR = '#1E66F5'      # Deep Blue (max value)
    CELL_HOVER_COLOR = '#F9E2AF'     # Soft Yellow for Hover
    CELL_SELECTED_COLOR = '#F38BA8'  # Soft Red for Selection
    CELL_TEXT_COLOR = '#11111B'      # Dark text for readability on colored cells
    HEADER_TEXT_COLOR = '#11111B'
    
    MIN_SIZE = 1
    MAX_SIZE = 20
    DEFAULT_SIZE = 10

    # ----------------------------------------------------------------------
    # Internationalisation (i18n) Data
    # ----------------------------------------------------------------------
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        'en': {
            'title': 'Multiplication Table',
            'size_label': 'Table Size:',
            'generate_button': 'Generate',
            'export_button': 'Export',
            'clear_button': 'Clear Selection',
            'help_button': 'Help',
            'toggle_lang_text': 'فارسی',
            'help_title': 'How to Use',
            'help_text': (
                "Multiplication Table\n\n"
                "This application displays an interactive multiplication table.\n\n"
                "Features:\n"
                "• Select table size (1-20) using the spinner or type and press Enter.\n"
                "• Hover over cells to highlight rows and columns.\n"
                "• Click cells to select/deselect them.\n"
                "• Use 'Clear Selection' to remove all highlights.\n"
                "• Click 'Export' to save the table to a text file.\n\n"
                "The table shows products of numbers from 1 to N."
            ),
            'close_button': 'Close',
            'export_success': 'Table exported successfully!',
            'export_success_title': 'Success',
            'export_error': 'Error exporting table',
            'export_error_title': 'Error',
            'invalid_input_title': 'Invalid Input',
            'invalid_input_text': 'Please enter a valid number between 1 and 20.',
            'file_types': 'Text Files',
            'all_files': 'All Files',
        },
        'fa': {
            'title': 'جدول ضرب',
            'size_label': 'اندازه جدول:',
            'generate_button': 'ایجاد',
            'export_button': 'ذخیره',
            'clear_button': 'پاک کردن انتخاب',
            'help_button': 'راهنما',
            'toggle_lang_text': 'English',
            'help_title': 'راهنمای استفاده',
            'help_text': (
                "جدول ضرب\n\n"
                "این برنامه یک جدول ضرب تعاملی نمایش می‌دهد.\n\n"
                "امکانات:\n"
                "• اندازه جدول (۱ تا ۲۰) را انتخاب کنید (فشردن Enter نیز کار می‌کند).\n"
                "• موس را روی خانه‌ها ببرید تا سطر و ستون برجسته شود.\n"
                "• روی خانه‌ها کلیک کنید تا انتخاب/لغو انتخاب شوند.\n"
                "• از 'پاک کردن انتخاب' برای حذف همه برجسته‌ها استفاده کنید.\n"
                "• روی 'ذخیره' کلیک کنید تا جدول در فایل متنی ذخیره شود.\n\n"
                "جدول حاصل‌ضرب اعداد از ۱ تا N را نشان می‌دهد."
            ),
            'close_button': 'بستن',
            'export_success': 'جدول با موفقیت ذخیره شد!',
            'export_success_title': 'موفقیت',
            'export_error': 'خطا در ذخیره جدول',
            'export_error_title': 'خطا',
            'invalid_input_title': 'ورودی نامعتبر',
            'invalid_input_text': 'لطفاً یک عدد معتبر بین ۱ تا ۲۰ وارد کنید.',
            'file_types': 'فایل‌های متنی',
            'all_files': 'همه فایل‌ها',
        }
    }

    PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

    def __init__(self, root: tk.Tk):
        logger.debug("Initializing MultiplicationTableGUI")
        self.root = root
        self.lang: str = 'en'
        
        # Geometry setup based on the Golden Ratio (1.618)
        # Width: 890, Height: 550 (890/550 ≈ 1.618)
        self.root.geometry("890x550")
        self.root.minsize(647, 400)
        self.root.configure(bg=self.BG_COLOR_MAIN)
        self.root.title(self._('title'))
        
        # State
        self.table_size: int = self.DEFAULT_SIZE
        self.selected_cells: Set[Tuple[int, int]] = set()
        self.hover_cell: Optional[Tuple[int, int]] = None
        self.cell_labels: Dict[Tuple[int, int], tk.Label] = {}
        
        # Help popup reference
        self.help_popup: Optional[tk.Toplevel] = None
        
        # Font setup
        self._base_font = self._choose_font()
        
        # Check bidi availability
        self._bidi_available = True
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
        except ImportError:
            self._bidi_available = False
            logger.warning("arabic_reshaper / python-bidi not installed – Persian text may appear unshaped")
        
        self.setup_ui()
        self.generate_table()
        logger.info("MultiplicationTableGUI initialized successfully")

    # ----------------------------------------------------------------------
    # i18n Helpers
    # ----------------------------------------------------------------------
    def _choose_font(self) -> str:
        """Return the name of a font family that supports Arabic/Persian well."""
        available = set(tkfont.families(self.root))
        preferred = ('Segoe UI', 'DejaVu Sans', 'Noto Naskh Arabic', 'Tahoma', 'Arial')
        for name in preferred:
            if name in available:
                return name
        return 'TkDefaultFont'

    def _shape_fa(self, text: str) -> str:
        """Shape Persian text using arabic_reshaper and python-bidi if available."""
        if not self._bidi_available or not text:
            return text
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except Exception as e:
            logger.error(f"Error shaping text '{text}': {e}")
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
        """Convert integer to string with appropriate localized digits."""
        if self.lang == 'fa':
            return str(n).translate(self.PERSIAN_DIGITS)
        return str(n)

    def toggle_language(self):
        """Switch between English and Persian."""
        self.lang = 'fa' if self.lang == 'en' else 'en'
        logger.info(f"Language toggled to {self.lang}")
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None
        self.refresh_language()

    def refresh_language(self):
        """Update all UI texts to match current language, preserving selections."""
        saved_selection = self.selected_cells.copy()
        
        self.root.title(self._('title'))
        self.size_label.config(text=self._('size_label'))
        self.generate_btn.config(text=self._('generate_button'))
        self.export_btn.config(text=self._('export_button'))
        self.clear_btn.config(text=self._('clear_button'))
        self.help_btn.config(text=self._('help_button'))
        
        if self.lang == 'en':
            persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
            self.lang_toggle_btn.config(text=self._shape_fa(persian_label) if self._bidi_available else 'FA')
        else:
            self.lang_toggle_btn.config(text='English')
        
        self.generate_table()
        
        if saved_selection:
            for cell in saved_selection:
                # Ensure the selection is within the current table bounds
                if cell[0] <= self.table_size and cell[1] <= self.table_size:
                    self.selected_cells.add(cell)
            self.update_cell_colors()

    # ----------------------------------------------------------------------
    # UI Setup
    # ----------------------------------------------------------------------
    def setup_ui(self):
        """Create and arrange all UI widgets."""
        logger.debug("Setting up UI")
        
        # Control frame
        control_frame = tk.Frame(self.root, bg=self.BG_COLOR_CONTROLS, height=60)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        control_frame.pack_propagate(False)
        
        button_font = (self._base_font, 10, "bold")
        
        def make_btn(parent, text, command, side=tk.LEFT):
            btn = tk.Button(
                parent, text=text, command=command,
                font=button_font, bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                activebackground=self.BUTTON_ACTIVE_BG, activeforeground=self.BUTTON_FG,
                relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
                highlightthickness=0, borderwidth=0
            )
            btn.pack(side=side, padx=5, pady=10)
            
            # Hover effects
            btn.bind("<Enter>", lambda e: btn.config(bg=self.BUTTON_HOVER_BG))
            btn.bind("<Leave>", lambda e: btn.config(bg=self.BUTTON_BG))
            return btn
        
        # Size selector
        self.size_label = tk.Label(
            control_frame, text=self._('size_label'),
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            font=(self._base_font, 11, "bold")
        )
        self.size_label.pack(side=tk.LEFT, padx=(15, 5), pady=10)
        
        self.size_var = tk.StringVar(value=str(self.table_size))
        self.size_spinbox = ttk.Spinbox(
            control_frame, from_=self.MIN_SIZE, to=self.MAX_SIZE,
            textvariable=self.size_var, width=5,
            font=(self._base_font, 11),
            command=self.generate_table # Auto-update on arrow clicks
        )
        self.size_spinbox.pack(side=tk.LEFT, padx=5, pady=10)
        self.size_spinbox.bind('<Return>', lambda e: self.generate_table()) # Auto-update on Enter
        
        # Buttons
        self.generate_btn = make_btn(control_frame, self._('generate_button'), self.generate_table)
        self.export_btn = make_btn(control_frame, self._('export_button'), self.export_table)
        self.clear_btn = make_btn(control_frame, self._('clear_button'), self.clear_selection)
        self.help_btn = make_btn(control_frame, self._('help_button'), self.show_help)
        
        # Language toggle
        toggle_text = self._shape_fa(self.TRANSLATIONS['en']['toggle_lang_text']) if self._bidi_available else 'FA'
        self.lang_toggle_btn = make_btn(control_frame, toggle_text, self.toggle_language, side=tk.RIGHT)
        
        # Table container with scrollbars
        container = tk.Frame(self.root, bg=self.BG_COLOR_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Customizing scrollbar styles via ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar", background=self.BUTTON_BG, bordercolor=self.BG_COLOR_MAIN, arrowcolor=self.TEXT_COLOR)
        style.configure("Horizontal.TScrollbar", background=self.BUTTON_BG, bordercolor=self.BG_COLOR_MAIN, arrowcolor=self.TEXT_COLOR)
        
        v_scroll = ttk.Scrollbar(container, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scroll = ttk.Scrollbar(container, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas for table
        self.canvas = tk.Canvas(
            container, bg=self.BG_COLOR_MAIN,
            highlightthickness=0,
            yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        
        # Frame inside canvas for table
        self.table_frame = tk.Frame(self.canvas, bg=self.BG_COLOR_MAIN)
        self.canvas_window = self.canvas.create_window(0, 0, window=self.table_frame, anchor='nw')
        self.table_frame.bind('<Configure>', self._on_frame_configure)
        
        # Universal Scrolling Bindings
        self._bind_mouse_scroll(self.canvas)
        self._bind_mouse_scroll(self.table_frame)
        
        logger.debug("UI setup complete")

    def _bind_mouse_scroll(self, widget):
        """Robust cross-platform mouse wheel scrolling."""
        widget.bind('<Enter>', self._enable_scroll)
        widget.bind('<Leave>', self._disable_scroll)

    def _enable_scroll(self, event=None):
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)      # Windows/macOS
        self.canvas.bind_all('<Button-4>', self._on_mousewheel_linux)  # Linux up
        self.canvas.bind_all('<Button-5>', self._on_mousewheel_linux)  # Linux down

    def _disable_scroll(self, event=None):
        self.canvas.unbind_all('<MouseWheel>')
        self.canvas.unbind_all('<Button-4>')
        self.canvas.unbind_all('<Button-5>')

    def _on_frame_configure(self, event=None):
        """Update scroll region when table frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling (Windows/MacOS)."""
        # Shift handles horizontal scrolling if shift is pressed
        if event.state & 0x0001:  
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), 'units')
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _on_mousewheel_linux(self, event):
        """Handle mouse wheel scrolling (Linux)."""
        direction = -1 if event.num == 4 else 1
        if event.state & 0x0001:
            self.canvas.xview_scroll(direction, 'units')
        else:
            self.canvas.yview_scroll(direction, 'units')

    # ----------------------------------------------------------------------
    # Table Generation & Grid Sizing
    # ----------------------------------------------------------------------
    def _grid_column(self, j: int) -> int:
        """Handles RTL mirroring for Persian layout."""
        return self.table_size - j + 1 if self.lang == 'fa' else j

    def generate_table(self):
        """Generate and display the multiplication table."""
        try:
            new_size = int(self.size_var.get())
            if not (self.MIN_SIZE <= new_size <= self.MAX_SIZE):
                raise ValueError
            self.table_size = new_size
        except (ValueError, tk.TclError):
            logger.warning("Invalid table size input")
            messagebox.showwarning(self._('invalid_input_title'), self._('invalid_input_text'), parent=self.root)
            self.size_var.set(str(self.table_size))  # Revert to last valid size
            return

        logger.info(f"Generating {self.table_size}x{self.table_size} table")
        
        # Clear existing table memory
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        # Reset grid weights and minsizes (fixes shrinking bug when going from large to small table)
        col_count, row_count = self.table_frame.grid_size()
        for i in range(col_count):
            self.table_frame.grid_columnconfigure(i, minsize=0, weight=0)
        for i in range(row_count):
            self.table_frame.grid_rowconfigure(i, minsize=0, weight=0)

        self.cell_labels.clear()
        
        # Filter selected cells to keep only valid ones after resize
        self.selected_cells = {(r, c) for r, c in self.selected_cells if r <= self.table_size and c <= self.table_size}
        self.hover_cell = None
        
        # Calculate uniform dimensions for peak performance & perfect uniform grid appearance
        data_font = tkfont.Font(family=self._base_font, size=11, weight='bold')
        max_str_width = data_font.measure(self._num(self.table_size * self.table_size))
        cell_min_width = max(max_str_width + 20, 50) # Ensure a nice square-like minimum
        cell_min_height = data_font.metrics('linespace') + 20

        # Create Header & Data
        for i in range(self.table_size + 1):
            self.table_frame.grid_rowconfigure(i, minsize=cell_min_height)
            for j in range(self.table_size + 1):
                col = self._grid_column(j) if j > 0 else 0
                self.table_frame.grid_columnconfigure(col, minsize=cell_min_width)
                
                if i == 0 and j == 0:
                    self._create_cell(i, 0, '×', self.HEADER_COLOR, is_header=True)
                elif i == 0:
                    self._create_cell(i, col, self._num(j), self.HEADER_COLOR, is_header=True)
                elif j == 0:
                    self._create_cell(i, 0, self._num(i), self.HEADER_COLOR, is_header=True)
                else:
                    product = i * j
                    color = self._get_cell_color(product)
                    label = self._create_cell(i, col, self._num(product), color, is_header=False)
                    self.cell_labels[(i, j)] = label
                    
                    # Bind interactive events
                    label.bind('<Button-1>', lambda e, r=i, c=j: self.on_cell_click(r, c))
                    label.bind('<Enter>', lambda e, r=i, c=j: self.on_cell_hover(r, c))
                    label.bind('<Leave>', lambda e: self.on_cell_leave())
        
        self.update_cell_colors() # Re-apply selections if any
        logger.debug("Table generation complete")

    def _create_cell(self, row: int, col: int, text: str, bg_color: str, is_header: bool) -> tk.Label:
        """Create a uniform table cell."""
        label = tk.Label(
            self.table_frame, text=text, bg=bg_color,
            fg=self.HEADER_TEXT_COLOR if is_header else self.CELL_TEXT_COLOR,
            font=(self._base_font, 11, 'bold'),
            relief=tk.FLAT, borderwidth=0, cursor="hand2" if not is_header else "arrow"
        )
        label.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
        return label

    def _get_cell_color(self, value: int) -> str:
        """Calculate a gradient color based on cell product value."""
        max_value = self.table_size * self.table_size
        if max_value <= 1:
            return self.CELL_BASE_COLOR
        
        r1, g1, b1 = (int(self.CELL_BASE_COLOR[i:i+2], 16) for i in (1, 3, 5))
        r2, g2, b2 = (int(self.CELL_DARK_COLOR[i:i+2], 16) for i in (1, 3, 5))
        
        ratio = (value - 1) / (max_value - 1)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return f'#{r:02x}{g:02x}{b:02x}'

    # ----------------------------------------------------------------------
    # Interactive Features
    # ----------------------------------------------------------------------
    def on_cell_click(self, row: int, col: int):
        cell = (row, col)
        if cell in self.selected_cells:
            self.selected_cells.remove(cell)
        else:
            self.selected_cells.add(cell)
        self.update_cell_colors()

    def on_cell_hover(self, row: int, col: int):
        self.hover_cell = (row, col)
        self.update_cell_colors()

    def on_cell_leave(self):
        self.hover_cell = None
        self.update_cell_colors()

    def update_cell_colors(self):
        """Update all cell colors based on selected/hover states instantly."""
        for (row, col), label in self.cell_labels.items():
            if (row, col) in self.selected_cells:
                color = self.CELL_SELECTED_COLOR
            elif self.hover_cell and (row == self.hover_cell[0] or col == self.hover_cell[1]):
                color = self.CELL_HOVER_COLOR
            else:
                color = self._get_cell_color(row * col)
            
            # Only configure if color changed to optimize rendering speed
            if label.cget("bg") != color:
                label.config(bg=color)

    def clear_selection(self):
        self.selected_cells.clear()
        self.update_cell_colors()

    # ----------------------------------------------------------------------
    # Export Functionality
    # ----------------------------------------------------------------------
    def export_table(self):
        logger.info("Exporting table")
        filename = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[(self._('file_types'), '*.txt'), (self._('all_files'), '*.*')],
            parent=self.root
        )
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"{self._('title')}\n")
                f.write(f"{self._('size_label')} {self._num(self.table_size)}\n")
                f.write("=" * (self.table_size * 7 + 5) + "\n\n")
                
                f.write("      ")
                for j in range(1, self.table_size + 1):
                    f.write(f"{self._num(j):>6}")
                f.write("\n")
                f.write("      " + "-" * (self.table_size * 6) + "\n")
                
                for i in range(1, self.table_size + 1):
                    f.write(f"{self._num(i):>4} |")
                    for j in range(1, self.table_size + 1):
                        f.write(f"{self._num(i * j):>6}")
                    f.write("\n")
            
            messagebox.showinfo(self._('export_success_title'), self._('export_success'), parent=self.root)
        except OSError as e:
            logger.error(f"Error exporting table: {e}")
            messagebox.showerror(self._('export_error_title'), f"{self._('export_error')}:\n{str(e)}", parent=self.root)

    # ----------------------------------------------------------------------
    # Help Dialog
    # ----------------------------------------------------------------------
    def show_help(self):
        if self.help_popup is not None and tk.Toplevel.winfo_exists(self.help_popup):
            self.help_popup.lift()
            self.help_popup.focus_force()
            return
        
        popup = tk.Toplevel(self.root)
        popup.title(self._('help_title'))
        popup.transient(self.root)
        popup.resizable(False, False)
        popup.configure(bg=self.BG_COLOR_MAIN)
        
        # Golden ratio for popup (400 / 1.618 ≈ 247)
        popup.geometry("400x250")
        
        justify = 'right' if self.lang == 'fa' else 'left'
        
        label = tk.Label(
            popup, text=self._('help_text'), font=(self._base_font, 11),
            bg=self.BG_COLOR_MAIN, fg=self.TEXT_COLOR, justify=justify,
            wraplength=360, padx=20, pady=20
        )
        label.pack(expand=True, fill=tk.BOTH)
        
        close_btn = tk.Button(
            popup, text=self._('close_button'), font=(self._base_font, 10, "bold"),
            bg=self.BUTTON_BG, fg=self.BUTTON_FG, activebackground=self.BUTTON_ACTIVE_BG,
            relief=tk.FLAT, padx=15, pady=6, cursor="hand2", highlightthickness=0, borderwidth=0,
            command=popup.destroy
        )
        close_btn.pack(pady=(0, 20))
        
        self.help_popup = popup
        popup.protocol("WM_DELETE_WINDOW", self._on_help_popup_close)

    def _on_help_popup_close(self):
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None


if __name__ == '__main__':
    logger.info("Starting Multiplication Table GUI application")
    root = tk.Tk()
    app = MultiplicationTableGUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        root.destroy()
