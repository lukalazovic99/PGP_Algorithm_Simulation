import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ─────────────────────────────────────────────────────────────────────────────
# Generate Key Dialog — popup window
# ─────────────────────────────────────────────────────────────────────────────

class GenerateKeyDialog(tk.Toplevel):
    """
    Modal popup that collects:
      - Name
      - Email
      - Key size (1024 or 2048 bits)
      - Password + confirm password
    Returns data via self.result (None if cancelled).
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Generate New RSA Key Pair")
        self.resizable(False, False)
        self.grab_set()                      # make it modal
        self.result = None

        self._build_ui()
        self._center_on_parent(parent)

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width() // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w  = self.winfo_width()
        h  = self.winfo_height()
        self.geometry(f"+{pw - w // 2}+{ph - h // 2}")

    def _build_ui(self):
        pad = {"padx": 20, "pady": 6}
        bg  = "#f7f7f7"
        self.configure(bg=bg)

        tk.Label(self, text="Generate RSA Key Pair",
                 bg=bg, font=("Helvetica", 13, "bold"),
                 fg="#222222").pack(pady=(18, 4))
        tk.Label(self, text="Fill in the details for your new key.",
                 bg=bg, fg="#666666",
                 font=("Helvetica", 9)).pack(pady=(0, 12))

        form = tk.Frame(self, bg=bg)
        form.pack(fill=tk.X, **pad)

        # ── Name ──────────────────────────────────────────────────────────────
        tk.Label(form, text="Name:", bg=bg, anchor="w",
                 width=18).grid(row=0, column=0, sticky="w", pady=4)
        self.name_entry = tk.Entry(form, width=32, relief=tk.SOLID, bd=1)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=4)

        # ── Email ─────────────────────────────────────────────────────────────
        tk.Label(form, text="Email:", bg=bg, anchor="w",
                 width=18).grid(row=1, column=0, sticky="w", pady=4)
        self.email_entry = tk.Entry(form, width=32, relief=tk.SOLID, bd=1)
        self.email_entry.grid(row=1, column=1, sticky="w", pady=4)

        # ── Key size ──────────────────────────────────────────────────────────
        tk.Label(form, text="Key size (bits):", bg=bg,
                 anchor="w", width=18).grid(row=2, column=0, sticky="w", pady=4)

        self.keysize_var = tk.IntVar(value=2048)
        size_frame = tk.Frame(form, bg=bg)
        size_frame.grid(row=2, column=1, sticky="w", pady=4)
        ttk.Radiobutton(size_frame, text="1024",
                        variable=self.keysize_var,
                        value=1024).pack(side=tk.LEFT, padx=(0, 16))
        ttk.Radiobutton(size_frame, text="2048",
                        variable=self.keysize_var,
                        value=2048).pack(side=tk.LEFT)

        # ── Password ──────────────────────────────────────────────────────────
        tk.Label(form, text="Password:", bg=bg, anchor="w",
                 width=18).grid(row=3, column=0, sticky="w", pady=(14, 4))
        self.password_entry = tk.Entry(form, show="•", width=32,
                                       relief=tk.SOLID, bd=1)
        self.password_entry.grid(row=3, column=1, sticky="w", pady=(14, 4))

        tk.Label(form, text="Confirm password:", bg=bg,
                 anchor="w", width=18).grid(row=4, column=0, sticky="w", pady=4)
        self.confirm_entry = tk.Entry(form, show="•", width=32,
                                      relief=tk.SOLID, bd=1)
        self.confirm_entry.grid(row=4, column=1, sticky="w", pady=4)

        tk.Label(form,
                 text="⚠  Remember this password — it cannot be recovered.",
                 bg=bg, fg="#c0392b",
                 font=("Helvetica", 8)).grid(row=5, column=0,
                                              columnspan=2, sticky="w", pady=(4, 0))

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(fill=tk.X, padx=20, pady=(16, 20))

        tk.Button(btn_frame, text="Cancel",
                  command=self.destroy,
                  relief=tk.FLAT, bg="#e0e0e0",
                  padx=14, pady=6).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Generate",
                  command=self._on_generate,
                  bg="#2c7be5", fg="white",
                  font=("Helvetica", 10, "bold"),
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2",
                  activebackground="#1a5cc8",
                  activeforeground="white").pack(side=tk.RIGHT)

    def _on_generate(self):
        name     = self.name_entry.get().strip()
        email    = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm  = self.confirm_entry.get()

        if not name:
            messagebox.showerror("Missing field", "Please enter a name.", parent=self)
            return
        if not email or "@" not in email:
            messagebox.showerror("Invalid email", "Please enter a valid email.", parent=self)
            return
        if not password:
            messagebox.showerror("Missing field", "Please enter a password.", parent=self)
            return
        if password != confirm:
            messagebox.showerror("Password mismatch",
                                 "Passwords do not match.", parent=self)
            return

        self.result = {
            "name":     name,
            "email":    email,
            "key_size": self.keysize_var.get(),
            "password": password,
        }
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Key Manager View — main tab
# ─────────────────────────────────────────────────────────────────────────────

class KeyManagerView(tk.Frame):
    """
    Key Manager tab — displays private and public key rings as tables.
    Allows the user to:
      - Generate a new RSA key pair
      - Delete a selected key
      - Import a public key or full key pair from .pem
      - Export a public key or full key pair to .pem
    """

    def __init__(self, parent, private_key_ring, public_key_ring):
        """
        Args:
            parent:           The ttk.Notebook tab frame this lives inside.
            private_key_ring: List of dicts — owned and written by key_ring.py
            public_key_ring:  List of dicts — owned and written by key_ring.py
        """
        super().__init__(parent, bg="#f0f0f0")
        self.pack(fill=tk.BOTH, expand=True)

        self.private_key_ring = private_key_ring
        self.public_key_ring  = public_key_ring

        self._build_ui()
        self._refresh_tables()

    # ─────────────────────────────────────────────────────────────────────────
    # UI CONSTRUCTION
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 16, "pady": 8}

        # ── Private Key Ring ──────────────────────────────────────────────────
        self._section_label("Private Key Ring")

        priv_outer = tk.Frame(self, bg="#f0f0f0")
        priv_outer.pack(fill=tk.BOTH, expand=True, **pad)

        # Table
        priv_cols = ("timestamp", "key_id", "user_name", "user_email", "key_size")
        self.priv_tree = ttk.Treeview(
            priv_outer,
            columns=priv_cols,
            show="headings",
            height=6,
            selectmode="browse"
        )
        self._configure_columns(self.priv_tree, {
            "timestamp":  ("Timestamp",   150),
            "key_id":     ("Key ID",      170),
            "user_name":  ("Name",        130),
            "user_email": ("Email",       170),
            "key_size":   ("Key Size",     80),
        })

        priv_scroll = ttk.Scrollbar(priv_outer, orient="vertical",
                                    command=self.priv_tree.yview)
        self.priv_tree.configure(yscrollcommand=priv_scroll.set)
        self.priv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        priv_scroll.pack(side=tk.LEFT, fill=tk.Y)

        # Buttons for private ring
        priv_btns = tk.Frame(self, bg="#f0f0f0")
        priv_btns.pack(fill=tk.X, padx=16, pady=(0, 4))

        self._btn(priv_btns, "＋  Generate Key Pair",
                  self._on_generate,  "#2c7be5", "white")
        self._btn(priv_btns, "✕  Delete Selected",
                  self._on_delete_private, "#e74c3c", "white")
        self._btn(priv_btns, "↑  Export Public Key (.pem)",
                  self._on_export_public, "#555555", "white")
        self._btn(priv_btns, "↑  Export Full Pair (.pem)",
                  self._on_export_private, "#555555", "white")

        # Divider
        tk.Frame(self, bg="#cccccc", height=1).pack(
            fill=tk.X, padx=16, pady=8)

        # ── Public Key Ring ───────────────────────────────────────────────────
        self._section_label("Public Key Ring")

        pub_outer = tk.Frame(self, bg="#f0f0f0")
        pub_outer.pack(fill=tk.BOTH, expand=True, **pad)

        pub_cols = ("timestamp", "key_id", "user_name", "user_email", "key_size")
        self.pub_tree = ttk.Treeview(
            pub_outer,
            columns=pub_cols,
            show="headings",
            height=6,
            selectmode="browse"
        )
        self._configure_columns(self.pub_tree, {
            "timestamp":  ("Timestamp",   150),
            "key_id":     ("Key ID",      170),
            "user_name":  ("Name",        130),
            "user_email": ("Email",       170),
            "key_size":   ("Key Size",     80),
        })

        pub_scroll = ttk.Scrollbar(pub_outer, orient="vertical",
                                   command=self.pub_tree.yview)
        self.pub_tree.configure(yscrollcommand=pub_scroll.set)
        self.pub_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pub_scroll.pack(side=tk.LEFT, fill=tk.Y)

        # Buttons for public ring
        pub_btns = tk.Frame(self, bg="#f0f0f0")
        pub_btns.pack(fill=tk.X, padx=16, pady=(0, 12))

        self._btn(pub_btns, "↓  Import Public Key (.pem)",
                  self._on_import_public, "#27ae60", "white")
        self._btn(pub_btns, "✕  Delete Selected",
                  self._on_delete_public, "#e74c3c", "white")

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS — UI
    # ─────────────────────────────────────────────────────────────────────────

    def _section_label(self, text):
        frame = tk.Frame(self, bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=16, pady=(12, 0))
        tk.Label(frame, text=text.upper(),
                 bg="#f0f0f0", fg="#888888",
                 font=("Helvetica", 8, "bold")).pack(side=tk.LEFT)
        tk.Frame(frame, bg="#cccccc", height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), pady=6)

    @staticmethod
    def _btn(parent, label, command, bg, fg):
        tk.Button(parent, text=label, command=command,
                  bg=bg, fg=fg,
                  relief=tk.FLAT,
                  padx=10, pady=5,
                  cursor="hand2",
                  font=("Helvetica", 9),
                  activebackground=bg,
                  activeforeground=fg).pack(side=tk.LEFT, padx=(0, 6), pady=4)

    @staticmethod
    def _configure_columns(tree, config: dict):
        for col, (heading, width) in config.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor="w")

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE REFRESH
    # ─────────────────────────────────────────────────────────────────────────

    def _refresh_tables(self):
        """Clears and repopulates both Treeview tables from the key rings."""
        # Private ring
        for row in self.priv_tree.get_children():
            self.priv_tree.delete(row)
        for entry in self.private_key_ring:
            self.priv_tree.insert("", tk.END, values=(
                entry.get("timestamp",  ""),
                entry.get("key_id",     ""),
                entry.get("user_name",  ""),
                entry.get("user_email", ""),
                f"{entry.get('key_size', '')} bit",
            ))

        # Public ring
        for row in self.pub_tree.get_children():
            self.pub_tree.delete(row)
        for entry in self.public_key_ring:
            self.pub_tree.insert("", tk.END, values=(
                entry.get("timestamp",  ""),
                entry.get("key_id",     ""),
                entry.get("user_name",  ""),
                entry.get("user_email", ""),
                f"{entry.get('key_size', '')} bit",
            ))

    def _get_selected_key_id(self, tree) -> str | None:
        """Returns the key_id of the selected row, or None if nothing selected."""
        selected = tree.focus()
        if not selected:
            return None
        values = tree.item(selected, "values")
        return values[1] if values else None   # key_id is column index 1

    # ─────────────────────────────────────────────────────────────────────────
    # BUTTON HANDLERS
    # ─────────────────────────────────────────────────────────────────────────

    def _on_generate(self):
        """Opens the generate dialog, then calls crypto layer to create the key pair."""
        dialog = GenerateKeyDialog(self)
        self.wait_window(dialog)

        if dialog.result is None:
            return   # user cancelled

        data = dialog.result

        # TODO: replace with real crypto call once rsa_keys.py is implemented
        # from crypto.rsa_keys import generate_key_pair
        # new_entry = generate_key_pair(
        #     name=data["name"],
        #     email=data["email"],
        #     key_size=data["key_size"],
        #     password=data["password"]
        # )
        # self.private_key_ring.append(new_entry)
        # self.public_key_ring.append({...public part only...})
        # self._refresh_tables()

        # Temporary placeholder so the UI flow is testable now
        messagebox.showinfo(
            "Key pair ready to generate",
            f"Name:     {data['name']}\n"
            f"Email:    {data['email']}\n"
            f"Key size: {data['key_size']} bits\n\n"
            f"(Crypto layer not yet connected.)"
        )

    def _on_delete_private(self):
        """Deletes the selected key from the private key ring."""
        key_id = self._get_selected_key_id(self.priv_tree)
        if not key_id:
            messagebox.showwarning("No selection",
                                   "Please select a key to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm delete",
            f"Delete private key {key_id}?\n\nThis cannot be undone."
        )
        if not confirm:
            return

        # TODO: replace with real call once key_ring.py is implemented
        # from models.key_ring import delete_private_key
        # delete_private_key(key_id)
        # self.private_key_ring = [k for k in self.private_key_ring
        #                          if k["key_id"] != key_id]
        # self._refresh_tables()

        messagebox.showinfo("Delete", f"Key {key_id} marked for deletion.\n"
                                      f"(Crypto layer not yet connected.)")

    def _on_delete_public(self):
        """Deletes the selected key from the public key ring."""
        key_id = self._get_selected_key_id(self.pub_tree)
        if not key_id:
            messagebox.showwarning("No selection",
                                   "Please select a key to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm delete",
            f"Delete public key {key_id}?"
        )
        if not confirm:
            return

        # TODO: replace with real call once key_ring.py is implemented
        # from models.key_ring import delete_public_key
        # delete_public_key(key_id)
        # self.public_key_ring = [k for k in self.public_key_ring
        #                         if k["key_id"] != key_id]
        # self._refresh_tables()

        messagebox.showinfo("Delete", f"Key {key_id} marked for deletion.\n"
                                      f"(Crypto layer not yet connected.)")

    def _on_export_public(self):
        """Exports only the public part of the selected private ring key to .pem."""
        key_id = self._get_selected_key_id(self.priv_tree)
        if not key_id:
            messagebox.showwarning("No selection",
                                   "Please select a key to export.")
            return

        path = filedialog.asksaveasfilename(
            title="Export public key as .pem",
            defaultextension=".pem",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if not path:
            return

        # TODO: replace with real call once rsa_keys.py is implemented
        # from crypto.rsa_keys import export_public_key
        # export_public_key(key_id, path)

        messagebox.showinfo("Export", f"Public key {key_id} → {path}\n"
                                      f"(Crypto layer not yet connected.)")

    def _on_export_private(self):
        """Exports the full key pair (public + encrypted private) to .pem."""
        key_id = self._get_selected_key_id(self.priv_tree)
        if not key_id:
            messagebox.showwarning("No selection",
                                   "Please select a key to export.")
            return

        path = filedialog.asksaveasfilename(
            title="Export full key pair as .pem",
            defaultextension=".pem",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if not path:
            return

        # TODO: replace with real call once rsa_keys.py is implemented
        # from crypto.rsa_keys import export_key_pair
        # export_key_pair(key_id, path)

        messagebox.showinfo("Export", f"Key pair {key_id} → {path}\n"
                                      f"(Crypto layer not yet connected.)")

    def _on_import_public(self):
        """Imports a public key from a .pem file into the public key ring."""
        path = filedialog.askopenfilename(
            title="Import public key from .pem",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if not path:
            return

        # TODO: replace with real call once rsa_keys.py is implemented
        # from crypto.rsa_keys import import_public_key
        # new_entry = import_public_key(path)
        # self.public_key_ring.append(new_entry)
        # self._refresh_tables()

        messagebox.showinfo("Import", f"Key imported from:\n{path}\n"
                                      f"(Crypto layer not yet connected.)")


# ─────────────────────────────────────────────────────────────────────────────
# Quick standalone test — run this file directly to preview the UI
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fake_private = [
        {
            "timestamp":  "2026-06-23 10:00:00",
            "key_id":     "AABBCCDD11223344",
            "user_name":  "Alice",
            "user_email": "alice@example.com",
            "key_size":   2048,
        },
        {
            "timestamp":  "2026-06-22 09:15:00",
            "key_id":     "EEFF001122334455",
            "user_name":  "Bob",
            "user_email": "bob@example.com",
            "key_size":   1024,
        },
    ]
    fake_public = [
        {
            "timestamp":  "2026-06-23 11:00:00",
            "key_id":     "FFEE998877665544",
            "user_name":  "Charlie",
            "user_email": "charlie@example.com",
            "key_size":   2048,
        },
    ]

    root = tk.Tk()
    root.title("PGP — Key Manager")
    root.geometry("720x700")
    root.resizable(True, True)

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    key_tab = tk.Frame(notebook)
    notebook.add(key_tab, text="  Key Manager  ")

    KeyManagerView(key_tab, fake_private, fake_public)

    root.mainloop()