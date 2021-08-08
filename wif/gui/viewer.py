import tkinter as tk
from tkinter import ttk
from wif.gui.imgview import ImageViewer
import wif.raytracer
import wif.gui.msgview


class ViewerWindow(tk.Frame):
    def __init__(self, parent, images, messages=None):
        super().__init__(parent)
        self.__notebook = ttk.Notebook(self)
        self.__notebook.pack(fill=tk.BOTH, expand=True)

        viewer_frame = tk.Frame(self.__notebook)
        viewer_frame.pack(fill=tk.BOTH, expand=True)
        viewer = ImageViewer(viewer_frame, images)
        viewer.pack(fill=tk.BOTH, expand=True)
        tab_title = 'Images'
        self.__notebook.add(viewer_frame, text=tab_title)

        if messages is not None:
            message_viewer = wif.gui.msgview.MessageViewer(self.__notebook, messages)
            tab_title = 'Messages'
            self.__notebook.add(message_viewer, text=tab_title)
        self.pack(expand=True, fill=tk.BOTH)
