#!/usr/bin/env python3
"""Entry point aplikasi kasir Abadi Minimarket."""
import tkinter as tk
from database import init_database
from login import show_login
from mainmenu import MainMenu


def main():
    init_database()

    root = tk.Tk()
    root.withdraw()  # sembunyikan root sampai login sukses

    def on_login_success(user):
        root.deiconify()
        MainMenu(root, user)

    show_login(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()