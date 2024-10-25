import json
from utils import save_data_list, load_all_data
from colorama import init, Fore

# Inisialisasi colorama
init(autoreset=True)

rpc_file = "rpc_data.json"

# Fungsi untuk menambahkan atau memuat RPC
def input_or_load_rpc():
    rpc_data_list = load_all_data(rpc_file)
    
    print(Fore.CYAN + "Daftar RPC yang tersedia:")
    if not rpc_data_list:
        print(Fore.RED + "⚠️  Belum ada data RPC. Silakan tambahkan RPC baru.")

    for idx, rpc in enumerate(rpc_data_list, 1):
        print(Fore.GREEN + f"{idx}. {rpc['nama']}: {rpc['rpc_url']} (Chain ID: {rpc['chain_id']})")
    
    rpc_index = input(Fore.CYAN + "Pilih nomor RPC yang ingin Anda gunakan (tekan Enter untuk membuat baru): ")
    if rpc_index == "":
        rpc_name = input(Fore.CYAN + "Masukkan nama untuk RPC ini: ")
        rpc_url = input(Fore.CYAN + "Masukkan URL RPC: ")
        chain_id = input(Fore.CYAN + "Masukkan Chain ID: ")
        
        new_rpc = {
            'nama': rpc_name,
            'rpc_url': rpc_url,
            'chain_id': chain_id
        }
        
        rpc_data_list.append(new_rpc)
        save_data_list(rpc_file, new_rpc)
        print(Fore.GREEN + f"✔️ RPC '{rpc_name}' berhasil ditambahkan.")
        return new_rpc
    
    rpc_index = int(rpc_index)
    return rpc_data_list[rpc_index - 1]
# Fungsi untuk menampilkan RPC yang ada
def display_rpcs():
    rpc_data_list = load_all_data(rpc_file)
    
    if not rpc_data_list:
        print(Fore.RED + "⚠️  Tidak ada data RPC yang tersedia.")
        return False
    
    for idx, rpc in enumerate(rpc_data_list, 1):
        print(Fore.GREEN + f"{idx}. {rpc['nama']}: {rpc['rpc_url']} (Chain ID: {rpc['chain_id']})")
    
    return True

# Fungsi untuk menghapus RPC yang ada
def delete_rpc():
    rpc_data_list = load_all_data(rpc_file)
    
    if not rpc_data_list:
        print(Fore.RED + "⚠️  Tidak ada data RPC yang tersedia untuk dihapus.")
        return
    
    for idx, rpc in enumerate(rpc_data_list, 1):
        print(Fore.GREEN + f"{idx}. {rpc['nama']}: {rpc['rpc_url']} (Chain ID: {rpc['chain_id']})")
    
    rpc_index = int(input(Fore.CYAN + "Pilih nomor RPC yang ingin Anda hapus: "))
    
    if 1 <= rpc_index <= len(rpc_data_list):
        rpc_to_delete = rpc_data_list.pop(rpc_index - 1)
        save_data_list(rpc_file, rpc_data_list)
        print(Fore.GREEN + f"✔️ RPC '{rpc_to_delete['nama']}' berhasil dihapus.")
    else:
        print(Fore.RED + "⚠️ Nomor RPC tidak valid.")

# Fungsi untuk memuat RPC berdasarkan indeks yang dipilih
def load_rpc_by_index(index):
    rpc_data_list = load_all_data(rpc_file)
    if 1 <= index <= len(rpc_data_list):
        return rpc_data_list[index - 1]
    else:
        print(Fore.RED + "⚠️ Nomor RPC tidak valid.")
        return None