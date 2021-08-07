import tkinter as tk
import wif.concurrency
from tkinter.scrolledtext import ScrolledText


class MessageViewer(tk.Frame):
    def __init__(self, parent, messages):
        super().__init__(parent)
        self.__view = ScrolledText(self)
        self.__view.pack(fill=tk.BOTH, expand=True)
        self.__message_channel = wif.concurrency.generate_in_background(messages)
        self.__fetch_messages()

    def __fetch_messages(self):
        while not self.__message_channel.empty:
            message = self.__message_channel.receive()
            self.__view.insert(tk.END, message)
        if not self.__message_channel.finished:
            self.after(500, self.__fetch_messages)
