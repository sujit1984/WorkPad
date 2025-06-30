import tkinter as tk
import json
import os
import datetime

DATA_FILE = "task_goals_data.json"

# Utility function to get current date
def get_current_date():
    return datetime.datetime.now().strftime("%A, %B %d, %Y")

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
    def __init__(self, master, title, save_callback, data=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title = title
        self.save_callback = save_callback
        self.visible = tk.BooleanVar(value=True)
        self.goal_vars = []
        self.goal_frames = []
        self.subgoal_sections = []

        self.data = data if data and isinstance(data, list) else []

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

        self.load_goals(self.data)

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
        self.items = items if items and isinstance(items, list) else []
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
# 4. GoalsWindow with Date Label
# ---------------------------
class GoalsWindow(tk.Toplevel):
    def __init__(self, master, data, save_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Goals")
        self.geometry("500x650")
        self.save_callback = save_callback

        # Date label at the top
        self.date_label = tk.Label(self, font=("Arial", 12, "bold"))
        self.date_label.pack(pady=5)
        self.update_date_label()

        # Validate and initialize data structure
        self.data = self.validate_data_structure(data)

        # Temporary dummy callback to prevent premature saves
        def dummy_save(): pass

        # Initialize sections with dummy callback
        self.sections = {
            'goals': GoalSection(self, "Goals", dummy_save, data=self.data['goals']),
            'monthly': CollapsibleSection(self, "Monthly Goals", self.data['monthly'], dummy_save),
            'weekly': CollapsibleSection(self, "Weekly Goals", self.data['weekly'], dummy_save),
            'daily': CollapsibleSection(self, "Daily Goals", self.data['daily'], dummy_save)
        }

        # Pack all sections
        for section in self.sections.values():
            section.pack(fill=tk.X, pady=3, padx=5)

        # Now set the real save callback after sections are initialized
        for section in self.sections.values():
            section.save_callback = self.save_all

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_date_label(self):
        self.date_label.config(text=get_current_date())
        self.after(60000, self.update_date_label)  # Update every 60 seconds

    def validate_data_structure(self, data):
        return {
            'goals': data.get('goals', []),
            'monthly': data.get('monthly', []),
            'weekly': data.get('weekly', []),
            'daily': data.get('daily', [])
        }

    def get_all_data(self):
        return {
            'goals': self.sections['goals'].get_goals(),
            'monthly': self.sections['monthly'].get_items(),
            'weekly': self.sections['weekly'].get_items(),
            'daily': self.sections['daily'].get_items()
        }

    def save_all(self):
        self.master.data['goals'] = self.get_all_data()
        self.save_callback()

    def on_close(self):
        self.save_all()
        self.destroy()

# ---------------------------
# 5. MainApp with Date Label and Duplicate Task Fix
# ---------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WorkPad")
        self.geometry("800x600")
        self.data = self.load_data()

        # Date label at the top
        self.date_label = tk.Label(self, font=("Arial", 12, "bold"))
        self.date_label.pack(pady=5)
        self.update_date_label()

        # Create main container
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize components with dummy callbacks first
        self.task_manager = TaskManager(self.main_frame, self.data['tasks'], lambda: None)
        self.task_manager.pack(fill=tk.BOTH, expand=True)

        # Initialize goals component (if applicable)
        self.goals_button = tk.Button(
            self.main_frame,
            text="Manage Goals",
            command=self.open_goals_window
        )
        self.goals_button.pack(pady=5)

        # Set real save callbacks AFTER initialization
        self.task_manager.save_callback = self.save_data

        # Remove duplicate task loading: do NOT call self.load_initial_data()

    def update_date_label(self):
        self.date_label.config(text=get_current_date())
        self.after(60000, self.update_date_label)  # Update every 60 seconds

    def save_data(self):
        data = {
            'tasks': self.task_manager.get_tasks(),
            'goals': self.data.get('goals', [])
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {'tasks': [], 'goals': []}

    def open_goals_window(self):
        GoalsWindow(self, self.data['goals'], self.save_data)

    def update_goals_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)

    def on_close(self):
        self.save_data()
        self.destroy()

# ---------------------------
# 6. TaskManager (unchanged)
# ---------------------------
class TaskManager(tk.Frame):
    def __init__(self, master, tasks, save_callback):
        super().__init__(master)
        self.save_callback = save_callback
        self.task_vars = []
        self.task_frames = []

        self.normal_font = ("TkDefaultFont", 10)
        self.strike_font = ("TkDefaultFont", 10, "overstrike")

        self.task_entry = tk.Entry(self)
        self.task_entry.pack(fill=tk.X, pady=5)
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=5)

        self.add_btn = tk.Button(self.button_frame, text="Add Task", command=self.add_task)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.remove_btn = tk.Button(self.button_frame, text="Remove Completed",
                                    command=self.remove_completed_tasks)
        self.remove_btn.pack(side=tk.LEFT, padx=5)

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

        cb = tk.Checkbutton(frame, variable=var, command=lambda: self.update_strikethrough(var, lbl))
        cb.pack(side=tk.LEFT)

        lbl = tk.Label(frame, text=text, font=self.normal_font)
        if var.get():
            lbl.config(font=self.strike_font)
        lbl.pack(side=tk.LEFT)

        frame.pack(anchor='w', pady=1, fill=tk.X)
        self.task_vars.append(var)
        self.task_frames.append(frame)
        self.task_entry.delete(0, tk.END)
        self.save_callback()

    def update_strikethrough(self, var, lbl):
        lbl.config(font=self.strike_font if var.get() else self.normal_font)
        self.save_callback()

    def remove_completed_tasks(self):
        for i in reversed(range(len(self.task_vars))):
            if self.task_vars[i].get():
                self.task_frames[i].destroy()
                del self.task_vars[i]
                del self.task_frames[i]
        self.save_callback()

    def get_tasks(self):
        return [{
            'text': frame.winfo_children()[1].cget("text"),
            'done': var.get()
        } for var, frame in zip(self.task_vars, self.task_frames)]

if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
