"""Setup dan operasi database SQLite."""
import sqlite3
import os
from datetime import datetime

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kasir.db")


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role     TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS barang (
            kode   TEXT PRIMARY KEY,
            nama   TEXT NOT NULL,
            harga  REAL NOT NULL,
            stok   INTEGER NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stok_masuk (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal   TEXT NOT NULL,
            kode      TEXT NOT NULL,
            qty       INTEGER NOT NULL,
            keterangan TEXT,
            user      TEXT,
            FOREIGN KEY (kode) REFERENCES barang(kode)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS penjualan (
            no_nota    TEXT PRIMARY KEY,
            tanggal    TEXT NOT NULL,
            kasir      TEXT NOT NULL,
            subtotal   REAL NOT NULL,
            diskon     REAL NOT NULL DEFAULT 0,
            total      REAL NOT NULL,
            bayar      REAL NOT NULL,
            kembali    REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS penjualan_detail (
            no_nota     TEXT NOT NULL,
            kode        TEXT NOT NULL,
            nama        TEXT NOT NULL,
            harga       REAL NOT NULL,
            qty         INTEGER NOT NULL,
            subtotal    REAL NOT NULL,
            PRIMARY KEY (no_nota, kode),
            FOREIGN KEY (no_nota) REFERENCES penjualan(no_nota),
            FOREIGN KEY (kode)    REFERENCES barang(kode)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS no_nota_seq (
            tanggal TEXT PRIMARY KEY,
            counter INTEGER NOT NULL
        )
    """)

    # Seed user default
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO users VALUES (?, ?, ?)", [
            ("admin", "4123", "admin"),
            ("kasir", "kasir", "kasir"),
        ])

    # Seed barang contoh
    cur.execute("SELECT COUNT(*) FROM barang")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO barang VALUES (?, ?, ?, ?)", [
            ("B001", "Beras Premium 5kg", 65000, 50),
            ("B002", "Minyak Goreng 2L",  32000, 30),
            ("B003", "Gula Pasir 1kg",    15000, 100),
            ("B004", "Telur Ayam 1kg",    28000, 25),
            ("B005", "Tepung Terigu 1kg", 12000, 75),
        ])

    conn.commit()
    conn.close()


# ---------- USER ----------
def cek_login(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------- BARANG ----------
def get_all_barang(keyword=""):
    conn = get_conn()
    if keyword:
        rows = conn.execute("""
            SELECT * FROM barang
            WHERE kode LIKE ? OR nama LIKE ?
            ORDER BY kode
        """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
    else:
        rows = conn.execute("SELECT * FROM barang ORDER BY kode").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_barang(kode):
    conn = get_conn()
    row = conn.execute("SELECT * FROM barang WHERE kode = ?", (kode,)).fetchone()
    conn.close()
    return dict(row) if row else None


def tambah_barang(kode, nama, harga, stok_awal, user):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO barang VALUES (?, ?, ?, ?)",
                     (kode, nama, harga, stok_awal))
        if stok_awal > 0:
            conn.execute("""
                INSERT INTO stok_masuk (tanggal, kode, qty, keterangan, user)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(timespec="seconds"),
                  kode, stok_awal, "Stok awal", user))
        conn.commit()
        return True, "Barang berhasil ditambahkan."
    except sqlite3.IntegrityError:
        return False, f"Kode '{kode}' sudah ada."
    finally:
        conn.close()


def update_barang(kode, nama, harga):
    conn = get_conn()
    conn.execute("UPDATE barang SET nama=?, harga=? WHERE kode=?",
                 (nama, harga, kode))
    conn.commit()
    conn.close()


def hapus_barang(kode):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM barang WHERE kode = ?", (kode,))
        conn.commit()
        return True, "Barang dihapus."
    except sqlite3.IntegrityError:
        return False, "Barang tidak bisa dihapus (sudah dipakai transaksi)."
    finally:
        conn.close()


# ---------- STOK ----------
def tambah_stok(kode, qty, keterangan, user):
    conn = get_conn()
    barang = conn.execute("SELECT * FROM barang WHERE kode=?", (kode,)).fetchone()
    if not barang:
        conn.close()
        return False, "Barang tidak ditemukan."
    conn.execute("UPDATE barang SET stok = stok + ? WHERE kode = ?", (qty, kode))
    conn.execute("""
        INSERT INTO stok_masuk (tanggal, kode, qty, keterangan, user)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(timespec="seconds"),
          kode, qty, keterangan, user))
    conn.commit()
    conn.close()
    return True, f"Stok {barang['nama']} bertambah {qty}."


def get_stok_masuk(tgl_dari, tgl_sampai):
    conn = get_conn()
    rows = conn.execute("""
        SELECT sm.*, b.nama FROM stok_masuk sm
        JOIN barang b ON b.kode = sm.kode
        WHERE DATE(sm.tanggal) BETWEEN ? AND ?
        ORDER BY sm.tanggal DESC
    """, (tgl_dari, tgl_sampai)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- PENJUALAN ----------
def generate_no_nota():
    """Format: YYYYMMDD-NNN, counter reset tiap hari."""
    today = datetime.now().strftime("%Y%m%d")
    conn = get_conn()
    row = conn.execute("SELECT counter FROM no_nota_seq WHERE tanggal=?",
                       (today,)).fetchone()
    if row:
        counter = row["counter"] + 1
        conn.execute("UPDATE no_nota_seq SET counter=? WHERE tanggal=?",
                     (counter, today))
    else:
        counter = 1
        conn.execute("INSERT INTO no_nota_seq VALUES (?, ?)", (today, counter))
    conn.commit()
    conn.close()
    return f"{today}-{counter:03d}"


def simpan_penjualan(no_nota, kasir, items, subtotal, diskon, total, bayar, kembali):
    """items: list of dict {kode, nama, harga, qty, subtotal}"""
    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO penjualan
            (no_nota, tanggal, kasir, subtotal, diskon, total, bayar, kembali)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (no_nota, datetime.now().isoformat(timespec="seconds"),
              kasir, subtotal, diskon, total, bayar, kembali))

        for it in items:
            conn.execute("""
                INSERT INTO penjualan_detail
                (no_nota, kode, nama, harga, qty, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (no_nota, it["kode"], it["nama"],
                  it["harga"], it["qty"], it["subtotal"]))
            conn.execute("UPDATE barang SET stok = stok - ? WHERE kode = ?",
                         (it["qty"], it["kode"]))

        conn.commit()
        return True, "Transaksi tersimpan."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


# ---------- LAPORAN ----------
def laporan_penjualan(tgl_dari, tgl_sampai):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM penjualan
        WHERE DATE(tanggal) BETWEEN ? AND ?
        ORDER BY tanggal DESC
    """, (tgl_dari, tgl_sampai)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def laporan_detail(no_nota):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM penjualan_detail WHERE no_nota = ?
    """, (no_nota,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def laporan_ringkasan_barang(tgl_dari, tgl_sampai):
    conn = get_conn()
    rows = conn.execute("""
        SELECT pd.kode, pd.nama,
               SUM(pd.qty) AS total_qty,
               SUM(pd.subtotal) AS total_rp
        FROM penjualan_detail pd
        JOIN penjualan p ON p.no_nota = pd.no_nota
        WHERE DATE(p.tanggal) BETWEEN ? AND ?
        GROUP BY pd.kode, pd.nama
        ORDER BY total_qty DESC
    """, (tgl_dari, tgl_sampai)).fetchall()
    conn.close()
    return [dict(r) for r in rows]