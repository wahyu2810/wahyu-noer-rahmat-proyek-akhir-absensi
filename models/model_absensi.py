import os
from dataclasses import dataclass
from typing import List, Optional

# Pilihan status kehadiran yang dipakai di seluruh aplikasi.
STATUS_OPTIONS = ["Hadir", "Izin", "Alfa", "Terlambat", "Belum Absen"]


@dataclass
class Absensi:
    id: Optional[int] = None
    nama: str = ''
    kelas: str = ''
    tanggal: str = ''
    jam_masuk: str = ''
    jam_keluar: str = ''
    status: str = ''
    keterangan: str = ''
    latitude: str = ''
    longitude: str = ''

    @staticmethod
    def _connect(db_path: Optional[str] = None):
        from database import get_connection
        return get_connection()

    @classmethod
    def create_table(cls, db_path: Optional[str] = None) -> None:
        conn = cls._connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS absensi (
                id SERIAL PRIMARY KEY,
                nama VARCHAR(100) NOT NULL,
                kelas VARCHAR(50),
                tanggal VARCHAR(20) NOT NULL,
                jam_masuk VARCHAR(20),
                jam_keluar VARCHAR(20),
                status VARCHAR(50) DEFAULT 'Hadir',
                keterangan TEXT,
                latitude VARCHAR(50),
                longitude VARCHAR(50)
            )
            '''
        )
        conn.commit()
        conn.close()

    @classmethod
    def from_row(cls, row: dict) -> 'Absensi':
        # psycopg2 RealDictCursor row is already a dict
        data = dict(row)
        return cls(
            id=data.get('id'),
            nama=data.get('nama', ''),
            kelas=data.get('kelas', ''),
            tanggal=data.get('tanggal', ''),
            jam_masuk=data.get('jam_masuk', ''),
            jam_keluar=data.get('jam_keluar', ''),
            status=data.get('status', ''),
            keterangan=data.get('keterangan', ''),
            latitude=data.get('latitude', ''),
            longitude=data.get('longitude', ''),
        )

    @classmethod
    def all(cls, db_path: Optional[str] = None) -> List['Absensi']:
        conn = cls._connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM absensi')
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def for_nama(cls, nama: str, db_path: Optional[str] = None) -> List['Absensi']:
        """Ambil hanya record milik satu mahasiswa (cocokkan berdasar nama)."""
        target = (nama or '').strip().lower()
        return [r for r in cls.all(db_path)
                if (r.nama or '').strip().lower() == target]

    @classmethod
    def count_by_status(cls, db_path: Optional[str] = None) -> dict:
        """Hitung jumlah record per status, mis. {'Hadir': 3, 'Izin': 1, ...}."""
        counts = {status: 0 for status in STATUS_OPTIONS}
        for record in cls.all(db_path):
            status = (record.status or '').strip().capitalize()
            counts[status] = counts.get(status, 0) + 1
        return counts

    @classmethod
    def find_by_id(cls, record_id: int, db_path: Optional[str] = None) -> Optional['Absensi']:
        conn = cls._connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM absensi WHERE id = %s', (record_id,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row) if row else None

    def save(self, db_path: Optional[str] = None) -> 'Absensi':
        conn = self._connect(db_path)
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute(
                    '''
                    UPDATE absensi
                    SET nama = %s, kelas = %s, tanggal = %s, jam_masuk = %s, jam_keluar = %s, status = %s, keterangan = %s, latitude = %s, longitude = %s
                    WHERE id = %s
                    ''',
                    (self.nama, self.kelas, self.tanggal, self.jam_masuk, self.jam_keluar, self.status, self.keterangan, self.latitude, self.longitude, self.id),
                )
            else:
                cursor.execute(
                    '''
                    INSERT INTO absensi (nama, kelas, tanggal, jam_masuk, jam_keluar, status, keterangan, latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    ''',
                    (self.nama, self.kelas, self.tanggal, self.jam_masuk, self.jam_keluar, self.status, self.keterangan, self.latitude, self.longitude),
                )
                row = cursor.fetchone()
                if row:
                    self.id = row['id']
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        return self

    def delete(self, db_path: Optional[str] = None) -> None:
        if not self.id:
            return
        conn = self._connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM absensi WHERE id = %s', (self.id,))
            conn.commit()
            self.id = None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        import math
        try:
            lat1 = float(lat1)
            lon1 = float(lon1)
            lat2 = float(lat2)
            lon2 = float(lon2)
        except (TypeError, ValueError):
            return 9999999.0  # Sangat jauh jika koordinat tidak valid
            
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @classmethod
    def auto_update_absensi(cls, db_path: Optional[str] = None) -> None:
        """
        Secara otomatis memperbarui status absensi hari ini untuk semua mahasiswa
        berdasarkan waktu saat ini dan aturan lokasi.
        """
        from models.simulation_state import get_current_time
        from models.model_users import User
        import datetime
        
        now = get_current_time()
        today = now.strftime("%Y-%m-%d")
        current_time_val = now.time()
        
        # Ambil semua mahasiswa
        mahasiswa_list = User.get_all_mahasiswa()
        
        # Ambil semua absensi hari ini
        conn = cls._connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM absensi WHERE tanggal = %s", (today,))
        rows = cursor.fetchall()
        conn.close()
        
        # Map nama -> record absensi
        absensi_map = {row['nama']: cls.from_row(row) for row in rows}
        
        # Kampus koordinat (UNU Indonesia Kampus B)
        CAMPUS_LAT = -6.490333
        CAMPUS_LON = 106.731667
        
        # Helper to check if a student has excuse
        def has_excuse(record):
            status_lower = (record.status or "").strip().lower()
            ket_lower = (record.keterangan or "").strip().lower()
            return status_lower in ["izin", "sakit"] or "izin" in ket_lower or "sakit" in ket_lower
            
        for m in mahasiswa_list:
            nama = m['nama']
            record = absensi_map.get(nama)
            
            if record is None:
                # Belum ada record absensi sama sekali hari ini
                if current_time_val >= datetime.time(9, 55):
                    # Sudah lewat 09:55 -> Alfa
                    new_record = cls(
                        nama=nama, kelas="", tanggal=today,
                        status="Alfa", keterangan="Tidak hadir (Alfa otomatis)"
                    )
                    new_record.save(db_path)
                elif current_time_val >= datetime.time(9, 40):
                    # Sudah lewat 09:40 -> Terlambat
                    new_record = cls(
                        nama=nama, kelas="", tanggal=today,
                        status="Terlambat", keterangan="Belum absen sampai jam 09:40"
                    )
                    new_record.save(db_path)
                else:
                    # Sebelum 09:40 -> Belum Absen
                    new_record = cls(
                        nama=nama, kelas="", tanggal=today,
                        status="Belum Absen", keterangan=""
                    )
                    new_record.save(db_path)
            else:
                # Sudah ada record absensi
                # Check excuse
                if has_excuse(record):
                    # Jangan diubah ke Alfa atau Terlambat jika sudah diisi Izin / Sakit
                    continue
                    
                # Jika statusnya Belum Absen atau Terlambat atau Hadir (tetapi luar kampus)
                # Mari kita cek apakah dia sudah absen masuk
                if record.jam_masuk:
                    # Sudah absen masuk. Cek lokasi absen masuknya
                    dist = cls.calculate_distance(record.latitude, record.longitude, CAMPUS_LAT, CAMPUS_LON)
                    is_inside = (dist <= 100.0)
                    
                    if is_inside:
                        # Jika di dalam radius
                        # Status sudah ditetapkan saat masuk, jangan ubah
                        pass
                    else:
                        # Dia absen masuk dari luar radius
                        # Keterangannya harus mengandung 'diluar area kampus'
                        changed = False
                        if "diluar area kampus" not in (record.keterangan or "").lower():
                            record.keterangan = "diluar area kampus"
                            changed = True
                            
                        # Jika sudah lewat 09:55 dan dia masih tercatat di luar kampus (dan tidak ada izin/sakit)
                        if current_time_val >= datetime.time(9, 55):
                            if record.status != "Alfa":
                                record.status = "Alfa"
                                changed = True
                        elif current_time_val >= datetime.time(9, 40):
                            # Jika lewat 09:40 tapi belum 09:55
                            if record.status != "Terlambat":
                                record.status = "Terlambat"
                                changed = True
                        if changed:
                            record.save(db_path)
                else:
                    # Belum absen masuk (jam_masuk kosong)
                    # Update status otomatis berdasarkan jam
                    changed = False
                    if current_time_val >= datetime.time(9, 55):
                        if record.status != "Alfa":
                            record.status = "Alfa"
                            record.keterangan = "Tidak hadir (Alfa otomatis)"
                            changed = True
                    elif current_time_val >= datetime.time(9, 40):
                        if record.status != "Terlambat":
                            record.status = "Terlambat"
                            record.keterangan = "Belum absen sampai jam 09:40"
                            changed = True
                    if changed:
                        record.save(db_path)
