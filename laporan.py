"""Menu laporan harian & bulanan."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import laporan_penjualan, laporan_detail, laporan_ringkasan_barang


class LaporanWindow:
    def __init__(self, root, user, on_close):
        self.root = root
        self.user = user
        self.on_close = on_close
        self.win = tk.Toplevel(root)
        self.win.title("Laporan")
        self.win.geometry("1000x650")
        self.win.grab_set()
        self.win.configure(bg="#f0f0f0")
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        self._build()
        self.mode_harian()

    def _build(self):
        h = tk.Frame(self.win, bg="#9C27B0", height=50)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="LAPORAN PENJUALAN",
                 bg="#9C27B0", fg="white",
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=20)

        # Filter
        f_filter = tk.Frame(self.win, bg="#f0f0f0")
        f_filter.pack(fill="x", padx=10, pady=10)

        tk.Button(f_filter, text="📅 Harian (hari ini)",
                  command=self.mode_harian,
                  bg="#2196F3", fg="white", padx=10, pady=5,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=3)
        tk.Button(f_filter, text="📆 Bulanan (bulan ini)",
                  command=self.mode_bulanan,
                  bg="#FF9800", fg="white", padx=10, pady=5,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=3)

        tk.Label(f_filter, text="Dari:", bg="#f0f0f0").pack(side="left", padx=(20, 3))
        self.e_dari = tk.Entry(f_filter, width=12, font=("Segoe UI", 10))
        self.e_dari.pack(side="left")
        tk.Label(f_filter, text="Sampai:", bg="#f0f0f0").pack(side="left", padx=(10, 3))
        self.e_sampai = tk.Entry(f_filter, width=12, font=("Segoe UI", 10))
        self.e_sampai.pack(side="left")
        tk.Label(f_filter, text="(YYYY-MM-DD)", bg="#f0f0f0",
                 fg="gray", font=("Segoe UI", 8)).pack(side="left", padx=5)
        tk.Button(f_filter, text="Terapkan", command=self.terapkan,
                  bg="#607D8B", fg="white", padx=10, pady=5,
                  font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        # Notebook tab: Ringkasan Nota | Ringkasan Barang
        self.nb = ttk.Notebook(self.win)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Tab 1: daftar nota
        f1 = tk.Frame(self.nb)
        self.nb.add(f1, text="Daftar Nota")
        cols = ("no_nota", "tanggal", "kasir", "subtotal", "diskon", "total")
        self.tree_nota = ttk.Treeview(f1, columns=cols, show="headings")
        for c, t, w in [("no_nota", "No. Nota", 110), ("tanggal", "Tanggal", 140),
                        ("kasir", "Kasir", 90), ("subtotal", "Subtotal", 120),
                        ("diskon", "Diskon", 100), ("total", "Total", 130)]:
            self.tree_nota.heading(c, text=t)
            self.tree_nota.column(c, width=w,
                                  anchor="e" if c in ("subtotal", "diskon", "total")
                                  else "center" if c in ("no_nota", "kasir") else "w")
        self.tree_nota.pack(fill="both", expand=True, side="left")
        sb = ttk.Scrollbar(f1, orient="vertical", command=self.tree_nota.yview)
        sb.pack(side="right", fill="y")
        self.tree_nota.configure(yscrollcommand=sb.set)
        self.tree_nota.bind("<Double-Button-1>", self.lihat_detail)

        # Tab 2: ringkasan barang
        f2 = tk.Frame(self.nb)
        self.nb.add(f2, text="Ringkasan Barang")
        cols2 = ("kode", "nama", "qty", "total")
        self.tree_barang = ttk.Treeview(f2, columns=cols2, show="headings")
        for c, t, w in [("kode", "Kode", 90), ("nama", "Nama Barang", 350),
                        ("qty", "Total Qty", 100), ("total", "Total Rp", 150)]:
            self.tree_barang.heading(c, text=t)
            self.tree_barang.column(c, width=w,
                                    anchor="e" if c == "total" else
                                    "center" if c in ("kode", "qty") else "w")
        self.tree_barang.pack(fill="both", expand=True, side="left")
        sb2 = ttk.Scrollbar(f2, orient="vertical", command=self.tree_barang.yview)
        sb2.pack(side="right", fill="y")
        self.tree_barang.configure(yscrollcommand=sb2.set)

        # Bar bawah
        f_bot = tk.Frame(self.win, bg="#f0f0f0")
        f_bot.pack(fill="x", padx=10, pady=10)
        self.lbl_ringkas = tk.Label(f_bot, text="", bg="#f0f0f0",
                                    fg="#1a237e",
                                    font=("Segoe UI", 11, "bold"))
        self.lbl_ringkas.pack(side="left")
        tk.Button(f_bot, text="Tutup", command=self.close,
                  bg="#9E9E9E", fg="white", padx=15, pady=6,
                  font=("Segoe UI", 10, "bold")).pack(side="right")

    # ---------- mode ----------
    def mode_harian(self):
        tgl = datetime.now().strftime("%Y-%m-%d")
        self.e_dari.delete(0, tk.END); self.e_dari.insert(0, tgl)
        self.e_sampai.delete(0, tk.END); self.e_sampai.insert(0, tgl)
        self.terapkan()

    def mode_bulanan(self):
        now = datetime.now()
        awal = now.replace(day=1)
        akhir = (awal + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        self.e_dari.delete(0, tk.END); self.e_dari.insert(0, awal.strftime("%Y-%m-%d"))
        self.e_sampai.delete(0, tk.END); self.e_sampai.insert(0, akhir.strftime("%Y-%m-%d"))
        self.terapkan()

    def terapkan(self):
        dari = self.e_dari.get().strip()
        sampai = self.e_sampai.get().strip()
        try:
            datetime.strptime(dari, "%Y-%m-%d")
            datetime.strptime(sampai, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Format", "Tanggal harus YYYY-MM-DD.")
            return

        # Nota
        for r in self.tree_nota.get_children():
            self.tree_nota.delete(r)
        notas = laporan_penjualan(dari, sampai)
        total_all = 0
        diskon_all = 0
        for n in notas:
            self.tree_nota.insert("", "end", values=(
                n["no_nota"], n["tanggal"][:19], n["kasir"],
                f"{n['subtotal']:,.0f}", f"{n['diskon']:,.0f}",
                f"{n['total']:,.0f}"
            ))
            total_all += n["total"]
            diskon_all += n["diskon"]

        # Ringkasan barang
        for r in self.tree_barang.get_children():
            self.tree_barang.delete(r)
        for b in laporan_ringkasan_barang(dari, sampai):
            self.tree_barang.insert("", "end", values=(
                b["kode"], b["nama"], b["total_qty"], f"{b['total_rp']:,.0f}"
            ))

        self.lbl_ringkas.config(
            text=(f"Periode: {dari} s/d {sampai}  |  "
                  f"Jumlah nota: {len(notas)}  |  "
                  f"Total diskon: Rp {diskon_all:,.0f}  |  "
                  f"Total penjualan: Rp {total_all:,.0f}")
        )

    def lihat_detail(self, event):
        sel = self.tree_nota.selection()
        if not sel:
            return
        no_nota = self.tree_nota.item(sel[0], "values")[0]
        details = laporan_detail(no_nota)

        w = tk.Toplevel(self.win)
        w.title(f"Detail Nota {no_nota}")
        w.geometry("650x400")
        t = ttk.Treeview(w, columns=("kode", "nama", "harga", "qty", "subtotal"),
                         show="headings")
        for c, txt, wd in [("kode", "Kode", 80), ("nama", "Nama", 250),
                           ("harga", "Harga", 100), ("qty", "Qty", 60),
                           ("subtotal", "Subtotal", 120)]:
            t.heading(c, text=txt)
            t.column(c, width=wd)
        for d in details:
            t.insert("", "end", values=(d["kode"], d["nama"],
                                        f"{d['harga']:,.0f}", d["qty"],
                                        f"{d['subtotal']:,.0f}"))
        t.pack(fill="both", expand=True, padx=10, pady=10)

    def close(self):
        self.win.destroy()
        self.on_close()