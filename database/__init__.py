"""
AGGRESSOR UC BOT - Database paketi.

Bu fayl `database` papkasini Python paketi sifatida belgilaydi
va butun loyiha bo'ylab foydalanish uchun global Database obyektini yaratadi.
"""

from config import config
from database.db import Database

# Butun loyiha bo'ylab ishlatiladigan global database obyekti.
# Boshqa modullar shunchaki `from database import db` orqali import qiladi.
db = Database(config.DATABASE_PATH)

__all__ = ["db", "Database"]
