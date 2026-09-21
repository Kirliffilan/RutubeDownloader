import customtkinter as ctk
from tkinter import ttk

from database import get_history, delete_history, clear_history

from ui.confirm_overlay import ConfirmOverlay

class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("📜 История")
        self.geometry("900x500")

        self.parent=parent

        self.transient(parent)
        self.grab_set()
        self.focus()

        self.configure(fg_color="#0b0f19")
        self.after(100, self._apply_theme)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#1a1a1a",
            foreground="white",
            fieldbackground="#1a1a1a",
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#2b2b2b",
            foreground="white"
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#1f6aa5")
            ],
            foreground=[
                ("selected", "white")
            ]
        )

        self.create_widgets()
        self.load_history()

    def _apply_theme(self):
        self._set_appearance_mode("dark")

    def create_widgets(self):
        self.table_frame=ctk.CTkFrame(self)
        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        columns=(
            "id",
            "title",
            "type",
            "season",
            "episode",
            "quality",
            "date"
        )

        self.table=ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings"
        )

        self.table.heading("id",text="ID")
        self.table.heading("title",text="Название")
        self.table.heading("type",text="Тип")
        self.table.heading("season",text="Сезон")
        self.table.heading("episode",text="Серия")
        self.table.heading("quality",text="Качество")
        self.table.heading("date",text="Дата")

        self.table.column("id",width=40)
        self.table.column("title",width=300)
        self.table.column("type",width=80)
        self.table.column("season",width=60)
        self.table.column("episode",width=60)
        self.table.column("quality",width=100)
        self.table.column("date",width=150)

        self.table.pack(
            fill="both",
            expand=True
        )

        buttons=ctk.CTkFrame(self)
        buttons.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkButton(
            buttons,
            text="Обновить",
            command=self.load_history
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            buttons,
            text="Удалить выбранное",
            command=self.delete_selected
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            buttons,
            text="Удалить всё",
            command=self.clear_all
        ).pack(
            side="left",
            padx=5
        )

    def load_history(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for row in get_history():
            self.table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[5],
                    row[6] if row[6] else "-",
                    row[7] if row[7] else "-",
                    row[9] if row[9] else "-",
                    row[4]
                )
            )

    def delete_selected(self):
        selected = self.table.selection()
        if not selected:
            return
        item = self.table.item(selected[0])
        history_id = item["values"][0]
        ConfirmOverlay(
            self,
            "Удалить запись и файл с диска?",
            lambda: self.remove_history(history_id)
        )

    def remove_history(self, history_id):
        delete_history(history_id)
        self.load_history()

    def clear_all(self):
        ConfirmOverlay(
            self,
            "Удалить всю историю и все файлы?",
            self.remove_all_history
        )

    def remove_all_history(self):
        clear_history()
        self.load_history()