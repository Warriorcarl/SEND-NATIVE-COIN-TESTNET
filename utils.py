import json
import os
from colorama import init, Fore

# Inisialisasi colorama
init(autoreset=True)

# Fungsi untuk menyimpan data ke dalam list di file JSON
def save_data_list(filename, new_data):
    all_data = load_all_data(filename)
    if isinstance(all_data, list):
        if isinstance(new_data, list):
            all_data.extend(new_data)  # Menggabungkan list baru langsung ke list utama
        else:
            all_data.append(new_data)
    else:
        all_data = [new_data]  # Buat list baru jika belum ada data
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=4)  # Gunakan indentasi untuk tampilan rapi
    print(Fore.GREEN + "✔️ Data berhasil disimpan.")

# Fungsi untuk memuat semua data dari file JSON
def load_all_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    print(Fore.RED + f"⚠️ File '{filename}' tidak ditemukan. Mengembalikan data kosong.")
    return []

# Fungsi untuk menghapus data dari list di file JSON berdasarkan kunci
def delete_data_from_list(filename, data_to_delete):
    all_data = load_all_data(filename)
    all_data = [data for data in all_data if data != data_to_delete]
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=4)
    print(Fore.GREEN + "✔️ Data berhasil dihapus.")