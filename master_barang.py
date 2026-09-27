"""Master barang: tambah, koreksi, hapus."""
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_all_barang, get_barang, tambah_barang, update_barang, hapus_barang


class MasterBarangWindow:
    def __init__(self, root, user, on_close):
        self.root = root
        self.user = user
        self.on_close = on_close
        self.win = tk.Toplevel(root)
        self.win.title("Master Barang")
        self.win.geometry("900x600")
        self.win.grab_set()
        self.win.configure(bg="#f0f0f0")
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        self.selected_kode = None
        self._build()
        self.refresh()

    def _build(self):
        # Header
        h = tk.Frame(self.win, bg="#4CAF50", height=50)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="MASTER BARANG",
                 bg="#4CAF50", fg="white",
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=20)

        # Pencarian
        f_cari = tk.Frame(self.win, bg="#f0f0f0")
        f_cari.pack(fill="x", padx=10, pady=8)
        tk.Label(f_cari, text="Cari:", bg="#f0f0f0").pack(side="left")
        self.e_cari = tk.Entry(f_cari, width=30, font=("Segoe UI", 11))
        self.e_cari.pack(side="left", padx=5)
        self.e_cari.bind("<KeyRelease>", lambda e: self.refresh())

        # Tabel
        f_tabel = tk.Frame(self.win, bg="#f0f0f0")
        f_tabel.pack(fill="both", expand=True, padx=10)

        cols = ("kode", "nama", "harga", "stok")
        self.tree = ttk.Treeview(f_tabel, columns=cols, show="headings")
        self.tree.heading("kode", text="Kode")
        self.tree.heading("nama", text="Nama Barang")
        self.tree.heading("harga", text="Harga")
        self.tree.heading("stok", text="Stok")
        self.tree.column("kode", width=100, anchor="center")
        self.tree.column("nama", width=400)
        self.tree.column("harga", width=150, anchor="e")
        self.tree.column("stok", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        sb = ttk.Scrollbar(f_tabel, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        # Form
        f_form = tk.LabelFrame(self.win, text=" Form Barang ",
                               font=("Segoe UI", 10, "bold"),
                               bg="#f0f0f0", padx=10, pady=10)
        f_form.pack(fill="x", padx=10, pady=8)

        tk.Label(f_form, text="Kode:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        self.e_kode = tk.Entry(f_form, width=15, font=("Segoe UI", 11))
        self.e_kode.grid(row=0, column=1, padx=5)

        tk.Label(f_form, text="Nama:", bg="#f0f0f0").grid(row=0, column=2, sticky="w")
        self.e_nama = tk.Entry(f_form, width=30, font=("Segoe UI", 11))
        self.e_nama.grid(row=0, column=3, padx=5)

        tk.Label(f_form, text="Harga:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=4)
        self.e_harga = tk.Entry(f_form, width=15, font=("Segoe UI", 11))
        self.e_harga.grid(row=1, column=1, padx=5, pady=4)

        tk.Label(f_form, text="Stok Awal:", bg="#f0f0f0").grid(row=1, column=2, sticky="w", pady=4)
        self.e_stok = tk.Entry(f_form, width=10, font=("Segoe UI", 11))
        self.e_stok.grid(row=1, column=3, padx=5, pady=4, sticky="w")

        # Tombol
        f_btn = tk.Frame(self.win, bg="#f0f0f0")
        f_btn.pack(fill="x", padx=10, pady=8)

        tk.Button(f_btn, text="Tambah Baru", command=self.aksi_tambah,
                  bg="#4CAF50", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=3)
        tk.Button(f_btn, text="Update", command=self.aksi_update,
                  bg="#FF9800", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=3)
        tk.Button(f_btn, text="Hapus", command=self.aksi_hapus,
                  bg="#f44336", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=3)
        tk.Button(f_btn, text="Bersihkan Form", command=self.clear_form,
                  bg="#607D8B", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=3)
        tk.Button(f_btn, text="Tutup", command=self.close,
                  bg="#9E9E9E", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="right", padx=3)

    def refresh(self):
        kw = self.e_cari.get().strip()
        for r in self.tree.get_children():
            self.tree.delete(r)
        for b in get_all_barang(kw):
            self.tree.insert("", "end", values=(
                b["kode"], b["nama"], f"Rp {b['harga']:,.0f}", b["stok"]
            ))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], "values")
        self.selected_kode = v[0]
        b = get_barang(v[0])
        if b:
            self.e_kode.delete(0, tk.END); self.e_kode.insert(0, b["kode"])
            self.e_nama.delete(0, tk.END); self.e_nama.insert(0, b["nama"])
            self.e_harga.delete(0, tk.END); self.e_harga.insert(0, str(b["harga"]))
            self.e_stok.delete(0, tk.END); self.e_stok.insert(0, str(b["stok"]))
            self.e_kode.config(state="disabled")

    def clear_form(self):
        self.selected_kode = None
        for e in (self.e_kode, self.e_nama, self.e_harga, self.e_stok):
            e.delete(0, tk.END)
        self.e_kode.config(state="normal")
        self.e_kode.focus()

    def aksi_tambah(self):
        kode = self.e_kode.get().strip().upper()
        nama = self.e_nama.get().strip()
        try:
            harga = float(self.e_harga.get() or 0)
            stok = int(self.e_stok.get() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Harga & stok harus angka.")
            return
        if not kode or not nama:
            messagebox.showwarning("Input", "Kode & nama wajib diisi.")
            return
        ok, msg = tambah_barang(kode, nama, harga, stok, self.user["username"])
        messagebox.showinfo("Info", msg)
        if ok:
            self.refresh()
            self.clear_form()

    def aksi_update(self):
        if not self.selected_kode:
            messagebox.showinfo("Info", "Pilih barang dulu.")
            return
        nama = self.e_nama.get().strip()
        try:
            harga = float(self.e_harga.get() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Harga harus angka.")
            return
        update_barang(self.selected_kode, nama, harga)
        messagebox.showinfo("Info", "Barang diperbarui.")
        self.refresh()
        self.clear_form()

    def aksi_hapus(self):
        if not self.selected_kode:
            messagebox.showinfo("Info", "Pilih barang dulu.")
            return
        if not messagebox.askyesno("Konfirmasi",
                                   f"Hapus barang {self.selected_kode}?"):
            return
        ok, msg = hapus_barang(self.selected_kode)
        messagebox.showinfo("Info", msg)
        if ok:
            self.refresh()
            self.clear_form()

    def close(self):
        self.win.destroy()
        self.on_close()