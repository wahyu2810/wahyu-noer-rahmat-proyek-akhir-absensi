import os
import sys
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.model_absensi import Absensi, STATUS_OPTIONS
from views import theme as T
from controllers.controller_face import FaceController


class MahasiswaDashboard:
    """Dashboard mahasiswa: absen masuk/pulang sederhana + rekap pribadi."""

    def __init__(self, master=None, user=None, on_logout=None):
        self.master = master or tk.Tk()
        self.user = user or {}
        self.on_logout = on_logout

        self.master.title("Sistem Absensi  •  Dashboard Mahasiswa  </>")
        self.master.configure(bg=T.COLOR_BG)
        self.master.resizable(False, False)
        T.center_window(self.master, 900, 700)

        Absensi.create_table()
        self.student_name = (
            self.user.get("nama") or self.user.get("username") or "Wahyu Noer Rahmat"
        )

        self._is_building = True
        self._tree_style = T.style_treeview()
        self._combo_style = T.style_combobox(self.master)
        self._build_ui()
        self._is_building = False
        self._refresh()
        self._update_face_status()

    # ------------------------------------------------------------------- build
    def _build_ui(self):
        container = tk.Frame(self.master, bg=T.COLOR_BG)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        self._build_header(container)

        body = tk.Frame(container, bg=T.COLOR_BG)
        body.pack(fill="both", expand=True)

        self._build_today_card(body)
        self._build_absen_panel(body)
        self._build_simulation_panel(body)
        self._build_table(body)
        self._build_summary(container)

    def _build_today_card(self, parent):
        card = tk.Frame(parent, bg=T.COLOR_PANEL, highlightthickness=1,
                        highlightbackground=T.COLOR_BORDER)
        card.pack(fill="x", pady=(0, 14))

        inner = tk.Frame(card, bg=T.COLOR_PANEL)
        inner.pack(fill="x", padx=16, pady=14)

        self.greet_label = tk.Label(
            inner, text="", font=("Segoe UI", 14, "bold"),
            fg=T.COLOR_TEXT, bg=T.COLOR_PANEL, anchor="w",
        )
        self.greet_label.pack(fill="x")

        stats = tk.Frame(inner, bg=T.COLOR_PANEL)
        stats.pack(fill="x", pady=(12, 0))
        self.stat_masuk = self._make_stat(stats, "JAM MASUK")
        self.stat_pulang = self._make_stat(stats, "JAM PULANG")
        self.stat_status = self._make_stat(stats, "STATUS HARI INI")

    def _make_stat(self, parent, title):
        block = tk.Frame(parent, bg=T.COLOR_PANEL)
        block.pack(side="left", padx=(0, 44))
        tk.Label(
            block, text=title, font=(T.MONO, 8, "bold"),
            fg=T.COLOR_MUTED, bg=T.COLOR_PANEL, anchor="w",
        ).pack(fill="x")
        value = tk.Label(
            block, text="—", font=(T.MONO, 16, "bold"),
            fg=T.COLOR_ACCENT, bg=T.COLOR_PANEL, anchor="w",
        )
        value.pack(fill="x")
        return value

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=T.COLOR_BG)
        header.pack(fill="x", pady=(0, 16))

        top = tk.Frame(header, bg=T.COLOR_BG)
        top.pack(fill="x")

        tk.Label(
            top, text="</>", font=(T.MONO, 22, "bold"),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG,
        ).pack(side="left")
        tk.Label(
            top, text="  Dashboard Mahasiswa", font=("Segoe UI", 17, "bold"),
            fg=T.COLOR_TEXT, bg=T.COLOR_BG,
        ).pack(side="left")

        T.make_button(top, "⏻  logout", self.logout, primary=False).pack(side="right")

        # Jam digital — diperbarui setiap detik
        self.clock_label = tk.Label(
            top, text="", font=(T.MONO, 12, "bold"),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG,
        )
        self.clock_label.pack(side="right", padx=(0, 18))
        self._update_clock()

        nim = self.user.get("nim") or "23260033"
        prodi = self.user.get("prodi") or "Teknik Informatika"
        tk.Label(
            header, text=f"$ whoami  →  {self.student_name}", font=(T.MONO, 11),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(14, 2))
        tk.Label(
            header, text=f"# NIM: {nim}   •   Prodi: {prodi}",
            font=(T.MONO, 10), fg=T.COLOR_TEXT, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(0, 2))
        tk.Label(
            header, text="// Absen kehadiran & lihat rekap pribadi",
            font=(T.MONO, 10), fg=T.COLOR_MUTED, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x")

    def _update_clock(self):
        """Perbarui label jam digital setiap detik."""
        if not self.clock_label.winfo_exists():
            return
        from models.simulation_state import get_current_time, use_simulation
        import models.simulation_state as sim
        
        now = get_current_time()
        if use_simulation:
            # Increment simulated time by 1 second
            new_time = now + timedelta(seconds=1)
            sim.simulated_hour = new_time.hour
            sim.simulated_minute = new_time.minute
            sim.simulated_second = new_time.second
            now = new_time

        hari = ["Senin", "Selasa", "Rabu", "Kamis",
                "Jumat", "Sabtu", "Minggu"][now.weekday()]
        bulan = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                 "Jul", "Agu", "Sep", "Okt", "Nov", "Des"][now.month]
        teks = f"🕐 {hari}, {now.day:02d} {bulan} {now.year}  {now:%H:%M:%S}"
        if use_simulation:
            teks += " (SIMULASI)"
        self.clock_label.config(text=teks)
        self.master.after(1000, self._update_clock)

    def _build_absen_panel(self, parent):
        panel = tk.Frame(parent, bg=T.COLOR_BG, highlightthickness=1,
                         highlightbackground=T.COLOR_BORDER)
        panel.pack(fill="x", pady=(0, 14))

        tk.Label(
            panel, text=f"# absen hari ini  •  {self._today()}",
            font=(T.MONO, 10, "bold"), fg=T.COLOR_ACCENT, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 8))

        # Row 1: Pengiriman keterangan Izin/Sakit
        row_izin = tk.Frame(panel, bg=T.COLOR_BG)
        row_izin.pack(fill="x", padx=14, pady=(0, 10))

        tk.Label(
            row_izin, text="Keterangan Izin/Sakit:", font=(T.MONO, 10),
            fg=T.COLOR_MUTED, bg=T.COLOR_BG,
        ).pack(side="left")

        self.keterangan_var = tk.StringVar()
        self.entry_keterangan = tk.Entry(
            row_izin, textvariable=self.keterangan_var, font=(T.MONO, 10), width=35,
            bg=T.COLOR_FIELD, fg=T.COLOR_TEXT, relief="flat", bd=0,
            insertbackground=T.COLOR_ACCENT,
            highlightthickness=1, highlightbackground=T.COLOR_BORDER,
            highlightcolor=T.COLOR_ACCENT,
        )
        self.entry_keterangan.pack(side="left", padx=(8, 0), ipady=3)

        self.btn_izin = T.make_button(row_izin, "✉ Kirim Izin/Sakit", self._submit_izin, primary=False)
        self.btn_izin.pack(side="left", padx=(8, 0))

        # Row 2: Absensi Utama & Registrasi Wajah
        row_absen = tk.Frame(panel, bg=T.COLOR_BG)
        row_absen.pack(fill="x", padx=14, pady=(0, 14))

        # Registrasi Wajah di sebelah kiri
        face_frame = tk.Frame(row_absen, bg=T.COLOR_BG)
        face_frame.pack(side="left")

        self.btn_register_face = T.make_button(
            face_frame, "📷 Daftar Wajah", self._register_face, primary=False
        )
        self.btn_register_face.pack(side="left")

        self.face_status_label = tk.Label(
            face_frame, text="", font=(T.MONO, 10, "bold"), bg=T.COLOR_BG
        )
        self.face_status_label.pack(side="left", padx=(8, 0))

        # Tombol Absen di sebelah kanan
        self.btn_pulang = T.make_button(row_absen, "➜  Pulang", self._absen_pulang, primary=False)
        self.btn_pulang.pack(side="right")
        self.btn_masuk = T.make_button(row_absen, "●  Masuk", self._absen_masuk, primary=True)
        self.btn_masuk.pack(side="right", padx=(0, 8))

    def _build_table(self, parent):
        editor = tk.Frame(parent, bg=T.COLOR_BG, highlightthickness=1,
                          highlightbackground=T.COLOR_BORDER)
        editor.pack(fill="both", expand=True)

        T.make_title_bar(editor, "riwayat_absen_saya.csv")

        tree_frame = tk.Frame(editor, bg=T.COLOR_PANEL)
        tree_frame.pack(fill="both", expand=True)

        columns = ("tanggal", "jam_masuk", "jam_keluar", "status")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings",
            height=8, selectmode="none", style=self._tree_style,
        )
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=140, anchor="w")
        self.tree.column("status", width=120, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview,
            style="Coding.Vertical.TScrollbar",
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("odd", background=T.COLOR_PANEL)
        self.tree.tag_configure("even", background="#1b212a")
        for status, color in T.STATUS_COLORS.items():
            self.tree.tag_configure(f"st_{status}", foreground=color)

    def _build_summary(self, parent):
        footer = tk.Frame(parent, bg=T.COLOR_BG)
        footer.pack(fill="x", pady=(16, 0))

        self.summary_label = tk.Label(
            footer, text="", font=(T.MONO, 10, "bold"),
            fg=T.COLOR_TEXT, bg=T.COLOR_BG, anchor="w", justify="left",
        )
        self.summary_label.pack(side="left")

        T.make_button(footer, "↻  segarkan", self._refresh, primary=False).pack(side="right")

    # ------------------------------------------------------------------- logic
    def _greeting(self):
        hour = datetime.now().hour
        if hour < 11:
            sapaan = "Selamat pagi"
        elif hour < 15:
            sapaan = "Selamat siang"
        elif hour < 19:
            sapaan = "Selamat sore"
        else:
            sapaan = "Selamat malam"
        first = self.student_name.split()[0] if self.student_name else "Mahasiswa"
        return f"{sapaan}, {first}! \U0001f44b"

    def _today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def _now_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _find_today(self):
        """Cari record absen milik mahasiswa ini untuk hari ini (atau None)."""
        today = self._today()
        for record in Absensi.for_nama(self.student_name):
            if record.tanggal == today:
                return record
        return None

    def _register_face(self):
        user_id = self.user.get("id")
        name = self.student_name
        success = FaceController.register_face(user_id, name)
        if success:
            self._update_face_status()

    def _update_face_status(self):
        user_id = self.user.get("id")
        if FaceController.is_face_registered(user_id):
            self.face_status_label.config(text="● Terdaftar", fg="#27c93f")
            self.btn_register_face.config(text="📷 Update Wajah")
        else:
            self.face_status_label.config(text="○ Belum Terdaftar", fg="#ff5f56")
            self.btn_register_face.config(text="📷 Daftar Wajah")

    def _submit_izin(self):
        ket = self.keterangan_var.get().strip()
        if not ket:
            messagebox.showwarning("Kirim Izin/Sakit", "Silakan isi alasan/keterangan izin atau sakit terlebih dahulu.")
            return
            
        record = self._find_today()
        if record:
            if record.jam_masuk and record.status == "Hadir":
                messagebox.showwarning("Kirim Izin/Sakit", "Anda sudah tercatat Hadir hari ini, tidak bisa mengubah ke status Izin.")
                return
            record.status = "Izin"
            record.keterangan = ket
            record.save()
        else:
            record = Absensi(
                nama=self.student_name, kelas="", tanggal=self._today(),
                jam_masuk="", jam_keluar="",
                status="Izin", keterangan=ket,
                latitude="", longitude=""
            )
            record.save()
            
        messagebox.showinfo("Kirim Izin/Sakit", f"Keterangan izin/sakit berhasil dikirim:\n\"{ket}\"")
        self.keterangan_var.set("")
        self._refresh()

    def _absen_masuk(self):
        user_id = self.user.get("id")
        if not FaceController.is_face_registered(user_id):
            messagebox.showwarning(
                "Absen Masuk", "Anda belum mendaftarkan wajah. Harap daftarkan wajah Anda terlebih dahulu."
            )
            return

        if not FaceController.verify_face(user_id, self.student_name):
            return

        from models.simulation_state import get_current_location, get_current_time
        lat, lon = get_current_location()
        
        # Hitung jarak ke UNU Indonesia Kampus B
        CAMPUS_LAT = -6.490333
        CAMPUS_LON = 106.731667
        dist = Absensi.calculate_distance(lat, lon, CAMPUS_LAT, CAMPUS_LON)
        
        now = get_current_time()
        now_str = now.strftime("%H:%M:%S")
        
        # Penentuan status otomatis sepenuhnya
        if dist <= 100.0:
            if now.time() <= datetime.time(9, 40):
                status = "Hadir"
            elif now.time() <= datetime.time(9, 55):
                status = "Terlambat"
            else:
                status = "Alfa"
            keterangan = ""
        else:
            if now.time() <= datetime.time(9, 55):
                status = "Terlambat"
            else:
                status = "Alfa"
            keterangan = "diluar area kampus"

        record = self._find_today()
        
        # Jika mahasiswa sudah izin, tanyakan konfirmasi
        if record and record.status == "Izin":
            if not messagebox.askyesno("Absen Masuk", "Anda sudah mengisi keterangan izin/sakit hari ini. Ubah menjadi absen masuk?"):
                return

        if record:
            record.jam_masuk = now_str
            record.status = status
            record.keterangan = keterangan
            record.latitude = str(lat)
            record.longitude = str(lon)
            record.save()
            messagebox.showinfo(
                "Absen Masuk",
                f"Absen masuk berhasil ({status}).\nKeterangan: {keterangan or 'di dalam area kampus'}",
            )
        else:
            record = Absensi(
                nama=self.student_name, kelas="", tanggal=self._today(),
                jam_masuk=now_str, jam_keluar="",
                status=status, keterangan=keterangan,
                latitude=str(lat), longitude=str(lon)
            )
            record.save()
            messagebox.showinfo(
                "Absen Masuk",
                f"Absen masuk berhasil ({status}).\nKeterangan: {keterangan or 'di dalam area kampus'}",
            )
        self._refresh()

    def _absen_pulang(self):
        user_id = self.user.get("id")
        if not FaceController.is_face_registered(user_id):
            messagebox.showwarning(
                "Absen Pulang", "Anda belum mendaftarkan wajah. Harap daftarkan wajah Anda terlebih dahulu."
            )
            return

        if not FaceController.verify_face(user_id, self.student_name):
            return

        from models.simulation_state import get_current_location, get_current_time
        lat, lon = get_current_location()
        now = get_current_time()
        now_str = now.strftime("%H:%M:%S")

        record = self._find_today()
        if not record:
            messagebox.showwarning(
                "Absen Pulang", "Anda belum absen masuk hari ini."
            )
            return
        if record.jam_keluar and not messagebox.askyesno(
            "Absen Pulang",
            f"Sudah absen pulang pukul {record.jam_keluar}. Perbarui?",
        ):
            return
        record.jam_keluar = now_str
        record.latitude = str(lat)
        record.longitude = str(lon)
        record.save()
        messagebox.showinfo(
            "Absen Pulang", f"Absen pulang tercatat pukul {record.jam_keluar}."
        )
        self._refresh()

    def _refresh(self):
        """Muat ulang riwayat & ringkasan — HANYA milik mahasiswa ini."""
        Absensi.auto_update_absensi()
        records = Absensi.for_nama(self.student_name)
        records.sort(key=lambda r: (r.tanggal or "", r.jam_masuk or ""), reverse=True)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, record in enumerate(records):
            bg_tag = "even" if idx % 2 == 0 else "odd"
            status = (record.status or "").capitalize()
            st_tag = f"st_{status}" if status in T.STATUS_COLORS else "odd"
            
            # Tampilkan keterangan lokasi jika di luar kampus
            ket = record.keterangan or ""
            val_status = status
            if ket == "diluar area kampus":
                val_status = f"{status} (Luar Kampus)"
            
            self.tree.insert("", tk.END, values=(
                record.tanggal, record.jam_masuk or "-",
                record.jam_keluar or "-", val_status,
            ), tags=(bg_tag, st_tag))

        self._update_today_card()
        self._update_summary(records)

    def _update_today_card(self):
        """Perbarui kartu status hari ini + aktif/nonaktif tombol."""
        self.greet_label.config(text=self._greeting())
        record = self._find_today()

        masuk = record.jam_masuk if record else ""
        self.stat_masuk.config(
            text=masuk or "belum",
            fg=T.COLOR_ACCENT if masuk else T.COLOR_MUTED,
        )
        pulang = record.jam_keluar if record else ""
        self.stat_pulang.config(
            text=pulang or "belum",
            fg=T.COLOR_ACCENT if pulang else T.COLOR_MUTED,
        )
        status = (record.status or "").capitalize() if record else ""
        self.stat_status.config(
            text=status or "—",
            fg=T.STATUS_COLORS.get(status, T.COLOR_MUTED),
        )

        # Tombol Pulang hanya aktif jika sudah absen masuk hari ini.
        self.btn_pulang.config(state="normal" if masuk else "disabled")

    def _update_summary(self, records):
        masuk = sum(1 for r in records if r.jam_masuk)
        pulang = sum(1 for r in records if r.jam_keluar)
        per_status = {s: 0 for s in STATUS_OPTIONS}
        for r in records:
            s = (r.status or "").capitalize()
            per_status[s] = per_status.get(s, 0) + 1
        rincian = "   ".join(f"{s}: {per_status.get(s, 0)}" for s in STATUS_OPTIONS)
        self.summary_label.config(
            text=(f"# kehadiran saya  →  Masuk: {masuk}   Pulang: {pulang}"
                  f"      {rincian}")
        )

    def _build_simulation_panel(self, parent):
        panel = tk.LabelFrame(
            parent, text=" [ PANEL SIMULASI & TESTING ] ",
            font=(T.MONO, 10, "bold"), fg=T.COLOR_ACCENT, bg=T.COLOR_BG,
            highlightthickness=1, highlightbackground=T.COLOR_BORDER,
            padx=14, pady=10, relief="flat"
        )
        panel.pack(fill="x", pady=(0, 14))

        # Baris 1: Status Simulasi & Preset Lokasi
        row1 = tk.Frame(panel, bg=T.COLOR_BG)
        row1.pack(fill="x", pady=(0, 6))

        import models.simulation_state as sim

        self.sim_enabled_var = tk.BooleanVar(value=sim.use_simulation)
        chk = tk.Checkbutton(
            row1, text="Aktifkan Simulasi", variable=self.sim_enabled_var,
            command=self._on_toggle_simulation, font=(T.MONO, 10),
            bg=T.COLOR_BG, fg=T.COLOR_TEXT, selectcolor=T.COLOR_PANEL,
            activebackground=T.COLOR_BG, activeforeground=T.COLOR_TEXT,
        )
        chk.pack(side="left")

        tk.Label(
            row1, text="  |  Lokasi Mock:", font=(T.MONO, 10),
            fg=T.COLOR_MUTED, bg=T.COLOR_BG
        ).pack(side="left")

        self.sim_loc_var = tk.StringVar(value="Dalam Kampus")
        loc_combo = ttk.Combobox(
            row1, values=["Dalam Kampus", "Luar Kampus (Stasiun Bogor)", "Custom Koordinat"],
            state="readonly", font=(T.MONO, 9), width=22, style=self._combo_style,
            textvariable=self.sim_loc_var
        )
        loc_combo.pack(side="left", padx=(8, 0))
        loc_combo.bind("<<ComboboxSelected>>", self._on_change_sim_loc)

        self.sim_lat_var = tk.StringVar(value=str(sim.simulated_lat))
        self.sim_lon_var = tk.StringVar(value=str(sim.simulated_lon))

        self.lbl_lat = tk.Label(row1, text=" Lat:", font=(T.MONO, 9), fg=T.COLOR_MUTED, bg=T.COLOR_BG)
        self.lbl_lat.pack(side="left", padx=(10, 0))
        self.ent_lat = tk.Entry(
            row1, textvariable=self.sim_lat_var, font=(T.MONO, 9), width=10,
            bg=T.COLOR_FIELD, fg=T.COLOR_TEXT, relief="flat", highlightthickness=1,
            highlightbackground=T.COLOR_BORDER, highlightcolor=T.COLOR_ACCENT
        )
        self.ent_lat.pack(side="left", padx=(4, 0))

        self.lbl_lon = tk.Label(row1, text=" Lon:", font=(T.MONO, 9), fg=T.COLOR_MUTED, bg=T.COLOR_BG)
        self.lbl_lon.pack(side="left", padx=(10, 0))
        self.ent_lon = tk.Entry(
            row1, textvariable=self.sim_lon_var, font=(T.MONO, 9), width=10,
            bg=T.COLOR_FIELD, fg=T.COLOR_TEXT, relief="flat", highlightthickness=1,
            highlightbackground=T.COLOR_BORDER, highlightcolor=T.COLOR_ACCENT
        )
        self.ent_lon.pack(side="left", padx=(4, 0))

        # Baris 2: Preset Waktu & Waktu Custom
        row2 = tk.Frame(panel, bg=T.COLOR_BG)
        row2.pack(fill="x")

        tk.Label(
            row2, text="Waktu Mock:", font=(T.MONO, 10),
            fg=T.COLOR_MUTED, bg=T.COLOR_BG
        ).pack(side="left")

        self.sim_time_preset_var = tk.StringVar(value="Sebelum (09:30)")
        time_combo = ttk.Combobox(
            row2, values=["Sebelum (09:30)", "Terlambat (09:45)", "Alfa (10:00)", "Custom Jam"],
            state="readonly", font=(T.MONO, 9), width=18, style=self._combo_style,
            textvariable=self.sim_time_preset_var
        )
        time_combo.pack(side="left", padx=(8, 18))
        time_combo.bind("<<ComboboxSelected>>", self._on_change_sim_time)

        self.sim_hour_var = tk.StringVar(value="09")
        self.sim_min_var = tk.StringVar(value="30")

        self.lbl_hour = tk.Label(row2, text="Jam (HH:MM):", font=(T.MONO, 9), fg=T.COLOR_MUTED, bg=T.COLOR_BG)
        self.lbl_hour.pack(side="left")
        self.ent_hour = tk.Entry(
            row2, textvariable=self.sim_hour_var, font=(T.MONO, 9), width=3,
            bg=T.COLOR_FIELD, fg=T.COLOR_TEXT, relief="flat", highlightthickness=1,
            highlightbackground=T.COLOR_BORDER, highlightcolor=T.COLOR_ACCENT, justify="center"
        )
        self.ent_hour.pack(side="left", padx=(4, 0))

        tk.Label(row2, text=":", font=(T.MONO, 9, "bold"), fg=T.COLOR_TEXT, bg=T.COLOR_BG).pack(side="left", padx=2)

        self.ent_min = tk.Entry(
            row2, textvariable=self.sim_min_var, font=(T.MONO, 9), width=3,
            bg=T.COLOR_FIELD, fg=T.COLOR_TEXT, relief="flat", highlightthickness=1,
            highlightbackground=T.COLOR_BORDER, highlightcolor=T.COLOR_ACCENT, justify="center"
        )
        self.ent_min.pack(side="left")

        # Sync keadaan awal
        self._on_toggle_simulation()
        self._on_change_sim_loc()
        self._on_change_sim_time()

        # Listeners
        self.sim_lat_var.trace_add("write", self._update_sim_coords)
        self.sim_lon_var.trace_add("write", self._update_sim_coords)
        self.sim_hour_var.trace_add("write", self._update_sim_time_from_entries)
        self.sim_min_var.trace_add("write", self._update_sim_time_from_entries)

    def _on_toggle_simulation(self):
        import models.simulation_state as sim
        sim.use_simulation = self.sim_enabled_var.get()
        state = "normal" if sim.use_simulation else "disabled"
        
        self.lbl_lat.config(fg=T.COLOR_TEXT if sim.use_simulation else T.COLOR_MUTED)
        self.lbl_lon.config(fg=T.COLOR_TEXT if sim.use_simulation else T.COLOR_MUTED)
        self.lbl_hour.config(fg=T.COLOR_TEXT if sim.use_simulation else T.COLOR_MUTED)
        
        self.ent_lat.config(state=state)
        self.ent_lon.config(state=state)
        self.ent_hour.config(state=state)
        self.ent_min.config(state=state)
        
        if not getattr(self, "_is_building", False):
            self._refresh()

    def _on_change_sim_loc(self, event=None):
        sel = self.sim_loc_var.get()
        if sel == "Dalam Kampus":
            self.sim_lat_var.set("-6.490333")
            self.sim_lon_var.set("106.731667")
            self.ent_lat.config(state="disabled")
            self.ent_lon.config(state="disabled")
        elif sel == "Luar Kampus (Stasiun Bogor)":
            self.sim_lat_var.set("-6.5944")
            self.sim_lon_var.set("106.7894")
            self.ent_lat.config(state="disabled")
            self.ent_lon.config(state="disabled")
        else:
            if self.sim_enabled_var.get():
                self.ent_lat.config(state="normal")
                self.ent_lon.config(state="normal")
        self._update_sim_coords()

    def _update_sim_coords(self, *args):
        import models.simulation_state as sim
        try:
            sim.simulated_lat = float(self.sim_lat_var.get())
            sim.simulated_lon = float(self.sim_lon_var.get())
        except ValueError:
            pass

    def _on_change_sim_time(self, event=None):
        sel = self.sim_time_preset_var.get()
        if sel == "Sebelum (09:30)":
            self.sim_hour_var.set("09")
            self.sim_min_var.set("30")
            self.ent_hour.config(state="disabled")
            self.ent_min.config(state="disabled")
        elif sel == "Terlambat (09:45)":
            self.sim_hour_var.set("09")
            self.sim_min_var.set("45")
            self.ent_hour.config(state="disabled")
            self.ent_min.config(state="disabled")
        elif sel == "Alfa (10:00)":
            self.sim_hour_var.set("10")
            self.sim_min_var.set("00")
            self.ent_hour.config(state="disabled")
            self.ent_min.config(state="disabled")
        else:
            if self.sim_enabled_var.get():
                self.ent_hour.config(state="normal")
                self.ent_min.config(state="normal")
        self._update_sim_time_from_entries()

    def _update_sim_time_from_entries(self, *args):
        import models.simulation_state as sim
        try:
            h = int(self.sim_hour_var.get())
            m = int(self.sim_min_var.get())
            if 0 <= h < 24 and 0 <= m < 60:
                sim.simulated_hour = h
                sim.simulated_minute = m
                sim.simulated_second = 0
        except ValueError:
            pass

    def logout(self):
        if self.on_logout:
            self.on_logout()
        else:
            self.master.destroy()

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    MahasiswaDashboard().run()
