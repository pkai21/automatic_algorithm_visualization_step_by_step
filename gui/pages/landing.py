import customtkinter as ctk

class LandingPage(ctk.CTkFrame):
    def __init__(self, master, on_create_counter, on_visualize_compare, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(center_frame, text="NFA TOOL SUITE", 
                             font=ctk.CTkFont(size=40, weight="bold"))
        title.pack(pady=(0, 50))

        btn_counter = ctk.CTkButton(
            center_frame,
            text="Create counter-examples",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=80,
            width=400,
            corner_radius=20,
            fg_color="#3B8ED0",
            hover_color="#36719F",
            command=on_create_counter
        )
        btn_counter.pack(pady=20)

        btn_visualize = ctk.CTkButton(
            center_frame,
            text="Visualize NFA comparisons",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=80,
            width=400,
            corner_radius=20,
            fg_color="#3B8ED0",
            hover_color="#36719F",
            command=on_visualize_compare
        )
        btn_visualize.pack(pady=20)