import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
from datetime import datetime


class WorkpadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workpad App")

        # Main container
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ================== Goals Section ==================
        goals_container = tk.LabelFrame(self.main_frame, text=" Goals ", font=("Arial", 12, "bold"))
        goals_container.pack(fill=tk.X, pady=(0, 10))

        # Goal entry
        self.goal_entry = tk.Entry(goals_container, width=40)
        self.goal_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.goal_entry.bind('<Return>', lambda e: self.add_goal())

        # Goal add button
        self.goal_add_btn = tk.Button(goals_container, text="Add Goal", command=self.add_goal)
        self.goal_add_btn.pack(side=tk.LEFT, padx=5)

        # Goals display area
        self.goals_frame = tk.Frame(self.main_frame)
        self.goals_frame.pack(fill=tk.X)
        self.goals = []

        # ================== Tasks Section ==================
        tasks_container = tk.LabelFrame(self.main_frame, text=" Daily Tasks ", font=("Arial", 12, "bold"))
        tasks_container.pack(fill=tk.BOTH, expand=True)

        # Date selection
        self.date_frame = tk.Frame(tasks_container)
        self.date_frame.pack(fill=tk.X, pady=5)

        self.date_entry = tk.Entry(self.date_frame, width=15)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))

        self.task_entry = tk.Entry(self.date_frame, width=40)
        self.task_entry.pack(side=tk.LEFT, padx=5)
        self.task_entry.bind('<Return>', lambda e: self.add_task())

        # Task buttons
        self.task_buttons_frame = tk.Frame(tasks_container)
        self.task_buttons_frame.pack(fill=tk.X, pady=5)

        self.add_btn = tk.Button(self.task_buttons_frame, text="Add Task", command=self.add_task)
        self.add_btn.pack(side=tk.LEFT, padx=2)

        self.clear_btn = tk.Button(self.task_buttons_frame, text="Clear Tasks", command=self.clear_tasks)
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        self.remove_done_btn = tk.Button(self.task_buttons_frame, text="Remove Done", command=self.remove_done_tasks)
        self.remove_done_btn.pack(side=tk.LEFT, padx=2)

        # Tasks display
        self.tasks_frame = tk.Frame(tasks_container)
        self.tasks_frame.pack(fill=tk.BOTH, expand=True)
        self.tasks = []

        # Font setup
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.strike_font = self.default_font.copy()
        self.strike_font.configure(overstrike=1)

    # ================== Goals Functions ==================
    def add_goal(self):
        goal_text = self.goal_entry.get().strip()
        if goal_text:
            goal_frame = tk.Frame(self.goals_frame, bd=1, relief=tk.GROOVE)
            goal_frame.pack(fill=tk.X, pady=2, padx=5)

            # Goal header
            header_frame = tk.Frame(goal_frame)
            header_frame.pack(fill=tk.X)

            goal_label = tk.Label(header_frame, text=goal_text, font=("Arial", 10, "bold"))
            goal_label.pack(side=tk.LEFT)

            # Subgoal entry
            sub_frame = tk.Frame(goal_frame)
            sub_frame.pack(fill=tk.X, padx=10, pady=5)

            sub_entry = tk.Entry(sub_frame, width=35)
            sub_entry.pack(side=tk.LEFT)
            sub_entry.bind('<Return>', lambda e, s=sub_entry, g=goal_frame: self.add_subgoal(g, s))

            sub_btn = tk.Button(sub_frame, text="+ Subgoal",
                                command=lambda s=sub_entry, g=goal_frame: self.add_subgoal(g, s))
            sub_btn.pack(side=tk.LEFT, padx=5)

            self.goals.append({
                'frame': goal_frame,
                'subgoals': []
            })
            self.goal_entry.delete(0, tk.END)

    def add_subgoal(self, goal_frame, entry_widget):
        sub_text = entry_widget.get().strip()
        if sub_text:
            sub_frame = tk.Frame(goal_frame)
            sub_frame.pack(fill=tk.X, padx=15, pady=2)

            var = tk.BooleanVar()
            cb = tk.Checkbutton(sub_frame, variable=var,
                                command=lambda v=var, f=sub_frame:
                                self.toggle_subgoal(v, f))
            cb.pack(side=tk.LEFT)

            label = tk.Label(sub_frame, text=sub_text)
            label.pack(side=tk.LEFT)

            entry_widget.delete(0, tk.END)

            self.goals[self.goals.index(next(g for g in self.goals if g['frame'] == goal_frame))] \
                ['subgoals'].append({
                'var': var,
                'label': label,
                'frame': sub_frame
            })

    def toggle_subgoal(self, var, frame):
        label = frame.winfo_children()[1]
        label.configure(font=self.strike_font if var.get() else self.default_font)

    # ================== Tasks Functions ==================
    def add_task(self, event=None):
        task_text = self.task_entry.get().strip()
        date_text = self.date_entry.get().strip()
        if task_text and date_text:
            var = tk.BooleanVar()

            task_frame = tk.Frame(self.tasks_frame)
            task_frame.pack(fill=tk.X, pady=2)

            # Checkbox
            cb = tk.Checkbutton(task_frame, variable=var,
                                command=lambda v=var, f=task_frame: self.toggle_task(v, f))
            cb.pack(side=tk.LEFT)

            # Date label
            date_label = tk.Label(task_frame, text=date_text, width=10, anchor='w')
            date_label.pack(side=tk.LEFT)

            # Task text
            task_label = tk.Label(task_frame, text=task_text)
            task_label.pack(side=tk.LEFT, padx=5)

            # Edit button
            edit_btn = tk.Button(task_frame, text="✎", command=lambda f=task_frame: self.edit_task(f))
            edit_btn.pack(side=tk.RIGHT)

            self.tasks.append({
                'var': var,
                'frame': task_frame,
                'date': date_label,
                'label': task_label
            })

            self.task_entry.delete(0, tk.END)

    def toggle_task(self, var, frame):
        label = frame.winfo_children()[2]
        label.configure(font=self.strike_font if var.get() else self.default_font)

    def edit_task(self, frame):
        # Placeholder for edit logic
        pass

    def clear_tasks(self):
        for task in self.tasks:
            task['frame'].destroy()
        self.tasks.clear()

    def remove_done_tasks(self):
        to_remove = [task for task in self.tasks if task['var'].get()]
        for task in to_remove:
            task['frame'].destroy()
            self.tasks.remove(task)



if __name__ == "__main__":
    root = tk.Tk()
    app = WorkpadApp(root)
    root.mainloop()
