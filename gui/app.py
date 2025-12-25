import customtkinter as ctk
from gui.pages.landing import LandingPage
from gui.pages.counter import CounterExamplePage
from gui.pages.compare import ComparisonPage

class NFAMinimizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Setup Window
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title("NFA Tool Suite")
        self.geometry("1600x1000")
        self.minsize(1400, 800)

        # Main Container (Stacking frames)
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to hold frames
        self.frames = {}

        self._init_frames()
        self.show_frame("LandingPage")

    def _init_frames(self):
        # 1. Landing Page
        landing = LandingPage(
            master=self.container,
            on_create_counter=lambda: self.show_frame("CounterExamplePage"),
            on_visualize_compare=lambda: self.show_frame("ComparisonPage")
        )
        self.frames["LandingPage"] = landing
        landing.grid(row=0, column=0, sticky="nsew")

        # 2. Counter Page
        counter = CounterExamplePage(
            master=self.container,
            on_home=lambda: self.show_frame("LandingPage")
        )
        self.frames["CounterExamplePage"] = counter
        counter.grid(row=0, column=0, sticky="nsew")

        # 3. Comparison Page
        compare = ComparisonPage(
            master=self.container,
            on_home=lambda: self.show_frame("LandingPage")
        )
        self.frames["ComparisonPage"] = compare
        compare.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

        # Update Title
        if page_name == "CounterExamplePage":
            self.title("NFA Tool Suite - Counter-Example Mode")
        elif page_name == "ComparisonPage":
            self.title("NFA Minimization Tool - Batch Mode")
        else:
            self.title("NFA Tool Suite")