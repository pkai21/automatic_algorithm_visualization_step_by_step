# ------------------------------------------------------------------------------
# Copyright (c) 2026 Phan_Van_Khai
# All rights reserved.
#
# This source code is the proprietary and confidential property of Phan_Van_Khai.
# Unauthorized copying, distribution, or modification of this file, 
# via any medium, is strictly prohibited.
# ------------------------------------------------------------------------------

import sys
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from gui.base import BaseView

# --- IMPORT LOGIC ---
from core.helper.read_input import list_nfa_files_in_folder, read_nfa_from_file
from core.src.bianchini_algo.algorithm_3 import MINIMIZENFA
from core.src.tarjan_algo.paige_tarjan import TARJANNFA
from core.helper.get_ouput import newNFA

# --- IMPORT BOTH VISUALIZATIONS ---
from core.visualization.visualization_bianchini_algo import visualize as visualize_v1
from core.visualization.visualization_couterexample import visualize_couterexample as visualize_v2

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
        self.nfa1_minimum = None
        self.nfa2_minimum = None
        self.file_buttons = []
        self.selected_algorithm = None
        self.is_auto_run = False
        self.is_auto_view = False 
        
        # --- VIEW STATES ---
        self.local_view_states = {
            "input1": "original",
            "input2": "original"
        }
        self.local_view_buttons = {} 
        
        # --- VIZ MODE MANAGEMENT ---
        self.panel_viz_modes = {
            "input1": "V1", "input2": "V1",
            "output1": "V1", "output2": "V1"
        }
        self.panel_data_cache = {} 

        self.is_maximized = False
        self.panel_wrappers = {} 

        self.theme_corner_radius = 20
        self.btn_corner_radius = 12
        self.section_bg_color = ("gray95", "gray17")
        self.main_bg_color = ("gray90", "gray13")
        self.configure(fg_color=self.main_bg_color)

        self._build_layout()
        self.show_algorithm_selection()

    def _build_layout(self):
        # 1. SIDEBAR CONTAINER 
        self.sidebar_width = 300
        self.sidebar_container = ctk.CTkFrame(self, width=self.sidebar_width, fg_color="transparent")
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        self.sidebar_container.pack_propagate(False)

        # 2. MAIN GRID 
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(0, 20), pady=20)
        
        self.grid_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.grid_frame.pack(expand=True, fill=tk.BOTH)
        
        self.grid_frame.grid_rowconfigure(0, weight=1)
        self.grid_frame.grid_rowconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

        layout_defs = [
            ("input1", 0, 0), ("input2", 0, 1), 
            ("output1", 1, 0), ("output2", 1, 1)
        ]
        
        self.panel_wrappers = {}

        for key, row, col in layout_defs:
            # Wrapper Frame 
            card = ctk.CTkFrame(self.grid_frame, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius, border_width=0)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            
            card.grid_rowconfigure(0, weight=1)
            card.grid_columnconfigure(0, weight=1)
            
            # Inner Container 
            container = ctk.CTkFrame(card, fg_color="transparent")
            container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            self.panel_wrappers[key] = card
            self.panels[key] = container
            
            # Canvas
            title = key.replace("input", "Input NFA ").replace("output", "Minimized NFA ")
            self.create_panel_canvas(key, title)
            
            # ==================================================================
            # CONTROL GROUP CONTAINER
            # ==================================================================
            control_group = ctk.CTkFrame(card, fg_color="transparent", height=30)
            control_group.place(relx=0.97, rely=0.02, anchor="ne")

            seg_btn = ctk.CTkSegmentedButton(control_group, values=["V1", "V2"], width=70, height=24,
                                             font=ctk.CTkFont(size=11, weight="bold"),
                                             selected_color="#3B8ED0",
                                             selected_hover_color="#36719F",
                                             unselected_color=("gray80", "gray30"),
                                             unselected_hover_color=("gray70", "gray40"),
                                             command=lambda v, k=key: self.on_switch_viz_mode(k, v))
            seg_btn.set("V1")
            seg_btn.pack(side="right", padx=0) 

            if key in ["input1", "input2"]:
                btn_toggle = ctk.CTkButton(control_group, text="Show Min", width=70, height=24, 
                                           font=ctk.CTkFont(size=11, weight="bold"),
                                           fg_color=("gray80", "gray30"), 
                                           text_color=("gray20", "gray90"),
                                           hover_color=("#3B8ED0", "#1F6AA5"),
                                           command=lambda k=key: self.toggle_local_view(k))
                btn_toggle.pack(side="right", padx=(0, 5)) 
                self.local_view_buttons[key] = btn_toggle

            # --- ZOOM EVENT ---
            if key in self.canvases:
                canvas_widget = self.canvases[key][0].get_tk_widget()
                canvas_widget.bind('<Double-1>', lambda event, k=key: self.toggle_maximize(k))

    # ==============================================================================
    # LOGIC RENDER & SWITCH MODE
    # ==============================================================================
    def on_switch_viz_mode(self, key, mode):
        self.panel_viz_modes[key] = mode
        if key in self.panel_data_cache:
            data, title = self.panel_data_cache[key]
            self._render_internal(data, key, title)

    def _render_internal(self, nfa_data, panel_key, title):
        mode = self.panel_viz_modes.get(panel_key, "V1")
        state_labels = None

        if len(nfa_data) == 7:
            Q, sigma, sigma_labels, F, delta, filename, state_labels = nfa_data
        else:
            Q, sigma, sigma_labels, F, delta, filename = nfa_data
        
        full_title = title.replace(" ", "_") + f"_{filename}"
        
        pil_image = None
        try:
            if mode == "V1":
                pil_image = visualize_v1(Q, F, delta, sigma, sigma_labels, full_title, len(Q), state_labels=state_labels, return_fig=True)
            else:
                pil_image = visualize_v2(Q, F, delta, sigma, sigma_labels, state_labels=state_labels, return_fig=True)
            
            if pil_image:
                self.update_panel_image(pil_image, panel_key, title)
        except Exception as e:
            print(f"Render Error ({mode}): {e}")

    def display_nfa_to_panel(self, nfa_data, panel_key, title):
        self.panel_data_cache[panel_key] = (nfa_data, title)
        self._render_internal(nfa_data, panel_key, title)

    # ==============================================================================
    # OTHER FUNCTIONS
    # ==============================================================================
    def toggle_maximize(self, target_key):
        layout_defs = [("input1", 0, 0), ("input2", 0, 1), ("output1", 1, 0), ("output2", 1, 1)]
        if self.is_maximized:
            for key, wrapper in self.panel_wrappers.items(): wrapper.grid_forget()
            for key, r, c in layout_defs: self.panel_wrappers[key].grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
            self.is_maximized = False
        else:
            for key, wrapper in self.panel_wrappers.items(): wrapper.grid_remove() 
            self.panel_wrappers[target_key].grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew", padx=0, pady=0)
            self.is_maximized = True
        self.grid_frame.update_idletasks()

    def toggle_local_view(self, key):
        is_showing_original = (self.local_view_states[key] == "original")
        target_nfa = None
        new_state = ""
        btn_text = ""
        btn_fg_color = ""

        if key == "input1":
            if is_showing_original:
                target_nfa = self.nfa1_minimum; new_state = "minimum"; btn_text = "Show Orig"; btn_fg_color = "#3B8ED0"
            else:
                target_nfa = self.nfa1_original; new_state = "original"; btn_text = "Show Min"; btn_fg_color = ("gray80", "gray30")
        elif key == "input2":
            if is_showing_original:
                target_nfa = self.nfa2_minimum; new_state = "minimum"; btn_text = "Show Orig"; btn_fg_color = "#3B8ED0"
            else:
                target_nfa = self.nfa2_original; new_state = "original"; btn_text = "Show Min"; btn_fg_color = ("gray80", "gray30")

        if target_nfa:
            title = "Input NFA 1" if key == "input1" else "Input NFA 2"
            self.display_nfa_to_panel(target_nfa, key, title)
            self.local_view_states[key] = new_state
            if key in self.local_view_buttons: self.local_view_buttons[key].configure(text=btn_text, fg_color=btn_fg_color)
        else:
            if new_state == "minimum": messagebox.showinfo("Info", "Chưa có dữ liệu Minimized NFA. Vui lòng bấm RUN trước.")

    def clear_sidebar(self):
        for widget in self.sidebar_container.winfo_children(): widget.destroy()

    def show_algorithm_selection(self):
        self.file_buttons = []
        self.current_file_index = -1
        self.is_auto_run = False
        self.is_auto_view = False
        self.file_list = []
        self.panel_data_cache = {} 
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
        left_frame2 = ctk.CTkFrame(self.sidebar_container, height=200, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        left_frame2.pack(side=tk.BOTTOM, fill=tk.X, anchor="s", pady=(15, 0))
        left_frame2.grid_columnconfigure(0, weight=1); left_frame2.grid_columnconfigure(1, weight=3); left_frame2.grid_columnconfigure(2, weight=1)
        left_frame2.grid_rowconfigure(0, weight=1); left_frame2.grid_rowconfigure(1, weight=1); left_frame2.grid_propagate(False)

        ctk.CTkButton(left_frame2, text="❮", width=40, height=40, font=ctk.CTkFont(size=30), fg_color="transparent", text_color=("gray40", "gray80"), hover_color=("gray90", "gray30"), command=self.prev_file).grid(row=0, column=0, rowspan=2)
        self.btn_run_all = ctk.CTkButton(left_frame2, text="RUN", width=110, height=50, corner_radius=25, font=ctk.CTkFont(size=14, weight="bold"), fg_color=("#3B8ED0", "#338CD4"), hover_color=("#36719F", "#296899"), command=self.toggle_auto_run)
        self.btn_run_all.grid(row=0, column=1, sticky="s", pady=(20, 5))
        self.btn_view = ctk.CTkButton(left_frame2, text="MINIMIM", width=110, height=50, corner_radius=25, font=ctk.CTkFont(size=14, weight="bold"), fg_color=("#3B8ED0", "#338CD4"), hover_color=("#36719F", "#296899"), command=self.toggle_auto_view)
        self.btn_view.grid(row=1, column=1, sticky="n", pady=(5, 20))
        ctk.CTkButton(left_frame2, text="❯", width=40, height=40, font=ctk.CTkFont(size=30), fg_color="transparent", text_color=("gray40", "gray80"), hover_color=("gray90", "gray30"), command=self.next_file).grid(row=0, column=2, rowspan=2)
        
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
        self.panel_data_cache = {}
        self.clear_panel_image("input1", "NFA 1")
        self.clear_panel_image("input2", "NFA 2")
        self.clear_panel_image("output1", "Minimized NFA 1")
        self.clear_panel_image("output2", "Minimized NFA 2")
        
        if not self.file_list or not (0 <= self.current_file_index < len(self.file_list)): return
        filepath = self.file_list[self.current_file_index]
        
        if self.last_file_index != -1 and self.last_file_index < len(self.file_buttons):
            self.file_buttons[self.last_file_index].configure(fg_color="transparent", text_color=("gray10", "gray90"))
        if self.current_file_index < len(self.file_buttons):
            self.file_buttons[self.current_file_index].configure(fg_color=["#3B8ED0", "#1F6AA5"], text_color="white")
        self.last_file_index = self.current_file_index

        try:
            nfa_list = read_nfa_from_file(filepath)
            if len(nfa_list) < 2: return
            self.nfa1_original, self.nfa2_original = nfa_list[0], nfa_list[2]
            self.nfa1_minimum, self.nfa2_minimum = nfa_list[1], nfa_list[3]

            self.local_view_states["input1"] = "original"
            self.local_view_states["input2"] = "original"
            for key in ["input1", "input2"]:
                if key in self.local_view_buttons: self.local_view_buttons[key].configure(text="Show Min", fg_color=("gray80", "gray30"))

            if self.is_auto_view:
                self.display_nfa_to_panel(self.nfa1_minimum, "input1", "Input NFA 1")
                self.display_nfa_to_panel(self.nfa2_minimum, "input2", "Input NFA 2")
                
                self.local_view_states["input1"] = "minimum"; self.local_view_states["input2"] = "minimum"
                for key in ["input1", "input2"]:
                    if key in self.local_view_buttons: self.local_view_buttons[key].configure(text="Show Orig", fg_color="#3B8ED0")
            else:
                self.display_nfa_to_panel(self.nfa1_original, "input1", "Input NFA 1")
                self.display_nfa_to_panel(self.nfa2_original, "input2", "Input NFA 2")

            if self.is_auto_run: self.execute_algorithm_now()
        except Exception as e: messagebox.showerror("Error", str(e))

    def prev_file(self):
        if not self.file_list: return
        self.current_file_index = (self.current_file_index - 1) % len(self.file_list)
        self.load_current_file()

    def next_file(self):
        if not self.file_list: return
        self.current_file_index = (self.current_file_index + 1) % len(self.file_list)
        self.load_current_file()

    def toggle_auto_run(self):
        self.is_auto_run = not self.is_auto_run
        if self.is_auto_run:
            self.btn_run_all.configure(text="STOP", fg_color="#E04F5F", hover_color="#C03947")
            self.execute_algorithm_now()
        else:
            self.btn_run_all.configure(text="RUN", fg_color=("#3B8ED0", "#338CD4"), hover_color=("#36719F", "#296899"))
            self.clear_panel_image("output1", "Minimized NFA 1")
            self.clear_panel_image("output2", "Minimized NFA 2")

    def toggle_auto_view(self):
        self.clear_panel_image("input1", "NFA 1")
        self.clear_panel_image("input2", "NFA 2")
        self.is_auto_view = not self.is_auto_view
        if self.is_auto_view:
            self.btn_view.configure(text="ORIGINAL", fg_color="#E04F5F", hover_color="#C03947")
            self.display_nfa_to_panel(self.nfa1_minimum, "input1", "Input NFA 1")
            self.display_nfa_to_panel(self.nfa2_minimum, "input2", "Input NFA 2")
            self.local_view_states["input1"] = "minimum"; self.local_view_states["input2"] = "minimum"
            for key in ["input1", "input2"]:
                if key in self.local_view_buttons: self.local_view_buttons[key].configure(text="Show Orig", fg_color="#3B8ED0")
        else:
            self.btn_view.configure(text="MINIMIM", fg_color=("#3B8ED0", "#338CD4"), hover_color=("#36719F", "#296899"))
            self.display_nfa_to_panel(self.nfa1_original, "input1", "Input NFA 1")
            self.display_nfa_to_panel(self.nfa2_original, "input2", "Input NFA 2")
            self.local_view_states["input1"] = "original"; self.local_view_states["input2"] = "original"
            for key in ["input1", "input2"]:
                if key in self.local_view_buttons: self.local_view_buttons[key].configure(text="Show Min", fg_color=("gray80", "gray30"))

    def execute_algorithm_now(self):
        if self.nfa1_original: self.run_minimization(self.nfa1_original, "output1", "Minimized NFA 1")
        if self.nfa2_original: self.run_minimization(self.nfa2_original, "output2", "Minimized NFA 2")

    def run_minimization(self, nfa_data, panel_key, title):
        Q, sigma, sigma_labels, F, delta, filename = nfa_data
        
        try:
            minimized = None
            if self.selected_algorithm == "Bianchini":
                minimized = MINIMIZENFA(1, Q=Q, sigma=sigma, F=F, delta=delta)
            elif self.selected_algorithm == "Tarjan":
                minimized = TARJANNFA(Q=Q, sigma=sigma, F=F, delta=delta)
            
            is_valid_result = False
            if minimized and isinstance(minimized, list) and len(minimized) > 0:
                if any(group for group in minimized): 
                    is_valid_result = True

            if is_valid_result:
                new_Q, new_F, new_delta, state_labels = newNFA(minimized, Q, F, sigma, delta)
                
                result_data = (new_Q, sigma, sigma_labels, new_F, new_delta, filename, state_labels)
                self.panel_data_cache[panel_key] = (result_data, title)
                
                mode = self.panel_viz_modes.get(panel_key, "V1")
                full_title = title + f"_{filename}"
                pil_image = None

                if mode == "V1":
                     pil_image = visualize_v1(new_Q, new_F, new_delta, sigma, sigma_labels, full_title, len(Q), state_labels=state_labels, return_fig=True)
                else:
                     pil_image = visualize_v2(new_Q, new_F, new_delta, sigma, sigma_labels, state_labels=state_labels, return_fig=True)

                if pil_image: 
                    self.update_panel_image(pil_image, panel_key, title)
            else:
                print(f"Warning: {self.selected_algorithm} returned invalid result: {minimized}")
                
        except Exception as e:
            print(f"Error running {self.selected_algorithm}: {e}")
            import traceback
            traceback.print_exc() 
            self.clear_panel_image(panel_key, "Error")

    def display_nfa_image(self, nfa_data, panel_key, title):
        self.display_nfa_to_panel(nfa_data, panel_key, title)