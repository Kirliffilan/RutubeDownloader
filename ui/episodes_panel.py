import customtkinter as ctk


class EpisodesPanel(ctk.CTkFrame):
    def __init__(self, parent, selection_callback=None):
        super().__init__(parent, fg_color="transparent")

        self.episodes = []
        self.checkboxes = []
        self.selection_callback = selection_callback

        self.create_widgets()

    def create_widgets(self):
        top = ctk.CTkFrame(self, fg_color="transparent")

        top.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            top,
            text="☑ Выделить всё",
            height=35,
            corner_radius=12,
            command=self.select_all,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            top,
            text="☐ Убрать всё",
            height=35,
            corner_radius=12,
            fg_color="#3a3f4b",
            hover_color="#505766",
            command=self.clear_all,
        ).pack(side="left", padx=5)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#10141f", corner_radius=15)

        self.scroll.pack(fill="both", expand=True)

    def set_episodes(self, episodes):
        self.episodes = episodes

        for widget in self.scroll.winfo_children():
            widget.destroy()

        self.checkboxes.clear()

        for item in episodes:
            season = item.get("season")

            episode = item.get("episode")

            if season and episode:
                text = f"{season} сезон " f"{episode} серия" f" | {item['title']}"

            else:
                text = f"🎬 {item['title']}"

            checkbox = ctk.CTkCheckBox(
                self.scroll,
                text=text,
                corner_radius=6,
                fg_color="#5865F2",
                hover_color="#4752C4",
                command=self.selection_changed,
            )

            checkbox.pack(fill="x", padx=10, pady=5)

            self.checkboxes.append(checkbox)
            checkbox.select()

    def select_all(self):
        for checkbox in self.checkboxes:
            checkbox.select()

        self.selection_changed()

    def clear_all(self):
        for checkbox in self.checkboxes:
            checkbox.deselect()

        self.selection_changed()

    def get_selected(self):
        result = []

        for index, checkbox in enumerate(self.checkboxes):
            if checkbox.get():
                result.append(self.episodes[index])

        return result

    def selection_changed(self):
        if self.selection_callback:
            self.selection_callback(self.get_selected())
