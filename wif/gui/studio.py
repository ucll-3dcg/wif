import tkinter as tk
import tkinter.scrolledtext
from tkinter import filedialog
from tkinter import ttk
import wif.io
from wif.gui.viewer import Viewer, convert_images
import wif.bgworker
import wif.raytracer


class EditorTab:
    def __init__(self, parent_notebook, filename, contents):
        frame = tk.Frame(parent_notebook)
        frame.pack(fill=tk.BOTH, expand=True)
        self.editor = tk.Text(frame)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.insert('1.0', contents)
        tab_title = filename if filename else 'untitled'
        parent_notebook.add(frame, text=tab_title)

    @property
    def script(self):
        return self.editor.get("1.0", tk.END)


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
        file_menu.add_command(label="Render", underline=0, command=self.__render_script, accelerator="F5")
        self.root.bind('<F5>', lambda event: self.__render_script())
        menubar.add_cascade(menu=file_menu, label="File", underline=0)

    def __render_script(self):
        script = self.selected_tab.script
        images, messages = wif.raytracer.render_script_to_collectors(script)
        ViewerWindow(self, images, messages)

    def __create_notebook(self):
        self.__notebook = ttk.Notebook(self.master)
        self.__notebook.pack(fill=tk.BOTH, expand=True)

    def __new_script(self):
        self.__add_editor_tab(None, '')

    def __add_editor_tab(self, filename, contents):
        tab = EditorTab(self.__notebook, filename, contents)
        self.__tabs.append(tab)
        self.__notebook.select(len(self.__tabs) - 1)

    def __open_wif_viewer(self, path):
        blocks = wif.io.read_blocks_from_file(path)
        images = convert_images(wif.io.read_images(blocks))
        collector = wif.bgworker.Collector(images)
        ViewerWindow(self, collector, wif.bgworker.Collector.create_empty())

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

    @property
    def selected_tab(self):
        return self.__tabs[self.__selected_tab_index]


class ViewerWindow(tk.Toplevel):
    def __init__(self, parent, image_collector, message_collector):
        super().__init__(parent)
        self.__notebook = ttk.Notebook(self)
        self.__notebook.pack(fill=tk.BOTH, expand=True)

        viewer_frame = tk.Frame(self.__notebook)
        viewer_frame.pack(fill=tk.BOTH, expand=True)
        viewer = Viewer(viewer_frame, image_collector)
        viewer.pack(fill=tk.BOTH, expand=True)
        tab_title = 'Images'
        self.__notebook.add(viewer_frame, text=tab_title)

        message_frame = tk.Frame(self.__notebook)
        message_frame.pack(fill=tk.BOTH, expand=True)
        self.__message_viewer = tk.scrolledtext.ScrolledText(message_frame)
        self.__message_viewer.pack(fill=tk.BOTH, expand=True)
        self.__message_viewer.insert('1.0', 'test')
        tab_title = 'Messages'
        self.__notebook.add(message_frame, text=tab_title)

        self.__message_collector = message_collector
        self.__fetch_messages()

    def __fetch_messages(self):
        while self.__message_collector.items_available:
            message = self.__message_collector.retrieve()
            self.__message_viewer.insert(tk.END, message)
        if not self.__message_collector.finished:
            self.after(100, self.__fetch_messages)
