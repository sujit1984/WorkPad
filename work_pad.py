import tkinter as tk
import tkinter.font as tkfont

class WorkpadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workpad App")
        self.tasks_frame = tk.Frame(self.root)
        self.tasks_frame.pack(pady=10)

        self.task_entry = tk.Entry(self.root, width=40)
        self.task_entry.pack(padx=10, pady=5)
        self.task_entry.bind('<Return>', self.add_task)  # Bind Enter key

        # Create a frame to hold the buttons side by side
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=5)

        self.add_button = tk.Button(self.buttons_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.buttons_frame, text="Clear Tasks", command=self.clear_tasks)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.tasks = []

        # Prepare fonts once
        self.default_font = tkfont.nametofont("TkDefaultFont")

    def add_task(self, event=None):  # Accept event for binding compatibility
        task_text = self.task_entry.get().strip()
        if task_text:
            var = tk.BooleanVar()
            # Copy the default font for strikethrough
            strike_font = self.default_font.copy()
            strike_font.configure(overstrike=1)

            row = tk.Frame(self.tasks_frame)
            label = tk.Label(row, text=task_text, font=self.default_font)
            cb = tk.Checkbutton(
                row,
                variable=var,
                command=lambda l=label, v=var, d=self.default_font, s=strike_font:
                    self.toggle_strike(l, v, d, s)
            )
            cb.pack(side=tk.LEFT)
            label.pack(side=tk.LEFT, padx=5)
            row.pack(anchor='w', pady=2)
            self.tasks.append({'var': var, 'label': label, 'row': row, 'cb': cb})

            # Bind double-click to edit
            label.bind("<Double-Button-1>", lambda e, l=label, t=task_text: self.edit_task(l))

            self.task_entry.delete(0, tk.END)

    def toggle_strike(self, label, var, default_font, strike_font):
        if var.get():
            label.configure(font=strike_font)
        else:
            label.configure(font=default_font)

    def clear_tasks(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        self.tasks.clear()

    def edit_task(self, label):
        # Get the current text
        current_text = label.cget("text")
        parent = label.master

        # Hide the label
        label.pack_forget()

        # Create an Entry widget in place of the label
        edit_entry = tk.Entry(parent, width=40)
        edit_entry.insert(0, current_text)
        edit_entry.pack(side=tk.LEFT, padx=5)
        edit_entry.focus_set()

        def save_edit(event=None):
            new_text = edit_entry.get().strip()
            if new_text:
                label.config(text=new_text)
            edit_entry.destroy()
            label.pack(side=tk.LEFT, padx=5)

        # Save on Enter or focus out
        edit_entry.bind("<Return>", save_edit)
        edit_entry.bind("<FocusOut>", save_edit)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkpadApp(root)
    root.mainloop()
