import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class SendDialog(tk.Frame):
    """
    Send Message tab — lets the user compose a PGP message with optional:
      - Authentication (signing with a private key via SHA-1 + RSA)
      - Confidentiality (encryption with a session key via AES128 or 3DES)
      - Compression (ZIP)
      - Radix-64 conversion
    """

    def __init__(self, parent, private_key_ring, public_key_ring):
        """
        Args:
            parent:           The ttk.Notebook tab frame this lives inside.
            private_key_ring: List of dicts from prstenovi_kljuceva.py — used to populate signing key dropdown.
            public_key_ring:  List of dicts from prstenovi_kljuceva.py — used to populate encryption key dropdown.
        """
        super().__init__(parent, bg="#f0f0f0")
        self.pack(fill=tk.BOTH, expand=True)

        self.private_key_ring = private_key_ring
        self.public_key_ring = public_key_ring

        # ── Internal state variables ──────────────────────────────────────────
        self.sign_var       = tk.BooleanVar(value=False)
        self.encrypt_var    = tk.BooleanVar(value=False)
        self.compress_var   = tk.BooleanVar(value=True)
        self.radix64_var    = tk.BooleanVar(value=True)
        self.algorithm_var  = tk.StringVar(value="AES128")
        self.sign_key_var   = tk.StringVar()
        self.enc_key_var    = tk.StringVar()
        self.output_path    = tk.StringVar(value="No file selected")

        self._build_ui()
        self._refresh_key_dropdowns()

    # ─────────────────────────────────────────────────────────────────────────
    # UI CONSTRUCTION
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Assembles all sections of the Send tab."""
        # Main scrollable canvas so it works on small screens too
        canvas = tk.Canvas(self, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        pad = {"padx": 18, "pady": 8}

        # ── Section: Message input ────────────────────────────────────────────
        self._section_label("Message")

        msg_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        msg_frame.pack(fill=tk.X, **pad)

        tk.Label(msg_frame, text="Message text:", bg="#f0f0f0",
                 anchor="w").pack(fill=tk.X)

        self.message_text = tk.Text(msg_frame, height=7, width=60,
                                    relief=tk.SOLID, bd=1, font=("Courier", 10))
        self.message_text.pack(fill=tk.X, pady=(4, 0))

        # ── Section: Services ─────────────────────────────────────────────────
        self._section_label("Services")

        services_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        services_frame.pack(fill=tk.X, **pad)

        # Signing checkbox → reveals signing options
        sign_cb = ttk.Checkbutton(
            services_frame,
            text="Sign message  (Authentication)",
            variable=self.sign_var,
            command=self._toggle_sign_options
        )
        sign_cb.grid(row=0, column=0, sticky="w", pady=2)

        # Encryption checkbox → reveals encryption options
        enc_cb = ttk.Checkbutton(
            services_frame,
            text="Encrypt message  (Confidentiality)",
            variable=self.encrypt_var,
            command=self._toggle_encrypt_options
        )
        enc_cb.grid(row=1, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            services_frame,
            text="Compress message  (ZIP)",
            variable=self.compress_var
        ).grid(row=2, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            services_frame,
            text="Convert to Radix-64",
            variable=self.radix64_var
        ).grid(row=3, column=0, sticky="w", pady=2)

        # ── Section: Signing options (hidden until checkbox ticked) ───────────
        self._section_label("Signing Options")

        self.sign_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="  Authentication — SHA-1 + RSA  ",
            bg="#f0f0f0", fg="#333333",
            relief=tk.GROOVE, bd=1,
            padx=12, pady=8
        )
        # Not packed yet — shown/hidden by _toggle_sign_options()

        tk.Label(self.sign_frame, text="Select private key to sign with:",
                 bg="#f0f0f0", anchor="w").grid(row=0, column=0, sticky="w")

        self.sign_key_dropdown = ttk.Combobox(
            self.sign_frame,
            textvariable=self.sign_key_var,
            state="readonly",
            width=45
        )
        self.sign_key_dropdown.grid(row=0, column=1, padx=(10, 0), sticky="w")

        tk.Label(self.sign_frame, text="Password for private key:",
                 bg="#f0f0f0", anchor="w").grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.sign_password_entry = tk.Entry(
            self.sign_frame, show="•", width=30,
            relief=tk.SOLID, bd=1
        )
        self.sign_password_entry.grid(row=1, column=1, padx=(10, 0),
                                      pady=(8, 0), sticky="w")

        # ── Section: Encryption options (hidden until checkbox ticked) ────────
        self._section_label("Encryption Options")

        self.enc_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="  Confidentiality — Session Key  ",
            bg="#f0f0f0", fg="#333333",
            relief=tk.GROOVE, bd=1,
            padx=12, pady=8
        )
        # Not packed yet — shown/hidden by _toggle_encrypt_options()

        tk.Label(self.enc_frame, text="Select recipient's public key:",
                 bg="#f0f0f0", anchor="w").grid(row=0, column=0, sticky="w")

        self.enc_key_dropdown = ttk.Combobox(
            self.enc_frame,
            textvariable=self.enc_key_var,
            state="readonly",
            width=45
        )
        self.enc_key_dropdown.grid(row=0, column=1, padx=(10, 0), sticky="w")

        tk.Label(self.enc_frame, text="Symmetric algorithm:",
                 bg="#f0f0f0", anchor="w").grid(row=1, column=0,
                                                 sticky="w", pady=(8, 0))

        algo_frame = tk.Frame(self.enc_frame, bg="#f0f0f0")
        algo_frame.grid(row=1, column=1, padx=(10, 0), pady=(8, 0), sticky="w")

        ttk.Radiobutton(algo_frame, text="AES-128",
                        variable=self.algorithm_var,
                        value="AES128").pack(side=tk.LEFT, padx=(0, 16))
        ttk.Radiobutton(algo_frame, text="3DES (TripleDES)",
                        variable=self.algorithm_var,
                        value="3DES").pack(side=tk.LEFT)

        # ── Section: Output file ──────────────────────────────────────────────
        self._section_label("Output")

        out_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        out_frame.pack(fill=tk.X, **pad)

        tk.Label(out_frame, text="Save message to:",
                 bg="#f0f0f0", anchor="w").pack(anchor="w")

        path_row = tk.Frame(out_frame, bg="#f0f0f0")
        path_row.pack(fill=tk.X, pady=(4, 0))

        self.output_label = tk.Label(
            path_row,
            textvariable=self.output_path,
            bg="#ffffff", relief=tk.SOLID, bd=1,
            anchor="w", padx=6,
            width=50, font=("Courier", 9)
        )
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(path_row, text="Browse…",
                   command=self._browse_output).pack(side=tk.LEFT, padx=(8, 0))

        # ── Send button ───────────────────────────────────────────────────────
        send_btn = tk.Button(
            self.scrollable_frame,
            text="  ▶  Send Message",
            command=self._on_send,
            bg="#2c7be5", fg="white",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=20, pady=10,
            cursor="hand2",
            activebackground="#1a5cc8",
            activeforeground="white"
        )
        send_btn.pack(pady=(16, 24))

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS — UI
    # ─────────────────────────────────────────────────────────────────────────

    def _section_label(self, text):
        """Renders a subtle section divider label."""
        frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        frame.pack(fill=tk.X, padx=18, pady=(14, 0))
        tk.Label(frame, text=text.upper(),
                 bg="#f0f0f0", fg="#888888",
                 font=("Helvetica", 8, "bold")).pack(side=tk.LEFT)
        tk.Frame(frame, bg="#cccccc", height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), pady=6
        )

    def _toggle_sign_options(self):
        """Shows or hides the signing options panel."""
        if self.sign_var.get():
            self.sign_frame.pack(fill=tk.X, padx=18, pady=4)
        else:
            self.sign_frame.pack_forget()

    def _toggle_encrypt_options(self):
        """Shows or hides the encryption options panel."""
        if self.encrypt_var.get():
            self.enc_frame.pack(fill=tk.X, padx=18, pady=4)
        else:
            self.enc_frame.pack_forget()

    def _browse_output(self):
        """Opens a file save dialog so the user picks where to write the output."""
        path = filedialog.asksaveasfilename(
            title="Save PGP message as…",
            defaultextension=".pgp",
            filetypes=[("PGP files", "*.pgp"), ("All files", "*.*")]
        )
        if path:
            self.output_path.set(path)

    def _refresh_key_dropdowns(self):
        """
        Populates both dropdowns from the key rings.
        Call this again whenever keys are added/removed.
        Format shown: "user@email.com  [KeyID: XXXXXXXXXXXXXXXX]"
        """
        private_options = [
            f"{entry['user_id']}  [KeyID: {entry['key_id']}]"
            for entry in self.private_key_ring
        ]
        public_options = [
            f"{entry['user_id']}  [KeyID: {entry['key_id']}]"
            for entry in self.public_key_ring
        ]

        self.sign_key_dropdown["values"] = private_options
        self.enc_key_dropdown["values"] = public_options

        if private_options:
            self.sign_key_var.set(private_options[0])
        if public_options:
            self.enc_key_var.set(public_options[0])

    # ─────────────────────────────────────────────────────────────────────────
    # SEND — collects inputs and hands off to crypto layer
    # ─────────────────────────────────────────────────────────────────────────

    def _on_send(self):
        """
        Validates all inputs, then calls the crypto pipeline.
        The actual crypto work will be done by:
            - signing.py       → sign()
            - compression.py   → compress()
            - encryption.py    → encrypt()
            - radix64/encode.py → encode()
            - models/message_sender.py → build_message()
        This method only handles GUI validation and feedback.
        """
        # ── 1. Collect message ────────────────────────────────────────────────
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Missing input", "Please enter a message to send.")
            return

        # ── 2. Collect output path ────────────────────────────────────────────
        output_path = self.output_path.get()
        if output_path == "No file selected":
            messagebox.showerror("Missing output", "Please choose where to save the output file.")
            return

        # ── 3. Collect signing options ────────────────────────────────────────
        sign          = self.sign_var.get()
        sign_key_id   = None
        sign_password = None

        if sign:
            selected_sign = self.sign_key_var.get()
            if not selected_sign:
                messagebox.showerror("Missing key", "Please select a private key for signing.")
                return
            sign_password = self.sign_password_entry.get()
            if not sign_password:
                messagebox.showerror("Missing password", "Please enter the password for the signing key.")
                return
            # Extract key_id from the dropdown label
            sign_key_id = self._extract_key_id(selected_sign)

        # ── 4. Collect encryption options ─────────────────────────────────────
        encrypt     = self.encrypt_var.get()
        enc_key_id  = None
        algorithm   = None

        if encrypt:
            selected_enc = self.enc_key_var.get()
            if not selected_enc:
                messagebox.showerror("Missing key", "Please select a recipient public key for encryption.")
                return
            enc_key_id = self._extract_key_id(selected_enc)
            algorithm  = self.algorithm_var.get()

        # ── 5. Other options ──────────────────────────────────────────────────
        compress = self.compress_var.get()
        radix64  = self.radix64_var.get()

        # ── 6. Hand off to crypto layer (to be implemented) ───────────────────
        params = {
            "message":      message,
            "sign":         sign,
            "sign_key_id":  sign_key_id,
            "sign_password": sign_password,
            "encrypt":      encrypt,
            "enc_key_id":   enc_key_id,
            "algorithm":    algorithm,
            "compress":     compress,
            "radix64":      radix64,
            "output_path":  output_path,
        }

        # TODO: replace this call with the real pipeline once crypto layer is ready
        # from models.message_sender import build_and_send
        # try:
        #     build_and_send(params, self.private_key_ring, self.public_key_ring)
        #     messagebox.showinfo("Success", f"Message saved to:\n{output_path}")
        # except Exception as e:
        #     messagebox.showerror("Error", str(e))

        # Temporary confirmation so the UI is testable right now
        summary = (
            f"Message collected ✓\n\n"
            f"  Sign:      {'Yes — key ' + str(sign_key_id) if sign else 'No'}\n"
            f"  Encrypt:   {'Yes — ' + str(algorithm) + ' key ' + str(enc_key_id) if encrypt else 'No'}\n"
            f"  Compress:  {'Yes' if compress else 'No'}\n"
            f"  Radix-64:  {'Yes' if radix64 else 'No'}\n"
            f"  Output:    {output_path}"
        )
        messagebox.showinfo("Ready to send", summary)

    @staticmethod
    def _extract_key_id(dropdown_value: str) -> str:
        """
        Pulls the key ID out of a dropdown label like:
        'user@email.com  [KeyID: XXXXXXXXXXXXXXXX]'
        """
        try:
            return dropdown_value.split("KeyID: ")[1].rstrip("]").strip()
        except IndexError:
            return ""


# ─────────────────────────────────────────────────────────────────────────────
# Quick standalone test — run this file directly to preview the UI
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Fake key ring data so the dropdowns are populated during preview
    fake_private = [
        {"user_id": "alice@example.com", "key_id": "AABBCCDD11223344"},
        {"user_id": "bob@example.com",   "key_id": "EEFF001122334455"},
    ]
    fake_public = [
        {"user_id": "charlie@example.com", "key_id": "FFEE998877665544"},
        {"user_id": "diana@example.com",   "key_id": "11223344AABBCCDD"},
    ]

    root = tk.Tk()
    root.title("PGP — Send Message")
    root.geometry("700x900")
    root.resizable(True, True)

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    send_tab = tk.Frame(notebook)
    notebook.add(send_tab, text="  Send Message  ")

    SendDialog(send_tab, fake_private, fake_public)

    root.mainloop()