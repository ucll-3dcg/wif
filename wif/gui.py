from PIL import ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import wif.io
from wif.viewer import ViewerApplication


class StudioApplication(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        super().__init__(self.root)
        self.__initialize()
        self.__create_menu()
        self.__create_notebook()

    def __initialize(self):
        self.root.geometry("1024x768")
        self.master.title('3D Studio')

    def __create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New script", underline=0, command=self.__new_script, accelerator="Ctrl+N")
        self.root.bind('<Control-n>', lambda event: self.__new_script())
        file_menu.add_command(label="Open file", underline=0, command=self.__open_file, accelerator="Ctrl+O")
        self.root.bind('<Control-o>', lambda event: self.__open_file())
        menubar.add_cascade(menu=file_menu, label="File", underline=0)
        self.master.config(menu=menubar)

    def __create_notebook(self):
        self.__notebook = ttk.Notebook(self.master)
        self.__notebook.pack(fill=tk.BOTH, expand=True)

    def __new_script(self):
        self.__add_editor_tab(None, '')

    def __add_editor_tab(self, filename, contents):
        frame = tk.Frame(self.__notebook)
        frame.pack(fill=tk.BOTH, expand=True)
        editor = tk.Text(frame)
        editor.pack(fill=tk.BOTH, expand=True)
        editor.insert('1.0', contents)
        tab_title = filename if filename else 'untitled'
        self.__notebook.add(frame, text=tab_title)

    def __open_wif_viewer(self, path):
        blocks = wif.io.read_blocks(path, 500000)
        queue = wif.io.read_images_in_background(blocks)
        ViewerWindow(self, queue)

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

    @property
    def __selected_tab_index(self):
        return self.__notebook.index(self.__notebook.select())


class ViewerWindow(tk.Toplevel):
    def __init__(self, parent, queue):
        super().__init__(parent)
        self.viewer = ViewerApplication(self, queue)
        self.viewer.pack(expand=True, fill=tk.BOTH)
