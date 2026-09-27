"""Window login."""
import tkinter as tk
from tkinter import messagebox
from database import cek_login


def show_login(root, on_success):
    """Tampilkan window login. on_success(user_dict) dipanggil jika sukses."""
    win = tk.Toplevel(root)
    win.title("Login - Abadi Minimarket")
    win.geometry("360x280")
    win.configure(bg="#1a237e")
    win.resizable(False, False)
    win.grab_set()

    # Center
    win.update_idletasks()
    x = (win.winfo_screenwidth() - 360) // 2
    y = (win.winfo_screenheight() - 280) // 2
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text="ABADI MINIMARKET",
             bg="#1a237e", fg="white",
             font=("Segoe UI", 16, "bold")).pack(pady=(25, 5))

    tk.Label(win, text="Silakan Login",
             bg="#1a237e", fg="#cfd8dc",
             font=("Segoe UI", 10)).pack(pady=(0, 15))

    frame = tk.Frame(win, bg="white", padx=20, pady=20)
    frame.pack(padx=20, fill="x")

    tk.Label(frame, text="Username:", bg="white",
             font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=4)
    e_user = tk.Entry(frame, font=("Segoe UI", 11), width=20)
    e_user.grid(row=0, column=1, padx=5, pady=4)
    e_user.focus()

    tk.Label(frame, text="Password:", bg="white",
             font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=4)
    e_pass = tk.Entry(frame, font=("Segoe UI", 11), width=20, show="*")
    e_pass.grid(row=1, column=1, padx=5, pady=4)

    def do_login(event=None):
        u = e_user.get().strip()
        p = e_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Login", "Isi username & password.")
            return
        user = cek_login(u, p)
        if user:
            win.destroy()
            on_success(user)
        else:
            messagebox.showerror("Login Gagal", "Username/password salah.")
            e_pass.delete(0, tk.END)
            e_pass.focus()

    e_user.bind("<Return>", lambda e: e_pass.focus())
    e_pass.bind("<Return>", do_login)

    tk.Button(frame, text="LOGIN", command=do_login,
              bg="#4CAF50", fg="white",
              font=("Segoe UI", 10, "bold"),
              padx=20, pady=6).grid(row=2, column=0, columnspan=2, pady=(12, 0))

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), root.destroy()))