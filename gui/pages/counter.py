# ------------------------------------------------------------------------------
# Copyright (c) 2026 Phan_Van_Khai
# All rights reserved.
#
# This source code is the proprietary and confidential property of Phan_Van_Khai.
# Unauthorized copying, distribution, or modification of this file, 
# via any medium, is strictly prohibited.
# ------------------------------------------------------------------------------

import sys
import tkinter as tk
import customtkinter as ctk
from core.gen.auto_gen_nfa.finite_gen_NFA_minimazation import finite_generate_delta
from core.gen.auto_gen_nfa.infinite_gen_NFA_minimazation import infinite_generate_delta
from core.gen.auto_gen_nfa.gen_NFA import gene_NFA
from core.helper.kameda_algo.get_output_kameda import get_kameda_out
from core.helper.kameda_algo.set_input_kameda import set_kameda_in
from core.helper.write_input import write_test_case
from core.helper.export_input_config_bianchini import get_nfa_config
from core.src.kameda_algo.algorithm_kameda import KamedaWeinerMinimizer
from core.src.tarjan_algo.paige_tarjan import TARJANNFA
from gui.base import BaseView

# --- IMPORT CORE LOGIC ---
from core.gen.validate import validate_Q, validate_F
from core.helper.input_config_bianchini import convert_F, convert_to_2d_array, convert_sigma

# --- IMPORT BOTH VISUALIZATIONS ---
from core.visualization.visualization_couterexample import visualize_couterexample as visualize_v1 
from core.visualization.visualization_bianchini_algo import visualize as visualize_v2            

# Import Algorithm
from core.src.bianchini_algo.algorithm_3 import MINIMIZENFA 
from core.helper.get_ouput import newNFA

class CounterExamplePage(BaseView):
    def __init__(self, master, on_home, **kwargs):
        super().__init__(master, **kwargs)
        self.on_home = on_home

        self.previous_mode = "manual"
        # --- DATA VARIABLES ---
        self.Q_counterexample = []
        self.F_counterexample = []
        self.sigma_counterexample = []
        self.sigma_labels_counterexample = {}
        self.delta_counterexample = []
        self.delta_rows = []

        # ---DATA MIMI --
        self.Q_mini_counterexample = []
        self.F_mini_counterexample = []
        self.delta_mini_counterexample = []

        # --- DATA AUTO ---
        self.auto_Q_count = 0
        self.auto_F_count = 0
        
        self.selected_algorithm = "Bianchini" 
        self.is_maximized = False
        self.maximized_frame = None

        # --- VIZ MODE & CACHE ---
        self.panel_data_cache = {} 
        self.panel_viz_modes = {} 

        # --- THEME CONFIGURATION ---
        self.theme_corner_radius = 20
        self.btn_corner_radius = 12
        self.section_bg_color = ("gray95", "gray17")
        self.main_bg_color = ("gray90", "gray13")
        
        self.configure(fg_color=self.main_bg_color)

        self.sidebar_container = ctk.CTkFrame(self, fg_color="transparent")
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        self.sidebar_container.pack_propagate(False) 

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(0, 20), pady=20)

        self.setup_selection_mode()

    def _clear_ui(self):
        for w in self.sidebar_container.winfo_children(): w.destroy()
        for w in self.main_area.winfo_children(): w.destroy()
        self.main_area.grid_columnconfigure(0, weight=0)
        self.main_area.grid_columnconfigure(1, weight=0)
        self.main_area.grid_rowconfigure(0, weight=0)
        self.main_area.grid_rowconfigure(1, weight=0)
        self.is_maximized = False
        self.maximized_frame = None
        self.panel_data_cache = {}
        self.panel_viz_modes = {}

    def setup_selection_mode(self):
        self._clear_ui()
        self.sidebar_container.configure(width=350)
        ctk.CTkButton(self.sidebar_container, text="🏠 Home Screen", fg_color="transparent", 
                      border_width=1, text_color="gray", command=self.on_home).pack(side=tk.TOP, anchor="w", pady=(0, 20))
        
        selection_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        selection_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ctk.CTkLabel(selection_frame, text="SELECT MODE", font=ctk.CTkFont(size=20, weight="bold"), 
                     text_color=("gray40", "gray70")).pack(pady=(30, 20))

        ctk.CTkButton(selection_frame, text="Automatically generate an NFA", 
                      font=ctk.CTkFont(size=16, weight="bold"), height=50,
                       fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius,
                      command=self.setup_auto_mode).pack(pady=15, padx=20, fill="x")

        ctk.CTkButton(selection_frame, text="Manually generate an NFA", 
                      font=ctk.CTkFont(size=16, weight="bold"), height=50,
                      fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius,
                      command=self.setup_input_mode).pack(pady=15, padx=20, fill="x")

        welcome_frame = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        welcome_frame.pack(expand=True, fill="both")
        ctk.CTkLabel(welcome_frame, text="Counter-Example Generator", font=ctk.CTkFont(size=30, weight="bold")).place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(welcome_frame, text="Please select an input method from the sidebar to begin.", 
                     font=ctk.CTkFont(size=16), text_color="gray").place(relx=0.5, rely=0.5, anchor="center")

    # ==============================================================================
    # ADD VIZ CONTROLS
    # ==============================================================================
    def add_viz_control(self, parent_frame, panel_key):
        """Thêm nút segmented V1/V2 vào góc panel"""
        self.panel_viz_modes[panel_key] = "V1" 
        
        seg_btn = ctk.CTkSegmentedButton(parent_frame, values=["V1", "V2"], width=60, height=24,
                                         font=ctk.CTkFont(size=10, weight="bold"),
                                         selected_color="#3B8ED0",
                                         unselected_color=("gray80", "gray30"),
                                         command=lambda v, k=panel_key: self.on_switch_viz_mode(k, v))
        seg_btn.set("V1")
        seg_btn.place(relx=0.96, rely=0.02, anchor="ne")

    def on_switch_viz_mode(self, key, mode):
        self.panel_viz_modes[key] = mode
        if key in self.panel_data_cache:
            self._render_from_cache(key)

    def _cache_and_render(self, key, Q, F, delta, sigma, labels, title, state_labels=None):
        """Lưu data và vẽ"""
        self.panel_data_cache[key] = {
            'Q': Q, 'F': F, 'delta': delta, 'sigma': sigma, 
            'labels': labels, 'title': title, 'state_labels': state_labels
        }
        self._render_from_cache(key)

    def _render_from_cache(self, key):
        data = self.panel_data_cache.get(key)
        if not data: return
        
        mode = self.panel_viz_modes.get(key, "V1")
        pil_image = None
        
        try:
            if mode == "V1":
                pil_image = visualize_v1(data['Q'], data['F'], data['delta'], 
                                         data['sigma'], data['labels'], 
                                         state_labels=data.get('state_labels'), return_fig=True)
            else:
                full_title = data['title'].replace(" ", "_") + "_viz"
                pil_image = visualize_v2(data['Q'], data['F'], data['delta'], 
                                         data['sigma'], data['labels'], 
                                         full_title, len(data['Q']), 
                                         state_labels=data.get('state_labels'), return_fig=True)
            
            if pil_image:
                self.update_panel_image(pil_image, key, data['title'])
        except Exception as e:
            print(f"Render Error {key} [{mode}]: {e}")

    # ==============================================================================
    # AUTO MODE
    # ==============================================================================
    def setup_auto_mode(self):
        self._clear_ui()
        self.Q_counterexample = []
        self.F_counterexample = []
        self.sigma_counterexample = []
        self.sigma_labels_counterexample = {}
        self.delta_counterexample = []
        self.delta_rows = []
        self.Q_mini_counterexample = []
        self.F_mini_counterexample = []
        self.delta_mini_counterexample = []
        self.previous_mode = "auto"

        self.sidebar_container.configure(width=400)
        ctk.CTkButton(self.sidebar_container, text="← Back to Mode Select", fg_color="transparent", 
                      border_width=1, text_color="gray", command=self.setup_selection_mode).pack(side=tk.TOP, anchor="w", pady=(0, 10))
        
        auto_input_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        auto_input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ctk.CTkLabel(auto_input_frame, text="AUTO GENERATOR", font=ctk.CTkFont(size=20, weight="bold"), 
                     text_color=("gray40", "gray70")).pack(pady=(15, 15))

        # INPUT Q/F/Sigma 
        ctk.CTkLabel(auto_input_frame, text="Set number of States (Q) (> 3):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(5, 2), fill="x")
        self.entry_Q_auto = ctk.CTkEntry(auto_input_frame, height=35)
        self.entry_Q_auto.pack(padx=20, pady=(0, 8), fill="x")
        self.entry_Q_auto.bind("<FocusOut>", self.validate_Q_auto)
        self.entry_Q_auto.bind("<Return>", self.validate_Q_auto)

        ctk.CTkLabel(auto_input_frame, text="Set number of Final States (F) (< Q):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(5, 2), fill="x")
        self.entry_F_auto = ctk.CTkEntry(auto_input_frame, height=35)
        self.entry_F_auto.pack(padx=20, pady=(0, 8), fill="x")
        self.entry_F_auto.bind("<FocusOut>", self.validate_F_auto)
        self.entry_F_auto.bind("<Return>", self.validate_F_auto)

        ctk.CTkLabel(auto_input_frame, text="Alphabet (Σ):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(5, 2), fill="x")
        self.entry_sigma_auto = ctk.CTkEntry(auto_input_frame, height=35)
        self.entry_sigma_auto.pack(padx=20, pady=(0, 20), fill="x")
        self.entry_sigma_auto.bind("<FocusOut>", self.validate_sigma_auto)
        self.entry_sigma_auto.bind("<Return>", self.validate_sigma_auto)

        type_frame = ctk.CTkFrame(auto_input_frame, fg_color="transparent")
        type_frame.pack(padx=20, pady=10, fill="x")
        type_frame.grid_columnconfigure(0, weight=1)
        type_frame.grid_columnconfigure(1, weight=1)
        self.btn_infinite = ctk.CTkButton(type_frame, text="Infinite NFA", height=40, fg_color="#3B8ED0", hover_color="#36719F", font=ctk.CTkFont(size=13, weight="bold"), command=self.on_click_infinite_nfa)
        self.btn_infinite.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.btn_finite = ctk.CTkButton(type_frame, text="Finite NFA", height=40, fg_color="#3B8ED0", hover_color="#36719F", font=ctk.CTkFont(size=13, weight="bold"), command=self.on_click_finite_nfa)
        self.btn_finite.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        ctk.CTkFrame(auto_input_frame, height=2, fg_color=("gray80", "gray30")).pack(fill="x", padx=20, pady=20)
        self.btn_generate_auto = ctk.CTkButton(auto_input_frame, text="GENERATE EXAMPLE", font=ctk.CTkFont(size=16, weight="bold"), height=45, fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius, command=self.setup_result_mode)
        self.btn_generate_auto.pack(padx=20, pady=(0, 20), fill="x")

        # --- MAIN AREA LAYOUT ---
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Top Frame
        self.frame_auto_top = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_auto_top.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 5)) 
        viz_inner_top = ctk.CTkFrame(self.frame_auto_top, fg_color="transparent")
        viz_inner_top.pack(expand=True, fill="both", padx=10, pady=10)
        self.panels['auto_viz_top'] = viz_inner_top
        self.create_panel_canvas("auto_viz_top", "NFA")
        
        self.add_viz_control(self.frame_auto_top, "auto_viz_top")

        if "auto_viz_top" in self.canvases:
            self.canvases["auto_viz_top"][0].get_tk_widget().bind('<Double-1>', lambda event: self.toggle_maximize(self.frame_auto_top))

        # Bottom Frame
        self.frame_auto_bottom = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_auto_bottom.grid(row=1, column=0, sticky="nsew", padx=0, pady=(5, 0))
        viz_inner_bottom = ctk.CTkFrame(self.frame_auto_bottom, fg_color="transparent")
        viz_inner_bottom.pack(expand=True, fill="both", padx=10, pady=10)
        self.panels['auto_viz_bottom'] = viz_inner_bottom
        self.create_panel_canvas("auto_viz_bottom", "Minimum NFA")
  
        self.add_viz_control(self.frame_auto_bottom, "auto_viz_bottom")

        if "auto_viz_bottom" in self.canvases:
            self.canvases["auto_viz_bottom"][0].get_tk_widget().bind('<Double-1>', lambda event: self.toggle_maximize(self.frame_auto_bottom))

    # ==============================================================================
    # INPUT MODE
    # ==============================================================================
    def setup_input_mode(self):
        self._clear_ui()
        self.Q_counterexample = []
        self.F_counterexample = []
        self.sigma_counterexample = []
        self.sigma_labels_counterexample = {}
        self.delta_counterexample = []
        self.delta_rows = []
        self.previous_mode = "manual"
        self.sidebar_container.configure(width=400)
        
        ctk.CTkButton(self.sidebar_container, text="← Back to Mode Select", fg_color="transparent", 
                      border_width=1, text_color="gray", command=self.setup_selection_mode).pack(side=tk.TOP, anchor="w", pady=(0, 10))
        
        input_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ctk.CTkLabel(input_frame, text="MANUAL INPUT", font=ctk.CTkFont(size=20, weight="bold"), text_color=("gray40", "gray70")).pack(pady=(15, 15))

        ctk.CTkLabel(input_frame, text="Set number of States (Q):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(5, 2), fill="x")
        self.entry_Q = ctk.CTkEntry(input_frame, height=35)
        self.entry_Q.pack(padx=20, pady=(0, 8), fill="x")
        self.entry_Q.bind("<FocusOut>", self.validate_Q_interactive)
        self.entry_Q.bind("<Return>", self.validate_Q_interactive)
        if self.Q_counterexample: self.entry_Q.insert(0, str(len(self.Q_counterexample)))

        ctk.CTkLabel(input_frame, text="Final States Indices (e.g: 0 2):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(5, 2), fill="x")
        self.entry_F = ctk.CTkEntry(input_frame, height=35)
        self.entry_F.pack(padx=20, pady=(0, 8), fill="x")
        self.entry_F.bind("<FocusOut>", self.validate_F_interactive)
        self.entry_F.bind("<Return>", self.validate_F_interactive)
        if self.F_counterexample:
            f_indices = [str(i) for i, val in enumerate(self.F_counterexample) if val == 1]
            self.entry_F.insert(0, " ".join(f_indices))

        ctk.CTkLabel(input_frame, text="Alphabet (Σ):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(5, 2), fill="x")
        self.entry_sigma = ctk.CTkEntry(input_frame, height=35)
        self.entry_sigma.pack(padx=20, pady=(0, 10), fill="x")
        self.entry_sigma.bind("<FocusOut>", self.validate_sigma_interactive)
        self.entry_sigma.bind("<Return>", self.validate_sigma_interactive)
        if self.sigma_counterexample: self.entry_sigma.insert(0, " ".join(map(str, self.sigma_counterexample)))

        delta_header = ctk.CTkFrame(input_frame, fg_color="transparent")
        delta_header.pack(padx=20, pady=(5, 5), fill="x")
        ctk.CTkLabel(delta_header, text="Transitions (δ) :", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(delta_header, text="+", width=25, height=25, font=ctk.CTkFont(size=18, weight="bold"), fg_color="#2CC985", hover_color="#25A970", command=self.add_transition_row).pack(side="right")

        self.delta_scroll = ctk.CTkScrollableFrame(input_frame, height=140, fg_color="transparent", label_text=None)
        self.delta_scroll.pack(padx=10, pady=(0, 5), fill="x", expand=False)
        self.delta_rows = []
        if not self.delta_rows: self.add_transition_row()

        ctk.CTkFrame(input_frame, height=2, fg_color=("gray80", "gray30")).pack(fill="x", padx=20, pady=10)
        self.btn_generate = ctk.CTkButton(input_frame, text="GENERATE EXAMPLE", font=ctk.CTkFont(size=16, weight="bold"), height=45, fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius, command=self.switch_to_result_mode)
        self.btn_generate.pack(padx=20, pady=(5, 20), fill="x")

        # --- Visualization Panel ---
        viz_container = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        viz_container.pack(expand=True, fill="both")
        viz_inner = ctk.CTkFrame(viz_container, fg_color="transparent")
        viz_inner.pack(expand=True, fill="both", padx=10, pady=10)
        self.panels['counter_input_viz'] = viz_inner
        self.create_panel_canvas("counter_input_viz", "Counter-Example Preview")
        
        self.add_viz_control(viz_container, "counter_input_viz")
        
        if self.Q_counterexample: self.perform_visualization("counter_input_viz")

    # ==============================================================================
    # RESULT MODE
    # ==============================================================================
    def setup_result_mode(self):
        self._clear_ui()
        self.sidebar_container.configure(width=300)

        def go_back():
            if self.previous_mode == "auto": self.setup_auto_mode()
            else: self.setup_input_mode()
                
        ctk.CTkButton(self.sidebar_container, text="← Back to Edit", fg_color="transparent", border_width=1, text_color="gray", command=go_back).pack(side=tk.TOP, anchor="w", pady=(0, 10))
        
        algo_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        algo_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(algo_frame, text="ALGORITHMS", font=ctk.CTkFont(size=18, weight="bold"), text_color=("gray40", "gray70")).pack(pady=(20, 10))
        self.algo_var = tk.StringVar(value=self.selected_algorithm)
        ctk.CTkRadioButton(algo_frame, text="Bianchini Algorithm", variable=self.algo_var, value="Bianchini", font=ctk.CTkFont(size=14)).pack(pady=10, padx=20, anchor="w")
        ctk.CTkRadioButton(algo_frame, text="Tarjan Algorithm", variable=self.algo_var, value="Tarjan", font=ctk.CTkFont(size=14)).pack(pady=10, padx=20, anchor="w")
        
        ctk.CTkButton(algo_frame, text="RUN OPTIMIZATION", font=ctk.CTkFont(size=14, weight="bold"), height=50, fg_color="#2CC985", hover_color="#25A970", corner_radius=self.btn_corner_radius, command=self.run_optimization_logic).pack(padx=20, pady=(30, 10), fill="x")
        ctk.CTkFrame(algo_frame, height=2, fg_color=("gray80", "gray30")).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(algo_frame, text="Save Test Case", font=ctk.CTkFont(size=14, weight="bold"), height=50, fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius, command=self.save_test_case_to_file).pack(padx=20, pady=(10, 30), fill="x")

        self.main_area.grid_columnconfigure(0, weight=1) 
        self.main_area.grid_columnconfigure(1, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        self.frame_input = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_input.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=0)
        self.frame_out1 = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_out1.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        self.frame_out2 = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_out2.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))

        def setup_panel(container_frame, panel_key, title):
            inner = ctk.CTkFrame(container_frame, fg_color="transparent")
            inner.pack(expand=True, fill="both", padx=5, pady=5)
            self.panels[panel_key] = inner
            self.create_panel_canvas(panel_key, title)
            self.add_viz_control(container_frame, panel_key)
            if panel_key in self.canvases:
                self.canvases[panel_key][0].get_tk_widget().bind('<Double-1>', lambda event, f=container_frame: self.toggle_maximize(f))

        setup_panel(self.frame_input, "result_input", "Original NFA")
        setup_panel(self.frame_out1, "result_output1", "Algorithm Result")
        setup_panel(self.frame_out2, "result_output2", "Minimum NFA")

        self.perform_visualization("result_input")
        self.perform_mini_visualization("result_output2")

    # ==============================================================================
    # OTHER LOGIC (ZOOM / VALIDATE / GENERATE)
    # ==============================================================================
    def toggle_maximize(self, target_frame):
        is_auto_mode = target_frame in [getattr(self, 'frame_auto_top', None), getattr(self, 'frame_auto_bottom', None)]
        if is_auto_mode: all_frames = [self.frame_auto_top, self.frame_auto_bottom]
        else: all_frames = [self.frame_input, self.frame_out1, self.frame_out2]

        if self.is_maximized:
            for f in all_frames: f.grid_forget()
            if is_auto_mode:
                self.frame_auto_top.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 5))
                self.frame_auto_bottom.grid(row=1, column=0, sticky="nsew", padx=0, pady=(5, 0))
            else:
                self.frame_input.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=0)
                self.frame_out1.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
                self.frame_out2.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
            self.is_maximized = False
            self.maximized_frame = None
        else:
            for f in all_frames: f.grid_remove()
            target_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew", padx=0, pady=0)
            self.is_maximized = True
            self.maximized_frame = target_frame
        self.main_area.update_idletasks()

    def on_click_infinite_nfa(self):
        self.clear_panel_image("auto_viz_top")
        self.clear_panel_image("auto_viz_bottom")
        if not self._validate_auto_inputs(): return

        delta_mini = infinite_generate_delta(self.auto_Q_count, self.auto_F_count, self.sigma_counterexample)
        self.Q_mini_counterexample = [i for i in range(self.auto_Q_count)]
        self.F_mini_counterexample = [0] * self.auto_Q_count
        for i in range((self.auto_Q_count - self.auto_F_count),self.auto_Q_count): self.F_mini_counterexample[i] = 1
        self.delta_mini_counterexample = convert_to_2d_array(delta_mini,self.Q_mini_counterexample,self.sigma_counterexample)
        
        self._cache_and_render("auto_viz_bottom", self.Q_mini_counterexample, self.F_mini_counterexample, self.delta_mini_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, "Minimum NFA")
        
        F1_val = [i for i in range((self.auto_Q_count-self.auto_F_count),self.auto_Q_count)]
        self.Q_counterexample, delta, F2_val = gene_NFA(self.Q_mini_counterexample, delta_mini, F1_val)
        self.F_counterexample = [0] * len(self.Q_counterexample)
        for i in F2_val: self.F_counterexample[i] = 1
        self.delta_counterexample = convert_to_2d_array(delta,self.Q_counterexample ,self.sigma_counterexample)

        self._cache_and_render("auto_viz_top", self.Q_counterexample, self.F_counterexample, self.delta_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, "NFA")

    def on_click_finite_nfa(self):
        self.clear_panel_image("auto_viz_top")
        self.clear_panel_image("auto_viz_bottom")
        if not self._validate_auto_inputs(): return

        delta_mini = finite_generate_delta(self.auto_Q_count, self.auto_F_count, self.sigma_counterexample)
        self.Q_mini_counterexample = [i for i in range(self.auto_Q_count)]
        self.F_mini_counterexample = [0] * self.auto_Q_count
        for i in range((self.auto_Q_count-self.auto_F_count),self.auto_Q_count): self.F_mini_counterexample[i] = 1
        self.delta_mini_counterexample = convert_to_2d_array(delta_mini,self.Q_mini_counterexample,self.sigma_counterexample)
        
        self._cache_and_render("auto_viz_bottom", self.Q_mini_counterexample, self.F_mini_counterexample, self.delta_mini_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, "Minimum NFA")
        
        F1_val = [i for i in range((self.auto_Q_count-self.auto_F_count),self.auto_Q_count)]
        self.Q_counterexample, delta, F2_val = gene_NFA(self.Q_mini_counterexample, delta_mini, F1_val)
        self.F_counterexample = [0] * len(self.Q_counterexample)
        for i in F2_val: self.F_counterexample[i] = 1
        self.delta_counterexample = convert_to_2d_array(delta,self.Q_counterexample ,self.sigma_counterexample)

        self._cache_and_render("auto_viz_top", self.Q_counterexample, self.F_counterexample, self.delta_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, "NFA")

    def run_optimization_logic(self):
        algo = self.algo_var.get()
        self.selected_algorithm = algo
        self.clear_panel_image("result_output1", f"Processing {algo}...")        
        if algo == "Bianchini":
            try:
                minimized = MINIMIZENFA(1, Q=self.Q_counterexample, sigma=self.sigma_counterexample, F=self.F_counterexample, delta=self.delta_counterexample)
                new_Q, new_F, new_delta, state_labels = newNFA(minimized, self.Q_counterexample, self.F_counterexample, self.sigma_counterexample, self.delta_counterexample)

                self._cache_and_render("result_output1", new_Q, new_F, new_delta, self.sigma_counterexample, self.sigma_labels_counterexample, "Minimized NFA", state_labels=state_labels)
                
            except Exception as e:
                self.clear_panel_image("result_output1", f"Error: {str(e)}")
        elif algo == "Tarjan":
            try:
                minimized = TARJANNFA(Q=self.Q_counterexample, sigma=self.sigma_counterexample, F=self.F_counterexample, delta=self.delta_counterexample)
                new_Q, new_F, new_delta, state_labels = newNFA(minimized, self.Q_counterexample, self.F_counterexample, self.sigma_counterexample, self.delta_counterexample)

                self._cache_and_render("result_output1", new_Q, new_F, new_delta, self.sigma_counterexample, self.sigma_labels_counterexample, "Minimized NFA", state_labels=state_labels)
                
            except Exception as e:
                self.clear_panel_image("result_output1", f"Error: {str(e)}")

    def perform_visualization(self, panel_key):
        self._cache_and_render(panel_key, self.Q_counterexample, self.F_counterexample, self.delta_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, "Visual Preview")
    
    def perform_mini_visualization(self, panel_key):
        if self.Q_mini_counterexample == []: 
            nfa = set_kameda_in(self.sigma_counterexample, self.sigma_labels_counterexample, self.F_counterexample,self.delta_counterexample)
            print("--- Original NFA ---")
            print(nfa.transitions)
            minimizer = KamedaWeinerMinimizer(nfa)
            min_nfa = minimizer.run()
            print("\n--- Minimized NFA (Kameda-Weiner) ---")
            print(min_nfa.start_states)
            print(min_nfa.accept_states)
            print(min_nfa.alphabet)
            print("Transitions:")
            for src, trans in min_nfa.transitions.items():
                for char, dests in trans.items():
                    print(f"  {src} --{char}--> {dests}")
            self.Q_mini_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, self.F_mini_counterexample, self.delta_mini_counterexample = get_kameda_out(min_nfa)
             
        self._cache_and_render(panel_key, self.Q_mini_counterexample, self.F_mini_counterexample, self.delta_mini_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, "Visual Preview")

    def _validate_auto_inputs(self):
        v_q = self.validate_Q_auto(is_submit=True)
        v_f = self.validate_F_auto(is_submit=True)
        v_s = self.validate_sigma_auto(is_submit=True)
        return v_q and v_f and v_s

    def validate_Q_auto(self, event=None, is_submit=False):
        q_str = self.entry_Q_auto.get().strip()
        if not q_str:
            color = "#C55455" if is_submit else ("gray", "gray")
            self.entry_Q_auto.configure(border_color=color)
            return False
        if q_str.isdigit():
            val = int(q_str)
            if val > 3:
                self.auto_Q_count = val
                self.entry_Q_auto.configure(border_color="#3B8ED0", text_color=("black", "white"))
                if not is_submit: self.validate_F_auto() 
                return True
            else:
                self.entry_Q_auto.configure(border_color="#C55455", text_color="#C55455")
                return False
        else:
            self.entry_Q_auto.configure(border_color="#C55455", text_color="#C55455")
            return False

    def validate_F_auto(self, event=None, is_submit=False):
        f_str = self.entry_F_auto.get().strip()
        if not f_str:
            color = "#C55455" if is_submit else ("gray", "gray")
            self.entry_F_auto.configure(border_color=color)
            return False
        if self.auto_Q_count <= 3:
            self.entry_F_auto.configure(border_color="#C55455")
            return False
        if f_str.isdigit():
            val = int(f_str)
            if 0 < val < self.auto_Q_count:
                self.auto_F_count = val
                self.entry_F_auto.configure(border_color="#3B8ED0", text_color=("black", "white"))
                return True
            else:
                self.entry_F_auto.configure(border_color="#C55455", text_color="#C55455")
                return False
        else:
            self.entry_F_auto.configure(border_color="#C55455", text_color="#C55455")
            return False

    def validate_sigma_auto(self, event=None, is_submit=False):
        raw_text = self.entry_sigma_auto.get().strip()
        if not raw_text:
            color = "#C55455" if is_submit else ("gray", "gray")
            self.entry_sigma_auto.configure(border_color=color)
            self.sigma_counterexample = []
            self.sigma_labels_counterexample ={}
            return False
        try:
            parsed = [int(s) for s in raw_text.replace(',', ' ').split() if s]
            if parsed:
                self.sigma_counterexample, self.sigma_labels_counterexample = convert_sigma(parsed)
                self.entry_sigma_auto.configure(border_color="#3B8ED0", text_color=("black", "white"))
                return True
            else:
                self.entry_sigma_auto.configure(border_color="#C55455")
                return False
        except:
            self.entry_sigma_auto.configure(border_color="#C55455")
            return False

    def switch_to_result_mode(self):
        list_delta_temp = self.collect_delta_data()
        if not self.Q_counterexample: return
        try:
            self.delta_counterexample = convert_to_2d_array(list_delta_temp, self.Q_counterexample, self.sigma_counterexample)
            self.setup_result_mode()
        except Exception as e: print(e)

    def validate_Q_interactive(self, event=None):
        q_str = self.entry_Q.get().strip()
        if not q_str: 
            self.entry_Q.configure(border_color=("gray", "gray"))
            return
        if q_str.isdigit() and validate_Q(int(q_str)):
            Q_count = int(q_str)
            self.entry_Q.configure(border_color="#3B8ED0", text_color=("black", "white"))
            self.Q_counterexample = list(range(0, Q_count))
            self.F_counterexample = [0]* len(self.Q_counterexample)
            self.validate_F_interactive()
            self.update_delta_dropdowns()
            self.perform_visualization("counter_input_viz")
        else:
            self.entry_Q.configure(border_color="#C55455", text_color="#C55455")
            self.clear_panel_image("counter_input_viz")

    def validate_F_interactive(self, event=None):
        if not self.Q_counterexample:
            self.entry_F.configure(border_color="#C55455")
            return
        raw_text = self.entry_F.get().strip()
        if not raw_text:
            self.F_counterexample = [0] * len(self.Q_counterexample)
            self.entry_F.configure(border_color=("gray", "gray"))
            self.perform_visualization("counter_input_viz")
            return
        try:
            parsed_indices = [int(s) for s in raw_text.replace(',', ' ').split() if s.isdigit()]
            if all(idx in self.Q_counterexample for idx in parsed_indices):
                self.F_counterexample = convert_F(parsed_indices, self.Q_counterexample)
                self.entry_F.configure(border_color="#3B8ED0", text_color=("black", "white"))
                self.perform_visualization("counter_input_viz")
            else:
                self.entry_F.configure(border_color="#C55455", text_color="#C55455")
                self.F_counterexample = []
        except Exception as e:
            print(f"Error validate F: {e}")
            self.entry_F.configure(border_color="#C55455", text_color="#C55455")

    def validate_sigma_interactive(self, event=None):
        raw_text = self.entry_sigma.get().strip()
        if not raw_text: 
            self.sigma_counterexample = []
            self.sigma_labels_counterexample = {}
            self.entry_sigma.configure(border_color=("gray", "gray"))
            return
        try:
            parsed = [int(s) for s in raw_text.replace(',', ' ').split() if s]
            self.sigma_counterexample, self.sigma_labels_counterexample  = convert_sigma(parsed)
            self.entry_sigma.configure(border_color="#3B8ED0", text_color=("black", "white"))
            self.update_delta_dropdowns()
            self.perform_visualization("counter_input_viz")
        except: self.entry_sigma.configure(border_color="#C55455")

    def add_transition_row(self):
        state_options = [str(x) for x in self.Q_counterexample]
        sigma_options = [str(self.sigma_labels_counterexample.get(x, x)) for x in self.sigma_counterexample]
        STATE_BG, SIGMA_BG, BORDER_DEFAULT, BORDER_WIDTH = ("white", "#343638"), ("gray95", "gray25"), ("#979DA2", "#565B5E"), 2
        row_frame = ctk.CTkFrame(self.delta_scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        center = ctk.CTkFrame(row_frame, fg_color="transparent")
        center.pack(anchor="center")
        def create_seamless_combo(parent, values, width, height, outer_radius, bg_color, gap):
            inner_radius = max(0, outer_radius - gap)
            wrapper = ctk.CTkFrame(parent, width=width, height=height, corner_radius=outer_radius, border_width=BORDER_WIDTH, border_color=BORDER_DEFAULT, fg_color=bg_color)
            combo = ctk.CTkComboBox(wrapper, width=width-(gap*2), height=height-(gap*2), corner_radius=inner_radius, border_width=0, justify="center", values=values, font=ctk.CTkFont(size=14, weight="bold"), dropdown_font=ctk.CTkFont(size=12), fg_color=bg_color, button_color=bg_color, button_hover_color=bg_color)
            combo.pack(expand=True, fill="both", padx=gap, pady=gap)
            combo.set("")
            def hide_arrow(w): 
                try: w._canvas.delete("dropdown_arrow") 
                except: pass
            combo.after(10, lambda: hide_arrow(combo))
            combo.bind("<Enter>", lambda e: hide_arrow(combo))
            combo.bind("<Configure>", lambda e: hide_arrow(combo))
            def open_dropdown(e):
                 if not combo._dropdown_menu.winfo_ismapped(): combo._open_dropdown_menu()
            combo._entry.bind("<Button-1>", open_dropdown)
            combo._canvas.bind("<Button-1>", open_dropdown)
            return wrapper, combo
        src_wrapper, src_combo = create_seamless_combo(center, state_options, 60, 60, 30, STATE_BG, 12)
        src_wrapper.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(center, text="—", font=("Arial", 20, "bold"), text_color="gray50").pack(side="left")
        symbol_wrapper, symbol_combo = create_seamless_combo(center, sigma_options, 50, 40, 10, SIGMA_BG, 6)
        symbol_wrapper.pack(side="left", padx=5)
        ctk.CTkLabel(center, text="➤", font=("Arial", 16), text_color="gray50").pack(side="left", padx=(0, 5))
        dest_wrapper, dest_combo = create_seamless_combo(center, state_options, 60, 60, 30, STATE_BG, 12)
        dest_wrapper.pack(side="left")
        row_data = { "frame": row_frame, "src_wrapper": src_wrapper, "src": src_combo, "symbol_wrapper": symbol_wrapper, "symbol": symbol_combo, "dest_wrapper": dest_wrapper, "dest": dest_combo }
        btn_del = ctk.CTkButton(center, text="×", width=30, height=30, corner_radius=15, fg_color="transparent", text_color="gray60", hover_color="#C55455", font=ctk.CTkFont(size=20, weight="bold"), command=lambda: self.delete_transition_row(row_frame, row_data))
        btn_del.pack(side="left", padx=(15, 0))
        self.delta_rows.append(row_data)
        for combo in [src_combo, symbol_combo, dest_combo]:
            combo.configure(command=lambda e: self.validate_transition_row(row_data))
            combo.bind("<FocusOut>", lambda e: self.validate_transition_row(row_data))
            combo.bind("<Return>", lambda e: self.validate_transition_row(row_data))

    def delete_transition_row(self, frame, row_data):
        if row_data in self.delta_rows: self.delta_rows.remove(row_data)
        frame.destroy()
        list_delta_temp = self.collect_delta_data()
        if self.Q_counterexample and self.sigma_counterexample:
            try:
                self.delta_counterexample = convert_to_2d_array(list_delta_temp, self.Q_counterexample, self.sigma_counterexample)
            except Exception as e: print(f"Error updating delta on delete: {e}")
        self.perform_visualization("counter_input_viz")

    def update_delta_dropdowns(self):
        state_ops = [str(x) for x in self.Q_counterexample]
        sigma_ops = [str(self.sigma_labels_counterexample.get(x, x)) for x in self.sigma_counterexample]
        for row in self.delta_rows:
            row["src"].configure(values=state_ops)
            row["symbol"].configure(values=sigma_ops) 
            row["dest"].configure(values=state_ops)

    def validate_transition_row(self, row_data, event=None):
        valid_states = [str(x) for x in self.Q_counterexample]
        valid_sigma_labels = [str(self.sigma_labels_counterexample.get(x, x)) for x in self.sigma_counterexample]
        row_data["src_wrapper"].configure(border_color="#3B8ED0" if row_data["src"].get() in valid_states else "#C55455")
        row_data["symbol_wrapper"].configure(border_color="#3B8ED0" if row_data["symbol"].get() in valid_sigma_labels else "#C55455")
        row_data["dest_wrapper"].configure(border_color="#3B8ED0" if row_data["dest"].get() in valid_states else "#C55455")
        list_delta_temp = self.collect_delta_data()
        if self.Q_counterexample and self.sigma_counterexample:
            try:
                self.delta_counterexample = convert_to_2d_array(list_delta_temp, self.Q_counterexample, self.sigma_counterexample)
            except Exception as e: print(f"Error updating delta: {e}")
        self.perform_visualization("counter_input_viz")
        
    def collect_delta_data(self):
        list_delta = []
        valid_states = [str(x) for x in self.Q_counterexample]
        label_to_index = {str(v): k for k, v in self.sigma_labels_counterexample.items()}
        for r in self.delta_rows:
            s_str = r["src"].get().strip()
            sym_label = r["symbol"].get().strip()
            d_str = r["dest"].get().strip()
            if s_str in valid_states and d_str in valid_states:
                if sym_label in label_to_index:
                    sym_index = label_to_index[sym_label]
                    entry = [int(s_str), int(d_str), int(sym_index)]
                    if entry not in list_delta: list_delta.append(entry)
        return list_delta

    def save_test_case_to_file(self):
        states, final_states, alphabet, transitions = get_nfa_config(self.Q_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, self.F_counterexample, self.delta_counterexample)
        states_mini, final_states_mini, alphabet_mini, transitions_mini = get_nfa_config(self.Q_mini_counterexample, self.sigma_counterexample, self.sigma_labels_counterexample, self.F_mini_counterexample, self.delta_mini_counterexample)
        saved_filename = write_test_case(states, alphabet, final_states, transitions, states_mini, alphabet_mini, final_states_mini, transitions_mini)
        if saved_filename: tk.messagebox.showinfo("Success", f"Saved to file NFA_test_case/{saved_filename}")
        else: tk.messagebox.showerror("Error", "Failed to save file.")