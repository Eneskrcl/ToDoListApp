import customtkinter as ctk
import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_name="tasks.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                status INTEGER DEFAULT 0,
                date TEXT
            )
        ''')
        self.conn.commit()

    def add_task(self, content):
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cursor.execute("INSERT INTO tasks (content, date) VALUES (?, ?)", (content, date_str))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        return self.cursor.fetchall()

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()


class TaskItem(ctk.CTkFrame):
    def __init__(self, master, task_id, content, date, delete_callback):
        super().__init__(master)
        self.task_id = task_id

        self.configure(fg_color="#2b2b2b", corner_radius=8)
        self.pack(fill="x", padx=10, pady=5)

        self.label_content = ctk.CTkLabel(self, text=content, font=ctk.CTkFont(size=14, weight="bold"))
        self.label_content.pack(side="left", padx=15, pady=10)

        self.label_date = ctk.CTkLabel(self, text=date, font=ctk.CTkFont(size=10), text_color="gray")
        self.label_date.pack(side="left", padx=5)

        self.delete_btn = ctk.CTkButton(self, text="Delete", width=60, height=28,
                                        fg_color="#d32f2f", hover_color="#b71c1c",
                                        command=lambda: delete_callback(self))
        self.delete_btn.pack(side="right", padx=15)


class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()

        self.title("TodoPro Enterprise")
        self.geometry("600x700")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        self.header = ctk.CTkLabel(self, text="TASK MANAGER", font=ctk.CTkFont(size=28, weight="bold"))
        self.header.grid(row=0, column=0, pady=30)

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=40, sticky="new")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter a new task...", height=45, border_width=1)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.add_btn = ctk.CTkButton(self.input_frame, text="+", width=50, height=45,
                                     font=ctk.CTkFont(size=20), command=self.add_task)
        self.add_btn.grid(row=0, column=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=20)
        self.grid_rowconfigure(2, weight=10)

    def add_task(self):
        content = self.entry.get()
        if content:
            task_id = self.db.add_task(content)
            date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            TaskItem(self.scroll_frame, task_id, content, date_now, self.delete_task)
            self.entry.delete(0, 'end')

    def load_tasks(self):
        for task in self.db.get_all_tasks():
            TaskItem(self.scroll_frame, task[0], task[1], task[3], self.delete_task)

    def delete_task(self, task_item):
        self.db.delete_task(task_item.task_id)
        task_item.destroy()


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()