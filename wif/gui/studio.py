import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import wif.raytracer
import wif.gui.msgview
from wif.gui.viewer import ViewerWindow


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


class MenuItem:
    def __init__(self, parent, label):
        self.__parent = parent
        self.__label = label

    def enable(self):
        self.__set_state('normal')

    def disable(self):
        self.__set_state('disabled')

    def __set_state(self, state):
        self.__parent.entryconfigure(self.__label, state=state)


class StudioApplication(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        super().__init__(self.root)
        self.__initialize()
        self.__create_menu()
        self.__create_notebook()
        self.__tabs = []
        self.__update()

    def __initialize(self):
        self.root.geometry("1024x768")
        self.master.title('3D Studio')

    def __create_menu(self):
        menubar = tk.Menu(self.master)
        self.__create_file_menu(menubar)
        self.master.config(menu=menubar)

    def __create_file_menu(self, menubar):
        file_menu = tk.Menu(menubar, tearoff=False)

        def add_menu_item(label, command, accelerator):
            index = label.index('_')
            real_label = label[:index] + label[index+1:]
            file_menu.add_command(label=real_label,
                                  underline=index,
                                  command=command,
                                  accelerator=accelerator)
            return MenuItem(file_menu, real_label)

        self.__new_script_menu = add_menu_item('_New script', self.__new_script, "CTRL+N")
        self.__open_file_menu = add_menu_item('_Open file', self.__open_file, "CTRL+O")
        self.__save_menu = add_menu_item('_Save file', self.__save_file, "CTRL+S")
        self.__save_as_menu = add_menu_item('Save file _as', self.__save_file_as, "ALT+S")
        self.__render_menu = add_menu_item('_Render', self.__render_script, "F5")

        self.root.bind('<Control-n>', lambda event: self.__new_script())
        self.root.bind('<Control-o>', lambda event: self.__open_file())
        self.root.bind('<Control-s>', lambda event: self.__save_file())
        self.root.bind('<Alt-s>', lambda event: self.__save_file_as())
        self.root.bind('<F5>', lambda event: self.__render_script())

        menubar.add_cascade(menu=file_menu, label="File", underline=0)

    def __render_script(self):
        script = self.selected_tab.script
        images, messages = wif.raytracer.raytrace(script)
        self.__view(images, messages)

    def __view(self, images, messages = None):
        ViewerWindow(tk.Toplevel(), images, messages)

    def __create_notebook(self):
        self.__notebook = ttk.Notebook(self.master)
        self.__notebook.pack(fill=tk.BOTH, expand=True)

    def __new_script(self):
        self.__add_editor_tab(None, '')
        self.__update()

    def __add_editor_tab(self, filename, contents):
        tab = EditorTab(self.__notebook, filename, contents)
        self.__tabs.append(tab)
        self.__notebook.select(len(self.__notebook.tabs()) - 1)

    def __open_wif_viewer(self, path):
        blocks = wif.reading.read_blocks_from_file(path)
        images = wif.reading.read_images(blocks)
        self.__view(images)

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
        self.__update()

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

    def __update(self):
        if self.__tabs:
            self.__save_menu.enable()
            self.__save_as_menu.enable()
            self.__render_menu.enable()
        else:
            self.__save_menu.disable()
            self.__save_as_menu.disable()
            self.__render_menu.disable()
