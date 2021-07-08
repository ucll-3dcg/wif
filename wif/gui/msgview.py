import tkinter as tk


class MessageViewer(tk.Frame):
    def __init__(self, parent, message_collector):
        super().__init__(parent)
        self.__view = tk.scrolledtext.ScrolledText(self)
        self.__view.pack(fill=tk.BOTH, expand=True)
        self.__message_collector = message_collector
        self.__fetch_messages()

    def __fetch_messages(self):
        while self.__message_collector.items_available:
            message = self.__message_collector.retrieve()
            self.__view.insert(tk.END, message)
        if not self.__message_collector.finished:
            self.after(500, self.__fetch_messages)
