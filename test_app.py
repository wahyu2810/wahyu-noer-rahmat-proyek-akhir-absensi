import tkinter as tk
from tkinter import messagebox
import sqlite3
from PIL import Image
# Inisialisasi Jendela Utama
root = tk.Tk()
root.title("Sanity Check - Sistem Absensi")
root.geometry("400x200")
# Fungsi Testing Sederhana
def cek_sistem():
    messagebox.showinfo("Sukses", "Environment Python, Tkinter, SQLite3 & Pillow Siap!")
# Komponen UI Dasar
btn_test = tk.Button(root, text="Uji Kesiapan Tools", command=cek_sistem)
btn_test.pack(padx=10, pady=10)
btn_test.pack(expand=True)
# Menjaga Aplikasi Tetap Berjalan
root.mainloop()