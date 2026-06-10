import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --- CONSTANTS & THEME ---
GOLDEN_RATIO = 1.61803398875
APP_WIDTH = 728
APP_HEIGHT = int(APP_WIDTH / GOLDEN_RATIO)  # 450px

BG_COLOR = "#F4F5F7"         # Modern soft off-white
TEXT_COLOR = "#2C3E50"       # Dark slate blue for high readability
ACCENT_COLOR = "#3498DB"     # Bright modern blue
MAX_NAME_LENGTH = 40         # Security: Prevent infinite input strings
MAX_COMMENT_LENGTH = 500

class PerfectFormApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.apply_theme()
        self.create_variables()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_window(self):
        """Configure the optimal window properties"""
        self.root.title("Registration Form")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.minsize(550, 400)
        self.root.configure(bg=BG_COLOR)
        
        # Intercept window close (X button) to prevent accidental data loss
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)
        
    def apply_theme(self):
        """Apply a modern, clean styling via ttk.Style"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure Frames & Labels
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#1A252F')
        
        # Configure Inputs (Radio, Checkbox)
        self.style.configure('TRadiobutton', background=BG_COLOR, font=('Segoe UI', 10))
        self.style.configure('TCheckbutton', background=BG_COLOR, font=('Segoe UI', 10))
        
        # Configure Buttons
        self.style.configure(
            'Action.TButton', 
            font=('Segoe UI', 10, 'bold'), 
            padding=6,
            background=ACCENT_COLOR,
            foreground="white"
        )
        self.style.map('Action.TButton', background=[('active', '#2980B9')]) # Darker blue on hover
        
        self.style.configure('Secondary.TButton', font=('Segoe UI', 10), padding=6)

    def create_variables(self):
        """Initialize and secure Tkinter variables"""
        self.name_var = tk.StringVar()
        # Live trace to prevent pasting/typing massive strings
        self.name_var.trace_add("write", self.limit_name_length)
        
        self.age_var = tk.StringVar(value="18-25")
        self.gender_var = tk.StringVar(value="Male")
        
        self.programming_var = tk.BooleanVar(value=False)
        self.music_var = tk.BooleanVar(value=False)
        self.sports_var = tk.BooleanVar(value=False)

    def limit_name_length(self, *args):
        """Enforce maximum character limit on the name field"""
        current_text = self.name_var.get()
        if len(current_text) > MAX_NAME_LENGTH:
            self.name_var.set(current_text[:MAX_NAME_LENGTH])

    def create_widgets(self):
        """Create and arrange all GUI widgets with perfect scaling"""
        main_frame = ttk.Frame(self.root, padding="25 20 25 20")
        main_frame.pack(expand=True, fill="both")
        
        # Responsive Grid Configurations
        main_frame.columnconfigure(1, weight=1)  # Input column expands horizontally
        main_frame.rowconfigure(5, weight=1)     # Comments row expands vertically
        
        # --- TITLE ---
        title = ttk.Label(main_frame, text="User Profile Configuration", style='Header.TLabel')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # --- NAME ---
        ttk.Label(main_frame, text="Full Name:").grid(row=1, column=0, sticky="w", pady=8)
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, font=('Segoe UI', 10))
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=8, padx=(15, 0))
        
        # --- AGE ---
        ttk.Label(main_frame, text="Age Range:").grid(row=2, column=0, sticky="w", pady=8)
        self.age_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.age_var, 
            values=["18-25", "26-35", "36-45", "46-55", "55+"],
            state="readonly",
            font=('Segoe UI', 10)
        )
        self.age_combo.grid(row=2, column=1, sticky="ew", pady=8, padx=(15, 0))
        
        # --- INTERESTS ---
        ttk.Label(main_frame, text="Interests:").grid(row=3, column=0, sticky="nw", pady=8)
        interests_frame = ttk.Frame(main_frame)
        interests_frame.grid(row=3, column=1, sticky="ew", pady=8, padx=(15, 0))
        
        ttk.Checkbutton(interests_frame, text="Programming", variable=self.programming_var).pack(side="left", padx=(0, 15))
        ttk.Checkbutton(interests_frame, text="Music", variable=self.music_var).pack(side="left", padx=(0, 15))
        ttk.Checkbutton(interests_frame, text="Sports", variable=self.sports_var).pack(side="left")
        
        # --- GENDER ---
        ttk.Label(main_frame, text="Gender:").grid(row=4, column=0, sticky="w", pady=8)
        gender_frame = ttk.Frame(main_frame)
        gender_frame.grid(row=4, column=1, sticky="ew", pady=8, padx=(15, 0))
        
        ttk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male").pack(side="left", padx=(0, 15))
        ttk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female").pack(side="left", padx=(0, 15))
        ttk.Radiobutton(gender_frame, text="Other", variable=self.gender_var, value="Other").pack(side="left")
        
        # --- COMMENTS (Fixed: Properly scales vertically) ---
        ttk.Label(main_frame, text="Comments:").grid(row=5, column=0, sticky="nw", pady=8)
        self.text_area = scrolledtext.ScrolledText(main_frame, width=30, height=5, wrap=tk.WORD, font=('Segoe UI', 10))
        self.text_area.grid(row=5, column=1, sticky="nsew", pady=8, padx=(15, 0))
        
        # Event to limit text area characters
        self.text_area.bind('<KeyRelease>', self.limit_comment_length)
        
        # --- BUTTONS ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0), sticky="e")
        
        # Buttons aligned right-to-left for modern OS standards
        ttk.Button(button_frame, text="Submit", style='Action.TButton', command=self.submit_form).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="Clear", style='Secondary.TButton', command=self.clear_form).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="Exit", style='Secondary.TButton', command=self.safe_exit).pack(side="right")
        
        self.name_entry.focus() # Auto-focus first input field

    def setup_bindings(self):
        """Keyboard accessibility"""
        self.root.bind('<Return>', lambda event: self.submit_form())
        self.root.bind('<Escape>', lambda event: self.safe_exit())

    def limit_comment_length(self, event):
        """Security: Restrict Comments to prevent memory overhead"""
        content = self.text_area.get("1.0", tk.END)
        if len(content) > MAX_COMMENT_LENGTH:
            self.text_area.delete(f"1.0 + {MAX_COMMENT_LENGTH}c", tk.END)
            self.text_area.mark_set(tk.INSERT, tk.END)

    def submit_form(self):
        """Validate and handle form submission securely"""
        name = self.name_var.get().strip()
        
        # Robust Validation
        if not name:
            messagebox.showwarning("Validation Error", "Please provide a Full Name.", parent=self.root)
            self.name_entry.focus()
            return
            
        # Data Extraction
        age = self.age_var.get()
        gender = self.gender_var.get()
        comments = self.text_area.get("1.0", tk.END).strip()
        
        interests = [
            i for i, var in zip(["Programming", "Music", "Sports"], 
                               [self.programming_var, self.music_var, self.sports_var]) 
            if var.get()
        ]
        interests_str = ", ".join(interests) if interests else "None"
        
        # Success Display
        info_message = (
            f"Registration Successful!\n\n"
            f"Name: {name}\n"
            f"Age Range: {age}\n"
            f"Gender: {gender}\n"
            f"Interests: {interests_str}\n"
            f"Comments:\n{comments if comments else 'None provided'}"
        )
        
        messagebox.showinfo("Success", info_message, parent=self.root)
        self.clear_form()
        
    def clear_form(self):
        """Reset state cleanly"""
        self.name_var.set("")
        self.age_var.set("18-25")
        self.gender_var.set("Male")
        self.programming_var.set(False)
        self.music_var.set(False)
        self.sports_var.set(False)
        self.text_area.delete("1.0", tk.END)
        
        self.name_entry.focus() # Reset cursor to top

    def safe_exit(self):
        # Only ask if they typed something
        if self.name_var.get().strip() or self.text_area.get("1.0", tk.END).strip():
            if not messagebox.askyesno("Exit", "You have unsaved data. Are you sure you want to exit?", parent=self.root):
                return
                
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PerfectFormApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
