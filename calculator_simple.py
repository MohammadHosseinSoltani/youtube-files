import tkinter as tk

class Calculator:
    def __init__(self):
        # Create main window
        self.window = tk.Tk()
        self.window.title("Calculator")
        self.window.geometry("300x400")
        self.window.resizable(False, False)
        
        # Variable to store the current expression
        self.expression = ""
        
        # Create the display entry widget
        self.display_var = tk.StringVar()
        self.display = tk.Entry(
            self.window, 
            textvariable=self.display_var,
            font=('Arial', 16),
            justify='right',
            state='readonly',
            bg='white'
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        
        # Create calculator buttons
        self.create_buttons()
        
        # Configure grid weights for responsive layout
        for i in range(4):
            self.window.grid_columnconfigure(i, weight=1)
        for i in range(6):
            self.window.grid_rowconfigure(i, weight=1)
    
    def create_buttons(self):
        # Button layout: (text, row, column, columnspan)
        buttons = [
            ('C', 1, 0, 1), ('±', 1, 1, 1), ('%', 1, 2, 1), ('÷', 1, 3, 1),
            ('7', 2, 0, 1), ('8', 2, 1, 1), ('9', 2, 2, 1), ('×', 2, 3, 1),
            ('4', 3, 0, 1), ('5', 3, 1, 1), ('6', 3, 2, 1), ('-', 3, 3, 1),
            ('1', 4, 0, 1), ('2', 4, 1, 1), ('3', 4, 2, 1), ('+', 4, 3, 1),
            ('0', 5, 0, 2), ('.', 5, 2, 1), ('=', 5, 3, 1)
        ]
        
        for (text, row, col, colspan) in buttons:
            if text in ['÷', '×', '-', '+', '=']:
                # Operator buttons with different color
                btn = tk.Button(
                    self.window,
                    text=text,
                    font=('Arial', 14, 'bold'),
                    bg='#ff9500',
                    fg='white',
                    command=lambda t=text: self.on_button_click(t)
                )
            elif text in ['C', '±', '%']:
                # Function buttons with gray color
                btn = tk.Button(
                    self.window,
                    text=text,
                    font=('Arial', 14),
                    bg='#a6a6a6',
                    fg='black',
                    command=lambda t=text: self.on_button_click(t)
                )
            else:
                # Number buttons
                btn = tk.Button(
                    self.window,
                    text=text,
                    font=('Arial', 14),
                    bg='#333333',
                    fg='white',
                    command=lambda t=text: self.on_button_click(t)
                )
            
            btn.grid(
                row=row, 
                column=col, 
                columnspan=colspan,
                padx=2, 
                pady=2, 
                sticky='nsew'
            )
    
    def on_button_click(self, char):
        """Handle button clicks and perform calculations"""
        if char == 'C':
            # Clear everything
            self.expression = ""
            self.display_var.set("")
        
        elif char == '=':
            # Calculate the result
            try:
                # Replace display symbols with Python operators
                calc_expression = self.expression.replace('×', '*').replace('÷', '/')
                result = str(eval(calc_expression))
                self.display_var.set(result)
                self.expression = result
            except:
                self.display_var.set("Error")
                self.expression = ""
        
        elif char == '±':
            # Toggle positive/negative
            if self.expression and self.expression[0] == '-':
                self.expression = self.expression[1:]
            elif self.expression:
                self.expression = '-' + self.expression
            self.display_var.set(self.expression)
        
        elif char == '%':
            # Convert to percentage
            try:
                result = str(float(self.expression) / 100)
                self.expression = result
                self.display_var.set(result)
            except:
                self.display_var.set("Error")
        
        else:
            # Add number or operator to expression
            self.expression += char
            self.display_var.set(self.expression)
    
    def run(self):
        """Start the calculator application"""
        self.window.mainloop()

# Create and run the calculator
if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
