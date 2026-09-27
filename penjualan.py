"""Menu penjualan (kasir)."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import (get_all_barang, get_barang, generate_no_nota,
                      simpan_penjualan, cek_login)


class PenjualanWindow:
    def __init__(self, root, user, on_close):
        self.root = root
        self.user = user
        self.on_close = on_close
        self.win = tk.Toplevel(root)
        self.win.title("Penjualan - Kasir")
        self.win.geometry("1050x680")
        self.win.grab_set()
        self.win.configure(bg="#f0f0f0")
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        self.cart = []
        self._build()
        self.e_cari.focus()

    def _build(self):
        # Header
        h = tk.Frame(self.win, bg="#2196F3", height=55)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="KASIR PENJUALAN",
                 bg="#2196F3", fg="white",
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=20)
        tk.Label(h, text=f"Kasir: {self.user['username']}",
                 bg="#2196F3", fg="#e3f2fd",
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

        # Info nota
        f_nota = tk.Frame(self.win, bg="#f0f0f0")
        f_nota.pack(fill="x", padx=10, pady=(8, 0))
        tk.Label(f_nota, text="No. Nota:", bg="#f0f0f0",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        self.lbl_nota = tk.Label(f_nota, text="-", bg="#f0f0f0",
                                 fg="#1a237e",
                                 font=("Consolas", 12, "bold"))
        self.lbl_nota.pack(side="left", padx=5)

        # Pencarian
        f_cari = tk.Frame(self.win, bg="#f0f0f0")
        f_cari.pack(fill="x", padx=10, pady=8)
        tk.Label(f_cari, text="Kode/Nama:", bg="#f0f0f0").pack(side="left")
        self.e_cari = tk.Entry(f_cari, width=30, font=("Segoe UI", 11))
        self.e_cari.pack(side="left", padx=5)
        self.e_cari.bind("<KeyRelease>", self.on_ketik)
        self.e_cari.bind("<Return>", lambda e: self.tambah_item())
        self.e_cari.bind("<Down>", self.fokus_listbox)

        tk.Label(f_cari, text="Qty:", bg="#f0f0f0").pack(side="left", padx=(10, 0))
        self.e_qty = tk.Entry(f_cari, width=5, font=("Segoe UI", 11))
        self.e_qty.insert(0, "1")
        self.e_qty.pack(side="left", padx=5)
        self.e_qty.bind("<Return>", lambda e: self.tambah_item())

        tk.Button(f_cari, text="Tambah", command=self.tambah_item,
                  bg="#4CAF50", fg="white", padx=10,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        self.lbl_info = tk.Label(f_cari, text="", bg="#f0f0f0",
                                 fg="green", font=("Segoe UI", 10, "bold"))
        self.lbl_info.pack(side="left", padx=10)

        # Listbox hasil cari
        self.listbox = tk.Listbox(self.win, height=3, font=("Consolas", 10))
        self.listbox.pack(fill="x", padx=10)
        self.listbox.bind("<<ListboxSelect>>", self.on_pilih_listbox)
        self.listbox.bind("<Double-Button-1>", self.on_pilih_listbox)

        # Tabel keranjang
        f_tab = tk.LabelFrame(self.win, text=" Keranjang ",
                              font=("Segoe UI", 10, "bold"),
                              bg="#f0f0f0", padx=5, pady=5)
        f_tab.pack(fill="both", expand=True, padx=10, pady=5)
        cols = ("kode", "nama", "harga", "qty", "subtotal")
        self.tree = ttk.Treeview(f_tab, columns=cols, show="headings", height=10)
        for c, t, w in [("kode", "Kode", 70), ("nama", "Nama Barang", 320),
                        ("harga", "Harga", 110), ("qty", "Qty", 60),
                        ("subtotal", "Subtotal", 130)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center" if c in ("kode", "qty") else
                             ("e" if c in ("harga", "subtotal") else "w"))
        self.tree.pack(fill="both", expand=True, side="left")
        sb = ttk.Scrollbar(f_tab, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        # Total
        f_total = tk.Frame(self.win, bg="#f0f0f0")
        f_total.pack(fill="x", padx=10, pady=(5, 10))
        tk.Label(f_total, text="TOTAL:", bg="#f0f0f0",
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        self.lbl_total = tk.Label(f_total, text="Rp 0", bg="#f0f0f0",
                                  fg="#008000",
                                  font=("Segoe UI", 20, "bold"))
        self.lbl_total.pack(side="left", padx=10)

        tk.Button(f_total, text="Hapus Item", command=self.hapus_item,
                  bg="#f44336", fg="white", padx=10, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="right", padx=3)
        tk.Button(f_total, text="BAYAR", command=self.proses_bayar,
                  bg="#4CAF50", fg="white", padx=20, pady=6,
                  font=("Segoe UI", 11, "bold")).pack(side="right", padx=3)
        tk.Button(f_total, text="Tutup", command=self.close,
                  bg="#9E9E9E", fg="white", padx=10, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="right", padx=3)

    # ---------- pencarian ----------
    def on_ketik(self, event):
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
            return
        kw = self.e_cari.get().strip()
        self.listbox.delete(0, tk.END)
        self.lbl_info.config(text="")
        if not kw:
            return
        hasil = get_all_barang(kw)[:15]
        for b in hasil:
            self.listbox.insert(
                tk.END,
                f"{b['kode']}  |  {b['nama']:<30}  |  Rp {b['harga']:>10,.0f}  |  Stok: {b['stok']}"
            )

    def fokus_listbox(self, event):
        if self.listbox.size() > 0:
            self.listbox.focus_set()
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(0)
            self.listbox.activate(0)

    def on_pilih_listbox(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        kode = self.listbox.get(sel[0]).split("|")[0].strip()
        self.e_cari.delete(0, tk.END)
        self.e_cari.insert(0, kode)
        self.e_qty.focus_set()
        self.e_qty.select_range(0, tk.END)

    # ---------- keranjang ----------
    def tambah_item(self):
        kw = self.e_cari.get().strip()
        if not kw:
            return
        b = get_barang(kw.upper())
        if not b:
            hasil = get_all_barang(kw)
            if not hasil:
                messagebox.showwarning("Tidak Ditemukan", f"Barang '{kw}' tidak ada.")
                return
            b = hasil[0]

        try:
            qty = int(self.e_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input", "Qty harus angka positif.")
            return

        if qty > b["stok"]:
            messagebox.showwarning("Stok Kurang",
                                   f"Stok '{b['nama']}' hanya {b['stok']}.")
            return

        for it in self.cart:
            if it["kode"] == b["kode"]:
                if it["qty"] + qty > b["stok"]:
                    messagebox.showwarning("Stok Kurang",
                                           f"Total qty melebihi stok ({b['stok']}).")
                    return
                it["qty"] += qty
                it["subtotal"] = it["harga"] * it["qty"]
                break
        else:
            self.cart.append({
                "kode": b["kode"], "nama": b["nama"], "harga": b["harga"],
                "qty": qty, "subtotal": b["harga"] * qty
            })

        self.refresh_tabel()
        self.e_cari.delete(0, tk.END)
        self.e_qty.delete(0, tk.END)
        self.e_qty.insert(0, "1")
        self.listbox.delete(0, tk.END)
        self.lbl_info.config(text="")
        self.e_cari.focus_set()

    def refresh_tabel(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        total = 0
        for it in self.cart:
            self.tree.insert("", "end", values=(
                it["kode"], it["nama"],
                f"Rp {it['harga']:,.0f}", it["qty"],
                f"Rp {it['subtotal']:,.0f}"
            ))
            total += it["subtotal"]
        self.lbl_total.config(text=f"Rp {total:,.0f}")

    def hapus_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Pilih item dulu.")
            return
        idx = self.tree.index(sel[0])
        del self.cart[idx]
        self.refresh_tabel()

    # ---------- bayar ----------
    def proses_bayar(self):
        if not self.cart:
            messagebox.showinfo("Info", "Keranjang kosong.")
            return

        subtotal = sum(it["subtotal"] for it in self.cart)

        dlg = tk.Toplevel(self.win)
        dlg.title("Pembayaran")
        dlg.geometry("380x420")
        dlg.grab_set()
        dlg.configure(bg="white")

        tk.Label(dlg, text="SUBTOTAL", bg="white",
                 font=("Segoe UI", 10)).pack(pady=(15, 0))
        tk.Label(dlg, text=f"Rp {subtotal:,.0f}", bg="white",
                 fg="#1a237e", font=("Segoe UI", 16, "bold")).pack()

        tk.Label(dlg, text="Diskon (Rp):", bg="white",
                 font=("Segoe UI", 10)).pack(pady=(10, 0))
        e_diskon = tk.Entry(dlg, font=("Segoe UI", 13), justify="right")
        e_diskon.insert(0, "0")
        e_diskon.pack(padx=20, fill="x")

        lbl_total = tk.Label(dlg, text=f"TOTAL: Rp {subtotal:,.0f}", bg="white",
                             fg="#008000", font=("Segoe UI", 14, "bold"))
        lbl_total.pack(pady=8)

        tk.Label(dlg, text="Bayar (Rp):", bg="white",
                 font=("Segoe UI", 10)).pack()
        e_bayar = tk.Entry(dlg, font=("Segoe UI", 14), justify="right")
        e_bayar.pack(padx=20, fill="x")
        e_bayar.focus()

        lbl_kembali = tk.Label(dlg, text="Kembalian: Rp 0", bg="white",
                               fg="#2196F3", font=("Segoe UI", 12, "bold"))
        lbl_kembali.pack(pady=8)

        state = {"total": subtotal, "diskon": 0}

        def recalc(event=None):
            try:
                diskon = float(e_diskon.get() or 0)
            except ValueError:
                diskon = 0
            if diskon < 0:
                diskon = 0
            total = max(0, subtotal - diskon)
            state["total"] = total
            state["diskon"] = diskon
            lbl_total.config(text=f"TOTAL: Rp {total:,.0f}")
            try:
                bayar = float(e_bayar.get() or 0)
                kembali = bayar - total
                if kembali >= 0:
                    lbl_kembali.config(text=f"Kembalian: Rp {kembali:,.0f}",
                                       fg="#2196F3")
                else:
                    lbl_kembali.config(text=f"Kurang: Rp {abs(kembali):,.0f}",
                                       fg="red")
            except ValueError:
                pass

        e_diskon.bind("<KeyRelease>", recalc)
        e_bayar.bind("<KeyRelease>", recalc)

        def konfirmasi():
            # Validasi password admin jika diskon > 0
            if state["diskon"] > 0 and self.user["role"] != "admin":
                pw = tk.simpledialog.askstring(
                    "Otorisasi Admin",
                    "Diskon memerlukan otorisasi admin.\nMasukkan password admin:",
                    show="*", parent=dlg)
                if not pw or not cek_login("admin", pw):
                    messagebox.showerror("Gagal", "Password admin salah.")
                    return

            try:
                bayar = float(e_bayar.get())
            except ValueError:
                messagebox.showwarning("Input", "Bayar harus angka.")
                return
            if bayar < state["total"]:
                messagebox.showwarning("Kurang", "Uang bayar kurang.")
                return

            kembali = bayar - state["total"]
            no_nota = generate_no_nota()
            ok, msg = simpan_penjualan(
                no_nota, self.user["username"], self.cart,
                subtotal, state["diskon"], state["total"], bayar, kembali
            )
            if not ok:
                messagebox.showerror("Gagal", msg)
                return

            self.tampilkan_struk(no_nota, subtotal, state["diskon"],
                                 state["total"], bayar, kembali)
            self.cart.clear()
            self.refresh_tabel()
            dlg.destroy()

        tk.Button(dlg, text="✔ Konfirmasi", command=konfirmasi,
                  bg="#4CAF50", fg="white", padx=20, pady=8,
                  font=("Segoe UI", 11, "bold")).pack(pady=10)

    def tampilkan_struk(self, no_nota, subtotal, diskon, total, bayar, kembali):
        L = 46
        s = "=" * L + "\n"
        s += "ABADI MINIMARKET".center(L) + "\n"
        s += "Jl. Merdeka No. 123, Jakarta".center(L) + "\n"
        s += "=" * L + "\n"
        s += f"No. Nota : {no_nota}\n"
        s += f"Tanggal  : {datetime.now():%d-%m-%Y %H:%M:%S}\n"
        s += f"Kasir    : {self.user['username']}\n"
        s += "-" * L + "\n"
        for it in self.cart:
            s += f"{it['nama']}\n"
            s += f"  {it['qty']} x {it['harga']:,.0f} = {it['subtotal']:,.0f}\n"
        s += "-" * L + "\n"
        s += f"SUBTOTAL : Rp {subtotal:>14,.0f}\n"
        if diskon > 0:
            s += f"DISKON   : Rp {diskon:>14,.0f}\n"
        s += f"TOTAL    : Rp {total:>14,.0f}\n"
        s += f"BAYAR    : Rp {bayar:>14,.0f}\n"
        s += f"KEMBALI  : Rp {kembali:>14,.0f}\n"
        s += "=" * L + "\n"
        s += "Terima kasih telah berbelanja".center(L) + "\n"
        s += "=" * L + "\n"

        win = tk.Toplevel(self.win)
        win.title(f"Struk {no_nota}")
        win.geometry("520x600")
        txt = tk.Text(win, font=("Consolas", 10), bg="white")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("1.0", s)
        txt.config(state="disabled")

    def close(self):
        self.win.destroy()
        self.on_close()


# import simpledialog di akhir agar tidak lupa
import tkinter.simpledialog