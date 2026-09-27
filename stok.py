"""Menu stok masuk."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_all_barang, get_barang, tambah_stok, get_stok_masuk


class StokWindow:
    def __init__(self, root, user, on_close):
        self.root = root
        self.user = user
        self.on_close = on_close
        self.win = tk.Toplevel(root)
        self.win.title("Stok Masuk")
        self.win.geometry("900x600")
        self.win.grab_set()
        self.win.configure(bg="#f0f0f0")
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        self._build()
        self.refresh_riwayat()

    def _build(self):
        h = tk.Frame(self.win, bg="#FF9800", height=50)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="STOK MASUK",
                 bg="#FF9800", fg="white",
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=20)

        # Form input
        f_form = tk.LabelFrame(self.win, text=" Tambah Stok ",
                               font=("Segoe UI", 10, "bold"),
                               bg="#f0f0f0", padx=10, pady=10)
        f_form.pack(fill="x", padx=10, pady=10)

        tk.Label(f_form, text="Kode Barang:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        self.e_kode = tk.Entry(f_form, width=15, font=("Segoe UI", 11))
        self.e_kode.grid(row=0, column=1, padx=5)
        self.e_kode.bind("<KeyRelease>", self.cari_barang)

        self.lbl_nama = tk.Label(f_form, text="", bg="#f0f0f0",
                                 fg="blue", font=("Segoe UI", 10, "bold"))
        self.lbl_nama.grid(row=0, column=2, columnspan=3, sticky="w", padx=10)

        tk.Label(f_form, text="Qty Tambah:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=4)
        self.e_qty = tk.Entry(f_form, width=10, font=("Segoe UI", 11))
        self.e_qty.grid(row=1, column=1, padx=5, pady=4)

        tk.Label(f_form, text="Keterangan:", bg="#f0f0f0").grid(row=1, column=2, sticky="w", pady=4)
        self.e_ket = tk.Entry(f_form, width=30, font=("Segoe UI", 11))
        self.e_ket.grid(row=1, column=3, padx=5, pady=4)

        tk.Button(f_form, text="Simpan Stok", command=self.aksi_simpan,
                  bg="#FF9800", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=8)

        # Riwayat
        f_riw = tk.LabelFrame(self.win, text=" Riwayat Stok Masuk (hari ini) ",
                              font=("Segoe UI", 10, "bold"),
                              bg="#f0f0f0", padx=10, pady=10)
        f_riw.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("tanggal", "kode", "nama", "qty", "keterangan", "user")
        self.tree = ttk.Treeview(f_riw, columns=cols, show="headings")
        for c, t, w in [("tanggal", "Tanggal", 140), ("kode", "Kode", 80),
                        ("nama", "Nama Barang", 220), ("qty", "Qty", 60),
                        ("keterangan", "Keterangan", 200), ("user", "User", 80)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center" if c in ("kode", "qty") else "w")
        self.tree.pack(fill="both", expand=True)

        tk.Button(self.win, text="Tutup", command=self.close,
                  bg="#9E9E9E", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="right", padx=10, pady=(0, 10))

    def cari_barang(self, event=None):
        kode = self.e_kode.get().strip().upper()
        if not kode:
            self.lbl_nama.config(text="")
            return
        b = get_barang(kode)
        if b:
            self.lbl_nama.config(
                text=f"{b['nama']}  |  Stok saat ini: {b['stok']}",
                fg="green")
        else:
            self.lbl_nama.config(text="❌ Kode tidak ditemukan", fg="red")

    def aksi_simpan(self):
        kode = self.e_kode.get().strip().upper()
        try:
            qty = int(self.e_qty.get() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Qty harus angka.")
            return
        if qty <= 0:
            messagebox.showwarning("Input", "Qty harus > 0.")
            return
        ok, msg = tambah_stok(kode, qty, self.e_ket.get().strip(),
                              self.user["username"])
        messagebox.showinfo("Info", msg)
        if ok:
            self.e_kode.delete(0, tk.END)
            self.e_qty.delete(0, tk.END)
            self.e_ket.delete(0, tk.END)
            self.lbl_nama.config(text="")
            self.refresh_riwayat()

    def refresh_riwayat(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        tgl = datetime.now().strftime("%Y-%m-%d")
        for s in get_stok_masuk(tgl, tgl):
            self.tree.insert("", "end", values=(
                s["tanggal"][:19], s["kode"], s["nama"],
                s["qty"], s["keterangan"] or "", s["user"] or ""
            ))

    def close(self):
        self.win.destroy()
        self.on_close()