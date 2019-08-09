import tkinter as tk
from PIL import ImageTk


class Application(tk.Frame):
    def __init__(self, root, frames):
        super().__init__(root)
        self.root = root
        self.__images = [ ImageTk.PhotoImage(frame) for frame in frames ]
        self.__index = 0
        self.pack()
        self.__create_widgets()
        self.__tick()

    def __create_widgets(self):
        self.__label = tk.Label(self)
        self.__label.pack()
        self.__update()

    def __update(self):
        image = self.__images[self.__index]
        self.__label.configure(image=image)
        self.__label.image = image

    def __tick(self):
        self.__index = (self.__index + 1) % len(self.__images)
        self.__update()
        self.root.after(1000 // 30, self.__tick)
