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
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class BaseView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvases = {}  
        self.panels = {}   

    def create_panel_canvas(self, panel_key: str, initial_title: str):
        """Tạo khu vực vẽ Matplotlib bên trong một widget container"""
        if panel_key not in self.panels:
            return
        
        panel = self.panels[panel_key]
        
        for widget in panel.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(initial_title, fontsize=12, pad=20)
        ax.axis('off')
        
        canvas = FigureCanvasTkAgg(fig, master=panel)
        canvas.draw()
        
        toolbar = NavigationToolbar2Tk(canvas, panel)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.canvases[panel_key] = (canvas, fig, ax)

    def update_panel_image(self, pil_image: Image.Image, panel_key: str, title: str = ""):
        if panel_key not in self.canvases:
            return
        canvas, fig, ax = self.canvases[panel_key]
        ax.cla()
        ax.set_position([0, 0, 1, 1]) 
        ax.imshow(pil_image, aspect='equal') 
        ax.axis('off') 
        canvas.draw()

    def clear_panel_image(self, panel_key: str, title: str = "No data"):
        if panel_key not in self.canvases:
            return
        canvas, fig, ax = self.canvases[panel_key]
        ax.cla()
        if title:
            ax.set_title(title)
        ax.axis('off')
        canvas.draw()