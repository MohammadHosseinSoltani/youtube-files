"""
Linear Sort GUI – visualization of various sorting algorithms.
Features animated auto-sort with adjustable speed and pause/resume.
Supports multiple sorting algorithms: Bubble Sort, Selection Sort,
Insertion Sort, Quick Sort, Merge Sort.

Now includes configurable data generation profiles:
  - Distinct Positive Ints (default)
  - Duplicate Positive Ints
  - Distinct Pos/Neg Ints
  - Duplicate Pos/Neg Ints
  - Random Floats [0, 1]
  - Random Floats [-1, 1]
  - Nearly Sorted
  - Reverse Sorted
  - Custom… (reveals type, min, max, unique controls)

Enhancements:
  - Two-color visualization: yellow for comparisons, red for swaps/accesses.
  - Final green sweep animation on successful sort.
  - Detailed debug logging for every step of every algorithm.
  - Fixed vanishing/duplication visual glitch in Insertion & Merge Sort
    by performing data movement before highlighting.
  - Merge Sort and Insertion Sort properly show compare/swap colors.
  - All existing features preserved (data profiles, i18n, negative/float support).
  - **Clean Mode** toggle: eliminates visible duplicates in Insertion and Merge Sort,
    while still showing comparison highlights.
  - Fixed unnecessary delays in Merge Sort splitting (both modes).
"""

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font as tkfont
from typing import List, Optional, Dict
import random
import logging

# ------------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------------
LOG_LEVEL = logging.DEBUG  # Debug level for detailed logs
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class LinearSortGUI:
    """
    A graphical user interface for visualizing sorting algorithms using Tkinter.
    Features animated auto-sort with adjustable speed, pause/resume,
    configurable data generation profiles, and i18n support.
    """

    # --- UI & Styling Constants ---
    BG_COLOR_MAIN = '#34495E'
    BG_COLOR_CONTROLS = '#2C3E50'
    TEXT_COLOR = 'white'
    BAR_COLOR_DEFAULT = '#3498DB'
    BAR_COLOR_COMPARING = '#F1C40F'   # Yellow for comparisons
    BAR_COLOR_SWAPPING = '#E74C3C'    # Red for swaps/accesses
    BAR_COLOR_SORTED = '#2ECC71'
    BAR_COLOR_PIVOT = '#F39C12'
    BAR_OUTLINE = '#2C3E50'
    ZERO_LINE_COLOR = '#7F8C8D'

    BUTTON_BG = '#3D5060'
    BUTTON_ACTIVE_BG = '#4A6274'
    BUTTON_FG = 'white'
    BUTTON_ACTIVE_FG = 'white'

    # --- Game Logic Constants ---
    MIN_ELEMENTS = 3
    MAX_ELEMENTS = 50
    DEFAULT_ELEMENTS = 15

    # Algorithm internal keys
    ALGO_KEYS = ['bubble', 'selection', 'insertion', 'quick', 'merge']
    # Data profile internal keys
    DATA_KEYS = [
        'distinct_positive_ints',
        'duplicate_positive_ints',
        'distinct_pos_neg_ints',
        'duplicate_pos_neg_ints',
        'random_floats_0_1',
        'random_floats_neg1_1',
        'nearly_sorted',
        'reverse_sorted',
        'custom'
    ]

    # ----------------------------------------------------------------------
    # Internationalisation (i18n) Data
    # ----------------------------------------------------------------------
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        'en': {
            # labels
            'elements_label': 'Elements:',
            'algorithm_label': 'Algorithm:',
            'data_label': 'Data:',
            'speed_label': 'Speed:',
            'type_label': 'Type:',
            'min_label': 'Min:',
            'max_label': 'Max:',
            'unique_check': 'Unique values',
            'clean_mode_btn': 'Clean Mode: OFF',
            'clean_mode_btn_on': 'Clean Mode: ON',
            'clean_mode_btn_off': 'Clean Mode: OFF',
            # radio buttons
            'integer_radio': 'Integers',
            'float_radio': 'Floats',
            # buttons
            'shuffle_button': 'Shuffle',
            'sort_button': 'Auto Sort',
            'stop_button': 'Stop',
            'pause_button': 'Pause',
            'resume_button': 'Resume',
            'toggle_lang_text': 'فارسی',
            'help_button': 'Help',
            'close_button': 'Close',
            # paused overlay
            'paused_text': '⏸ PAUSED',
            # stats template
            'stats_template': '{algo}  |  Comparisons: {comparisons}  |  Swaps: {swaps}',
            # algorithm names
            'algo_bubble': 'Bubble Sort',
            'algo_selection': 'Selection Sort',
            'algo_insertion': 'Insertion Sort',
            'algo_quick': 'Quick Sort',
            'algo_merge': 'Merge Sort',
            # data profile names
            'data_distinct_positive_ints': 'Distinct Positive Ints',
            'data_duplicate_positive_ints': 'Duplicate Positive Ints',
            'data_distinct_pos_neg_ints': 'Distinct Pos/Neg Ints',
            'data_duplicate_pos_neg_ints': 'Duplicate Pos/Neg Ints',
            'data_random_floats_0_1': 'Random Floats [0, 1]',
            'data_random_floats_neg1_1': 'Random Floats [-1, 1]',
            'data_nearly_sorted': 'Nearly Sorted',
            'data_reverse_sorted': 'Reverse Sorted',
            'data_custom': 'Custom…',
            # dialogs
            'confirm_reset': 'Reset and start auto-sort?',
            'sort_complete_title': 'Sorting Complete!',
            'sort_complete_msg': 'Array sorted using {algo}\nComparisons: {comparisons}\nSwaps: {swaps}',
            'unique_impossible': 'Range [{low}, {high}] only has {range_size} values, but {n} elements requested.\nFalling back to duplicates.',
            'float_unique_warning': 'Uniqueness cannot be guaranteed for floats; allowing duplicates.',
            # help title template
            'help_title_template': 'How {algo} Works',
            # per‑algorithm help texts (unchanged, included for completeness)
            'help_bubble': (
                "Bubble Sort\n\n"
                "Concept:\n"
                "Repeatedly steps through the array, compares adjacent items, and swaps them if they are in the wrong order. After each full pass, the largest unsorted element \"bubbles\" up to its correct final position at the right end. The process continues until no more swaps are needed.\n\n"
                "In this visualizer:\n"
                "• Two adjacent bars being compared turn yellow.\n"
                "• If a swap occurs, the bars exchange places and are highlighted red.\n"
                "• After each pass, the element that has reached its correct spot turns green.\n"
                "• The sorted part grows from right to left.\n\n"
                "Comparisons count each time two bars are compared.\n"
                "Swaps count each time two bars are exchanged."
            ),
            'help_selection': (
                "Selection Sort\n\n"
                "Concept:\n"
                "Divides the array into a sorted segment (left) and an unsorted segment (right). In each step, it finds the smallest element in the unsorted part and swaps it with the leftmost unsorted element, growing the sorted portion by one.\n\n"
                "In this visualizer:\n"
                "• The current minimum candidate and the bar being inspected are shown in yellow.\n"
                "• Once the smallest element is found, it is swapped with the first unsorted bar, which then turns green after a red swap highlight.\n"
                "• The sorted section builds from the left.\n\n"
                "Comparisons count each time a bar is compared against the current minimum.\n"
                "Swaps count each time two bars are exchanged."
            ),
            'help_insertion': (
                "Insertion Sort\n\n"
                "Concept:\n"
                "Builds the sorted array one element at a time. It takes the next unsorted element (key) and inserts it into the correct position within the already sorted prefix, shifting larger elements one position to the right as needed.\n\n"
                "In this visualizer:\n"
                "• The bar being inserted (key) is compared with sorted bars from right to left; the two compared bars appear yellow.\n"
                "• When a larger sorted bar is found, it shifts right with a red highlight.\n"
                "• Once the correct spot is found, the key is placed there (with a swap highlight) and the prefix grows.\n\n"
                "Comparisons count each time the key is compared to a sorted bar.\n"
                "Swaps count each shift and the final placement."
            ),
            'help_quick': (
                "Quick Sort\n\n"
                "Concept:\n"
                "A divide-and-conquer algorithm. It picks a pivot element and partitions the array so that all elements less than the pivot are moved to its left, and all greater elements to its right. The process is then applied recursively to the left and right sub-arrays.\n\n"
                "In this visualizer:\n"
                "• The pivot is highlighted in gold.\n"
                "• During partitioning, each element being compared to the pivot appears yellow.\n"
                "• Swaps occur as elements are rearranged around the pivot; they flash red.\n"
                "• When partitioning is complete, the pivot is placed in its final sorted position (with a red highlight) and turns green.\n"
                "• The algorithm then recurses on the left and right partitions.\n\n"
                "Comparisons count each time an element is compared to the pivot.\n"
                "Swaps count each time two elements are exchanged."
            ),
            'help_merge': (
                "Merge Sort\n\n"
                "Concept:\n"
                "A recursive divide-and-conquer algorithm. It splits the array into halves until each sub-array contains a single element (already sorted). Then it repeatedly merges these sub-arrays back together, comparing the smallest remaining elements of each and placing the smaller one into the merged result.\n\n"
                "In this visualizer:\n"
                "• The splitting phase is not shown (it happens instantly).\n"
                "• During merging, the two elements currently being compared are highlighted in yellow.\n"
                "• The element being placed into the merged array appears red briefly.\n"
                "• Once a merge is complete, all bars in that merged range turn green.\n\n"
                "Comparisons count each time two elements from different sub-arrays are compared.\n"
                "Swaps count each element placement during the merge."
            ),
        },
        'fa': {
            'elements_label': ':عناصر',
            'algorithm_label': ':الگوریتم',
            'data_label': ':داده‌ها',
            'speed_label': ':سرعت',
            'type_label': ':نوع',
            'min_label': ':حداقل',
            'max_label': ':حداکثر',
            'unique_check': 'مقادیر یکتا',
            'clean_mode_btn': 'حالت تمیز: خاموش',
            'clean_mode_btn_on': 'حالت تمیز: روشن',
            'clean_mode_btn_off': 'حالت تمیز: خاموش',
            'integer_radio': 'اعداد صحیح',
            'float_radio': 'اعشاری',
            'shuffle_button': 'درهم‌ریزی',
            'sort_button': 'مرتب‌سازی خودکار',
            'stop_button': 'توقف',
            'pause_button': 'مکث',
            'resume_button': 'ادامه',
            'toggle_lang_text': 'English',
            'help_button': 'راهنما',
            'close_button': 'بستن',
            'paused_text': '⏸ مکث',
            'stats_template': '{algo}  |  مقایسه‌ها: {comparisons}  |  جابجایی‌ها: {swaps}',
            'algo_bubble': 'مرتب‌سازی حبابی',
            'algo_selection': 'مرتب‌سازی انتخابی',
            'algo_insertion': 'مرتب‌سازی درجی',
            'algo_quick': 'مرتب‌سازی سریع',
            'algo_merge': 'مرتب‌سازی ادغامی',
            'data_distinct_positive_ints': 'اعداد صحیح مثبت یکتا',
            'data_duplicate_positive_ints': 'اعداد صحیح مثبت تکراری',
            'data_distinct_pos_neg_ints': 'اعداد صحیح مثبت/منفی یکتا',
            'data_duplicate_pos_neg_ints': 'اعداد صحیح مثبت/منفی تکراری',
            'data_random_floats_0_1': 'اعداد اعشاری [0, 1]',
            'data_random_floats_neg1_1': 'اعداد اعشاری [-1, 1]',
            'data_nearly_sorted': 'تقریباً مرتب',
            'data_reverse_sorted': 'مرتب معکوس',
            'data_custom': 'سفارشی…',
            'confirm_reset': 'بازی فعلی ریست شده و مرتب‌سازی شروع شود؟',
            'sort_complete_title': 'مرتب‌سازی کامل شد!',
            'sort_complete_msg': 'آرایه با الگوریتم {algo} مرتب شد\nمقایسه‌ها: {comparisons}\nجابجایی‌ها: {swaps}',
            'unique_impossible': 'بازه [{low}, {high}] تنها {range_size} مقدار دارد، اما {n} عنصر درخواست شده.\nاز مقادیر تکراری استفاده می‌شود.',
            'float_unique_warning': 'امکان یکتاسازی برای اعداد اعشاری تضمین نمی‌شود؛ مقادیر تکراری مجاز است.',
            'help_title_template': 'نحوه کار {algo}',
            'help_bubble': (
                "مرتب‌سازی حبابی\n\n"
                "مفهوم:\n"
                "الگوریتم به‌طور تکراری از ابتدای آرایه عبور می‌کند و هر دو عنصر مجاور را مقایسه می‌کند. اگر ترتیب آن‌ها نادرست باشد (عنصر چپ بزرگتر از راست)، جابجا می‌شوند. پس از هر گذر کامل، بزرگترین عنصر باقی‌مانده به انتهای بخش مرتب‌نشده حرکت می‌کند و جایگاه نهایی خود را پیدا می‌کند. این روند تا زمانی ادامه می‌یابد که دیگر نیازی به جابجایی نباشد.\n\n"
                "در این برنامه:\n"
                "• دو میله مجاور که مقایسه می‌شوند، زرد رنگ می‌شوند.\n"
                "• در صورت جابجایی، میله‌ها موقعیت خود را عوض کرده و قرمز می‌شوند.\n"
                "• در پایان هر گذر، عنصری که به جایگاه صحیح خود رسیده سبز می‌شود.\n"
                "• بخش مرتب از راست به چپ رشد می‌کند.\n\n"
                "شمارش مقایسه‌ها: هر بار که دو میله مقایسه می‌شوند.\n"
                "شمارش جابجایی‌ها: هر بار که دو میله جابجا می‌شوند."
            ),
            'help_selection': (
                "مرتب‌سازی انتخابی\n\n"
                "مفهوم:\n"
                "آرایه را به دو بخش مرتب (چپ) و نامرتب (راست) تقسیم می‌کند. در هر مرحله، کوچکترین عنصر در بخش نامرتب را پیدا کرده و آن را با اولین عنصر نامرتب جابجا می‌کند. به این ترتیب بخش مرتب یک واحد گسترش می‌یابد.\n\n"
                "در این برنامه:\n"
                "• کاندیدای کمینه فعلی و میله در حال بررسی به رنگ زرد نمایش داده می‌شوند.\n"
                "• پس از یافتن کوچکترین عنصر، با اولین میله نامرتب جابجا شده (با قرمز) و آن میله سبز می‌شود.\n"
                "• بخش مرتب از سمت چپ رشد می‌کند.\n\n"
                "شمارش مقایسه‌ها: هر بار که میله‌ای با کمینه فعلی مقایسه می‌شود.\n"
                "شمارش جابجایی‌ها: هر بار که دو میله جابجا می‌شوند."
            ),
            'help_insertion': (
                "مرتب‌سازی درجی\n\n"
                "مفهوم:\n"
                "آرایه را عنصر به عنصر مرتب می‌کند. عنصر بعدی (کلید) را با بخش مرتب شده (از راست به چپ) مقایسه می‌کند و عناصر بزرگتر را یک خانه به راست جابجا می‌کند تا جای مناسب کلید پیدا شود. سپس کلید در آن مکان قرار می‌گیرد.\n\n"
                "در این برنامه:\n"
                "• عنصر کلید با میله‌های مرتب مقایسه می‌شود؛ دو میله مقایسه‌شونده زرد رنگ می‌شوند.\n"
                "• در صورت نیاز، میله بزرگتر به راست شیفت داده می‌شود (قرمز).\n"
                "• پس از یافتن مکان صحیح، کلید در آن قرار گرفته (با قرمز) و بخش مرتب گسترش می‌یابد.\n\n"
                "شمارش مقایسه‌ها: هر بار که کلید با یک میله مرتب مقایسه می‌شود.\n"
                "شمارش جابجایی‌ها: هر شیفت و جایدادن نهایی."
            ),
            'help_quick': (
                "مرتب‌سازی سریع\n\n"
                "مفهوم:\n"
                "یک الگوریتم تقسیم و غلبه است. یک عنصر به عنوان محور انتخاب می‌شود. آرایه به دو بخش تقسیم می‌شود: عناصر کوچکتر از محور به چپ و بزرگتر به راست منتقل می‌شوند. سپس همین روند به صورت بازگشتی روی بخش‌های چپ و راست اعمال می‌شود.\n\n"
                "در این برنامه:\n"
                "• عنصر محور با رنگ طلایی مشخص می‌شود.\n"
                "• در حین تقسیم‌بندی، هر عنصری که با محور مقایسه می‌شود زرد رنگ است.\n"
                "• در صورت نیاز، جابجایی برای چینش عناصر حول محور با رنگ قرمز انجام می‌شود.\n"
                "• پس از اتمام تقسیم‌بندی، محور در جایگاه نهایی خود با قرمز جابجا شده و سبز می‌شود.\n"
                "• سپس الگوریتم روی زیرآرایه‌های چپ و راست تکرار می‌شود.\n\n"
                "شمارش مقایسه‌ها: هر بار که یک عنصر با محور مقایسه می‌شود.\n"
                "شمارش جابجایی‌ها: هر بار که دو عنصر جابجا می‌شوند."
            ),
            'help_merge': (
                "مرتب‌سازی ادغامی\n\n"
                "مفهوم:\n"
                "یک الگوریتم بازگشتی تقسیم و غلبه. آرایه را به‌طور بازگشتی به دو نیمه تقسیم می‌کند تا به زیرآرایه‌های تک‌عنصری برسد (که به‌خودی‌خود مرتب هستند). سپس این زیرآرایه‌ها را با هم ادغام می‌کند؛ در هر مرحله دو عنصر از دو زیرآرایه مقایسه (زرد) شده و کوچکترین آن‌ها به آرایه مقصد منتقل می‌شود (قرمز).\n\n"
                "در این برنامه:\n"
                "• فاز تقسیم نمایش داده نمی‌شود (به‌صورت لحظه‌ای رخ می‌دهد).\n"
                "• در حین ادغام، دو عنصری که مقایسه می‌شوند زرد و عنصر در حال جایگذاری قرمز است.\n"
                "• پس از اتمام ادغام یک بازه، تمام میله‌های آن بازه سبز می‌شوند.\n\n"
                "شمارش مقایسه‌ها: هر بار که دو عنصر از زیرآرایه‌های مختلف مقایسه می‌شوند.\n"
                "شمارش جابجایی‌ها: هر بار که عنصری در حین ادغام در آرایه قرار می‌گیرد."
            ),
        }
    }

    PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

    def __init__(self, root: tk.Tk):
        logger.debug("Initializing LinearSortGUI")
        self.root = root
        self.lang: str = 'en'
        self.root.title("Linear Sort Visualizer")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        self._base_font = self._choose_font()
        self._configure_ttk_style()

        # State
        self.num_elements: int = self.DEFAULT_ELEMENTS
        self.array: List[float] = []
        self.comparisons: int = 0
        self.swaps: int = 0
        self.sorted_indices: set[int] = set()
        self.comparing_indices: List[int] = []
        self.swapping_indices: List[int] = []   # indices currently being swapped
        self.pivot_index: Optional[int] = None

        # Auto-sort state
        self.is_sorting: bool = False
        self.is_paused: bool = False
        self.stop_sort_flag: bool = False
        self.sort_delay: int = 100
        self.sort_after_id: Optional[str] = None
        self.sort_algorithm: str = 'bubble'

        # Algorithm-specific state
        self.sort_state: dict = {}

        # Data generation state
        self.data_profile: str = 'distinct_positive_ints'

        # Custom options
        self.custom_type = tk.StringVar(value="integer")
        self.custom_min = tk.DoubleVar(value=1.0)
        self.custom_max = tk.DoubleVar(value=self.DEFAULT_ELEMENTS)
        self.custom_unique = tk.BooleanVar(value=True)

        self._generating = False

        # Clean mode toggle
        self.clean_mode: bool = False

        # Help pop-up reference
        self.help_popup: Optional[tk.Toplevel] = None

        # Sweep animation state
        self.sweep_index: Optional[int] = None
        self._sweep_after_id: Optional[str] = None

        # i18n combobox lists
        self._algo_display = []
        self._data_display = []
        self._algo_reverse: Dict[str, str] = {}
        self._data_reverse: Dict[str, str] = {}
        self._rebuild_combobox_lists()

        self.setup_ui()
        self.generate_array()
        logger.info("LinearSortGUI initialized successfully")

    # ----------------------------------------------------------------------
    # i18n Helpers
    # ----------------------------------------------------------------------
    def _choose_font(self) -> str:
        available = set(tkfont.families(self.root))
        preferred = ('DejaVu Sans', 'Noto Naskh Arabic', 'Arial')
        for name in preferred:
            if name in available:
                return name
        logger.debug("Preferred fonts not found, falling back to TkDefaultFont")
        return 'TkDefaultFont'

    def _configure_ttk_style(self):
        style = ttk.Style(self.root)
        style.configure('I18n.TCombobox', font=(self._base_font, 11))
        style.configure('I18n.TSpinbox', font=(self._base_font, 12))
        style.map('I18n.TCombobox', fieldbackground=[('readonly', 'white')])
        logger.debug("ttk style configured")

    def _shape_fa(self, text: str) -> str:
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except ImportError:
            if not getattr(self, '_bidi_warning_logged', False):
                logger.warning("arabic_reshaper / python-bidi not installed – "
                               "Persian text may appear unshaped or in wrong order.")
                self._bidi_warning_logged = True
            return text

    def _(self, key: str, **kwargs: object) -> str:
        text = self._raw(key)
        if kwargs:
            text = text.format(**kwargs)
        if self.lang == 'fa':
            text = self._shape_fa(text)
        return text

    def _raw(self, key: str) -> str:
        try:
            return self.TRANSLATIONS[self.lang][key]
        except KeyError:
            logger.warning(f"Missing translation key '{key}' for language '{self.lang}'")
            return self.TRANSLATIONS['en'].get(key, key)

    def _num(self, n: int) -> str:
        if self.lang == 'fa':
            return str(n).translate(self.PERSIAN_DIGITS)
        return str(n)

    def toggle_language(self):
        self.lang = 'fa' if self.lang == 'en' else 'en'
        logger.info(f"Language toggled to {self.lang}")
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None
        self.refresh_language()

    def refresh_language(self):
        logger.debug("Refreshing all UI strings for new language")
        self._rebuild_combobox_lists()

        self.algo_combo.unbind('<<ComboboxSelected>>')
        self.data_combo.unbind('<<ComboboxSelected>>')

        try:
            self.algo_combo.config(values=self._algo_display)
            self.data_combo.config(values=self._data_display)

            algo_display = self._(f'algo_{self.sort_algorithm}')
            data_display = self._(f'data_{self.data_profile}')
            self.algo_var.set(algo_display)
            self.data_var.set(data_display)
        finally:
            self.algo_combo.bind('<<ComboboxSelected>>', self.on_algorithm_change)
            self.data_combo.bind('<<ComboboxSelected>>', self.on_data_profile_change)

        self.elements_label.config(text=self._('elements_label'))
        self.algorithm_label.config(text=self._('algorithm_label'))
        self.data_label.config(text=self._('data_label'))
        self.speed_label.config(text=self._('speed_label'))
        self.type_label.config(text=self._('type_label'))
        self.min_label.config(text=self._('min_label'))
        self.max_label.config(text=self._('max_label'))
        self.unique_check.config(text=self._('unique_check'))
        self.type_int_rb.config(text=self._('integer_radio'))
        self.type_float_rb.config(text=self._('float_radio'))

        self.shuffle_btn.config(text=self._('shuffle_button'))
        self.sort_btn.config(text=self._('sort_button'))
        self.help_btn.config(text=self._('help_button'))

        if self.lang == 'en':
            persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
            self.lang_toggle_btn.config(text=self._shape_fa(persian_label))
        else:
            self.lang_toggle_btn.config(text=self._('toggle_lang_text'))

        # Update clean mode button text
        self._update_clean_mode_button_text()

        self._align_stats_label()
        self.update_stats_label()
        self.draw_array()
        self._set_ui_state(
            enabled=not self.is_sorting,
            paused=self.is_paused if self.is_sorting else False
        )

    def _align_stats_label(self):
        if self.lang == 'fa':
            self.stats_label.config(anchor='e', justify='right')
        else:
            self.stats_label.config(anchor='w', justify='left')

    def _rebuild_combobox_lists(self):
        self._algo_display = [self._(f'algo_{key}') for key in self.ALGO_KEYS]
        self._data_display = [self._(f'data_{key}') for key in self.DATA_KEYS]
        self._algo_reverse = {display: key for display, key in zip(self._algo_display, self.ALGO_KEYS)}
        self._data_reverse = {display: key for display, key in zip(self._data_display, self.DATA_KEYS)}
        logger.debug("Combo box lists rebuilt")

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def setup_ui(self):
        logger.debug("Setting up UI")
        control_frame = tk.Frame(self.root, bg=self.BG_COLOR_CONTROLS, height=120)
        control_frame.pack(fill=tk.X)
        control_frame.pack_propagate(False)

        row1 = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        row1.pack(fill=tk.X, pady=5)

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

        self.elements_label = tk.Label(row1, text=self._('elements_label'),
                                       bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                       font=(self._base_font, 12))
        self.elements_label.pack(side=tk.LEFT, padx=10)
        self.element_var = tk.IntVar(value=self.num_elements)
        self.element_spinbox = ttk.Spinbox(
            row1, from_=self.MIN_ELEMENTS, to=self.MAX_ELEMENTS,
            textvariable=self.element_var, width=4, style='I18n.TSpinbox',
            command=self.on_element_change, state='readonly'
        )
        self.element_spinbox.pack(side=tk.LEFT, padx=5)

        self.algorithm_label = tk.Label(row1, text=self._('algorithm_label'),
                                        bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                        font=(self._base_font, 12))
        self.algorithm_label.pack(side=tk.LEFT, padx=15)
        self.algo_var = tk.StringVar(value=self._algo_display[self.ALGO_KEYS.index(self.sort_algorithm)])
        self.algo_combo = ttk.Combobox(
            row1, textvariable=self.algo_var, width=15, style='I18n.TCombobox',
            values=self._algo_display, state='readonly'
        )
        self.algo_combo.pack(side=tk.LEFT, padx=5)
        self.algo_combo.bind('<<ComboboxSelected>>', self.on_algorithm_change)

        self.data_label = tk.Label(row1, text=self._('data_label'),
                                   bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                   font=(self._base_font, 12))
        self.data_label.pack(side=tk.LEFT, padx=15)
        self.data_var = tk.StringVar(value=self._data_display[self.DATA_KEYS.index(self.data_profile)])
        self.data_combo = ttk.Combobox(
            row1, textvariable=self.data_var, width=22, style='I18n.TCombobox',
            values=self._data_display, state='readonly'
        )
        self.data_combo.pack(side=tk.LEFT, padx=5)
        self.data_combo.bind('<<ComboboxSelected>>', self.on_data_profile_change)

        self.shuffle_btn = make_btn(row1, self._('shuffle_button'), self.generate_array)
        self.shuffle_btn.pack(side=tk.LEFT, padx=15)
        self.sort_btn = make_btn(row1, self._('sort_button'), self.auto_sort)
        self.sort_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = make_btn(row1, self._('stop_button'), self.interrupt_sort)
        self.pause_resume_btn = make_btn(row1, self._('pause_button'), self.pause_sort)

        self.speed_label = tk.Label(row1, text=self._('speed_label'),
                                    bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                    font=(self._base_font, 12))
        self.speed_label.pack(side=tk.LEFT, padx=10)
        self.speed_slider = tk.Scale(
            row1, from_=10, to=500, orient=tk.HORIZONTAL,
            command=self.set_sort_delay, length=120,
            showvalue=False, bg=self.BG_COLOR_CONTROLS,
            fg=self.TEXT_COLOR, highlightthickness=0
        )
        self.speed_slider.set(400)
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        persian_label = self.TRANSLATIONS['en']['toggle_lang_text']
        self.lang_toggle_btn = make_btn(row1, self._shape_fa(persian_label),
                                        self.toggle_language)
        self.lang_toggle_btn.config(padx=12)
        self.lang_toggle_btn.pack(side=tk.LEFT, padx=10)

        self.clean_mode_btn = make_btn(row1, '', self.toggle_clean_mode)
        self.clean_mode_btn.pack(side=tk.LEFT, padx=10)
        self._update_clean_mode_button_text()

        self.help_btn = make_btn(row1, self._('help_button'), self.show_help)
        self.help_btn.pack(side=tk.LEFT, padx=10)

        # Custom options row
        self.custom_frame = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)

        self.type_label = tk.Label(self.custom_frame, text=self._('type_label'),
                                   bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                   font=(self._base_font, 11))
        self.type_label.pack(side=tk.LEFT, padx=5)
        self.type_int_rb = tk.Radiobutton(self.custom_frame, text=self._('integer_radio'),
                                          variable=self.custom_type, value="integer",
                                          command=self.on_custom_option_change,
                                          bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                          activebackground=self.BG_COLOR_CONTROLS,
                                          activeforeground=self.TEXT_COLOR,
                                          selectcolor=self.BG_COLOR_MAIN,
                                          font=(self._base_font, 10))
        self.type_float_rb = tk.Radiobutton(self.custom_frame, text=self._('float_radio'),
                                            variable=self.custom_type, value="float",
                                            command=self.on_custom_option_change,
                                            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                            activebackground=self.BG_COLOR_CONTROLS,
                                            activeforeground=self.TEXT_COLOR,
                                            selectcolor=self.BG_COLOR_MAIN,
                                            font=(self._base_font, 10))
        self.type_int_rb.pack(side=tk.LEFT)
        self.type_float_rb.pack(side=tk.LEFT)

        self.min_label = tk.Label(self.custom_frame, text=self._('min_label'),
                                  bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                  font=(self._base_font, 11))
        self.min_label.pack(side=tk.LEFT, padx=5)
        self.min_spinbox = ttk.Spinbox(
            self.custom_frame, from_=-1000, to=1000, width=5,
            textvariable=self.custom_min, command=self.on_custom_option_change,
            style='I18n.TSpinbox'
        )
        self.min_spinbox.pack(side=tk.LEFT)
        self.max_label = tk.Label(self.custom_frame, text=self._('max_label'),
                                  bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
                                  font=(self._base_font, 11))
        self.max_label.pack(side=tk.LEFT, padx=5)
        self.max_spinbox = ttk.Spinbox(
            self.custom_frame, from_=-1000, to=1000, width=5,
            textvariable=self.custom_max, command=self.on_custom_option_change,
            style='I18n.TSpinbox'
        )
        self.max_spinbox.pack(side=tk.LEFT)

        self.unique_check = tk.Checkbutton(
            self.custom_frame, text=self._('unique_check'),
            variable=self.custom_unique, command=self.on_custom_option_change,
            bg=self.BG_COLOR_CONTROLS, fg=self.TEXT_COLOR,
            activebackground=self.BG_COLOR_CONTROLS,
            activeforeground=self.TEXT_COLOR,
            selectcolor=self.BG_COLOR_MAIN,
            font=(self._base_font, 10)
        )
        self.unique_check.pack(side=tk.LEFT, padx=10)

        self.custom_frame.pack_forget()

        # Bottom row for stats
        bottom_row = tk.Frame(control_frame, bg=self.BG_COLOR_CONTROLS)
        bottom_row.pack(fill=tk.X, pady=5)

        self.stats_label = tk.Label(
            bottom_row, text="", bg=self.BG_COLOR_CONTROLS,
            fg=self.TEXT_COLOR, font=(self._base_font, 14, 'bold')
        )
        self.stats_label.pack(side=tk.LEFT, padx=20)

        # Canvas
        self.canvas = tk.Canvas(self.root, bg=self.BG_COLOR_MAIN, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        self.root.update_idletasks()
        self._align_stats_label()
        self.draw_array()
        logger.debug("UI setup complete")

    # ------------------------------------------------------------------
    # Clean mode toggle
    # ------------------------------------------------------------------
    def toggle_clean_mode(self):
        if self.is_sorting:
            logger.warning("Cannot toggle clean mode while sorting")
            return
        self.clean_mode = not self.clean_mode
        logger.info(f"Clean mode set to {self.clean_mode}")
        self._update_clean_mode_button_text()

    def _update_clean_mode_button_text(self):
        if self.clean_mode:
            text = self._('clean_mode_btn_on')
        else:
            text = self._('clean_mode_btn_off')
        self.clean_mode_btn.config(text=text)

    # ------------------------------------------------------------------
    # Help pop-up
    # ------------------------------------------------------------------
    def show_help(self):
        if self.help_popup is not None and tk.Toplevel.winfo_exists(self.help_popup):
            self.help_popup.lift()
            self.help_popup.focus_force()
            return
        logger.debug(f"Opening help for algorithm {self.sort_algorithm}")
        popup = tk.Toplevel(self.root)
        raw_algo = self._raw(f'algo_{self.sort_algorithm}')
        popup.title(f"Help – {raw_algo}")
        popup.transient(self.root)
        popup.resizable(False, False)
        popup.configure(bg=self.BG_COLOR_MAIN)

        help_text = self._(f'help_{self.sort_algorithm}')

        text_frame = tk.Frame(popup, bg=self.BG_COLOR_MAIN)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        text_widget = tk.Text(
            text_frame, wrap='word', font=(self._base_font, 12),
            bg=self.BG_COLOR_MAIN, fg=self.TEXT_COLOR,
            highlightthickness=0, borderwidth=0, relief=tk.FLAT,
            width=55, height=18
        )
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.insert('1.0', help_text)
        if self.lang == 'fa':
            text_widget.tag_configure('rtl', justify='right')
            text_widget.tag_add('rtl', '1.0', 'end')
        text_widget.config(state='disabled')

        close_btn = tk.Button(
            popup, text=self._('close_button'), font=(self._base_font, 10),
            bg=self.BUTTON_BG, fg=self.BUTTON_FG,
            activebackground=self.BUTTON_ACTIVE_BG,
            activeforeground=self.BUTTON_ACTIVE_FG,
            relief=tk.FLAT, padx=8, pady=2,
            highlightthickness=0, borderwidth=0,
            command=popup.destroy
        )
        close_btn.pack(pady=(5, 15))

        self.help_popup = popup
        popup.protocol("WM_DELETE_WINDOW", self._on_help_popup_close)

    def _on_help_popup_close(self):
        logger.debug("Help popup closed")
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def on_element_change(self):
        new_count = self.element_var.get()
        logger.debug(f"Element count changed to {new_count}, is_sorting={self.is_sorting}")
        if not self.is_sorting and new_count != self.num_elements:
            self.num_elements = new_count
            logger.info(f"Element count updated to {new_count}, regenerating array")
            self.generate_array()

    def on_algorithm_change(self, event=None):
        display = self.algo_var.get()
        key = self._algo_reverse.get(display)
        if key is None:
            return
        logger.debug(f"Algorithm changed to '{key}', is_sorting={self.is_sorting}")
        if self.help_popup is not None:
            self.help_popup.destroy()
            self.help_popup = None
        if not self.is_sorting:
            self.sort_algorithm = key
            if self.comparisons > 0 or self.swaps > 0:
                logger.info("Resetting array due to algorithm change with existing stats")
                self.generate_array()
            else:
                self.update_stats_label()

    def on_data_profile_change(self, event=None):
        display = self.data_var.get()
        key = self._data_reverse.get(display)
        if key is None:
            return
        logger.debug(f"Data profile changed to '{key}', is_sorting={self.is_sorting}")
        if self.is_sorting:
            return
        self.data_profile = key
        if key == 'custom':
            self.custom_frame.pack(fill=tk.X, pady=5, after=self.speed_slider.master)
        else:
            self.custom_frame.pack_forget()
        self.generate_array()

    def on_custom_option_change(self):
        if self.is_sorting:
            return
        if self.data_profile == 'custom':
            self.generate_array()

    def set_sort_delay(self, value: str):
        delay = 510 - int(float(value))
        logger.debug(f"Speed slider changed: value={value}, new delay={delay}ms")
        self.sort_delay = delay

    def on_canvas_resize(self, event):
        logger.debug(f"Canvas resized to {event.width}x{event.height}, redrawing")
        self.draw_array()

    # ------------------------------------------------------------------
    # Array Generation & UI State
    # ------------------------------------------------------------------
    def generate_array(self):
        if self._generating:
            return
        self._generating = True
        try:
            logger.info(f"Generating new array with profile '{self.data_profile}'")
            if self.is_sorting:
                logger.debug("Interrupting current sort before generating new array")
                self.interrupt_sort()

            self.element_spinbox.config(command='')
            self.num_elements = self.element_var.get()
            n = self.num_elements

            profile = self.data_profile
            if profile == 'distinct_positive_ints':
                arr = list(range(1, n + 1))
                random.shuffle(arr)
            elif profile == 'duplicate_positive_ints':
                arr = [random.randint(1, n) for _ in range(n)]
            elif profile == 'distinct_pos_neg_ints':
                half = n // 2
                arr = list(range(-half + 1, half + 1)) if n % 2 == 0 else list(range(-half, half + 1))
                random.shuffle(arr)
            elif profile == 'duplicate_pos_neg_ints':
                half = n // 2
                arr = [random.randint(-half, half) for _ in range(n)]
            elif profile == 'random_floats_0_1':
                arr = [random.uniform(0, 1) for _ in range(n)]
            elif profile == 'random_floats_neg1_1':
                arr = [random.uniform(-1, 1) for _ in range(n)]
            elif profile == 'nearly_sorted':
                arr = list(range(1, n + 1))
                swaps = max(1, n // 4)
                for _ in range(swaps):
                    i = random.randint(0, n - 2)
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
            elif profile == 'reverse_sorted':
                arr = list(range(n, 0, -1))
            elif profile == 'custom':
                typ = self.custom_type.get()
                low = self.custom_min.get()
                high = self.custom_max.get()
                if low > high:
                    low, high = high, low
                unique = self.custom_unique.get()
                if typ == 'integer':
                    low_int = int(round(low))
                    high_int = int(round(high))
                    if unique:
                        range_size = high_int - low_int + 1
                        if n > range_size:
                            messagebox.showwarning(
                                "Invalid Selection",
                                self._('unique_impossible', low=str(low_int), high=str(high_int),
                                       range_size=str(range_size), n=str(n)),
                                parent=self.root
                            )
                            self.custom_unique.set(False)
                            arr = [random.randint(low_int, high_int) for _ in range(n)]
                        else:
                            arr = list(range(low_int, high_int + 1))
                            random.shuffle(arr)
                            arr = arr[:n]
                    else:
                        arr = [random.randint(low_int, high_int) for _ in range(n)]
                else:  # float
                    if unique:
                        messagebox.showwarning(
                            "Uniqueness Disabled",
                            self._('float_unique_warning'),
                            parent=self.root
                        )
                        self.custom_unique.set(False)
                    arr = [random.uniform(low, high) for _ in range(n)]
            else:
                arr = list(range(1, n + 1))
                random.shuffle(arr)

            self.array = arr
            logger.debug(f"Generated array of length {len(self.array)}")
            self.comparisons = 0
            self.swaps = 0
            self.sorted_indices = set()
            self.comparing_indices = []
            self.swapping_indices = []
            self.pivot_index = None
            self.sort_state = {}
            self.sweep_index = None
            self._cancel_sweep()
            self.update_stats_label()
            self._set_ui_state(True)
            self.element_spinbox.config(command=self.on_element_change)
            self.draw_array()
        finally:
            self._generating = False

    def update_stats_label(self):
        raw_algo = self._raw(f'algo_{self.sort_algorithm}')
        text = self._('stats_template',
                      algo=raw_algo,
                      comparisons=self._num(self.comparisons),
                      swaps=self._num(self.swaps))
        self.stats_label.config(text=text)

    def _set_ui_state(self, enabled: bool, paused: bool = False):
        logger.debug(f"Setting UI state to enabled={enabled}, paused={paused}")
        if enabled:
            self.shuffle_btn.config(state='normal')
            self.sort_btn.config(state='normal')
            self.element_spinbox.config(state='readonly')
            self.algo_combo.config(state='readonly')
            self.data_combo.config(state='readonly')
            self.speed_slider.config(state='normal')
            self.help_btn.config(state='normal')
            self.clean_mode_btn.config(state='normal')
            for child in self.custom_frame.winfo_children():
                child.config(state='normal')
            self.stop_btn.pack_forget()
            self.pause_resume_btn.pack_forget()
        else:
            self.shuffle_btn.config(state='disabled')
            self.sort_btn.config(state='disabled')
            self.element_spinbox.config(state='disabled')
            self.algo_combo.config(state='disabled')
            self.data_combo.config(state='disabled')
            self.help_btn.config(state='disabled')
            self.clean_mode_btn.config(state='disabled')
            for child in self.custom_frame.winfo_children():
                child.config(state='disabled')
            self.speed_slider.config(state='normal')

            self.stop_btn.pack_forget()
            self.pause_resume_btn.pack_forget()

            if paused:
                self.pause_resume_btn.config(text=self._('resume_button'), command=self.resume_sort)
                self.pause_resume_btn.pack(side=tk.LEFT, padx=5, after=self.sort_btn)
                self.stop_btn.pack(side=tk.LEFT, padx=5, after=self.pause_resume_btn)
                logger.debug("UI set to paused: Resume + Stop visible")
            else:
                self.pause_resume_btn.config(text=self._('pause_button'), command=self.pause_sort)
                self.pause_resume_btn.pack(side=tk.LEFT, padx=5, after=self.sort_btn)
                self.stop_btn.pack(side=tk.LEFT, padx=5, after=self.pause_resume_btn)
                logger.debug("UI set to active solving: Pause + Stop visible")

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw_array(self):
        logger.debug(f"Drawing array of length {len(self.array)}")
        self.canvas.delete('all')
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()

        if w <= 1 or h <= 1 or not self.array:
            logger.debug("Canvas too small or empty array, skipping draw")
            return

        n = len(self.array)
        bar_width = w / n
        min_bar_width = 2
        if bar_width < min_bar_width:
            bar_width = min_bar_width
            total_width = bar_width * n
            start_x = max(0, (w - total_width) / 2)
        else:
            total_width = w
            start_x = 0
            bar_width = total_width / n

        min_val = min(self.array)
        max_val = max(self.array)
        padding = 20
        has_negatives = (min_val < 0)
        is_float = any(isinstance(v, float) for v in self.array)

        if has_negatives:
            range_val = max_val - min_val
            if range_val == 0:
                range_val = 1
            scale = (h - 2 * padding) / range_val
            zero_y = h - (padding + (0 - min_val) * scale)
        else:
            if max_val == 0:
                max_val = 1
            zero_y = h

        # Sweep mode: override colors
        if self.sweep_index is not None:
            sweep = self.sweep_index
            for i, val in enumerate(self.array):
                x1 = start_x + i * bar_width
                x2 = x1 + bar_width - 2
                if has_negatives:
                    bar_height = abs(val) * scale
                    if val >= 0:
                        y1 = zero_y - bar_height
                        y2 = zero_y
                    else:
                        y1 = zero_y
                        y2 = zero_y + bar_height
                else:
                    bar_height = ((h - padding) * val) / max_val
                    y1 = h - bar_height
                    y2 = h

                color = self.BAR_COLOR_SORTED if i <= sweep else self.BAR_COLOR_DEFAULT
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=self.BAR_OUTLINE, width=1)

                if bar_width > 20:
                    text_size = max(8, min(12, int(bar_width * 0.4)))
                    if is_float:
                        label = f"{val:.2f}"
                    else:
                        label = self._num(int(val)) if self.lang == 'fa' and isinstance(val, (int, float)) and val == int(val) else str(val)
                    text_y = y1 - 10 if val >= 0 or not has_negatives else y2 + 10
                    self.canvas.create_text((x1 + x2) / 2, text_y, text=label, fill=self.TEXT_COLOR,
                                            font=(self._base_font, text_size))

            if has_negatives:
                self.canvas.create_line(0, zero_y, w, zero_y, fill=self.ZERO_LINE_COLOR, dash=(4, 4))

            if self.is_sorting and self.is_paused:
                self._draw_paused_overlay(w)
            return

        # Normal drawing
        for i, val in enumerate(self.array):
            x1 = start_x + i * bar_width
            x2 = x1 + bar_width - 2

            if has_negatives:
                bar_height = abs(val) * scale if scale else 0
                if val >= 0:
                    y1 = zero_y - bar_height
                    y2 = zero_y
                else:
                    y1 = zero_y
                    y2 = zero_y + bar_height
            else:
                bar_height = ((h - padding) * val) / max_val
                y1 = h - bar_height
                y2 = h

            # Color priority: sorted > pivot > swapping > comparing > default
            if i in self.sorted_indices:
                color = self.BAR_COLOR_SORTED
            elif i == self.pivot_index:
                color = self.BAR_COLOR_PIVOT
            elif i in self.swapping_indices:
                color = self.BAR_COLOR_SWAPPING
            elif i in self.comparing_indices:
                color = self.BAR_COLOR_COMPARING
            else:
                color = self.BAR_COLOR_DEFAULT

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=self.BAR_OUTLINE, width=1)

            if bar_width > 20:
                text_size = max(8, min(12, int(bar_width * 0.4)))
                if is_float:
                    label = f"{val:.2f}"
                else:
                    label = self._num(int(val)) if self.lang == 'fa' and isinstance(val, (int, float)) and val == int(val) else str(val)
                text_y = y1 - 10 if val >= 0 or not has_negatives else y2 + 10
                self.canvas.create_text((x1 + x2) / 2, text_y, text=label, fill=self.TEXT_COLOR,
                                        font=(self._base_font, text_size))

        if has_negatives:
            self.canvas.create_line(0, zero_y, w, zero_y, fill=self.ZERO_LINE_COLOR, dash=(4, 4))

        if self.is_sorting and self.is_paused:
            self._draw_paused_overlay(w)

    def _draw_paused_overlay(self, w):
        pause_text = self._('paused_text')
        bbox = self.canvas.bbox(self.canvas.create_text(
            w / 2, 30, text=pause_text,
            fill='white', font=(self._base_font, 20, 'bold'), anchor='n'
        ))
        if bbox:
            self.canvas.create_rectangle(
                bbox[0] - 10, bbox[1] - 5, bbox[2] + 10, bbox[3] + 5,
                fill='#2C3E50', outline='', stipple='gray50'
            )
            self.canvas.create_text(
                w / 2, 30, text=pause_text,
                fill='white', font=(self._base_font, 20, 'bold'), anchor='n'
            )

    # ------------------------------------------------------------------
    # Sweep Animation
    # ------------------------------------------------------------------
    def _start_sweep(self):
        logger.debug("Starting final sweep animation")
        self._cancel_sweep()
        self.sweep_index = 0
        self._disable_controls_during_sweep()
        self._sweep_after_id = self.root.after(10, self._sweep_step)

    def _sweep_step(self):
        if self.sweep_index is None:
            logger.debug("Sweep cancelled mid-way")
            return
        self.draw_array()
        self.sweep_index += 1
        logger.debug(f"Sweep step: index {self.sweep_index}")
        if self.sweep_index < len(self.array):
            self._sweep_after_id = self.root.after(10, self._sweep_step)
        else:
            logger.debug("Sweep animation finished")
            self._sweep_finished()

    def _sweep_finished(self):
        self.sweep_index = None
        self._sweep_after_id = None
        self.draw_array()
        self._enable_controls_after_sweep()
        self._set_ui_state(True)
        logger.info("Sorting completed successfully")
        raw_algo = self._raw(f'algo_{self.sort_algorithm}')
        msg = self._('sort_complete_msg',
                     algo=raw_algo,
                     comparisons=self._num(self.comparisons),
                     swaps=self._num(self.swaps))
        messagebox.showinfo(self._('sort_complete_title'), msg, parent=self.root)

    def _cancel_sweep(self):
        if self._sweep_after_id is not None:
            try:
                self.root.after_cancel(self._sweep_after_id)
            except (tk.TclError, ValueError):
                pass
            self._sweep_after_id = None
        self.sweep_index = None

    def _disable_controls_during_sweep(self):
        logger.debug("Disabling controls for sweep")
        self.shuffle_btn.config(state='disabled')
        self.sort_btn.config(state='disabled')
        self.element_spinbox.config(state='disabled')
        self.algo_combo.config(state='disabled')
        self.data_combo.config(state='disabled')
        self.help_btn.config(state='disabled')
        self.clean_mode_btn.config(state='disabled')
        self.speed_slider.config(state='disabled')
        self.stop_btn.pack_forget()
        self.pause_resume_btn.pack_forget()

    def _enable_controls_after_sweep(self):
        logger.debug("Re-enabling controls after sweep")
        self.shuffle_btn.config(state='normal')
        self.sort_btn.config(state='normal')
        self.element_spinbox.config(state='readonly')
        self.algo_combo.config(state='readonly')
        self.data_combo.config(state='readonly')
        self.speed_slider.config(state='normal')
        self.help_btn.config(state='normal')
        self.clean_mode_btn.config(state='normal')

    # ------------------------------------------------------------------
    # Auto-sort Control
    # ------------------------------------------------------------------
    def auto_sort(self):
        logger.info(f"Auto Sort requested with algorithm '{self.sort_algorithm}'")
        if self.is_sorting:
            logger.warning("Sort already in progress, ignoring auto_sort request")
            return

        if self.comparisons > 0 or self.swaps > 0:
            logger.debug("Array has been partially sorted; asking user to confirm reset")
            if not messagebox.askyesno("Confirm", self._('confirm_reset'), parent=self.root):
                logger.info("User cancelled auto-sort reset")
                return
            self.generate_array()

        self.is_sorting = True
        self.is_paused = False
        self.stop_sort_flag = False
        self._set_ui_state(False, paused=False)

        if self.sort_algorithm == 'bubble':
            self.sort_state = {'i': 0, 'j': 0, 'phase': 'compare'}
            logger.debug("Bubble sort initialized with i=0, j=0, phase=compare")
            self.sort_after_id = self.root.after(self.sort_delay, self._bubble_sort_step)
        elif self.sort_algorithm == 'selection':
            self.sort_state = {'i': 0, 'min_idx': 0, 'j': 0, 'phase': 'find_min'}
            logger.debug("Selection sort initialized with i=0, min_idx=0, j=0, phase=find_min")
            self.sort_after_id = self.root.after(self.sort_delay, self._selection_sort_step)
        elif self.sort_algorithm == 'insertion':
            if self.clean_mode:
                logger.debug("Insertion sort clean mode selected")
                self.sort_state = {'i': 1, 'phase': 'init_clean', 'comparisons_done': []}
            else:
                self.sort_state = {'i': 1, 'j': 0, 'key': 0, 'phase': 'compare'}
            self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
        elif self.sort_algorithm == 'quick':
            self.sort_state = {
                'stack': [(0, len(self.array) - 1)],
                'phase': 'partition',
                'low': 0, 'high': 0, 'pivot': 0, 'i': 0, 'j': 0
            }
            logger.debug("Quick sort initialized with stack containing full array")
            self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
        elif self.sort_algorithm == 'merge':
            if self.clean_mode:
                logger.debug("Merge sort clean mode selected")
                self.sort_state = {
                    'stack': [(0, len(self.array) - 1, 'split')],
                    'merge_state': None,
                    'clean_merge': None
                }
            else:
                self.sort_state = {
                    'stack': [(0, len(self.array) - 1, 'split')],
                    'merge_state': None
                }
            # Merge sort (both modes) will start with a 0‑ms delay to begin splitting instantly
            self.sort_after_id = self.root.after(0, self._merge_sort_step)
        else:
            logger.error(f"Unknown sort algorithm: {self.sort_algorithm}")
            self.finish_sort(interrupted=True)

    def pause_sort(self):
        logger.info("Pause requested")
        if self.is_sorting and not self.is_paused:
            self.is_paused = True
            if self.sort_after_id is not None:
                try:
                    self.root.after_cancel(self.sort_after_id)
                except (tk.TclError, ValueError):
                    pass
                self.sort_after_id = None
            self._set_ui_state(False, paused=True)
            self.draw_array()
            logger.debug("Sort paused, UI updated")
        else:
            logger.debug("Pause ignored – not sorting or already paused")

    def resume_sort(self):
        logger.info("Resume requested")
        if self.is_sorting and self.is_paused:
            self.is_paused = False
            self._set_ui_state(False, paused=False)
            self.draw_array()
            logger.debug("Sort resumed, proceeding")
            if self.sort_algorithm == 'bubble':
                self._bubble_sort_step()
            elif self.sort_algorithm == 'selection':
                self._selection_sort_step()
            elif self.sort_algorithm == 'insertion':
                self._insertion_sort_step()
            elif self.sort_algorithm == 'quick':
                self._quick_sort_step()
            elif self.sort_algorithm == 'merge':
                self._merge_sort_step()
            else:
                self.finish_sort(interrupted=True)
        else:
            logger.debug("Resume ignored – not sorting or not paused")

    def interrupt_sort(self):
        logger.info("Interrupting sort")
        self.stop_sort_flag = True
        self.is_paused = False
        if self.sort_after_id is not None:
            try:
                self.root.after_cancel(self.sort_after_id)
            except (tk.TclError, ValueError):
                pass
            finally:
                self.sort_after_id = None
        self.finish_sort(interrupted=True)

    def finish_sort(self, interrupted: bool = False):
        logger.info(f"Finishing sort (interrupted={interrupted})")
        self.is_sorting = False
        self.is_paused = False
        self.stop_sort_flag = False
        self.sort_after_id = None
        self.comparing_indices = []
        self.swapping_indices = []
        self.pivot_index = None

        if not interrupted and len(self.sorted_indices) == len(self.array):
            logger.debug("Sort completed successfully, starting sweep")
            self._start_sweep()
        else:
            self._cancel_sweep()
            self._set_ui_state(True)
            self.draw_array()
            logger.debug("Sort finished with interruption or incomplete state")

    # ------------------------------------------------------------------
    # Sorting Step Functions (with detailed logging)
    # ------------------------------------------------------------------
    def _should_stop_after_step(self) -> bool:
        if self.stop_sort_flag:
            logger.debug("Stop flag detected, finishing sort")
            self.finish_sort(interrupted=True)
            return True
        return False

    # ---- Bubble Sort ----
    def _bubble_sort_step(self):
        if self._should_stop_after_step():
            return
        if self.is_paused:
            return

        state = self.sort_state
        i, j, phase = state['i'], state['j'], state['phase']
        n = len(self.array)

        logger.debug(f"Bubble step: i={i}, j={j}, phase={phase}")

        if i >= n - 1:
            logger.debug("Bubble sort completed all passes")
            self.sorted_indices = set(range(n))
            self.comparing_indices = []
            self.swapping_indices = []
            self.draw_array()
            self.finish_sort()
            return

        if phase == 'compare':
            if j >= n - i - 1:
                logger.debug(f"Bubble pass {i} finished, marking index {n-i-1} as sorted")
                self.sorted_indices.add(n - i - 1)
                state['i'] += 1
                state['j'] = 0
                state['phase'] = 'compare'
                self.comparing_indices = []
                self.draw_array()
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._bubble_sort_step)
                return

            self.comparing_indices = [j, j + 1]
            self.comparisons += 1
            self.update_stats_label()
            logger.debug(f"Comparing indices {j} and {j+1}, values {self.array[j]} vs {self.array[j+1]}")
            self.draw_array()

            if self.array[j] > self.array[j + 1]:
                state['phase'] = 'swap'
                logger.debug(f"Swap needed between {j} and {j+1}")
            else:
                state['j'] += 1
                state['phase'] = 'compare'

            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._bubble_sort_step)
            return

        elif phase == 'swap':
            logger.debug(f"Swapping elements at {j} and {j+1}")
            # Perform swap first, then highlight (swap is exchange, safe both ways)
            self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
            self.swaps += 1
            self.update_stats_label()
            self.swapping_indices = [j, j + 1]
            self.comparing_indices = []  # clear compare highlight
            self.draw_array()
            self.swapping_indices = []
            state['j'] += 1
            state['phase'] = 'compare'

            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._bubble_sort_step)

    # ---- Selection Sort ----
    def _selection_sort_step(self):
        if self._should_stop_after_step():
            return
        if self.is_paused:
            return

        state = self.sort_state
        i, min_idx, j, phase = state['i'], state['min_idx'], state['j'], state['phase']
        n = len(self.array)

        logger.debug(f"Selection step: i={i}, min_idx={min_idx}, j={j}, phase={phase}")

        if i >= n:
            logger.debug("Selection sort completed")
            self.sorted_indices = set(range(n))
            self.comparing_indices = []
            self.swapping_indices = []
            self.draw_array()
            self.finish_sort()
            return

        if phase == 'find_min':
            if j == i:
                state['min_idx'] = i
                state['j'] = i + 1
                logger.debug(f"Starting new selection pass at i={i}")
            if state['j'] >= n:
                state['phase'] = 'pre_swap'
                self.comparing_indices = []
                logger.debug(f"Found min at index {min_idx}, transitioning to pre_swap")
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._selection_sort_step)
                return

            self.comparing_indices = [min_idx, state['j']]
            self.comparisons += 1
            self.update_stats_label()
            logger.debug(f"Comparing current min {self.array[min_idx]} at {min_idx} with {self.array[state['j']]} at {state['j']}")
            if self.array[state['j']] < self.array[min_idx]:
                state['min_idx'] = state['j']
                logger.debug(f"New minimum found at {state['j']} value {self.array[state['j']]}")
            self.draw_array()
            state['j'] += 1
            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._selection_sort_step)
            return

        elif phase == 'pre_swap':
            min_idx = state['min_idx']
            if min_idx != i:
                logger.debug(f"Preparing swap: elements at {i} and {min_idx}")
                # Perform swap first, then highlight
                self.array[i], self.array[min_idx] = self.array[min_idx], self.array[i]
                self.swaps += 1
                self.update_stats_label()
                self.swapping_indices = [i, min_idx]
            else:
                logger.debug("Minimum already in place, no swap needed")
            self.comparing_indices = []
            self.draw_array()
            state['phase'] = 'do_swap'
            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._selection_sort_step)
            return

        elif phase == 'do_swap':
            min_idx = state['min_idx']
            if min_idx != i:
                # already swapped in pre_swap
                pass
            self.sorted_indices.add(i)
            logger.debug(f"Element at {i} now sorted")
            self.swapping_indices = []
            self.comparing_indices = []
            state['i'] += 1
            state['j'] = state['i']
            state['min_idx'] = state['i']
            state['phase'] = 'find_min'
            self.draw_array()
            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._selection_sort_step)

    # ---- Insertion Sort ----
    def _insertion_sort_step(self):
        if self._should_stop_after_step():
            return
        if self.is_paused:
            return

        state = self.sort_state
        n = len(self.array)

        if self.clean_mode:
            # Clean mode insertion: animate comparisons, then batch movement
            phase = state.get('phase')
            if phase == 'init_clean':
                i = state['i']
                if i >= n:
                    logger.debug("Insertion sort clean complete")
                    self.sorted_indices = set(range(n))
                    self.comparing_indices = []
                    self.swapping_indices = []
                    self.draw_array()
                    self.finish_sort()
                    return
                key = self.array[i]
                # Find insertion point and collect compared indices
                j = i - 1
                comparisons = []
                while j >= 0 and self.array[j] > key:
                    comparisons.append(j)  # we compare key with element at j
                    j -= 1
                # Record the correct insertion position
                state['insert_pos'] = j + 1
                state['key'] = key
                state['comparisons'] = comparisons  # these are the indices of the larger elements we compared against
                state['comp_idx'] = 0
                state['phase'] = 'show_comparisons'
                # Fall through to show first comparison
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                return

            elif phase == 'show_comparisons':
                comparisons = state['comparisons']
                comp_idx = state['comp_idx']
                if comp_idx < len(comparisons):
                    # Show yellow between key (at i) and the sorted element being compared
                    self.comparing_indices = [state['i'], comparisons[comp_idx]]
                    self.comparisons += 1
                    self.update_stats_label()
                    logger.debug(f"Clean insertion: comparing key at {state['i']} with index {comparisons[comp_idx]}")
                    self.draw_array()
                    state['comp_idx'] += 1
                    if not self._should_stop_after_step() and not self.is_paused:
                        self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                    return
                else:
                    # All comparisons shown, now perform the shift and placement in one go
                    state['phase'] = 'execute_insertion'
                    if not self._should_stop_after_step() and not self.is_paused:
                        self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                    return

            elif phase == 'execute_insertion':
                i = state['i']
                key = state['key']
                insert_pos = state['insert_pos']
                # Shift elements right
                for k in range(i, insert_pos, -1):
                    self.array[k] = self.array[k-1]
                    self.swaps += 1
                # Place key
                self.array[insert_pos] = key
                self.swaps += 1
                self.update_stats_label()
                # Show the moved element(s) as swapping briefly
                self.swapping_indices = list(range(insert_pos, i+1))
                self.comparing_indices = []
                self.draw_array()
                self.swapping_indices = []
                # Advance to next element
                state['i'] += 1
                state['phase'] = 'init_clean'
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                return
        else:
            # Original insertion sort (verbose/duplicate mode)
            i, j, key, phase = state['i'], state['j'], state['key'], state['phase']

            logger.debug(f"Insertion step: i={i}, j={j}, key={key}, phase={phase}")

            if i >= n:
                logger.debug("Insertion sort completed")
                self.sorted_indices = set(range(n))
                self.comparing_indices = []
                self.swapping_indices = []
                self.draw_array()
                self.finish_sort()
                return

            if phase == 'compare':
                state['key'] = self.array[i]
                state['j'] = i - 1
                state['phase'] = 'shift_compare'
                logger.debug(f"Starting insertion for element at {i} with key={state['key']}")
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                return

            elif phase == 'shift_compare':
                if state['j'] >= 0:
                    self.comparing_indices = [state['j'], state['j'] + 1]
                    self.comparisons += 1
                    self.update_stats_label()
                    logger.debug(f"Comparing key {state['key']} with element at {state['j']} value {self.array[state['j']]}")
                    self.draw_array()
                    if self.array[state['j']] > state['key']:
                        state['phase'] = 'shift_execute'
                        logger.debug(f"Shift needed for element at {state['j']}")
                    else:
                        state['phase'] = 'place_key'
                        logger.debug("Key is in correct place")
                    if not self._should_stop_after_step() and not self.is_paused:
                        self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                    return
                else:
                    state['phase'] = 'place_key'
                    logger.debug("Reached beginning, placing key")
                    if not self._should_stop_after_step() and not self.is_paused:
                        self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                    return

            elif phase == 'shift_execute':
                logger.debug(f"Shifting element at {state['j']} to {state['j']+1}")
                # Perform shift first, then highlight
                self.array[state['j'] + 1] = self.array[state['j']]
                self.swaps += 1
                self.update_stats_label()
                self.swapping_indices = [state['j'], state['j'] + 1]
                self.comparing_indices = []
                self.draw_array()
                self.swapping_indices = []
                state['j'] -= 1
                state['phase'] = 'shift_compare'
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)
                return

            elif phase == 'place_key':
                logger.debug(f"Placing key {state['key']} at position {state['j']+1}")
                # Place key first, then highlight
                self.array[state['j'] + 1] = state['key']
                self.swaps += 1
                self.update_stats_label()
                self.swapping_indices = [state['j'] + 1]
                self.comparing_indices = []
                self.draw_array()
                self.swapping_indices = []
                # No marking as sorted
                state['i'] += 1
                state['phase'] = 'compare'
                self.draw_array()
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._insertion_sort_step)

    # ---- Quick Sort ----
    def _quick_sort_step(self):
        if self._should_stop_after_step():
            return
        if self.is_paused:
            return

        state = self.sort_state
        phase = state['phase']

        logger.debug(f"Quick step: phase={phase}, stack size={len(state.get('stack',[]))}")

        if phase == 'partition' and not state['stack']:
            logger.debug("Quick sort complete")
            self.sorted_indices = set(range(len(self.array)))
            self.comparing_indices = []
            self.swapping_indices = []
            self.pivot_index = None
            self.draw_array()
            self.finish_sort()
            return

        if phase == 'partition':
            if not state['stack']:
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
                return
            low, high = state['stack'].pop()
            logger.debug(f"Partitioning range [{low}, {high}]")
            if low < high:
                state['low'] = low
                state['high'] = high
                state['pivot'] = self.array[high]
                self.pivot_index = high
                state['i'] = low - 1
                state['j'] = low
                state['phase'] = 'compare'
                logger.debug(f"Pivot set to {self.array[high]} at index {high}")
            else:
                if low == high:
                    self.sorted_indices.add(low)
                    logger.debug(f"Single element {low} marked sorted")
                    self.draw_array()
            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
            return

        elif phase == 'compare':
            if state['j'] < state['high']:
                self.comparing_indices = [state['j'], state['high']]
                self.comparisons += 1
                self.update_stats_label()
                logger.debug(f"Comparing element at {state['j']} (value {self.array[state['j']]}) with pivot {state['pivot']}")
                self.draw_array()
                if self.array[state['j']] < state['pivot']:
                    state['i'] += 1
                    if state['i'] != state['j']:
                        state['phase'] = 'swap'
                        logger.debug(f"Partition swap needed between i={state['i']} and j={state['j']}")
                        if not self._should_stop_after_step() and not self.is_paused:
                            self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
                        return
                state['j'] += 1
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
            else:
                state['phase'] = 'pre_place_pivot'
                logger.debug("Partition scan complete, preparing pivot placement")
                if not self._should_stop_after_step() and not self.is_paused:
                    self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
            return

        elif phase == 'swap':
            i, j = state['i'], state['j']
            logger.debug(f"Executing partition swap between {i} and {j}")
            # Swap first, then highlight
            self.array[i], self.array[j] = self.array[j], self.array[i]
            self.swaps += 1
            self.update_stats_label()
            self.swapping_indices = [i, j]
            self.comparing_indices = []
            self.draw_array()
            self.swapping_indices = []
            state['j'] += 1
            state['phase'] = 'compare'
            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
            return

        elif phase == 'pre_place_pivot':
            pivot_pos = state['i'] + 1
            if pivot_pos != state['high']:
                logger.debug(f"Preparing to place pivot from {state['high']} to {pivot_pos}")
                self.array[pivot_pos], self.array[state['high']] = self.array[state['high']], self.array[pivot_pos]
                self.swaps += 1
                self.update_stats_label()
                self.swapping_indices = [pivot_pos, state['high']]
                self.comparing_indices = []
                self.draw_array()
            else:
                logger.debug("Pivot already in final position")
                self.comparing_indices = []
                self.draw_array()
            state['phase'] = 'place_pivot'
            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)
            return

        elif phase == 'place_pivot':
            pivot_pos = state['i'] + 1
            logger.debug(f"Placing pivot at {pivot_pos}")
            # already swapped in pre_place_pivot
            self.sorted_indices.add(pivot_pos)
            logger.debug(f"Pivot index {pivot_pos} now sorted")
            if pivot_pos + 1 < state['high']:
                state['stack'].append((pivot_pos + 1, state['high']))
                logger.debug(f"Pushing right partition ({pivot_pos+1}, {state['high']})")
            if state['low'] < pivot_pos - 1:
                state['stack'].append((state['low'], pivot_pos - 1))
                logger.debug(f"Pushing left partition ({state['low']}, {pivot_pos-1})")
            state['phase'] = 'partition'
            self.comparing_indices = []
            self.swapping_indices = []
            self.pivot_index = None
            self.draw_array()
            if not self._should_stop_after_step() and not self.is_paused:
                self.sort_after_id = self.root.after(self.sort_delay, self._quick_sort_step)

    # ---- Merge Sort ----
    def _merge_sort_step(self):
        if self._should_stop_after_step():
            return
        if self.is_paused:
            return

        state = self.sort_state
        if not self.clean_mode:
            # --- original merge sort, fixed splitting delay ---
            # Process splits instantly until we have a merge_state ready
            while state.get('merge_state') is None and state['stack']:
                left, right, action = state['stack'].pop()
                logger.debug(f"Merge stack pop: left={left}, right={right}, action={action}")
                if action == 'split':
                    if left < right:
                        mid = (left + right) // 2
                        state['stack'].append((left, right, 'merge'))
                        state['stack'].append((mid + 1, right, 'split'))
                        state['stack'].append((left, mid, 'split'))
                        logger.debug(f"Splitting [{left}, {right}] into [{left}, {mid}] and [{mid+1}, {right}]")
                    # no delay, continue looping
                    continue
                elif action == 'merge':
                    mid = (left + right) // 2
                    left_arr = self.array[left:mid + 1].copy()
                    right_arr = self.array[mid + 1:right + 1].copy()
                    state['merge_state'] = {
                        'left': left, 'right': right, 'mid': mid,
                        'left_arr': left_arr, 'right_arr': right_arr,
                        'i': 0, 'j': 0, 'k': left,
                        'phase': 'compare'
                    }
                    logger.debug(f"Starting merge of [{left}, {mid}] and [{mid+1}, {right}]")
                    break   # we have a merge to animate; suspend splitting

            # If no active merge and stack empty → sort complete
            if state.get('merge_state') is None and not state['stack']:
                logger.debug("Merge sort complete")
                self.sorted_indices = set(range(len(self.array)))
                self.comparing_indices = []
                self.swapping_indices = []
                self.draw_array()
                self.finish_sort()
                return

            # Animate the current merge step (if any)
            ms = state.get('merge_state')
            if ms is not None:
                logger.debug(f"Merge state: i={ms['i']}, j={ms['j']}, k={ms['k']}, phase={ms['phase']}")
                if ms['phase'] == 'compare':
                    if ms['i'] < len(ms['left_arr']) and ms['j'] < len(ms['right_arr']):
                        self.comparing_indices = [ms['left'] + ms['i'], ms['mid'] + 1 + ms['j']]
                        self.comparisons += 1
                        self.update_stats_label()
                        logger.debug(f"Comparing left[{ms['i']}]={ms['left_arr'][ms['i']]} and right[{ms['j']}]={ms['right_arr'][ms['j']]}")
                        self.draw_array()
                        if ms['left_arr'][ms['i']] <= ms['right_arr'][ms['j']]:
                            ms['chosen_side'] = 'left'
                        else:
                            ms['chosen_side'] = 'right'
                        ms['phase'] = 'copy'
                        if not self._should_stop_after_step() and not self.is_paused:
                            self.sort_after_id = self.root.after(self.sort_delay, self._merge_sort_step)
                        return
                    elif ms['i'] < len(ms['left_arr']):
                        ms['chosen_side'] = 'left'
                        ms['phase'] = 'copy'
                        logger.debug("Copying remaining left elements")
                        if not self._should_stop_after_step() and not self.is_paused:
                            self.sort_after_id = self.root.after(self.sort_delay, self._merge_sort_step)
                        return
                    elif ms['j'] < len(ms['right_arr']):
                        ms['chosen_side'] = 'right'
                        ms['phase'] = 'copy'
                        logger.debug("Copying remaining right elements")
                        if not self._should_stop_after_step() and not self.is_paused:
                            self.sort_after_id = self.root.after(self.sort_delay, self._merge_sort_step)
                        return
                    else:
                        # Merge complete – clean up and loop back to process more splits
                        logger.debug(f"Merge of range [{ms['left']}, {ms['right']}] complete")
                        state['merge_state'] = None
                        self.comparing_indices = []
                        # loop back immediately to process next split/merge
                        if not self._should_stop_after_step() and not self.is_paused:
                            self.sort_after_id = self.root.after(0, self._merge_sort_step)
                        return

                elif ms['phase'] == 'copy':
                    if ms['chosen_side'] == 'left':
                        source_idx = ms['left'] + ms['i']
                        logger.debug(f"Copying left element from {source_idx} to {ms['k']}")
                        # Perform copy first, then highlight
                        self.array[ms['k']] = ms['left_arr'][ms['i']]
                        self.swaps += 1
                        self.update_stats_label()
                        self.swapping_indices = [source_idx, ms['k']]
                        self.comparing_indices = []
                        self.draw_array()
                        ms['i'] += 1
                    else:
                        source_idx = ms['mid'] + 1 + ms['j']
                        logger.debug(f"Copying right element from {source_idx} to {ms['k']}")
                        self.array[ms['k']] = ms['right_arr'][ms['j']]
                        self.swaps += 1
                        self.update_stats_label()
                        self.swapping_indices = [source_idx, ms['k']]
                        self.comparing_indices = []
                        self.draw_array()
                        ms['j'] += 1
                    ms['k'] += 1
                    self.swapping_indices = []
                    ms['phase'] = 'compare'
                    if not self._should_stop_after_step() and not self.is_paused:
                        self.sort_after_id = self.root.after(self.sort_delay, self._merge_sort_step)
                    return

        else:
            # Clean mode merge sort: no duplicate display, comparisons visible
            if 'clean_merge' not in state:
                state['clean_merge'] = None

            # Process splits instantly (no delay) until a clean_merge is ready
            while state.get('clean_merge') is None and state['stack']:
                left, right, action = state['stack'].pop()
                if action == 'split':
                    if left < right:
                        mid = (left + right) // 2
                        state['stack'].append((left, right, 'merge'))
                        state['stack'].append((mid + 1, right, 'split'))
                        state['stack'].append((left, mid, 'split'))
                        logger.debug(f"Clean merge: splitting [{left}, {right}]")
                    # continue instantly
                    continue
                elif action == 'merge':
                    # Build the merged list and comparison pairs
                    mid = (left + right) // 2
                    left_arr = self.array[left:mid+1].copy()
                    right_arr = self.array[mid+1:right+1].copy()
                    i = j = 0
                    merged = []
                    comp_pairs = []
                    while i < len(left_arr) and j < len(right_arr):
                        comp_pairs.append( (left + i, mid + 1 + j) )
                        if left_arr[i] <= right_arr[j]:
                            merged.append(left_arr[i])
                            i += 1
                        else:
                            merged.append(right_arr[j])
                            j += 1
                    while i < len(left_arr):
                        merged.append(left_arr[i])
                        i += 1
                    while j < len(right_arr):
                        merged.append(right_arr[j])
                        j += 1
                    state['clean_merge'] = {
                        'left': left,
                        'right': right,
                        'merged': merged,
                        'comp_pairs': comp_pairs,
                        'comp_index': 0,
                        'phase': 'show_comparisons'
                    }
                    break   # we will now animate these comparisons with delay

            # If nothing to do, finish
            if state.get('clean_merge') is None and not state['stack']:
                logger.debug("Clean merge sort complete")
                self.sorted_indices = set(range(len(self.array)))
                self.comparing_indices = []
                self.swapping_indices = []
                self.draw_array()
                self.finish_sort()
                return

            # Animate the clean merge
            cm = state.get('clean_merge')
            if cm is not None:
                if cm['phase'] == 'show_comparisons':
                    if cm['comp_index'] < len(cm['comp_pairs']):
                        pair = cm['comp_pairs'][cm['comp_index']]
                        self.comparing_indices = [pair[0], pair[1]]
                        self.comparisons += 1
                        self.update_stats_label()
                        logger.debug(f"Clean merge: comparing indices {pair[0]} and {pair[1]}")
                        self.draw_array()
                        cm['comp_index'] += 1
                        if not self._should_stop_after_step() and not self.is_paused:
                            self.sort_after_id = self.root.after(self.sort_delay, self._merge_sort_step)
                        return
                    else:
                        cm['phase'] = 'apply_merge'
                        # fall through to apply_merge after a short delay
                        if not self._should_stop_after_step() and not self.is_paused:
                            self.sort_after_id = self.root.after(self.sort_delay, self._merge_sort_step)
                        return
                elif cm['phase'] == 'apply_merge':
                    left, right = cm['left'], cm['right']
                    merged = cm['merged']
                    for idx in range(left, right+1):
                        self.array[idx] = merged[idx - left]
                    self.swaps += (right - left + 1)  # counting each placement as a swap for stats
                    self.update_stats_label()
                    # Highlight the whole merged range as swapping briefly
                    self.swapping_indices = list(range(left, right+1))
                    self.comparing_indices = []
                    self.draw_array()
                    self.swapping_indices = []
                    # Clean merge done for this segment
                    state['clean_merge'] = None
                    logger.debug(f"Clean merge applied to [{left}, {right}]")
                    # Loop back immediately to process the next split/merge
                    if not self._should_stop_after_step() and not self.is_paused:
                        self.sort_after_id = self.root.after(0, self._merge_sort_step)
                    return


if __name__ == '__main__':
    logger.info("Starting Linear Sort GUI application")
    root = tk.Tk()
    app = LinearSortGUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        root.destroy()
