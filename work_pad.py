import tkinter as tk
import json
import os

DATA_FILE = "task_goals_data.json"


# ---------------------------
# 1. SubGoalSection (unchanged)
# ---------------------------
class SubGoalSection(tk.Frame):
    def __init__(self, master, subgoals, save_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.save_callback = save_callback
        self.subgoal_vars = []
        self.subgoal_frames = []
        self.subgoals_frame = tk.Frame(self)
        self.subgoals_frame.pack(fill=tk.BOTH, expand=True)
        self.entry_frame = tk.Frame(self)
        self.entry = tk.Entry(self.entry_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda event: self.add_subgoal())
        self.add_btn = tk.Button(self.entry_frame, text="Add Sub-goal", command=self.add_subgoal)
        self.add_btn.pack(side=tk.LEFT, padx=2)
        self.entry_frame.pack(fill=tk.X, pady=3)
        for sg in subgoals:
            self.add_subgoal(sg['text'], sg['done'])

    def add_subgoal(self, text=None, checked=False):
        if text is None:
            text = self.entry.get().strip()
        if not text:
            return
        var = tk.BooleanVar(value=checked)
        frame = tk.Frame(self.subgoals_frame)
        cb = tk.Checkbutton(frame, variable=var, command=self.save_callback)
        cb.pack(side=tk.LEFT)
        lbl = tk.Label(frame, text=text)
        lbl.pack(side=tk.LEFT)
        frame.pack(anchor='w', pady=1)
        self.subgoal_vars.append(var)
        self.subgoal_frames.append(frame)
        self.entry.delete(0, tk.END)
        self.save_callback()

    def get_subgoals(self):
        return [{
            'text': frame.winfo_children()[1].cget("text"),
            'done': var.get()
        } for var, frame in zip(self.subgoal_vars, self.subgoal_frames)]


# ---------------------------
# 2. GoalSection (unchanged)
# ---------------------------
class GoalSection(tk.Frame):
    def __init__(self, master, title, save_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title = title
        self.save_callback = save_callback
        self.visible = tk.BooleanVar(value=True)
        self.goal_vars = []
        self.goal_frames = []
        self.subgoal_sections = []

        self.header = tk.Frame(self)
        self.toggle_btn = tk.Button(self.header, text="▼", width=2, command=self.toggle)
        self.toggle_btn.pack(side=tk.LEFT)
        self.title_lbl = tk.Label(self.header, text=title, font=("Arial", 10, "bold"))
        self.title_lbl.pack(side=tk.LEFT, padx=5)
        self.header.pack(fill=tk.X)

        self.body = tk.Frame(self)
        self.body.pack(fill=tk.BOTH, expand=True)

        self.entry_frame = tk.Frame(self.body)
        self.entry = tk.Entry(self.entry_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda event: self.add_goal())
        self.add_btn = tk.Button(self.entry_frame, text="Add Goal", command=self.add_goal)
        self.add_btn.pack(side=tk.LEFT, padx=2)
        self.entry_frame.pack(fill=tk.X, pady=3)

        self.goals_frame = tk.Frame(self.body)
        self.goals_frame.pack(fill=tk.BOTH, expand=True)

    def toggle(self):
        if self.visible.get():
            self.body.pack_forget()
            self.toggle_btn.configure(text="►")
        else:
            self.body.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.configure(text="▼")
        self.visible.set(not self.visible.get())

    def add_goal(self, text=None, checked=False, subgoals=None):
        if text is None:
            text = self.entry.get().strip()
        if not text:
            return
        var = tk.BooleanVar(value=checked)
        frame = tk.Frame(self.goals_frame, relief=tk.RAISED, bd=1)
        cb = tk.Checkbutton(frame, variable=var, command=self.save_callback)
        cb.pack(side=tk.LEFT)
        lbl = tk.Label(frame, text=text, font=("Arial", 10))
        lbl.pack(side=tk.LEFT)
        frame.pack(anchor='w', pady=2, fill=tk.X)
        self.goal_vars.append(var)
        self.goal_frames.append(frame)

        subgoal_section = SubGoalSection(frame, subgoals if subgoals else [], self.save_callback)
        subgoal_section.pack(fill=tk.X, padx=30, pady=2)
        self.subgoal_sections.append(subgoal_section)
        self.entry.delete(0, tk.END)
        self.save_callback()

    def load_goals(self, goals):
        for goal in goals:
            self.add_goal(goal['text'], goal['done'], goal.get('subgoals', []))

    def get_goals(self):
        return [{
            'text': frame.winfo_children()[1].cget("text"),
            'done': var.get(),
            'subgoals': sub_section.get_subgoals()
        } for var, frame, sub_section in zip(self.goal_vars, self.goal_frames, self.subgoal_sections)]


# ---------------------------
# 3. CollapsibleSection (unchanged)
# ---------------------------
class CollapsibleSection(tk.Frame):
    def __init__(self, master, title, items=None, save_callback=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title = title
        self.items = items if items else []
        self.save_callback = save_callback
        self.visible = tk.BooleanVar(value=True)
        self.check_vars = []
        self.item_frames = []

        self.header = tk.Frame(self)
        self.toggle_btn = tk.Button(self.header, text="▼", width=2, command=self.toggle)
        self.toggle_btn.pack(side=tk.LEFT)
        self.title_lbl = tk.Label(self.header, text=title, font=("Arial", 10, "bold"))
        self.title_lbl.pack(side=tk.LEFT, padx=5)
        self.header.pack(fill=tk.X)

        self.body = tk.Frame(self)
        self.body.pack(fill=tk.BOTH, expand=True)

        self.entry_frame = tk.Frame(self.body)
        self.entry = tk.Entry(self.entry_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda event: self.add_item())
        self.add_btn = tk.Button(self.entry_frame, text="Add", command=self.add_item)
        self.add_btn.pack(side=tk.LEFT, padx=2)
        self.entry_frame.pack(fill=tk.X, pady=3)

        self.items_frame = tk.Frame(self.body)
        self.items_frame.pack(fill=tk.BOTH, expand=True)

        self.load_items(self.items)

    def toggle(self):
        if self.visible.get():
            self.body.pack_forget()
            self.toggle_btn.configure(text="►")
        else:
            self.body.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.configure(text="▼")
        self.visible.set(not self.visible.get())

    def add_item(self, text=None, checked=False):
        if text is None:
            text = self.entry.get().strip()
        if not text:
            return
        var = tk.BooleanVar(value=checked)
        frame = tk.Frame(self.items_frame)
        cb = tk.Checkbutton(frame, variable=var, command=self.save_callback)
        cb.pack(side=tk.LEFT)
        lbl = tk.Label(frame, text=text)
        lbl.pack(side=tk.LEFT)
        frame.pack(anchor='w', pady=1)
        self.check_vars.append(var)
        self.item_frames.append(frame)
        self.entry.delete(0, tk.END)
        if self.save_callback:
            self.save_callback()

    def load_items(self, items):
        for item in items:
            self.add_item(item['text'], item['done'])

    def get_items(self):
        return [{
            'text': frame.winfo_children()[1].cget("text"),
            'done': var.get()
        } for var, frame in zip(self.check_vars, self.item_frames)]


# ---------------------------
# 4. Fixed GoalsWindow
# ---------------------------
class GoalsWindow(tk.Toplevel):
    def __init__(self, master, data, save_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Goals")
        self.geometry("500x650")
        self.sections = {}
        self.save_callback = save_callback

        # Ensure complete data structure
        data = data or {}
        required_keys = ['goals', 'monthly', 'weekly', 'daily']
        for key in required_keys:
            if key not in data:
                data[key] = []

        # Initialize all sections first
        self.sections = {
            'goals': GoalSection(self, "Goals", self.save_all),
            'monthly': CollapsibleSection(self, "Monthly Goals", data['monthly'], self.save_all),
            'weekly': CollapsibleSection(self, "Weekly Goals", data['weekly'], self.save_all),
            'daily': CollapsibleSection(self, "Daily Goals", data['daily'], self.save_all)
        }

        # Pack all sections
        for section in self.sections.values():
            section.pack(fill=tk.X, pady=3, padx=5)

        # Load goals data after initialization
        self.sections['goals'].load_goals(data['goals'])

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_all_data(self):
        return {
            'goals': self.sections['goals'].get_goals(),
            'monthly': self.sections['monthly'].get_items(),
            'weekly': self.sections['weekly'].get_items(),
            'daily': self.sections['daily'].get_items()
        }

    def save_all(self):
        all_data = {
            'tasks': self.master.task_manager.get_tasks(),
            'goals': self.get_all_data()
        }
        with open(DATA_FILE, "w") as f:
            json.dump(all_data, f, indent=2)
        self.save_callback()

    def on_close(self):
        self.save_all()
        self.destroy()


# ---------------------------
# 5. TaskManager (unchanged)
# ---------------------------
class TaskManager(tk.Frame):
    def __init__(self, master, tasks, save_callback):
        super().__init__(master)
        self.save_callback = save_callback
        self.task_vars = []
        self.task_frames = []

        self.task_entry = tk.Entry(self)
        self.task_entry.pack(fill=tk.X, pady=5)
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        self.add_btn = tk.Button(self, text="Add Task", command=self.add_task)
        self.add_btn.pack(pady=5)

        self.tasks_frame = tk.Frame(self)
        self.tasks_frame.pack(fill=tk.BOTH, expand=True)

        for task in tasks:
            self.add_task(task['text'], task['done'])

    def add_task(self, text=None, checked=False):
        if text is None:
            text = self.task_entry.get().strip()
        if not text:
            return
        var = tk.BooleanVar(value=checked)
        frame = tk.Frame(self.tasks_frame)
        cb = tk.Checkbutton(frame, variable=var, command=self.save_callback)
        cb.pack(side=tk.LEFT)
        lbl = tk.Label(frame, text=text)
        lbl.pack(side=tk.LEFT)
        frame.pack(anchor='w', pady=1)
        self.task_vars.append(var)
        self.task_frames.append(frame)
        self.task_entry.delete(0, tk.END)

    def get_tasks(self):
        return [{
            'text': frame.winfo_children()[1].cget("text"),
            'done': var.get()
        } for var, frame in zip(self.task_vars, self.task_frames)]


# ---------------------------
# 6. Fixed MainApp
# ---------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task & Goals Manager")
        self.geometry("500x400")
        self.load_data()

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.task_manager = TaskManager(self.main_frame, self.data['tasks'], self.save_data)
        self.task_manager.pack(fill=tk.BOTH, expand=True)

        self.goals_btn = tk.Button(self.main_frame, text="Manage Goals", command=self.open_goals_window)
        self.goals_btn.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_data(self):
        # Initialize with complete structure
        self.data = {
            'tasks': [],
            'goals': {
                'goals': [],
                'monthly': [],
                'weekly': [],
                'daily': []
            }
        }

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    loaded_data = json.load(f)

                    # Migrate old data format
                    if isinstance(loaded_data.get('goals', {}), list):
                        self.data = {
                            'tasks': loaded_data.get('tasks', []),
                            'goals': {
                                'goals': loaded_data.get('goals', []),
                                'monthly': [],
                                'weekly': [],
                                'daily': []
                            }
                        }
                    else:
                        # Merge loaded data with default structure
                        for key in ['tasks', 'goals']:
                            if key in loaded_data:
                                self.data[key] = loaded_data[key]

                        # Ensure all goal sections exist
                        for section in ['goals', 'monthly', 'weekly', 'daily']:
                            if section not in self.data['goals']:
                                self.data['goals'][section] = []

            except Exception as e:
                print(f"Error loading data: {e}")

    def save_data(self):
        data = {
            'tasks': self.task_manager.get_tasks(),
            'goals': self.data['goals']
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def open_goals_window(self):
        GoalsWindow(self, self.data['goals'], self.update_goals_data)

    def update_goals_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)

    def on_close(self):
        self.save_data()
        self.destroy()



if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
