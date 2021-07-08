import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import wif.io
from wif.viewer import Viewer


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
        self.__create_file_menu(menubar)
        self.master.config(menu=menubar)

    def __create_file_menu(self, menubar):
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New script", underline=0, command=self.__new_script, accelerator="Ctrl+N")
        self.root.bind('<Control-n>', lambda event: self.__new_script())
        file_menu.add_command(label="Open file", underline=0, command=self.__open_file, accelerator="Ctrl+O")
        self.root.bind('<Control-o>', lambda event: self.__open_file())
        file_menu.add_command(label="Render", underline=0, command=self.__render_script, accelerator="F5")
        self.root.bind('<F5>', lambda event: self.__render_script())
        menubar.add_cascade(menu=file_menu, label="File", underline=0)

    def __render_script(self):
        print("Rendering!")

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
        blocks = wif.io.read_blocks_from_file(path, 500000)
        ViewerWindow(self, blocks)

    def __open_file(self):
        filetypes = [
            ('Scripts', '*.chai'),
            ('WIF files', '*.wif'),
            ('All files', '*.*'),
        ]
        # filename = filedialog.askopenfilename(filetypes=filetypes)
        filename = "../quick.wif"
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
    def __init__(self, parent, blocks):
        super().__init__(parent)
        self.__notebook = ttk.Notebook(self)
        self.__notebook.pack(fill=tk.BOTH, expand=True)

        viewer_frame = tk.Frame(self.__notebook)
        viewer_frame.pack(fill=tk.BOTH, expand=True)
        viewer = Viewer(viewer_frame, blocks)
        viewer.pack(fill=tk.BOTH, expand=True)
        tab_title = 'messages'
        self.__notebook.add(viewer_frame, text=tab_title)

        message_frame = tk.Frame(self.__notebook)
        message_frame.pack(fill=tk.BOTH, expand=True)
        editor = tk.Text(message_frame)
        editor.pack(fill=tk.BOTH, expand=True)
        editor.insert('1.0', 'test')
        tab_title = 'messages'
        self.__notebook.add(message_frame, text=tab_title)
