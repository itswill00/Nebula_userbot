import functools
from hydrogram import filters

# Registry Global untuk menyimpan info perintah
# Format: { 'Kategori': { 'cmd': 'info' } }
CMD_HELP = {}

def on_cmd(command, category="General", info="Belum ada info."):
    """
    Dekorator kustom untuk mendaftarkan perintah dan bantuan secara otomatis.
    """
    if category not in CMD_HELP:
        CMD_HELP[category] = {}
    
    CMD_HELP[category][command] = info
    
    # Menggunakan filter standar Hydrogram
    # filters.me memastikan hanya pemilik akun yang bisa menjalankan
    return filters.command(command, prefixes=".") & filters.me
