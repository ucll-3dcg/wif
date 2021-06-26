import tkinter as tk
from PIL import ImageTk
from queue import Queue
from wif.io import read_images
import wif.bgworker as bgworker

class ViewerApplication(tk.Frame):
    def __init__(self, parent, blocks):
        super().__init__(parent)
        self.__images = []
        self.__create_variables()
        self.pack()
        self.__create_widgets()
        self.__tick()
        self.__read_images_in_background(blocks)

    def __read_images_in_background(self, blocks):
        queue = Queue()

        async def read():
            async for image in read_images(blocks):
                queue.put(ImageTk.PhotoImage(image))
            queue.put(None)

        bgworker.perform_async(read())

        def fetch_images_from_queue():
            nonlocal queue
            finished = False

            if not queue.empty():
                while not queue.empty():
                    image = queue.get()
                    if not image:
                        finished = True
                    else:
                        self.__images.append(image)
                self.__frame_slider.configure(to=len(self.__images) - 1)

            if not finished:
                self.after(100, fetch_images_from_queue)

        fetch_images_from_queue()

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
        self.__index = tk.IntVar(value=0)
        self.__index.trace_add('write', callback)

    def __create_fps_variable(self):
        self.__fps = tk.IntVar(value=30)

    def __create_widgets(self):
        self.__frame_slider = tk.Scale(self, variable=self.__index, from_=0, to=0, orient=tk.HORIZONTAL)
        self.__frame_slider.pack()
        fps_slider = tk.Scale(self, variable=self.__fps, from_=1, to=60, orient=tk.HORIZONTAL)
        fps_slider.pack()
        animation_checkbox = tk.Checkbutton(self, text="Animate", variable=self.__animating)
        animation_checkbox.pack()
        self.__label = tk.Label(self)
        self.__label.pack()
        self.__update()

    def __update(self):
        if self.__images:
            image = self.__images[self.__index.get()]
            self.__label.configure(image=image)
            self.__label.image = image

    def __tick(self):
        if self.__images:
            self.__index.set((self.__index.get() + 1) % len(self.__images))
        if self.__animating.get():
            self.__schedule_tick()

    def __schedule_tick(self):
        self.after(1000 // self.__fps.get(), self.__tick)
