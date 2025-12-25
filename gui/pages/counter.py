import tkinter as tk
import customtkinter as ctk
from gui.base import BaseView

# --- IMPORT CORE LOGIC ---
from core.gen.validate import validate_Q
from core.helper.bianchini_algo.input_config_bianchini import convert_F, convert_to_2d_array
from core.visualization.visualization_couterexample import visualize_couterexample

# Import Algorithm
from core.src.bianchini_algo.algorithm_3 import MINIMIZENFA 
from core.helper.bianchini_algo.get_ouput import newNFA

class CounterExamplePage(BaseView):
    def __init__(self, master, on_home, **kwargs):
        super().__init__(master, **kwargs)
        self.on_home = on_home

        # --- DATA VARIABLES ---
        self.Q_counterexample = []
        self.F_counterexample = []
        self.sigma_counterexample = []
        self.delta_counterexample = []
        self.delta_rows = []
        
        self.selected_algorithm = "Bianchini" 
        
        # Biến theo dõi trạng thái phóng to
        self.is_maximized = False
        self.maximized_frame = None

        # --- THEME CONFIGURATION ---
        self.theme_corner_radius = 20
        self.btn_corner_radius = 12
        self.section_bg_color = ("gray95", "gray17")
        self.main_bg_color = ("gray90", "gray13")
        
        self.configure(fg_color=self.main_bg_color)

        # --- LAYOUT STRUCTURE ---
        self.sidebar_container = ctk.CTkFrame(self, fg_color="transparent")
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        self.sidebar_container.pack_propagate(False) 

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(0, 20), pady=20)

        self.setup_input_mode()

    def _clear_ui(self):
        """Xóa sạch widget"""
        for w in self.sidebar_container.winfo_children(): w.destroy()
        for w in self.main_area.winfo_children(): w.destroy()
        
        # Reset grid config
        self.main_area.grid_columnconfigure(0, weight=0)
        self.main_area.grid_columnconfigure(1, weight=0)
        self.main_area.grid_rowconfigure(0, weight=0)
        self.main_area.grid_rowconfigure(1, weight=0)
        
        # Reset trạng thái maximize
        self.is_maximized = False
        self.maximized_frame = None

    # ==============================================================================
    # MODE 1: INPUT MODE 
    # ==============================================================================
    def setup_input_mode(self):
        self._clear_ui()
        self.sidebar_container.configure(width=400)
        
        # Sidebar
        ctk.CTkButton(self.sidebar_container, text="🏠 Home Screen", fg_color="transparent", border_width=1, text_color="gray", command=self.on_home).pack(side=tk.TOP, anchor="w", pady=(0, 20))
        input_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ctk.CTkLabel(input_frame, text="INPUT PARAMETERS", font=ctk.CTkFont(size=20, weight="bold"), text_color=("gray40", "gray70")).pack(pady=(30, 20))

        # Inputs
        ctk.CTkLabel(input_frame, text="Set number of States(Q) :", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(10, 5), fill="x")
        self.entry_Q = ctk.CTkEntry(input_frame, height=40)
        self.entry_Q.pack(padx=20, pady=(0, 15), fill="x")
        self.entry_Q.bind("<FocusOut>", self.validate_Q_interactive)
        self.entry_Q.bind("<Return>", self.validate_Q_interactive)
        if self.Q_counterexample: self.entry_Q.insert(0, str(len(self.Q_counterexample)))

        ctk.CTkLabel(input_frame, text="Alphabet (Σ):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=20, pady=(10, 5), fill="x")
        self.entry_sigma = ctk.CTkEntry(input_frame, height=40)
        self.entry_sigma.pack(padx=20, pady=(0, 20), fill="x")
        self.entry_sigma.bind("<FocusOut>", self.validate_sigma_interactive)
        self.entry_sigma.bind("<Return>", self.validate_sigma_interactive)
        if self.sigma_counterexample: self.entry_sigma.insert(0, " ".join(map(str, self.sigma_counterexample)))

        delta_header = ctk.CTkFrame(input_frame, fg_color="transparent")
        delta_header.pack(padx=20, pady=(10, 5), fill="x")
        ctk.CTkLabel(delta_header, text="Transitions (δ) :", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(delta_header, text="+", width=30, height=30, font=ctk.CTkFont(size=18, weight="bold"), fg_color="#2CC985", hover_color="#25A970", command=self.add_transition_row).pack(side="right")

        self.delta_scroll = ctk.CTkScrollableFrame(input_frame, height=200, fg_color="transparent", label_text=None)
        self.delta_scroll.pack(padx=10, pady=(0, 10), fill="x", expand=False)
        self.delta_rows = []
        self.add_transition_row()

        ctk.CTkFrame(input_frame, height=2, fg_color=("gray80", "gray30")).pack(fill="x", padx=20, pady=10)
        self.btn_generate = ctk.CTkButton(input_frame, text="GENERATE EXAMPLE", font=ctk.CTkFont(size=16, weight="bold"), height=50, fg_color="#3B8ED0", hover_color="#36719F", corner_radius=self.btn_corner_radius, command=self.switch_to_result_mode)
        self.btn_generate.pack(padx=20, pady=30, fill="x")

        # Main Viz
        viz_container = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        viz_container.pack(expand=True, fill="both")
        viz_inner = ctk.CTkFrame(viz_container, fg_color="transparent")
        viz_inner.pack(expand=True, fill="both", padx=10, pady=10)
        self.panels['counter_input_viz'] = viz_inner
        self.create_panel_canvas("counter_input_viz", "Counter-Example Preview")
        if self.Q_counterexample: self.perform_visualization("counter_input_viz")

    # ==============================================================================
    # MODE 2: RESULT MODE 
    # ==============================================================================
    def setup_result_mode(self):
        self._clear_ui()
        self.sidebar_container.configure(width=300)

        # --- Sidebar ---
        ctk.CTkButton(self.sidebar_container, text="← Back to Edit", fg_color="transparent", border_width=1, text_color="gray", command=self.setup_input_mode).pack(side=tk.TOP, anchor="w", pady=(0, 10))
        algo_frame = ctk.CTkFrame(self.sidebar_container, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        algo_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ctk.CTkLabel(algo_frame, text="ALGORITHMS", font=ctk.CTkFont(size=18, weight="bold"), text_color=("gray40", "gray70")).pack(pady=(20, 10))
        self.algo_var = tk.StringVar(value=self.selected_algorithm)
        ctk.CTkRadioButton(algo_frame, text="Bianchini Algorithm", variable=self.algo_var, value="Bianchini", font=ctk.CTkFont(size=14)).pack(pady=10, padx=20, anchor="w")
        ctk.CTkRadioButton(algo_frame, text="Tarjan Algorithm", variable=self.algo_var, value="Tarjan", font=ctk.CTkFont(size=14)).pack(pady=10, padx=20, anchor="w")
        ctk.CTkButton(algo_frame, text="RUN OPTIMIZATION", font=ctk.CTkFont(size=14, weight="bold"), height=50, fg_color="#2CC985", hover_color="#25A970", corner_radius=self.btn_corner_radius, command=self.run_optimization_logic).pack(padx=20, pady=30, fill="x")

        # --- Main Area Grid Configuration ---
        # Cấu hình lưới 2 cột, 2 dòng
        self.main_area.grid_columnconfigure(0, weight=1) 
        self.main_area.grid_columnconfigure(1, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Lưu tham chiếu các Frame chứa để thao tác ẩn/hiện
        # 1. Khung Trái (Input) - Chiếm cột 0, trải dài 2 hàng
        self.frame_input = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_input.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=0)
        
        # 2. Khung Phải Trên (Output 1) - Cột 1, Hàng 0
        self.frame_out1 = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_out1.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        # 3. Khung Phải Dưới (Output 2) - Cột 1, Hàng 1
        self.frame_out2 = ctk.CTkFrame(self.main_area, fg_color=self.section_bg_color, corner_radius=self.theme_corner_radius)
        self.frame_out2.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))

        # --- Tạo Inner Frame & Canvas ---
        # Helper để tạo nội dung và gán sự kiện Double Click
        def setup_panel(container_frame, panel_key, title):
            inner = ctk.CTkFrame(container_frame, fg_color="transparent")
            inner.pack(expand=True, fill="both", padx=5, pady=5)
            self.panels[panel_key] = inner
            self.create_panel_canvas(panel_key, title)
            
            # GÁN SỰ KIỆN DOUBLE CLICK VÀO CANVAS
            if panel_key in self.canvases:
                canvas_widget = self.canvases[panel_key][0].get_tk_widget()
                # Bind sự kiện nháy đúp chuột trái
                canvas_widget.bind('<Double-1>', lambda event, f=container_frame: self.toggle_maximize(f))

        setup_panel(self.frame_input, "result_input", "Original NFA (Double-click to Zoom)")
        setup_panel(self.frame_out1, "result_output1", "Algorithm Result (Double-click to Zoom)")
        setup_panel(self.frame_out2, "result_output2", "Secondary Result (Double-click to Zoom)")

        # Vẽ hình Input ban đầu
        self.perform_visualization("result_input")

    # ==============================================================================
    # LOGIC PHÓNG TO / THU NHỎ 
    # ==============================================================================
    def toggle_maximize(self, target_frame):
        """
        Hàm xử lý logic khi nháy đúp vào một khung hình.
        - Nếu đang bình thường -> Phóng to khung đó.
        - Nếu đang phóng to -> Trở về trạng thái 3 khung.
        """
        
        # Danh sách tất cả các frame
        all_frames = [self.frame_input, self.frame_out1, self.frame_out2]

        if self.is_maximized:
            # --- TRƯỜNG HỢP 1: ĐANG PHÓNG TO -> THU NHỎ LẠI ---
            print("Restoring view...")
            
            # Xóa layout hiện tại (đang maximized)
            for f in all_frames:
                f.grid_forget()

            # Thiết lập lại Grid chuẩn (3 khung)
            self.frame_input.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=0)
            self.frame_out1.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
            self.frame_out2.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
            
            self.is_maximized = False
            self.maximized_frame = None

        else:
            # --- TRƯỜNG HỢP 2: ĐANG BÌNH THƯỜNG -> PHÓNG TO TARGET ---
            print("Maximizing view...")
            
            # Ẩn tất cả các frame
            for f in all_frames:
                f.grid_remove() # grid_remove giúp ẩn nhưng nhớ các thuộc tính cũ (tuy nhiên ta set lại tay cho chắc)
            
            # Chỉ hiển thị frame được chọn và cho nó chiếm toàn bộ (row 0->2, col 0->2)
            target_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew", padx=0, pady=0)
            
            self.is_maximized = True
            self.maximized_frame = target_frame

        # Cập nhật lại giao diện (đôi khi cần thiết để Canvas render lại đúng kích thước)
        self.main_area.update_idletasks()

    # ==============================================================================
    # CÁC HÀM LOGIC CŨ
    # ==============================================================================
    def switch_to_result_mode(self):
        list_delta_temp = self.collect_delta_data()
        if not self.Q_counterexample: return
        try:
            self.delta_counterexample = convert_to_2d_array(list_delta_temp, self.Q_counterexample, self.sigma_counterexample)
            self.setup_result_mode()
        except Exception as e: print(e)

    def run_optimization_logic(self):
        algo = self.algo_var.get()
        self.selected_algorithm = algo
        self.clear_panel_image("result_output1", f"Processing {algo}...")
        self.clear_panel_image("result_output2", "Waiting...")
        
        if algo == "Bianchini":
            try:
                minimized = MINIMIZENFA(1, Q=self.Q_counterexample, sigma=self.sigma_counterexample, F=self.F_counterexample, delta=self.delta_counterexample)
                new_Q, new_F, new_delta, state_labels = newNFA(minimized, self.Q_counterexample, self.F_counterexample, self.sigma_counterexample, self.delta_counterexample)
                
                img1 = visualize_couterexample(new_Q, new_F, new_delta, self.sigma_counterexample, state_labels, return_fig=True)
                if img1: self.update_panel_image(img1, "result_output1", "Minimized NFA (Bianchini)")
                
                self.clear_panel_image("result_output2", "Analysis Complete")
            except Exception as e:
                self.clear_panel_image("result_output1", f"Error: {str(e)}")
        elif algo == "Tarjan":
             self.clear_panel_image("result_output1", "Tarjan Not Implemented")

    def validate_Q_interactive(self, event=None):
        q_str = self.entry_Q.get().strip()
        if not q_str: self.entry_Q.configure(border_color=("gray", "gray")); return
        if q_str.isdigit() and validate_Q(int(q_str)):
            Q_count = int(q_str)
            self.entry_Q.configure(border_color="#3B8ED0", text_color=("black", "white"))
            self.Q_counterexample = list(range(0, Q_count))
            self.F_counterexample = convert_F([Q_count // 2], self.Q_counterexample)
            self.update_delta_dropdowns()
            self.perform_visualization("counter_input_viz")
        else:
            self.entry_Q.configure(border_color="#C55455", text_color="#C55455")
            self.clear_panel_image("counter_input_viz")

    def validate_sigma_interactive(self, event=None):
        raw_text = self.entry_sigma.get().strip()
        if not raw_text: self.sigma_counterexample = []; self.entry_sigma.configure(border_color=("gray", "gray")); return
        try:
            parsed = [int(s) for s in raw_text.replace(',', ' ').split() if s]
            self.sigma_counterexample = parsed
            self.entry_sigma.configure(border_color="#3B8ED0", text_color=("black", "white"))
            self.update_delta_dropdowns()
            self.perform_visualization("counter_input_viz")
        except: self.entry_sigma.configure(border_color="#C55455")

    def add_transition_row(self):
        state_options = [str(x) for x in self.Q_counterexample]
        sigma_options = [str(x) for x in self.sigma_counterexample]
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

        row_data = {
            "frame": row_frame, "src_wrapper": src_wrapper, "src": src_combo,
            "symbol_wrapper": symbol_wrapper, "symbol": symbol_combo,
            "dest_wrapper": dest_wrapper, "dest": dest_combo
        }
        
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
        self.perform_visualization("counter_input_viz")

    def update_delta_dropdowns(self):
        state_ops = [str(x) for x in self.Q_counterexample]
        sigma_ops = [str(x) for x in self.sigma_counterexample]
        for row in self.delta_rows:
            row["src"].configure(values=state_ops); row["symbol"].configure(values=sigma_ops); row["dest"].configure(values=state_ops)

    def validate_transition_row(self, row_data, event=None):
        valid_states = [str(x) for x in self.Q_counterexample]
        valid_sigma = [str(x) for x in self.sigma_counterexample]
        row_data["src_wrapper"].configure(border_color="#3B8ED0" if row_data["src"].get() in valid_states else "#C55455")
        row_data["symbol_wrapper"].configure(border_color="#3B8ED0" if row_data["symbol"].get() in valid_sigma else "#C55455")
        row_data["dest_wrapper"].configure(border_color="#3B8ED0" if row_data["dest"].get() in valid_states else "#C55455")
        self.perform_visualization("counter_input_viz")

    def collect_delta_data(self):
        list_delta = []
        valid_states = [str(x) for x in self.Q_counterexample]
        valid_sigma = [str(x) for x in self.sigma_counterexample]
        for r in self.delta_rows:
            s, sym, d = r["src"].get().strip(), r["symbol"].get().strip(), r["dest"].get().strip()
            if s in valid_states and sym in valid_sigma and d in valid_states:
                entry = [int(s), int(d), int(sym)]
                if entry not in list_delta: list_delta.append(entry)
        return list_delta

    def perform_visualization(self, panel_key):
        try:
            if panel_key == "counter_input_viz":
                list_delta_temp = self.collect_delta_data()
                delta_to_draw = convert_to_2d_array(list_delta_temp, self.Q_counterexample, self.sigma_counterexample)
            else:
                delta_to_draw = self.delta_counterexample
            pil_image = visualize_couterexample(self.Q_counterexample, self.F_counterexample, delta_to_draw, self.sigma_counterexample, return_fig=True)
            if pil_image: self.update_panel_image(pil_image, panel_key, "Visual Preview")
        except Exception as e: print(f"Viz Error ({panel_key}): {e}")