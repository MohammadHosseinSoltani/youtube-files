import tkinter as tk
from decimal import Decimal, InvalidOperation

# --- THEME & UI CONSTANTS ---
GOLDEN_RATIO = 1.618
APP_WIDTH = 340
APP_HEIGHT = int(APP_WIDTH * GOLDEN_RATIO) # 550px

BG_COLOR = "#1C1C1C"       # Deep dark background
TEXT_COLOR = "#FFFFFF"     # White text
NUM_BG = "#505050"         # Dark gray for numbers
NUM_ACTIVE = "#737373"     # Lighter gray for number hover
OP_BG = "#FF9F0A"          # Vibrant orange for operators
OP_ACTIVE = "#FFB340"      # Lighter orange for operator hover
UTIL_BG = "#D4D4D2"        # Light gray for utils (C, ±, %)
UTIL_ACTIVE = "#EAEAEA"    # Lighter gray for utils hover
UTIL_TEXT = "#000000"      # Black text for top row

MAX_DIGITS = 12            # Prevent text overflow

class PerfectCalculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Calculator")
        self.window.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.window.resizable(False, False)
        self.window.configure(bg=BG_COLOR)
        
        # State Machine Variables
        self.display_value = "0"
        self.stored_value = None
        self.operator = None
        self.waiting_for_new_value = True
        self.last_operand = None  # To allow repeated '=' presses
        self.error_state = False
        
        self.create_display()
        self.create_buttons()
        self.bind_keys()

    def create_display(self):
        """Creates a responsive, borderless display area."""
        self.display_frame = tk.Frame(self.window, bg=BG_COLOR)
        self.display_frame.pack(expand=True, fill="both")
        
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        self.display_label = tk.Label(
            self.display_frame, 
            textvariable=self.display_var,
            font=("Helvetica", 48),  # Fixed: Removed 'light'
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="e",
            padx=20
        )
        self.display_label.pack(expand=True, fill="both", side="bottom")

    def create_buttons(self):
        """Creates the grid of buttons using modern styling."""
        buttons_frame = tk.Frame(self.window, bg=BG_COLOR)
        buttons_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Layout mapping: (Text, Row, Col, Colspan, BG Color, Active Color, Text Color, Command)
        layout = [
            ('C', 0, 0, 1, UTIL_BG, UTIL_ACTIVE, UTIL_TEXT, self.clear),
            ('±', 0, 1, 1, UTIL_BG, UTIL_ACTIVE, UTIL_TEXT, self.toggle_sign),
            ('%', 0, 2, 1, UTIL_BG, UTIL_ACTIVE, UTIL_TEXT, self.percentage),
            ('÷', 0, 3, 1, OP_BG, OP_ACTIVE, TEXT_COLOR, lambda: self.set_operator('/')),

            ('7', 1, 0, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('7')),
            ('8', 1, 1, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('8')),
            ('9', 1, 2, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('9')),
            ('×', 1, 3, 1, OP_BG, OP_ACTIVE, TEXT_COLOR, lambda: self.set_operator('*')),

            ('4', 2, 0, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('4')),
            ('5', 2, 1, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('5')),
            ('6', 2, 2, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('6')),
            ('−', 2, 3, 1, OP_BG, OP_ACTIVE, TEXT_COLOR, lambda: self.set_operator('-')),

            ('1', 3, 0, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('1')),
            ('2', 3, 1, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('2')),
            ('3', 3, 2, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('3')),
            ('+', 3, 3, 1, OP_BG, OP_ACTIVE, TEXT_COLOR, lambda: self.set_operator('+')),

            ('0', 4, 0, 2, NUM_BG, NUM_ACTIVE, TEXT_COLOR, lambda: self.input_number('0')),
            ('.', 4, 2, 1, NUM_BG, NUM_ACTIVE, TEXT_COLOR, self.input_decimal),
            ('=', 4, 3, 1, OP_BG, OP_ACTIVE, TEXT_COLOR, self.calculate),
        ]

        for i in range(5):
            buttons_frame.rowconfigure(i, weight=1)
        for i in range(4):
            buttons_frame.columnconfigure(i, weight=1)

        for (text, row, col, span, bg, abg, fg, cmd) in layout:
            btn = tk.Button(
                buttons_frame, text=text, bg=bg, fg=fg,
                activebackground=abg, activeforeground=fg,
                font=("Helvetica", 20), borderwidth=0, highlightthickness=0,
                command=cmd, relief="flat", cursor="hand2"
            )
            btn.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=3, pady=3)

    def bind_keys(self):
        """Binds keyboard strokes to calculator functions."""
        for i in range(10):
            self.window.bind(str(i), lambda e, num=str(i): self.input_number(num))
        
        self.window.bind('.', lambda e: self.input_decimal())
        self.window.bind('<Return>', lambda e: self.calculate())
        self.window.bind('<KP_Enter>', lambda e: self.calculate())
        self.window.bind('=', lambda e: self.calculate())
        self.window.bind('+', lambda e: self.set_operator('+'))
        self.window.bind('-', lambda e: self.set_operator('-'))
        self.window.bind('*', lambda e: self.set_operator('*'))
        self.window.bind('/', lambda e: self.set_operator('/'))
        self.window.bind('<BackSpace>', lambda e: self.backspace())
        self.window.bind('<Escape>', lambda e: self.clear())

    def update_display(self):
        """Formats the number with commas and dynamic font sizing."""
        if self.error_state:
            self.display_var.set("Error")
            self.display_label.config(font=("Helvetica", 40)) # Fixed
            return

        # Separate minus sign, integer, and decimal parts
        val = self.display_value
        is_negative = val.startswith('-')
        if is_negative: val = val[1:]

        parts = val.split('.')
        int_part = parts[0]
        dec_part = f".{parts[1]}" if len(parts) > 1 else ""

        # Add commas to integer part
        if len(int_part) > 0:
            formatted_int = f"{int(int_part):,}"
        else:
            formatted_int = "0"

        formatted_val = f"{'-' if is_negative else ''}{formatted_int}{dec_part}"
        
        # Dynamic font sizing
        length = len(formatted_val)
        if length > 12: font_size = 28
        elif length > 9: font_size = 36
        else: font_size = 48
        
        self.display_label.config(font=("Helvetica", font_size)) # Fixed
        self.display_var.set(formatted_val)

    # --- LOGIC ---

    def input_number(self, num):
        if self.error_state: self.clear()
        
        if self.waiting_for_new_value:
            self.display_value = num
            self.waiting_for_new_value = False
        else:
            # Prevent typing more than MAX_DIGITS
            if len(self.display_value.replace('.', '').replace('-', '')) < MAX_DIGITS:
                if self.display_value == "0":
                    self.display_value = num
                else:
                    self.display_value += num
        self.update_display()

    def input_decimal(self):
        if self.error_state: self.clear()
        
        if self.waiting_for_new_value:
            self.display_value = "0."
            self.waiting_for_new_value = False
        elif "." not in self.display_value:
            self.display_value += "."
        self.update_display()

    def set_operator(self, op):
        if self.error_state: self.clear()
        
        if not self.waiting_for_new_value and self.operator:
            self.calculate()
        
        self.operator = op
        self.stored_value = self.display_value
        self.waiting_for_new_value = True

    def calculate(self):
        if self.error_state or not self.operator: 
            return

        # If user presses '=' repeatedly, reuse the last typed number
        if self.waiting_for_new_value and self.last_operand:
            second_operand = self.last_operand
        else:
            second_operand = self.display_value
            self.last_operand = second_operand

        try:
            # Using Decimal prevents floating point glitches (e.g. 0.1+0.2=0.300004)
            num1 = Decimal(self.stored_value)
            num2 = Decimal(second_operand)

            if self.operator == '+': result = num1 + num2
            elif self.operator == '-': result = num1 - num2
            elif self.operator == '*': result = num1 * num2
            elif self.operator == '/':
                if num2 == 0: raise ZeroDivisionError
                result = num1 / num2

            # Clean up trailing zeros (e.g., 5.0 -> 5)
            result = result.normalize()
            self.display_value = str(result)
            self.stored_value = self.display_value
            self.waiting_for_new_value = True
            self.update_display()

        except (ZeroDivisionError, InvalidOperation):
            self.error_state = True
            self.update_display()

    def percentage(self):
        if self.error_state: return
        try:
            val = Decimal(self.display_value) / Decimal('100')
            self.display_value = str(val.normalize())
            self.waiting_for_new_value = True
            self.update_display()
        except:
            pass

    def toggle_sign(self):
        if self.error_state or self.display_value == "0" or self.display_value == "0.": return
        
        if self.display_value.startswith('-'):
            self.display_value = self.display_value[1:]
        else:
            self.display_value = '-' + self.display_value
        self.update_display()

    def backspace(self):
        if self.error_state or self.waiting_for_new_value: return
        
        self.display_value = self.display_value[:-1]
        if self.display_value in ("", "-"):
            self.display_value = "0"
            self.waiting_for_new_value = True
            
        self.update_display()

    def clear(self):
        self.display_value = "0"
        self.stored_value = None
        self.operator = None
        self.waiting_for_new_value = True
        self.last_operand = None
        self.error_state = False
        self.update_display()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PerfectCalculator()
    app.run()
