import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from receiver.receiver_entry import receive_message_from_file


class ReceiveDialog(tk.Frame):
    """
    Receive Message tab - lets the user open a .pgp file, supply the password
    for their private key (needed when the message is encrypted), and see:
      - the recovered message
      - whether the signature is valid, and who signed it

    All work is delegated to the receiver backend
    (receiver.receiver_entry.receive_message_from_file).
    """

    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")
        self.pack(fill=tk.BOTH, expand=True)

        self.input_path = tk.StringVar(value="No file selected")

        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        pad = {"padx": 18, "pady": 8}

        # -- Section: input file --
        self._section_label("Message File")

        file_frame = tk.Frame(self, bg="#f0f0f0")
        file_frame.pack(fill=tk.X, **pad)

        tk.Label(file_frame, text="Open .pgp file:",
                 bg="#f0f0f0", anchor="w").pack(anchor="w")

        path_row = tk.Frame(file_frame, bg="#f0f0f0")
        path_row.pack(fill=tk.X, pady=(4, 0))

        self.path_label = tk.Label(
            path_row, textvariable=self.input_path,
            bg="#ffffff", relief=tk.SOLID, bd=1,
            anchor="w", padx=6, width=50, font=("Courier", 9)
        )
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(path_row, text="Browse...",
                   command=self._browse_input).pack(side=tk.LEFT, padx=(8, 0))

        # -- Section: password --
        self._section_label("Private Key Password")

        pw_frame = tk.Frame(self, bg="#f0f0f0")
        pw_frame.pack(fill=tk.X, **pad)

        tk.Label(pw_frame,
                 text="Needed only if the message is encrypted:",
                 bg="#f0f0f0", anchor="w").pack(anchor="w")

        self.password_entry = tk.Entry(pw_frame, show="\u2022", width=30,
                                       relief=tk.SOLID, bd=1)
        self.password_entry.pack(anchor="w", pady=(4, 0))

        # -- Receive button --
        recv_btn = tk.Button(
            self, text="  \u25bc  Receive Message",
            command=self._on_receive,
            bg="#27ae60", fg="white",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT, padx=20, pady=10,
            cursor="hand2",
            activebackground="#1f8f4f", activeforeground="white"
        )
        recv_btn.pack(pady=(16, 8))

        # -- Section: result --
        self._section_label("Result")

        result_frame = tk.Frame(self, bg="#f0f0f0")
        result_frame.pack(fill=tk.BOTH, expand=True, **pad)

        # signature status line
        self.status_label = tk.Label(
            result_frame, text="", bg="#f0f0f0", anchor="w",
            font=("Helvetica", 10, "bold"), justify="left"
        )
        self.status_label.pack(fill=tk.X, anchor="w")

        # recovered message box (read-only)
        tk.Label(result_frame, text="Recovered message:",
                 bg="#f0f0f0", anchor="w").pack(fill=tk.X, pady=(8, 0))

        self.message_box = tk.Text(result_frame, height=8, width=60,
                                   relief=tk.SOLID, bd=1, font=("Courier", 10),
                                   state=tk.DISABLED, bg="#ffffff")
        self.message_box.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # save button (hidden until there is something to save)
        self.save_btn = tk.Button(
            result_frame, text="Save message to file...",
            command=self._on_save, relief=tk.FLAT,
            bg="#555555", fg="white", padx=12, pady=5,
            cursor="hand2"
        )
        # packed only after a successful receive
        self._recovered_message = None

    # -------------------------------------------------------------- helpers

    def _section_label(self, text):
        frame = tk.Frame(self, bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=18, pady=(14, 0))
        tk.Label(frame, text=text.upper(),
                 bg="#f0f0f0", fg="#888888",
                 font=("Helvetica", 8, "bold")).pack(side=tk.LEFT)
        tk.Frame(frame, bg="#cccccc", height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), pady=6)

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Open PGP message",
            filetypes=[("PGP files", "*.pgp"), ("All files", "*.*")]
        )
        if path:
            self.input_path.set(path)

    def _set_message_box(self, text):
        self.message_box.config(state=tk.NORMAL)
        self.message_box.delete("1.0", tk.END)
        self.message_box.insert("1.0", text)
        self.message_box.config(state=tk.DISABLED)

    # -------------------------------------------------------------- actions

    def _on_receive(self):
        path = self.input_path.get()
        if path == "No file selected":
            messagebox.showerror("Missing file", "Please choose a .pgp file to open.")
            return

        password = self.password_entry.get()

        # The backend raises on tampered / malformed input, and returns a dict
        # with "result" on key/password errors. Handle both cleanly.
        try:
            result = receive_message_from_file(path, password)
        except Exception as e:
            self.status_label.config(text="\u2717  Could not read message", fg="#c0392b")
            self._set_message_box("")
            self._recovered_message = None
            self.save_btn.pack_forget()
            messagebox.showerror(
                "Receive failed",
                "The message could not be decrypted or verified.\n\n"
                f"Details: {type(e).__name__}: {e}"
            )
            return

        # key-lookup / password errors come back as a dict without a message
        if result.get("message") is None:
            reason = result.get("result", "unknown error")
            self.status_label.config(text="\u2717  " + str(reason), fg="#c0392b")
            self._set_message_box("")
            self._recovered_message = None
            self.save_btn.pack_forget()
            messagebox.showerror("Receive failed", str(reason))
            return

        # success - show message and signature status
        message = result["message"]
        self._recovered_message = message
        self._set_message_box(message)

        sig = result.get("signature_verification_result") or {}
        valid = sig.get("valid")
        reason = sig.get("reason", "")

        if valid is True:
            self.status_label.config(
                text="\u2713  Signature VALID  (message is authentic)", fg="#1e8449")
        elif valid is False:
            self.status_label.config(
                text="\u2717  Signature INVALID  (" + str(reason) + ")", fg="#c0392b")
        else:
            self.status_label.config(
                text="\u2139  Message was not signed", fg="#555555")

        # offer to save the recovered message
        self.save_btn.pack(anchor="w", pady=(8, 0))

    def _on_save(self):
        if self._recovered_message is None:
            return
        path = filedialog.asksaveasfilename(
            title="Save recovered message",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._recovered_message)
        except Exception as e:
            messagebox.showerror("Save failed", str(e))
            return
        messagebox.showinfo("Saved", f"Message saved to:\n{path}")


# standalone preview
if __name__ == "__main__":
    root = tk.Tk()
    root.title("PGP - Receive Message")
    root.geometry("700x760")
    nb = ttk.Notebook(root)
    nb.pack(fill=tk.BOTH, expand=True)
    tab = tk.Frame(nb)
    nb.add(tab, text="  Receive Message  ")
    ReceiveDialog(tab)
    root.mainloop()