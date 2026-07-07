import tkinter as tk
from tkinter import ttk

from keys.prstenovi_kljuceva import (
    load_prsten_privatnih_kljuceva,
    load_prsten_javnih_kljuceva,
)
from gui.key_manager_view import KeyManagerView
from gui.send_dialog import SendDialog
from gui.receive_dialog import ReceiveDialog


def load_rings():
    """Reads both key rings from disk. Returns ([], []) if a file is missing."""
    try:
        priv = load_prsten_privatnih_kljuceva()
    except Exception:
        priv = []
    try:
        pub = load_prsten_javnih_kljuceva()
    except Exception:
        pub = []
    return priv, pub


class PGPApp(tk.Tk):
    """
    Main application window. Holds the three tabs:
      - Key Manager  (generate / delete / import / export keys)
      - Send         (compose and send a PGP message)
      - Receive      (partner's receiver - slot reserved below)

    Key rings live on disk (PRkeys.json / PUkeys.json). Each tab reads them
    as needed. When the user switches to the Send tab, its dropdowns are
    reloaded from disk so keys generated in the Key Manager tab appear
    without restarting the app.
    """

    def __init__(self):
        super().__init__()
        self.title("PGP - Zastita podataka")
        self.geometry("760x820")
        self.minsize(700, 600)

        priv, pub = load_rings()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Key Manager
        key_tab = tk.Frame(self.notebook)
        self.notebook.add(key_tab, text="  Key Manager  ")
        self.key_view = KeyManagerView(key_tab, priv, pub)

        # Tab 2: Send
        send_tab = tk.Frame(self.notebook)
        self.notebook.add(send_tab, text="  Send Message  ")
        self.send_view = SendDialog(send_tab, priv, pub)

        # Tab 3: Receive
        recv_tab = tk.Frame(self.notebook)
        self.notebook.add(recv_tab, text="  Receive Message  ")
        self.receive_view = ReceiveDialog(recv_tab)

        # Cross-tab sync: refresh whichever tab just became visible.
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        """Reloads keys for the tab that just became visible."""
        current = self.notebook.tab(self.notebook.select(), "text").strip()
        if current == "Send Message":
            self.send_view.reload_keys()
        elif current == "Key Manager":
            self.key_view._reload_rings()


if __name__ == "__main__":
    app = PGPApp()
    app.mainloop()