import customtkinter as ctk
from tkinter import ttk

from database import (
    get_history,
    delete_history,
    clear_history,
    delete_history_by_season,
    delete_history_by_show,
)

from ui.confirm_overlay import ConfirmOverlay


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("📜 История")
        self.geometry("900x500")

        self.parent = parent

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
            borderwidth=0,
        )

        style.configure("Treeview.Heading", background="#2b2b2b", foreground="white")

        style.map(
            "Treeview",
            background=[("selected", "#1f6aa5")],
            foreground=[("selected", "white")],
        )

        self.create_widgets()
        self.load_history()

    def _apply_theme(self):
        self._set_appearance_mode("dark")

    def create_widgets(self):
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("data",)
        self.table = ttk.Treeview(
            self.table_frame, columns=columns, show="tree headings"
        )

        self.table.heading("#0", text="История загрузок")
        self.table.heading("data", text="")
        self.table.column("#0", width=600, minwidth=300)
        self.table.column("data", width=0, stretch=False)

        vsb = ttk.Scrollbar(
            self.table_frame, orient="vertical", command=self.table.yview
        )
        hsb = ttk.Scrollbar(
            self.table_frame, orient="horizontal", command=self.table.xview
        )
        self.table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.table.bind("<Double-1>", self.on_double_click)

        buttons = ctk.CTkFrame(self)
        buttons.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(buttons, text="Обновить", command=self.load_history).pack(
            side="left", padx=5
        )

        ctk.CTkButton(buttons, text="Копировать ссылку", command=self.copy_url).pack(
            side="left", padx=5
        )

        ctk.CTkButton(
            buttons, text="Удалить выбранное", command=self.delete_selected
        ).pack(side="left", padx=5)

        ctk.CTkButton(buttons, text="Удалить всё", command=self.clear_all).pack(
            side="left", padx=5
        )

        self.history_data = {}

    def load_history(self):
        for item in self.table.get_children():
            self.table.delete(item)

        self.history_data = {}
        rows = get_history()

        videos = []
        serials = {}

        for row in rows:
            item_id = row["id"]
            self.history_data[item_id] = row

            if row["type"] == "video" or not row["show_name"]:
                videos.append(row)
            else:
                show_name = row["show_name"]
                season = row["season"] if row["season"] else 0
                if show_name not in serials:
                    serials[show_name] = {}
                if season not in serials[show_name]:
                    serials[show_name][season] = []
                serials[show_name][season].append(row)

        for video in videos:
            self.add_video_item(video)

        for show_name, seasons in sorted(serials.items()):
            show_id = self.table.insert(
                "",
                "end",
                text=f"📺 {show_name}",
                open=True,
                values=("show", show_name),
            )

            for season_num in sorted(seasons.keys()):
                episodes = seasons[season_num]
                episodes.sort(key=lambda x: x["episode"] if x["episode"] else 999)

                season_text = (
                    f"📁 {season_num} сезон ({len(episodes)} серий)"
                    if season_num
                    else f"📁 Без сезона ({len(episodes)} серий)"
                )
                season_id = self.table.insert(
                    show_id,
                    "end",
                    text=season_text,
                    open=True,
                    values=("season", show_name, season_num),
                )

                for ep in episodes:
                    ep_title = ep["title"]
                    if ep["episode"]:
                        ep_text = f"🎬 {ep['episode']} серия — {ep_title}"
                    else:
                        ep_text = f"🎬 {ep_title}"
                    self.table.insert(
                        season_id,
                        "end",
                        text=ep_text,
                        open=False,
                        values=("episode", ep["id"]),
                    )

    def add_video_item(self, video):
        title = video["title"]
        quality = video["quality"] if video["quality"] else "-"
        date = video["date"]
        item_text = f"🎬 {title} [{quality}] ({date})"
        self.table.insert("", "end", text=item_text, open=False, values=("video", video["id"]))

    def on_double_click(self, event):
        self.copy_url()

    def get_selected_item_data(self):
        selected = self.table.selection()
        if not selected:
            return None, None, None
        item = selected[0]
        values = self.table.item(item, "values")
        if not values:
            return None, None, None
        item_type = values[0]
        return item, item_type, values

    def copy_url(self):
        item, item_type, values = self.get_selected_item_data()
        if not item:
            self.show_notification("Ничего не выбрано")
            return

        url = None

        if item_type == "video":
            history_id = int(values[1])
            row = self.history_data.get(history_id)
            if row:
                url = row["url"]
        elif item_type == "episode":
            history_id = int(values[1])
            row = self.history_data.get(history_id)
            if row:
                url = row["url"]
        elif item_type == "season":
            show_name = values[1]
            season = int(values[2]) if values[2].isdigit() else values[2]
            for row in self.history_data.values():
                if (
                    row["show_name"] == show_name
                    and row["season"] == season
                    and row["type"] == "serial"
                ):
                    url = row["series_url"] or row["url"]
                    break
        elif item_type == "show":
            show_name = values[1]
            for row in self.history_data.values():
                if row["show_name"] == show_name and row["type"] == "serial":
                    url = row["series_url"] or row["url"]
                    break

        if not url:
            self.show_notification("Ссылка недоступна")
            return

        self.clipboard_clear()
        self.clipboard_append(url)
        self.show_notification("Ссылка скопирована")

    def show_notification(self, text):
        notif = ctk.CTkLabel(
            self, text=text, fg_color="#1f6aa5", corner_radius=8, padx=15, pady=5
        )
        notif.place(relx=0.5, rely=0.9, anchor="center")
        self.after(2000, notif.destroy)

    def delete_selected(self):
        item, item_type, values = self.get_selected_item_data()
        if not item:
            return

        if item_type == "video":
            history_id = int(values[1])
            row = self.history_data.get(history_id)
            if row:
                ConfirmOverlay(
                    self,
                    f"Удалить видео и файл с диска?\n\n{row['title']}",
                    lambda: self.remove_history(history_id),
                )
        elif item_type == "episode":
            history_id = int(values[1])
            row = self.history_data.get(history_id)
            if row:
                ep_info = (
                    f"{row['season']} сезон {row['episode']} серия"
                    if row["season"] and row["episode"]
                    else row["title"]
                )
                ConfirmOverlay(
                    self,
                    f"Удалить серию и файл с диска?\n\n{ep_info} — {row['title']}",
                    lambda: self.remove_history(history_id),
                )
        elif item_type == "season":
            show_name = values[1]
            season = int(values[2]) if values[2].isdigit() else values[2]
            ConfirmOverlay(
                self,
                f"Удалить весь сезон и все его файлы?\n\n{show_name} — {season} сезон",
                lambda: self.remove_season(show_name, season),
            )
        elif item_type == "show":
            show_name = values[1]
            ConfirmOverlay(
                self,
                f"Удалить весь сериал и все его файлы?\n\n{show_name}",
                lambda: self.remove_show(show_name),
            )

    def remove_history(self, history_id):
        delete_history(history_id)
        self.load_history()

    def remove_season(self, show_name, season):
        delete_history_by_season(show_name, season)
        self.load_history()

    def remove_show(self, show_name):
        delete_history_by_show(show_name)
        self.load_history()

    def clear_all(self):
        ConfirmOverlay(
            self, "Удалить всю историю и все файлы?", self.remove_all_history
        )

    def remove_all_history(self):
        clear_history()
        self.load_history()
