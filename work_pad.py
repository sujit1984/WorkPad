import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont

class WorkpadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workpad App")
        self.tasks_frame = tk.Frame(self.root)
        self.tasks_frame.pack(pady=10)

        self.task_entry = tk.Entry(self.root, width=40)
        self.task_entry.pack(padx=10, pady=5)
        self.task_entry.bind('<Return>', self.add_task)

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=5)

        self.add_button = tk.Button(self.buttons_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.buttons_frame, text="Clear Tasks", command=self.confirm_clear)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.remove_done_button = tk.Button(self.buttons_frame, text="Remove Done", command=self.remove_done_tasks)
        self.remove_done_button.pack(side=tk.LEFT, padx=5)

        self.tasks = []
        self.default_font = tkfont.nametofont("TkDefaultFont")

    def add_task(self, event=None):
        task_text = self.task_entry.get().strip()
        if task_text:
            var = tk.BooleanVar()
            strike_font = self.default_font.copy()
            strike_font.configure(overstrike=1)

            row = tk.Frame(self.tasks_frame)
            serial_label = tk.Label(row, text=f"{len(self.tasks)+1}.", width=4, anchor='e', font=self.default_font)
            serial_label.pack(side=tk.LEFT, padx=(0, 5))

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

            self.tasks.append({'var': var, 'label': label, 'row': row, 'cb': cb, 'serial_label': serial_label})
            label.bind("<Double-Button-1>", lambda e, l=label: self.edit_task(l))
            self.task_entry.delete(0, tk.END)
            self.update_task_numbers()

    def toggle_strike(self, label, var, default_font, strike_font):
        if var.get():
            label.configure(font=strike_font)
        else:
            label.configure(font=default_font)

    def confirm_clear(self):
        if self.tasks:
            response = messagebox.askyesno(
                "Confirm Clear",
                "Are you sure you want to delete all tasks?",
                icon='warning'
            )
            if response:
                self.clear_tasks()

    def clear_tasks(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        self.tasks.clear()
        self.save_tasks()

    def edit_task(self, label):
        current_text = label.cget("text")
        parent = label.master
        label.pack_forget()
        edit_entry = tk.Entry(parent, width=40)
        edit_entry.insert(0, current_text)
        edit_entry.pack(side=tk.LEFT, padx=5)
        edit_entry.focus_set()

        def save_edit(event=None):
            new_text = edit_entry.get().strip()
            if new_text:
                label.config(text=new_text)
                for task in self.tasks:
                    if task['label'] == label:
                        task['label'].config(text=new_text)
                        break
            edit_entry.destroy()
            label.pack(side=tk.LEFT, padx=5)

        edit_entry.bind('<Return>', save_edit)
        edit_entry.bind('<FocusOut>', save_edit)

    def update_task_numbers(self):
        for idx, task in enumerate(self.tasks, 1):
            task['serial_label'].config(text=f"{idx}.")

    def remove_done_tasks(self):
        # Save all tasks (including done) before removing
        self.save_tasks()
        # Archive the done tasks before removing them
        done_tasks = [task for task in self.tasks if task['var'].get()]
        self.archive_tasks(done_tasks)
        # Remove all checked (done) tasks from GUI and self.tasks
        for task in done_tasks:
            task['row'].destroy()
            self.tasks.remove(task)
        self.update_task_numbers()
        messagebox.showinfo("Info", f"Removed {len(done_tasks)} completed task(s). All tasks were saved to tasks.txt and completed tasks archived.")

    def save_tasks(self):
        # Save all tasks (done and pending) to tasks.txt
        with open("tasks.txt", "w", encoding="utf-8") as f:
            for task in self.tasks:
                status = "DONE" if task['var'].get() else "PENDING"
                f.write(f"{task['label'].cget('text')} | {status}\n")

    def archive_tasks(self, done_tasks):
        # Append done tasks to an archive file
        with open("tasks_archive.txt", "a", encoding="utf-8") as f:
            for task in done_tasks:
                f.write(f"{task['label'].cget('text')} | DONE\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkpadApp(root)
    root.mainloop()
