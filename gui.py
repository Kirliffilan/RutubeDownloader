import customtkinter as ctk

from ui.main_window import MainWindow


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode(
            "dark"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        self.title(
            "🎬 Rutube Downloader"
        )

        self.geometry(
            "1200x800"
        )

        self.minsize(
            1000,
            700
        )

        self.configure(
            fg_color="#0b0f19"
        )

        self.center_window()

        window = MainWindow(
            self
        )

        window.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )


    def center_window(self):
        self.update_idletasks()

        width = 1200
        height = 800

        x = (
            self.winfo_screenwidth()
            -
            width
        ) // 2

        y = (
            self.winfo_screenheight()
            -
            height
        ) // 2

        self.geometry(
            f"{width}x{height}+{x}+{y}"
        )