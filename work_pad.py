import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
from datetime import datetime
import json
import os

DATA_FILE = "workpad_data.json"

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
        self.last_date = datetime.today().strftime('%Y-%m-%d')
        self.date_entry.insert(0, self.last_date)

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

        # Start the dynamic date updater
        self.update_date_periodically()

        # Load data from file if exists
        self.load_data()

        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

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
            self.save_data()

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
            self.save_data()

    def toggle_subgoal(self, var, frame):
        label = frame.winfo_children()[1]
        label.configure(font=self.strike_font if var.get() else self.default_font)
        self.save_data()

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
            self.save_data()

    def toggle_task(self, var, frame):
        label = frame.winfo_children()[2]
        label.configure(font=self.strike_font if var.get() else self.default_font)
        self.save_data()

    def edit_task(self, frame):
        # Placeholder for edit logic
        pass

    def clear_tasks(self):
        for task in self.tasks:
            task['frame'].destroy()
        self.tasks.clear()
        self.save_data()

    def remove_done_tasks(self):
        to_remove = [task for task in self.tasks if task['var'].get()]
        for task in to_remove:
            task['frame'].destroy()
            self.tasks.remove(task)
        self.save_data()

    # ================== Persistent Storage ==================
    def save_data(self):
        data = {
            "goals": [],
            "tasks": []
        }
        # Save goals and subgoals
        for goal in self.goals:
            goal_frame = goal['frame']
            header = goal_frame.winfo_children()[0]
            goal_label = header.winfo_children()[0]
            goal_text = goal_label.cget("text")
            subgoals = []
            for sub in goal['subgoals']:
                subgoals.append({
                    "text": sub['label'].cget("text"),
                    "done": sub['var'].get()
                })
            data["goals"].append({
                "text": goal_text,
                "subgoals": subgoals
            })
        # Save tasks
        for task in self.tasks:
            data["tasks"].append({
                "text": task['label'].cget("text"),
                "date": task['date'].cget("text"),
                "done": task['var'].get()
            })
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Load goals
        for goal_data in data.get("goals", []):
            self.goal_entry.delete(0, tk.END)
            self.goal_entry.insert(0, goal_data["text"])
            self.add_goal()
            goal = self.goals[-1]
            for subgoal in goal_data.get("subgoals", []):
                sub_entry = goal['frame'].winfo_children()[1].winfo_children()[0]
                sub_entry.delete(0, tk.END)
                sub_entry.insert(0, subgoal["text"])
                self.add_subgoal(goal['frame'], sub_entry)
                sub = goal['subgoals'][-1]
                if subgoal.get("done"):
                    sub['var'].set(True)
                    self.toggle_subgoal(sub['var'], sub['frame'])
        # Load tasks
        for task_data in data.get("tasks", []):
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, task_data["date"])
            self.task_entry.delete(0, tk.END)
            self.task_entry.insert(0, task_data["text"])
            self.add_task()
            task = self.tasks[-1]
            if task_data.get("done"):
                task['var'].set(True)
                self.toggle_task(task['var'], task['frame'])

    def on_close(self):
        self.save_data()
        self.root.destroy()

    # ================== Dynamic Date Updater ==================
    def update_date_periodically(self):
        """Check and update the date entry every 2 hours."""
        current_date = datetime.today().strftime('%Y-%m-%d')
        if self.last_date != current_date:
            self.last_date = current_date
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, current_date)
        # Schedule to run again after 2 hours (7200000 ms)
        self.root.after(7200000, self.update_date_periodically)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkpadApp(root)
    root.mainloop()
