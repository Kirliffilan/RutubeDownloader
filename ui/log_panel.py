import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.create_widgets()


    def create_widgets(self):
        ctk.CTkLabel(
            self,
            text="📥 Загрузка",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            pady=(0,5)
        )

        self.status = ctk.CTkLabel(
            self,
            text="Ожидание...",
            text_color="#b5bac1"
        )

        self.status.pack(
            anchor="w"
        )

        self.progress = ctk.CTkProgressBar(
            self,
            height=18,
            corner_radius=10,
            progress_color="#5865F2"
        )

        self.progress.pack(
            fill="x",
            pady=10
        )

        self.progress.set(
            0
        )

        self.progress_text = ctk.CTkLabel(
            self,
            text="0%",
            font=("Segoe UI", 13, "bold")
        )

        self.progress_text.pack()

        ctk.CTkLabel(
            self,
            text="Лог",
            font=("Segoe UI", 14, "bold")
        ).pack(
            anchor="w",
            pady=(15,5)
        )

        self.log = ctk.CTkTextbox(
            self,
            height=220,
            corner_radius=15,
            fg_color="#10141f"
        )

        self.log.pack(
            fill="both",
            expand=True
        )


    def write(self, text):
        self.log.insert(
            "end",
            text + "\n"
        )

        self.log.see(
            "end"
        )


    def set_progress(self, data):
        percent = data.get(
            "percent",
            0
        )

        speed = data.get(
            "speed",
            ""
        )

        eta = data.get(
            "eta",
            ""
        )

        self.progress.set(
            percent / 100
        )

        text = f"{percent:.1f}%"

        if speed:
            text += f"   ⚡ {speed}"

        if eta:
            text += f"   ⏱ {eta}"

        self.progress_text.configure(
            text=text
        )

        if percent >= 100:
            self.status.configure(
                text="✅ Завершено",
                text_color="#23a55a"
            )

        elif percent > 0:
            self.status.configure(
                text="⬇ Скачивание...",
                text_color="#5865F2"
            )


    def callback(self, mode, value):
        self.after(
            0,
            lambda: self.handle_callback(
                mode,
                value
            )
        )


    def handle_callback(self, mode, value):
        if mode == "progress":
            self.set_progress(
                value
            )

        elif mode == "log":
            self.write(
                value
            )