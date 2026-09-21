import customtkinter as ctk
from tkinter import filedialog

from config import get_default_save_path


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, settings, save_callback):
        super().__init__(parent)
        self.settings = settings
        self.save_callback = save_callback
        self.title("⚙ Настройки")
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f19")
        self.create_widgets()
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        frame = ctk.CTkFrame(
            self,
            fg_color="#151a27",
            corner_radius=22,
            border_width=2,
            border_color="#5865F2",
        )

        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="⚙ Настройки", font=("Segoe UI", 28, "bold")).pack(
            pady=(20, 25)
        )

        ctk.CTkLabel(frame, text="Папка сохранения", font=("Segoe UI", 15)).pack(
            anchor="w", padx=25
        )

        folder_frame = ctk.CTkFrame(frame, fg_color="transparent")
        folder_frame.pack(fill="x", padx=25, pady=(8, 20))

        folder_frame.grid_columnconfigure(0, weight=1)

        self.folder_entry = ctk.CTkEntry(folder_frame, height=40, corner_radius=12)

        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.folder_entry.insert(
            0, self.settings.get("save_path", get_default_save_path())
        )

        ctk.CTkButton(
            folder_frame,
            text="...",
            width=55,
            height=40,
            corner_radius=12,
            command=self.choose_folder,
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            frame,
            text="Дополнительная папка для видео (необязательно)",
            font=("Segoe UI", 15),
        ).pack(anchor="w", padx=25)

        self.video_folder = ctk.CTkEntry(frame, height=40, corner_radius=12)

        self.video_folder.pack(fill="x", padx=25, pady=(8, 20))

        self.video_folder.insert(0, self.settings.get("video_folder", ""))

        ctk.CTkLabel(frame, text="Качество", font=("Segoe UI", 15)).pack(
            anchor="w", padx=25
        )

        self.quality = ctk.CTkComboBox(
            frame,
            height=40,
            corner_radius=12,
            values=["Максимальное", "2160", "1440", "1080", "720", "480", "360"],
        )

        self.quality.pack(fill="x", padx=25, pady=(8, 20))

        self.quality.set(str(self.settings.get("quality", "Максимальное")))

        ctk.CTkLabel(frame, text="Максимум сезонов", font=("Segoe UI", 15)).pack(
            anchor="w", padx=25
        )

        self.max_seasons = ctk.CTkEntry(frame, height=40, corner_radius=12)

        self.max_seasons.pack(fill="x", padx=25, pady=(8, 20))

        self.max_seasons.insert(0, str(self.settings.get("max_seasons", 5)))

        ctk.CTkLabel(frame, text="Максимум серий", font=("Segoe UI", 15)).pack(
            anchor="w", padx=25
        )

        self.max_episodes = ctk.CTkEntry(frame, height=40, corner_radius=12)

        self.max_episodes.pack(fill="x", padx=25, pady=(8, 20))

        self.max_episodes.insert(0, str(self.settings.get("max_episodes", 10)))

        buttons = ctk.CTkFrame(frame, fg_color="transparent")

        buttons.pack(fill="x", padx=25, pady=(20, 10))

        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            buttons,
            text="💾 Сохранить",
            height=40,
            corner_radius=15,
            fg_color="#2479b8",
            hover_color="#1d6399",
            command=self.save,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            buttons,
            text="Отмена",
            height=40,
            corner_radius=15,
            fg_color="#4b5568",
            hover_color="#3b4353",
            command=self.destroy,
        ).grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def choose_folder(self):
        folder = filedialog.askdirectory()

        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def save(self):
        data = {
            "save_path": self.folder_entry.get(),
            "video_folder": self.video_folder.get(),
            "quality": self.quality.get(),
            "max_seasons": int(self.max_seasons.get()),
            "max_episodes": int(self.max_episodes.get()),
        }

        self.save_callback(data)
        self.destroy()
