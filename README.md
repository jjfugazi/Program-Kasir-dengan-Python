# 🛒 Kasir App - Abadi Minimarket

Aplikasi kasir (Point of Sale) sederhana berbasis **Python + Tkinter + SQLite**.
Dibuat untuk toko/minimarket kecil dengan fitur lengkap: multi-user, master barang,
stok masuk, penjualan dengan pencarian otomatis, diskon ber-otorisasi, dan laporan.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Fitur

### 👥 Multi-User
- **Admin** (username: `admin`, password: `4123`) — akses penuh semua menu
- **Kasir** (username: `kasir`, password: `kasir`) — hanya menu penjualan
- Logout & login ulang tanpa restart aplikasi

### 📦 Master Barang
- Tambah barang baru + stok awal
- Koreksi nama & harga barang
- Hapus barang (dengan proteksi jika sudah dipakai transaksi)

### ➕ Stok Masuk
- Tambah stok barang dengan keterangan
- Riwayat stok masuk harian

### 🛒 Penjualan (Kasir)
- Pencarian barang **real-time** saat mengetik kode/nama
- Keranjang transaksi dengan qty
- **Diskon saat pembayaran** — jika diisi > 0, butuh otorisasi password admin
- Perhitungan kembalian otomatis
- Struk ditampilkan setelah bayar

### 📊 Laporan
- **Harian** (default: hari ini)
- **Bulanan** (default: bulan ini)
- Custom range tanggal (YYYY-MM-DD)
- Dua tab: Daftar Nota & Ringkasan Barang
- Double-click nota untuk lihat detail item

### 🔢 Nomor Nota Otomatis
- Format: `YYYYMMDD-NNN` (reset tiap hari)
- Contoh: `20241125-001`, `20241125-002`
- Kunci transaksi: **no_nota + kode_barang**

---

## 📸 Screenshot

> Tambahkan screenshot Anda di folder `screenshots/` dan ganti path di bawah.

| Login | Menu Utama |
|---|---|
| ![Login](screenshots/login.png) | ![Menu](screenshots/menu.png) |

| Penjualan | Laporan |
|---|---|
| ![Penjualan](screenshots/penjualan.png) | ![Laporan](screenshots/laporan.png) |

---

## 🚀 Instalasi

### Prasyarat
- **Python 3.8+** ([download](https://www.python.org/downloads/))
- **Tkinter** (biasanya sudah bawaan)

### Linux (Debian/Ubuntu/Arch)
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-tk

# Arch
sudo pacman -S python tk
```

### Windows
Python dari python.org sudah menyertakan Tkinter. Tidak perlu install tambahan.

### macOS
```bash
brew install python-tk
```

---

## ▶️ Menjalankan

```bash
# 1. Clone repo
git clone https://github.com/USERNAME/kasir_app.git
cd kasir_app

# 2. Jalankan langsung (tidak perlu install apapun)
python3 kasir.py
```

Pada startup pertama, file `kasir.db` akan dibuat otomatis dan diisi 5 barang contoh.

---

## 🔑 Akun Default

| Username | Password | Role |
|---|---|---|
| `admin` | `4123` | Admin (full akses) |
| `kasir` | `kasir` | Kasir (hanya penjualan) |

> ⚠️ **Ganti password default** jika dipakai di produksi.
> (Fitur ganti password akan ditambahkan pada versi berikutnya.)

---

## 📖 Cara Pakai

### Alur Dasar
1. **Login** sebagai admin untuk setup awal
2. **Master Barang** → tambah barang yang akan dijual
3. **Stok Masuk** → tambah stok barang
4. **Logout**, login sebagai kasir
5. **Penjualan** → lakukan transaksi
6. **Login admin lagi** → lihat **Laporan**

### Tips Cepat
- Di menu Penjualan: ketik kode/nama barang → daftar muncul di bawah → klik/Enter untuk pilih
- Tekan **Enter** di field Qty untuk langsung tambah ke keranjang
- Klik **BAYAR** → isi diskon (opsional) → isi bayar → konfirmasi
- Jika kasir mengisi diskon > 0 → diminta password admin

---

## 🗄 Struktur Database

| Tabel | Isi |
|---|---|
| `users` | User & role |
| `barang` | Master barang |
| `stok_masuk` | Riwayat stok tambahan |
| `penjualan` | Header nota penjualan |
| `penjualan_detail` | Detail item per nota |
| `no_nota_seq` | Counter nomor nota harian |

Database menggunakan **SQLite** (file tunggal `kasir.db`), tidak perlu server.

---

## 🔄 Backup & Restore Database

**Backup:**
```bash
cp kasir.db kasir_backup_$(date +%Y%m%d).db
```

**Restore:**
```bash
cp kasir_backup_20241125.db kasir.db
```

**Reset (mulai dari nol):**
```bash
rm kasir.db
python3 kasir.py   # database baru dibuat otomatis
```

---

## 📂 Struktur Proyek

```
kasir_app/
├── kasir.py              # Entry point
├── database.py           # Semua operasi SQLite
├── login.py              # Window login
├── mainmenu.py           # Menu utama setelah login
├── master_barang.py      # CRUD master barang
├── stok.py               # Menu stok masuk
├── penjualan.py          # Menu transaksi penjualan
├── laporan.py            # Laporan harian & bulanan
├── .gitignore
└── README.md
```

---

## 🛠 Pengembangan

### Ide Fitur Selanjutnya
- [ ] Cetak struk ke printer thermal 58mm
- [ ] Export laporan ke CSV/Excel
- [ ] Grafik penjualan (matplotlib)
- [ ] Barcode scanner
- [ ] Manajemen user (tambah/hapus kasir)
- [ ] Backup otomatis harian
- [ ] Cetak PDF struk

### Kontribusi
Pull request selalu diterima. Untuk perubahan besar, buka issue dulu untuk diskusi.

---

## 📄 Lisensi

MIT License — bebas dipakai, dimodifikasi, dan didistribusikan.

---

## 🙏 Kredit

Dibuat sebagai proyek pembelajaran Python + Tkinter + SQLite.

Referensi:
- [Python Tkinter Docs](https://docs.python.org/3/library/tkinter.html)
- [SQLite Python](https://docs.python.org/3/library/sqlite3.html)
