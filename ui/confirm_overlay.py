import customtkinter as ctk


class ConfirmOverlay:
    def __init__(self, parent, message, callback):
        self.callback = callback
        self.overlay = ctk.CTkFrame(parent, fg_color="#000000", corner_radius=0)

        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.overlay.lift()

        self.box = ctk.CTkFrame(
            self.overlay,
            width=420,
            height=220,
            fg_color="#151a27",
            corner_radius=20,
            border_width=2,
            border_color="#238636",
        )

        self.box.place(relx=0.5, rely=0.5, anchor="center")

        self.box.pack_propagate(False)

        ctk.CTkLabel(
            self.box,
            text="⚠ Подтверждение",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            self.box, text=message, wraplength=330, font=("Segoe UI", 14)
        ).pack(expand=True)

        buttons = ctk.CTkFrame(self.box, fg_color="transparent")

        buttons.pack(pady=20)

        ctk.CTkButton(
            buttons,
            text="Удалить",
            width=130,
            height=35,
            corner_radius=15,
            fg_color="#ed4245",
            hover_color="#c03550",
            command=self.confirm,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            buttons,
            text="Отмена",
            width=130,
            height=35,
            corner_radius=15,
            command=self.destroy,
        ).pack(side="left", padx=10)

    def confirm(self):
        self.destroy()
        self.callback()

    def destroy(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
