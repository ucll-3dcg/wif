import tkinter as tk
import tkinter.scrolledtext
from tkinter import filedialog
from tkinter import ttk
import wif.io
from wif.gui.imgview import ImageViewer, convert_images
import wif.bgworker
import wif.raytracer
import wif.gui.msgview


class EditorTab:
    def __init__(self, parent_notebook, filename, contents):
        frame = tk.Frame(parent_notebook)
        frame.pack(fill=tk.BOTH, expand=True)
        self.editor = tk.Text(frame)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.insert('1.0', contents)
        self.__filename = filename
        tab_title = filename if filename else 'untitled'
        parent_notebook.add(frame, text=tab_title)

    @property
    def script(self):
        return self.editor.get("1.0", tk.END)

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, value):
        self.__filename = value

    def save(self):
        with open(self.filename, 'w') as file:
            file.write(self.script)


class StudioApplication(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        super().__init__(self.root)
        self.__initialize()
        self.__create_menu()
        self.__create_notebook()
        self.__tabs = []

    def __initialize(self):
        self.root.geometry("1024x768")
        self.master.title('3D Studio')

    def __create_menu(self):
        menubar = tk.Menu(self.master)
        self.__create_file_menu(menubar)
        self.master.config(menu=menubar)

    def __create_file_menu(self, menubar):
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New script", underline=0, command=self.__new_script, accelerator="Ctrl+N")
        self.root.bind('<Control-n>', lambda event: self.__new_script())
        file_menu.add_command(label="Open file", underline=0, command=self.__open_file, accelerator="Ctrl+O")
        self.root.bind('<Control-o>', lambda event: self.__open_file())
        file_menu.add_command(label="Save file", underline=0, command=self.__save_file, accelerator="Ctrl+S")
        self.root.bind('<Control-s>', lambda event: self.__save_file())
        file_menu.add_command(label="Save file as", underline=0, command=self.__save_file_as, accelerator="Alt+S")
        self.root.bind('<Alt-s>', lambda event: self.__save_file_as())
        file_menu.add_command(label="Render", underline=0, command=self.__render_script, accelerator="F5")
        self.root.bind('<F5>', lambda event: self.__render_script())
        menubar.add_cascade(menu=file_menu, label="File", underline=0)

    def __render_script(self):
        script = self.selected_tab.script
        image_data, messages = wif.raytracer.invoke_raytracer(script)
        images = wif.reading.read_images(image_data)
        ViewerWindow(self, images, messages)

    def __create_notebook(self):
        self.__notebook = ttk.Notebook(self.master)
        self.__notebook.pack(fill=tk.BOTH, expand=True)

    def __new_script(self):
        self.__add_editor_tab(None, '')

    def __add_editor_tab(self, filename, contents):
        tab = EditorTab(self.__notebook, filename, contents)
        self.__tabs.append(tab)
        self.__notebook.select(len(self.__notebook.tabs()) - 1)

    def __open_wif_viewer(self, path):
        blocks = wif.reading.read_blocks_from_file(path)
        images = wif.reading.read_images(blocks)
        ViewerWindow(self, images)

    def __open_file(self):
        filetypes = [
            ('Scripts', '*.chai'),
            ('WIF files', '*.wif'),
            ('All files', '*.*'),
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename.endswith('.wif'):
            self.__open_wif_viewer(filename)
        elif filename.endswith('.chai'):
            with open(filename) as file:
                contents = file.read()
            self.__add_editor_tab(file.name, contents)

    def __save_file(self):
        tab = self.selected_tab
        if tab.filename:
            tab.save()
        else:
            self.__save_file_as()

    def __save_file_as(self):
        tab = self.selected_tab
        filetypes = [('Scripts', '*.chai')]
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension='.chai')
        if filename:
            tab.filename = filename
            tab.save()
            index = self.__tabs.index(tab)
            self.__notebook.tab(index, text=filename)

    @property
    def __selected_tab_index(self):
        return self.__notebook.index(self.__notebook.select())

    @property
    def selected_tab(self):
        return self.__tabs[self.__selected_tab_index]


class ViewerWindow(tk.Toplevel):
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
