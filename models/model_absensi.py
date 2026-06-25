import os
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

BASE_DIR = os.path.dirname(__file__)
DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'absensi.db'))


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

    @staticmethod
    def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
        path = db_path or DATABASE_PATH
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def create_table(cls, db_path: Optional[str] = None) -> None:
        conn = cls._connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS absensi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kelas TEXT,
                tanggal TEXT NOT NULL,
                jam_masuk TEXT,
                jam_keluar TEXT,
                status TEXT,
                keterangan TEXT
            )
            '''
        )
        conn.commit()
        conn.close()

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Absensi':
        return cls(
            id=row.get('id'),
            nama=row.get('nama', ''),
            kelas=row.get('kelas', ''),
            tanggal=row.get('tanggal', ''),
            jam_masuk=row.get('jam_masuk', ''),
            jam_keluar=row.get('jam_keluar', ''),
            status=row.get('status', ''),
            keterangan=row.get('keterangan', ''),
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
    def find_by_id(cls, record_id: int, db_path: Optional[str] = None) -> Optional['Absensi']:
        conn = cls._connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM absensi WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row) if row else None

    def save(self, db_path: Optional[str] = None) -> 'Absensi':
        conn = self._connect(db_path)
        cursor = conn.cursor()
        if self.id:
            cursor.execute(
                '''
                UPDATE absensi
                SET nama = ?, kelas = ?, tanggal = ?, jam_masuk = ?, jam_keluar = ?, status = ?, keterangan = ?
                WHERE id = ?
                ''',
                (self.nama, self.kelas, self.tanggal, self.jam_masuk, self.jam_keluar, self.status, self.keterangan, self.id),
            )
        else:
            cursor.execute(
                '''
                INSERT INTO absensi (nama, kelas, tanggal, jam_masuk, jam_keluar, status, keterangan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (self.nama, self.kelas, self.tanggal, self.jam_masuk, self.jam_keluar, self.status, self.keterangan),
            )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self

    def delete(self, db_path: Optional[str] = None) -> None:
        if not self.id:
            return
        conn = self._connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM absensi WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
        self.id = None
