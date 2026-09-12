import customtkinter as ctk
import threading

from config import get_settings, save_settings
from rutube import get_video_info
from search import Searcher
from downloader import Downloader

from ui.settings_window import SettingsWindow
from ui.episodes_panel import EpisodesPanel
from ui.log_panel import LogPanel
from ui.error_overlay import ErrorOverlay


class MainWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="#0b0f19",
            corner_radius=0
        )

        self.settings = get_settings()
        self.video = None
        self.episodes = []
        self.error_overlay = None

        self.searcher = Searcher()
        self.downloader = Downloader()

        self.download_mode = ctk.StringVar(
            value="Видео"
        )

        self.create_widgets()


    def create_widgets(self):
        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            6,
            weight=1
        )

        ctk.CTkLabel(
            self,
            text="🎬 Rutube Downloader",
            font=("Segoe UI", 26, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 20)
        )

        url_frame = ctk.CTkFrame(
            self,
            fg_color="#151a27",
            corner_radius=18,
            border_width=2,
            border_color="#5865F2"
        )

        url_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=5
        )

        url_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.url_entry = ctk.CTkEntry(
            url_frame,
            height=40,
            placeholder_text="Вставьте ссылку Rutube...",
            corner_radius=12
        )

        self.url_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=10
        )

        self.url_entry.bind(
            "<Control-KeyPress>",
            self.handle_paste
        )

        ctk.CTkButton(
            url_frame,
            text="📋",
            width=50,
            height=40,
            corner_radius=12,
            command=self.paste
        ).grid(
            row=0,
            column=1,
            padx=10
        )

        ctk.CTkButton(
            self,
            text="Получить информацию",
            height=40,
            corner_radius=15,
            command=self.load_video
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=10
        )

        actions = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        actions.grid(
            row=2,
            column=1,
            sticky="e"
        )

        ctk.CTkButton(
            actions,
            text="⚙ Настройки",
            corner_radius=15,
            command=self.show_settings
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            actions,
            text="🔎 Найти",
            corner_radius=15,
            command=self.search
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            actions,
            text="⛔",
            width=50,
            fg_color="#ed4245",
            hover_color="#c03550",
            corner_radius=15,
            command=self.searcher.stop_search
        ).pack(
            side="left"
        )

        mode_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        mode_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=5
        )

        ctk.CTkRadioButton(
            mode_frame,
            text="🎬 Видео",
            variable=self.download_mode,
            value="Видео"
        ).pack(
            side="left",
            padx=10
        )

        ctk.CTkRadioButton(
            mode_frame,
            text="📺 Сериал",
            variable=self.download_mode,
            value="Сериал"
        ).pack(
            side="left",
            padx=10
        )

        info = ctk.CTkFrame(
            self,
            fg_color="#151a27",
            corner_radius=18,
            border_width=2,
            border_color="#5865F2"
        )

        info.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=10
        )

        ctk.CTkLabel(
            info,
            text="Информация",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=5
        )

        self.info = ctk.CTkTextbox(
            info,
            height=100,
            corner_radius=12
        )

        self.info.pack(
            fill="x",
            padx=10,
            pady=10
        )

        left = ctk.CTkFrame(
            self,
            fg_color="#151a27",
            corner_radius=18,
            border_width=2,
            border_color="#5865F2"
        )

        left.grid(
            row=6,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        right = ctk.CTkFrame(
            self,
            fg_color="#151a27",
            corner_radius=18,
            border_width=2,
            border_color="#5865F2"
        )

        right.grid(
            row=6,
            column=1,
            sticky="nsew"
        )

        self.episodes_panel = EpisodesPanel(
            left
        )

        self.episodes_panel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        ctk.CTkButton(
            right,
            text="⬇ Скачать выбранное",
            height=40,
            corner_radius=15,
            command=self.start_download
        ).pack(
            fill="x",
            padx=10,
            pady=5
        )

        ctk.CTkButton(
            right,
            text="⛔ Остановить",
            height=40,
            corner_radius=15,
            fg_color="#ed4245",
            hover_color="#c03550",
            command=self.downloader.stop_download
        ).pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.log_panel = LogPanel(
            right
        )

        self.log_panel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )


    def show_error(self, text):
        if self.error_overlay:
            self.error_overlay.destroy()

        self.error_overlay = ErrorOverlay(
            self,
            text
        )


    def handle_paste(self, event):
        self.paste()

        return "break"


    def paste(self):
        try:
            self.url_entry.delete(
                0,
                "end"
            )

            self.url_entry.insert(
                0,
                self.clipboard_get()
            )

        except Exception:
            pass


    def show_settings(self):
        SettingsWindow(
            self.winfo_toplevel(),
            self.settings,
            self.save_settings
        )


    def save_settings(self, data):
        self.settings = data

        save_settings(
            data
        )


    def load_video(self):
        threading.Thread(
            target=self.get_video,
            daemon=True
        ).start()


    def get_video(self):
        try:
            self.video = get_video_info(
                self.url_entry.get()
            )

            self.after(
                0,
                self.update_info
            )

        except Exception as e:
            self.after(
                0,
                lambda: self.show_error(
                    str(e)
                )
            )


    def update_info(self):
        self.info.delete(
            "0.0",
            "end"
        )

        self.info.insert(
            "end",
            (
                f"Название: {self.video['title']}\n"
                f"Автор: {self.video['author_name']}\n"
                f"Сериал: {self.video['show_name']}\n"
                f"Сезон: {self.video.get('season') or '-'}\n"
                f"Серия: {self.video.get('episode') or '-'}"
            )
        )

    def search(self):
        if not self.video:
            self.show_error(
                "Сначала получите информацию"
            )

            return

        if self.download_mode.get() == "Видео":
            self.episodes = [
                self.video
            ]

            self.episodes_panel.set_episodes(
                self.episodes
            )

            self.log_panel.callback(
                "log",
                "Добавлено видео"
            )

            return

        threading.Thread(
            target=self.search_thread,
            daemon=True
        ).start()


    def search_thread(self):
        result = self.searcher.find_seasons(
            self.video,
            self.settings,
            self.log_panel.callback
        )

        self.episodes = []

        for season in sorted(result):
            for episode in sorted(result[season]):
                self.episodes.append(
                    result[season][episode]
                )

        self.after(
            0,
            lambda: self.episodes_panel.set_episodes(
                self.episodes
            )
        )


    def start_download(self):
        selected = self.episodes_panel.get_selected()

        if not selected:
            self.show_error(
                "Выберите видео"
            )

            return

        threading.Thread(
            target=lambda: self.downloader.download_all(
                selected,
                self.settings,
                self.video.get(
                    "show_name",
                    "Видео"
                ),
                self.log_panel.callback
            ),
            daemon=True
        ).start()