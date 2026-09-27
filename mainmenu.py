"""Menu utama setelah login."""
import tkinter as tk
from tkinter import messagebox


class MainMenu:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"Abadi Minimarket - {user['username'].title()} ({user['role']})")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

        self._build()

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _build(self):
        self._clear()

        # Header
        header = tk.Frame(self.root, bg="#1a237e", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ABADI MINIMARKET",
                 bg="#1a237e", fg="white",
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=20)
        tk.Label(header, text=f"Login: {self.user['username']}  |  Role: {self.user['role'].upper()}",
                 bg="#1a237e", fg="#cfd8dc",
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

        # Container tombol menu
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(expand=True, fill="both", padx=40, pady=30)

        role = self.user["role"]

        # Menu untuk SEMUA user
        self._add_menu(container, "🛒  PENJUALAN (KASIR)",
                       lambda: self._open_penjualan(), "#2196F3")

        # Menu HANYA admin
        if role == "admin":
            self._add_menu(container, "📦  MASTER BARANG",
                           lambda: self._open_master(), "#4CAF50")
            self._add_menu(container, "➕  STOK MASUK",
                           lambda: self._open_stok(), "#FF9800")
            self._add_menu(container, "📊  LAPORAN",
                           lambda: self._open_laporan(), "#9C27B0")

        # Tombol logout
        tk.Button(self.root, text="Logout",
                  command=self._logout,
                  bg="#f44336", fg="white",
                  font=("Segoe UI", 10, "bold"),
                  padx=20, pady=6).pack(side="bottom", anchor="e",
                                        padx=20, pady=15)

    def _add_menu(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command,
                        bg=color, fg="white",
                        font=("Segoe UI", 14, "bold"),
                        anchor="w", padx=20, pady=15,
                        relief="flat", cursor="hand2")
        btn.pack(fill="x", pady=6)

    def _open_penjualan(self):
        from penjualan import PenjualanWindow
        PenjualanWindow(self.root, self.user, self._build)

    def _open_master(self):
        from master_barang import MasterBarangWindow
        MasterBarangWindow(self.root, self.user, self._build)

    def _open_stok(self):
        from stok import StokWindow
        StokWindow(self.root, self.user, self._build)

    def _open_laporan(self):
        from laporan import LaporanWindow
        LaporanWindow(self.root, self.user, self._build)

    def _logout(self):
        if messagebox.askyesno("Logout", "Yakin ingin logout?"):
            self._clear()
            from login import show_login
            show_login(self.root, lambda u: MainMenu(self.root, u))