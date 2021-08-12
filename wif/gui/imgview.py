from PIL import ImageTk
import tkinter as tk
import wif.encoding
import wif.concurrency
from tkinter import filedialog


_save_movie_caption = 'Save movie'
_save_frame_caption = 'Save frame'


class ImageViewer(tk.Frame):
    def __init__(self, parent, images):
        super().__init__(parent)
        self.__menu = self.__create_menu()
        self.__original_images = []
        self.__converted_images = []
        self.__create_variables()
        self.__create_widgets()
        self.__create_keybindings()
        self.__done_receiving_images = False
        self.__tick()
        self.__read_images_in_background(images)

    def __create_keybindings(self):
        self.bind_all('<space>', lambda event: self.__toggle_animation())

    def __toggle_animation(self):
        self.__animating.set(not self.__animating.get())

    def __create_menu(self):
        menu = tk.Menu(self.master, tearoff=False)
        self.__save_menu = tk.Menu(menu, tearoff=False)
        self.__save_menu.add_command(label=_save_movie_caption,
                                     state='disabled',
                                     underline=0,
                                     command=self.__save_movie)
        self.__save_menu.add_command(label=_save_frame_caption,
                                     state='disabled',
                                     underline=6,
                                     command=self.__save_frame)
        menu.add_cascade(menu=self.__save_menu,
                         label='Save',
                         underline=0)
        return menu

    def __save_frame(self):
        filetypes = [
            ('PNG Files', '*.png'),
            ('JPEG Files', '*.jpg'),
        ]
        filename = filedialog.asksaveasfilename(filetypes=filetypes,
                                                defaultextension='.png')

        if filename:
            image = self.__original_images[self.__image_index.get()]
            image.save(filename)

    def __save_movie(self):
        filetypes = [('MP4 Files', '*.mp4')]
        filename = filedialog.asksaveasfilename(filetypes=filetypes,
                                                defaultextension='.mp4')
        if filename:
            def task():
                wif.encoding.create_mp4(self.__original_images, filename)
            wif.concurrency.run_in_background(task)

    def __read_images_in_background(self, images):
        converted_images = self.__convert_images(images)
        channel = wif.concurrency.generate_in_background(converted_images)

        def fetch_images_from_channel():
            while not channel.empty:
                original_image, converted_image = channel.receive()
                self.__original_images.append(original_image)
                self.__converted_images.append(converted_image)
            self.__framecount.set(len(self.__converted_images))
            self.__status.set(f'Received frame #{self.__framecount.get()}')
            if not channel.finished:
                self.after(100, fetch_images_from_channel)
            else:
                self.__on_done_receiving_images()

        fetch_images_from_channel()

    def __on_done_receiving_images(self):
        '''
        Called when all images have been received.
        '''
        self.__done_receiving_images = True
        self.__save_menu.entryconfig(_save_movie_caption, state='normal')
        self.__save_menu.entryconfig(_save_frame_caption, state='normal')
        self.__status.set(f'Finished! Received {self.__framecount.get()} frames')

    def __create_variables(self):
        self.__create_frame_index_variable()
        self.__create_framecount_variable()
        self.__create_animating_variable()
        self.__create_fps_variable()
        self.__create_status_variable()

    def __create_status_variable(self):
        self.__status = tk.StringVar(value='')

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
        self.__image_index = tk.IntVar(value=0)
        self.__image_index.trace_add('write', callback)

    def __create_fps_variable(self):
        self.__fps = tk.IntVar(value=30)

    def __create_widgets(self):
        self.__create_top_frame()
        self.__create_status_bar()
        self.__create_center_frame()
        self.__update()

    def __create_top_frame(self):
        self.__top_frame = tk.Frame(self)
        self.__top_frame.pack(side='top', fill='x')

        self.__frame_slider = tk.Scale(self.__top_frame,
                                       variable=self.__image_index,
                                       from_=0,
                                       to=0,
                                       orient=tk.HORIZONTAL)
        self.__frame_slider.pack(fill='x')

        fps_slider = tk.Scale(self.__top_frame,
                              variable=self.__fps,
                              from_=1,
                              to=60,
                              orient=tk.HORIZONTAL)
        fps_slider.pack(fill='x')

        animation_checkbox = tk.Checkbutton(self.__top_frame,
                                            text="Animate",
                                            variable=self.__animating)
        animation_checkbox.pack()

    def __create_center_frame(self):
        self.__center_frame = tk.Frame(self)
        self.__center_frame.pack(expand=True)

        self.__label = tk.Label(self.__center_frame, anchor=tk.CENTER)
        self.__label.bind('<Button-3>', self.__show_context_menu)
        self.__label.pack()

    def __create_status_bar(self):
        self.__status_bar = tk.Frame(self)
        self.__status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.__label = tk.Label(self.__status_bar,
                                anchor=tk.W,
                                textvariable=self.__status)
        self.__label.pack()

    def __show_context_menu(self, event):
        try:
            self.__menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.__menu.grab_release()

    def __update(self):
        if self.__converted_images:
            index = self.__image_index.get()
            image = self.__converted_images[index]
            self.__label.configure(image=image)
            self.__label.image = image

    def __tick(self):
        if self.__converted_images:
            new_index = (self.__image_index.get() + 1) % len(self.__converted_images)
            self.__image_index.set(new_index)
        if self.__animating.get():
            self.__schedule_tick()

    def __schedule_tick(self):
        self.after(1000 // self.__fps.get(), self.__tick)

    def __convert_image(self, image):
        return ImageTk.PhotoImage(image)

    def __convert_images(self, images):
        for image in images:
            yield (image, self.__convert_image(image))
