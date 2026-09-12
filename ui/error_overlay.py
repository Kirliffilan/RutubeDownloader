import customtkinter as ctk


class ErrorOverlay:
    def __init__(self, parent, message):
        self.parent = parent

        self.overlay = ctk.CTkFrame(
            parent,
            fg_color="#000000",
            corner_radius=0
        )

        self.overlay.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        self.overlay.lift()

        self.box = ctk.CTkFrame(
            self.overlay,
            width=420,
            height=220,
            fg_color="#151a27",
            corner_radius=20,
            border_width=2,
            border_color="#ed4245"
        )

        self.box.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        self.box.pack_propagate(
            False
        )

        ctk.CTkLabel(
            self.box,
            text="⚠ Ошибка",
            font=(
                "Segoe UI",
                22,
                "bold"
            ),
            text_color="#ed4245"
        ).pack(
            pady=(25,10)
        )

        ctk.CTkLabel(
            self.box,
            text=message,
            wraplength=330,
            font=(
                "Segoe UI",
                14
            )
        ).pack(
            expand=True
        )

        ctk.CTkButton(
            self.box,
            text="Понятно",
            width=130,
            height=35,
            corner_radius=15,
            fg_color="#ed4245",
            hover_color="#c03550",
            command=self.destroy
        ).pack(
            pady=20
        )

    def destroy(self):
        self.overlay.destroy()
        self.overlay = None