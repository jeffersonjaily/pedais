# ui/drag_manager.py

import tkinter as tk
from tkinter import ttk
import layout_config as layout

class DragManager:
    """
    Classe dedicada a gerenciar a funcionalidade de arrastar e soltar
    para os pedais na interface.
    """
    def __init__(self, app_instance):
        self.app = app_instance
        self.drag_widget = None
        self.placeholder = None

    def add_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_press)
        widget.bind("<B1-Motion>", self.on_motion)
        widget.bind("<ButtonRelease-1>", self.on_release)
        widget.configure(cursor="hand2")

    def on_press(self, event):
        if isinstance(event.widget, (ttk.LabelFrame, ttk.Frame)):
            self.drag_widget = event.widget
            try:
                grid_info = self.drag_widget.grid_info()
                if not grid_info: return
                self.placeholder = ttk.Frame(self.drag_widget.master, width=self.drag_widget.winfo_width(), height=self.drag_widget.winfo_height())
                self.placeholder.grid(row=grid_info['row'], column=grid_info['column'], padx=layout.PEDAL_PADDING_X, pady=layout.PEDAL_PADDING_Y)
                self.drag_widget.lift()
            except Exception:
                self.drag_widget = None

    def on_motion(self, event):
        if not self.drag_widget: return
        self.drag_widget.place(x=event.x_root - self.app.winfo_rootx() - (self.drag_widget.winfo_width()//2),
                               y=event.y_root - self.app.winfo_rooty() - (self.drag_widget.winfo_height()//2))

    def on_release(self, event):
        if not self.drag_widget: return

        if self.placeholder: self.placeholder.destroy()
        self.drag_widget.place_forget()
        
        target_widget = self.drag_widget.winfo_containing(event.x_root, event.y_root)
        if target_widget and hasattr(target_widget, 'winfo_toplevel') and target_widget.winfo_toplevel() == self.app:
            # Lógica para encontrar o pedal alvo subindo na hierarquia de widgets
            active_chain_type = 'instrument' if self.app.notebook.tab(self.app.notebook.select(), "text").startswith('🎸') else 'voice'
            
            while not hasattr(target_widget, 'effect_name') and target_widget.master:
                target_widget = target_widget.master
                if target_widget == self.app: break

            if hasattr(target_widget, 'effect_name') and target_widget != self.drag_widget:
                drag_index = self.app.pedal_frames[active_chain_type].index(self.drag_widget)
                target_index = self.app.pedal_frames[active_chain_type].index(target_widget)
                
                self.app.pedal_frames[active_chain_type].insert(target_index, self.app.pedal_frames[active_chain_type].pop(drag_index))
                self.app.pedal_widgets[active_chain_type].insert(target_index, self.app.pedal_widgets[active_chain_type].pop(drag_index))
        
        self.app.on_pedal_reorder()
        self.drag_widget = None
