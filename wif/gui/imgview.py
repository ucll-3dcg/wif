from PIL import ImageTk
import tkinter as tk
import wif.io
import wif.bgworker
import wif.concurrency


class ImageViewer(tk.Frame):
    def __init__(self, parent, images):
        super().__init__(parent)
        self.__menu = self.__create_menu()
        self.__images = []
        self.__create_variables()
        self.__create_widgets()
        self.__tick()
        self.__read_images_in_background(images)

    def __create_menu(self):
        menu = tk.Menu(self.master, tearoff=False)
        save_menu = tk.Menu(menu, tearoff=False)
        save_menu.add_command(label='Save as mp4',
                              underline=0,
                              command=self.__save_as_mp4)
        menu.add_cascade(menu=save_menu,
                         label='Save',
                         underline=0)
        return menu

    def __save_as_mp4(self):
        async def images():
            for image in self.__images:
                print(dir(image))
                yield image
        task = wif.io.create_mp4(images(), 'test.mp4')
        wif.bgworker.perform_async(task)

    def __read_images_in_background(self, images):
        converted_images = convert_images(images)
        channel = wif.concurrency.generate_in_background(converted_images)

        def fetch_images_from_channel():
            while not channel.empty:
                image = channel.receive()
                self.__images.append(image)
            self.__framecount.set(len(self.__images))
            if not channel.finished:
                self.after(100, fetch_images_from_channel)

        fetch_images_from_channel()

    def __create_variables(self):
        self.__create_frame_index_variable()
        self.__create_framecount_variable()
        self.__create_animating_variable()
        self.__create_fps_variable()

    def __create_framecount_variable(self):
        def callback(var, idx, mode):
            self.__frame_slider.configure(to=self.__framecount.get() - 1)
        self.__framecount = tk.IntVar(value=0)
        self.__framecount.trace_add('write', callback)

    def __create_animating_variable(self):
        def callback(var, idx, mode):
            if self.__animating.get():
                self.__tick()
        self.__animating = tk.BooleanVar(value=True)
        self.__animating.trace_add('write', callback)

    def __create_frame_index_variable(self):
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
        self.__label.bind('<Button-3>', self.__show_context_menu)
        self.__update()

    def __show_context_menu(self, event):
        try:
            self.__menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.__menu.grab_release()

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


def convert_image(image):
    return ImageTk.PhotoImage(image)


def convert_images(images):
    for image in images:
        yield convert_image(image)
