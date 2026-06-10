#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("728x450")
        self.root.resizable(True, True)
        self.root.minsize(600, 400)
        
        self.include_uppercase = tk.BooleanVar(value=True)
        self.include_lowercase = tk.BooleanVar(value=True)
        self.include_numbers = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=False)
        
        self.password_length = tk.IntVar(value=12)
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Password Generator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        length_frame = ttk.LabelFrame(main_frame, text="Password Length", padding="10")
        length_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(length_frame, text="Length:").grid(row=0, column=0, sticky=tk.W)
        
        length_spinbox = ttk.Spinbox(length_frame, from_=4, to=128, width=10,
                                   textvariable=self.password_length)
        length_spinbox.grid(row=0, column=1, padx=(10, 0))
        
        options_frame = ttk.LabelFrame(main_frame, text="Character Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(options_frame, text="Uppercase Letters (A-Z)",
                       variable=self.include_uppercase).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(options_frame, text="Lowercase Letters (a-z)",
                       variable=self.include_lowercase).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(options_frame, text="Numbers (0-9)",
                       variable=self.include_numbers).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(options_frame, text="Symbols (!@#$%^&*)",
                       variable=self.include_symbols).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        generate_btn = ttk.Button(main_frame, text="Generate Password",
                                command=self.generate_password)
        generate_btn.grid(row=3, column=0, columnspan=2, pady=(10, 10))
        
        result_frame = ttk.LabelFrame(main_frame, text="Generated Password", padding="10")
        result_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.password_text = tk.Text(result_frame, height=2, width=45, wrap=tk.WORD,
                                   font=("Courier", 12), state=tk.DISABLED)
        self.password_text.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        button_frame = ttk.Frame(result_frame)
        button_frame.grid(row=1, column=0, columnspan=2)
        
        copy_btn = ttk.Button(button_frame, text="Copy to Clipboard",
                            command=self.copy_password)
        copy_btn.grid(row=0, column=0, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear",
                             command=self.clear_password)
        clear_btn.grid(row=0, column=1)
        
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def generate_password(self):
        characters = ""
        
        if self.include_uppercase.get():
            characters += string.ascii_uppercase
        if self.include_lowercase.get():
            characters += string.ascii_lowercase
        if self.include_numbers.get():
            characters += string.digits
        if self.include_symbols.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not characters:
            messagebox.showwarning("No Character Types", 
                                 "Please select at least one character type!")
            return
        
        try:
            length = self.password_length.get()
            if length < 1:
                raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showwarning("Invalid Length", 
                                 "Please enter a valid positive number for length.")
            return
            
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        self.display_password(password)
    
    def display_password(self, password):
        self.password_text.config(state=tk.NORMAL)
        self.password_text.delete(1.0, tk.END)
        self.password_text.insert(1.0, password)
        self.password_text.config(state=tk.DISABLED)
    
    def copy_password(self):
        password = self.password_text.get(1.0, tk.END).strip()
        if password:
            if HAS_PYPERCLIP:
                try:
                    pyperclip.copy(password)
                    messagebox.showinfo("Copied", "Password copied to clipboard!")
                    return
                except Exception:
                    pass
            
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(password)
                self.root.update()
                messagebox.showinfo("Copied", "Password copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")
        else:
            messagebox.showwarning("No Password", "Generate a password first!")
    
    def clear_password(self):
        self.password_text.config(state=tk.NORMAL)
        self.password_text.delete(1.0, tk.END)
        self.password_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
