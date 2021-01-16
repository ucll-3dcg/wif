import tkinter as tk
from PIL import ImageTk


class Application(tk.Frame):
    def __init__(self, frames):
        self.root = tk.Tk()
        super().__init__(self.root)
        self.__images = [ ImageTk.PhotoImage(frame) for frame in frames ]
        self.__create_variables()
        self.pack()
        self.__create_widgets()
        self.__tick()

    def __create_variables(self):
        self.__create_index_variable()
        self.__create_animating_variable()
        self.__create_fps_variable()

    def __create_animating_variable(self):
        def callback(var, idx, mode):
            if self.__animating.get():
                self.__tick()
        self.__animating = tk.BooleanVar(value=True)
        self.__animating.trace_add('write', callback)

    def __create_index_variable(self):
        def callback(var, idx, mode):
            self.__update()
        self.__index = tk.IntVar(0)
        self.__index.trace_add('write', callback)

    def __create_fps_variable(self):
        self.__fps = tk.IntVar(value=30)

    def __create_widgets(self):
        frame_slider = tk.Scale(self, variable=self.__index, from_=0, to=len(self.__images) - 1, orient=tk.HORIZONTAL)
        frame_slider.pack()
        fps_slider = tk.Scale(self, variable=self.__fps, from_=1, to=60, orient=tk.HORIZONTAL)
        fps_slider.pack()
        animation_checkbox = tk.Checkbutton(self, text="Animate", variable=self.__animating)
        animation_checkbox.pack()
        self.__label = tk.Label(self)
        self.__label.pack()
        self.__update()

    def __update(self):
        image = self.__images[self.__index.get()]
        self.__label.configure(image=image)
        self.__label.image = image

    def __tick(self):
        self.__index.set((self.__index.get() + 1) % len(self.__images))
        if self.__animating.get():
            self.__schedule_tick()

    def __schedule_tick(self):
        self.root.after(1000 // self.__fps.get(), self.__tick)
