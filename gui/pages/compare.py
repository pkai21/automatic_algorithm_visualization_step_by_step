import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from gui.base import BaseView

# --- IMPORT LOGIC ---
from core.helper.bianchini_algo.read_input import list_nfa_files_in_folder, read_nfa_from_file
from core.src.bianchini_algo.algorithm_3 import MINIMIZENFA
from core.helper.bianchini_algo.get_ouput import newNFA
from core.visualization.visualization_bianchini_algo import visualize

class ComparisonPage(BaseView):
    def __init__(self, master, on_home, **kwargs):
        super().__init__(master, **kwargs)
        self.on_home = on_home
        
        # --- Data Variables ---
        self.folder_path = None
        self.file_list = []
        self.current_file_index = -1
        self.last_file_index = -1
        self.nfa1_original = None
        self.nfa2_original = None
        self.file_buttons = []
        self.selected_algorithm = None
        self.is_auto_run = False
        
        # Biến quản lý trạng thái Zoom
        self.is_maximized = False
        self.panel_wrappers = {} # Lưu trữ các frame cha của panel để grid/ungrid
        
        # --- Theme Config ---
        self.theme_corner_radius = 20
        self.btn_corner_radius = 12
        self.section_bg_color = ("gray95", "gray17")
        self.main_bg_color = ("gray90", "gray13")
        self.configure(fg_color=self.main_bg_color)

        self._build_layout()
        self.show_algorithm_selection()

    def _build_layout(self):
        # 1. SIDEBAR CONTAINER (Left)
        self.sidebar_width = 300
        self.sidebar_container = ctk.CTkFrame(self, width=self.sidebar_width, fg_color="transparent")
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        self.sidebar_container.pack_propagate(False)

        # 2. MAIN GRID (Right)
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(0, 20), pady=20)
        
        self.grid_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.grid_frame.pack(expand=True, fill=tk.BOTH)
        
        # Cấu hình Grid 2x2
        self.grid_frame.grid_rowconfigure(0, weight=1)
        self.grid_frame.grid_rowconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

        # Định nghĩa vị trí 4 panels
        # Key - Row - Col
        layout_defs = [
            ("input1", 0, 0), ("input2", 0, 1), 
            ("output1", 1, 0), ("output2", 1, 1)
        ]
        
        self.panel_wrappers = {}

        for key, row, col in layout_defs:
            # Wrapper Frame (Cái khung màu xám)
            card = ctk.CTkFrame(self.grid_frame, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius, border_width=0)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            
            # Cấu hình grid bên trong card để inner frame bung ra
            card.grid_rowconfigure(0, weight=1)
            card.grid_columnconfigure(0, weight=1)
            
            # Inner Container (Nơi chứa Canvas)
            container = ctk.CTkFrame(card, fg_color="transparent")
            container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # Lưu tham chiếu
            self.panel_wrappers[key] = card
            self.panels[key] = container
            
            # Tạo Canvas
            title = key.replace("input", "Input NFA ").replace("output", "Minimized NFA ")
            self.create_panel_canvas(key, title)
            
            # --- GÁN SỰ KIỆN DOUBLE CLICK ---
            if key in self.canvases:
                # canvases[key] = (canvas, fig, ax) -> Lấy phần tử 0 là canvas widget
                canvas_widget = self.canvases[key][0].get_tk_widget()
                # Bind event, truyền key vào hàm toggle
                canvas_widget.bind('<Double-1>', lambda event, k=key: self.toggle_maximize(k))

    # ==============================================================================
    # LOGIC PHÓNG TO / THU NHỎ (NEW)
    # ==============================================================================
    def toggle_maximize(self, target_key):
        """
        Logic:
        - Nếu đang zoom: Khôi phục lại grid 2x2.
        - Nếu chưa zoom: Ẩn hết 3 cái kia, set target_key chiếm row=0, col=0, rowspan=2, columnspan=2.
        """
        # Định nghĩa lại layout chuẩn để restore
        layout_defs = [
            ("input1", 0, 0), ("input2", 0, 1), 
            ("output1", 1, 0), ("output2", 1, 1)
        ]

        if self.is_maximized:
            # --- RESTORE VIEW ---
            print("Restoring grid view...")
            
            # Xóa grid hiện tại (đang bị maximize)
            for key, wrapper in self.panel_wrappers.items():
                wrapper.grid_forget()
            
            # Grid lại từng cái vào vị trí cũ
            for key, r, c in layout_defs:
                wrapper = self.panel_wrappers[key]
                wrapper.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
            
            self.is_maximized = False
            
        else:
            # --- MAXIMIZE VIEW ---
            print(f"Maximizing {target_key}...")
            
            # Ẩn tất cả các frame
            for key, wrapper in self.panel_wrappers.items():
                wrapper.grid_remove() 
            
            # Chỉ hiện target frame và cho chiếm toàn bộ không gian
            target_wrapper = self.panel_wrappers[target_key]
            target_wrapper.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew", padx=0, pady=0)
            
            self.is_maximized = True
            
        # Cập nhật GUI (quan trọng để Canvas resize mượt mà)
        self.grid_frame.update_idletasks()

    # ==============================================================================
    # LOGIC SIDEBAR & NAVIGATION (GIỮ NGUYÊN)
    # ==============================================================================
    def clear_sidebar(self):
        for widget in self.sidebar_container.winfo_children(): widget.destroy()

    def show_algorithm_selection(self):
        self.file_buttons = []
        self.current_file_index = -1
        self.is_auto_run = False
        self.file_list = []
        self.clear_sidebar()
        self.clear_panel_image("input1", "Input NFA 1")
        self.clear_panel_image("input2", "Input NFA 2")
        self.clear_panel_image("output1", "Minimized NFA 1")
        self.clear_panel_image("output2", "Minimized NFA 2")

        ctk.CTkButton(self.sidebar_container, text="🏠 Home Screen", fg_color="transparent", border_width=1, text_color="gray", command=self.on_home).pack(side=tk.TOP, anchor="w", pady=(0, 10))
        algo_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        algo_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(algo_frame, text="SELECT ALGORITHM", font=ctk.CTkFont(family="Arial", size=20, weight="bold"), text_color=("gray40", "gray70")).pack(pady=(40, 30))
        
        for name in ["Bianchini", "Tarjan"]:
            ctk.CTkButton(algo_frame, text=f"{name} Algorithm", font=ctk.CTkFont(size=16, weight="bold"), height=60, fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius, command=lambda n=name: self.on_algorithm_selected(n)).pack(padx=20, pady=15, fill="x")
        
        ctk.CTkLabel(algo_frame, text="Please choose an algorithm to proceed.", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray60").pack(side=tk.BOTTOM, pady=40)

    def on_algorithm_selected(self, algo_name):
        self.selected_algorithm = algo_name
        self.setup_nfa_controls()

    def setup_nfa_controls(self):
        self.clear_sidebar()
        
        # Bottom Controls
        left_frame2 = ctk.CTkFrame(self.sidebar_container, height=120, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        left_frame2.pack(side=tk.BOTTOM, fill=tk.X, anchor="s", pady=(15, 0))
        left_frame2.grid_columnconfigure((0, 2), weight=1)
        left_frame2.grid_columnconfigure(1, weight=3)
        left_frame2.grid_rowconfigure(0, weight=1)
        left_frame2.grid_propagate(False)

        ctk.CTkButton(left_frame2, text="❮", width=50, height=50, font=ctk.CTkFont(size=22), fg_color="transparent", text_color=("gray40", "gray80"), hover_color=("gray90", "gray30"), command=self.prev_file).grid(row=0, column=0)
        self.btn_run_all = ctk.CTkButton(left_frame2, text="RUN", width=70, height=70, corner_radius=35, font=ctk.CTkFont(size=14, weight="bold"), fg_color=("#3B8ED0", "#338CD4"), hover_color=("#36719F", "#296899"), command=self.toggle_auto_run)
        self.btn_run_all.grid(row=0, column=1)
        ctk.CTkButton(left_frame2, text="❯", width=50, height=50, font=ctk.CTkFont(size=22), fg_color="transparent", text_color=("gray40", "gray80"), hover_color=("gray90", "gray30"), command=self.next_file).grid(row=0, column=2)

        # Top Config
        left_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        left_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ctk.CTkButton(left_frame, text="← Algorithms", width=80, height=24, fg_color="transparent", text_color="gray60", anchor="w", command=self.show_algorithm_selection).pack(padx=10, pady=(10, 0), anchor="w")
        ctk.CTkLabel(left_frame, text=f"Mode: {self.selected_algorithm}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3B8ED0").pack(pady=(0, 5))
        ctk.CTkLabel(left_frame, text="NFA CONFIGURATION", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color=("gray40", "gray70")).pack(pady=5)

        select_panel = ctk.CTkFrame(left_frame, fg_color=("white", "gray25"), corner_radius=15, border_width=1, border_color=("gray85", "gray35"))
        select_panel.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(select_panel, text="📂", font=ctk.CTkFont(size=30)).pack(pady=(10, 0))
        self.folder_label = ctk.CTkLabel(select_panel, text="No folder selected", font=ctk.CTkFont(family="Consolas", size=12), text_color=("gray40", "gray80"), fg_color=("white", "gray15"), corner_radius=8, width=280, height=28, anchor="center")
        self.folder_label.pack(padx=15, pady=5)
        ctk.CTkButton(select_panel, text="Browse Folder", font=ctk.CTkFont(size=13, weight="bold"), height=40, fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius, command=self.select_folder).pack(padx=15, pady=(5, 15), fill="x")

        ctk.CTkLabel(left_frame, text="AVAILABLE FILES", font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray60", "gray50"), anchor="w").pack(padx=25, pady=5, fill="x")
        self.file_scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color=("white", "gray20"), corner_radius=15, label_text=None)
        self.file_scroll_frame.pack(padx=20, pady=(0, 10), expand=True, fill="both")

        if self.file_list: self.populate_file_list()

    # ==============================================================================
    # FILE HANDLING LOGIC (GIỮ NGUYÊN)
    # ==============================================================================
    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.folder_path = folder
        self.folder_label.configure(text=f".../{os.path.basename(folder)}")
        try:
            _, full_paths = list_nfa_files_in_folder(self.folder_path)
            self.file_list = sorted(full_paths)
            self.populate_file_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.file_list = []

    def populate_file_list(self):
        for w in self.file_scroll_frame.winfo_children(): w.destroy()
        self.file_buttons = []
        for idx, path in enumerate(self.file_list):
            btn = ctk.CTkButton(self.file_scroll_frame, text=os.path.basename(path), anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), height=30, border_width=0, corner_radius=8, command=lambda i=idx: self.on_file_click(i))
            btn.pack(fill="x", padx=4, pady=1)
            self.file_buttons.append(btn)
        if self.file_list and self.current_file_index == -1:
            self.current_file_index = 0
            self.load_current_file()

    def on_file_click(self, index):
        self.current_file_index = index
        self.load_current_file()

    def load_current_file(self):
        if not self.file_list or not (0 <= self.current_file_index < len(self.file_list)): return
        filepath = self.file_list[self.current_file_index]
        
        # Highlight UI
        if self.last_file_index != -1 and self.last_file_index < len(self.file_buttons):
            self.file_buttons[self.last_file_index].configure(fg_color="transparent", text_color=("gray10", "gray90"))
        if self.current_file_index < len(self.file_buttons):
            self.file_buttons[self.current_file_index].configure(fg_color=["#3B8ED0", "#1F6AA5"], text_color="white")
        self.last_file_index = self.current_file_index

        try:
            nfa_list = read_nfa_from_file(filepath)
            if len(nfa_list) < 2: return
            self.nfa1_original, self.nfa2_original = nfa_list[0], nfa_list[1]
            self.display_nfa_image(self.nfa1_original, "input1", "Input NFA 1")
            self.display_nfa_image(self.nfa2_original, "input2", "Input NFA 2")
            
            if self.is_auto_run: self.execute_algorithm_now()
            else: 
                self.clear_panel_image("output1", "Minimized NFA 1")
                self.clear_panel_image("output2", "Minimized NFA 2")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def prev_file(self):
        if not self.file_list: return
        self.current_file_index = (self.current_file_index - 1) % len(self.file_list)
        self.load_current_file()

    def next_file(self):
        if not self.file_list: return
        self.current_file_index = (self.current_file_index + 1) % len(self.file_list)
        self.load_current_file()

    # ==============================================================================
    # ALGORITHM EXECUTION (GIỮ NGUYÊN)
    # ==============================================================================
    def toggle_auto_run(self):
        self.is_auto_run = not self.is_auto_run
        if self.is_auto_run:
            self.btn_run_all.configure(text="STOP", fg_color="#E04F5F", hover_color="#C03947")
            self.execute_algorithm_now()
        else:
            self.btn_run_all.configure(text="RUN", fg_color=("#3B8ED0", "#338CD4"), hover_color=("#36719F", "#296899"))

    def execute_algorithm_now(self):
        if self.nfa1_original: self.run_minimization(self.nfa1_original, "output1", "Minimized NFA 1")
        if self.nfa2_original: self.run_minimization(self.nfa2_original, "output2", "Minimized NFA 2")

    def run_minimization(self, nfa_data, panel_key, title):
        Q, sigma, F, delta, filename = nfa_data
        if self.selected_algorithm == "Bianchini":
            try:
                minimized = MINIMIZENFA(1, Q=Q, sigma=sigma, F=F, delta=delta)
                new_Q, new_F, new_delta, state_labels = newNFA(minimized, Q, F, sigma, delta)
                pil_image = visualize(new_Q, new_F, new_delta, sigma, title.replace(" ", "_") + f"_{filename}", len(Q), state_labels=state_labels, return_fig=True)
                if pil_image: self.update_panel_image(pil_image, panel_key, title)
            except Exception as e:
                print(e)
                self.clear_panel_image(panel_key, "Error")
        elif self.selected_algorithm == "Tarjan":
             self.clear_panel_image(panel_key, "TODO: Implement Tarjan")

    def display_nfa_image(self, nfa_data, panel_key, title):
        Q, sigma, F, delta, filename = nfa_data
        try:
            pil_image = visualize(Q, F, delta, sigma, title.replace(" ", "_") + f"_{filename}", len(Q), return_fig=True)
            if pil_image: self.update_panel_image(pil_image, panel_key, title)
        except Exception as e: print(e)