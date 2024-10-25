from utils import save_data_list, load_all_data
from colorama import init, Fore, Style

# Inisialisasi colorama
init(autoreset=True)

wallet_file = "wallet_data.json"

# Fungsi untuk menambahkan atau memuat wallet
def input_or_load_wallet():
    wallet_data_list = load_all_data(wallet_file)
    
    print(Fore.CYAN + "Daftar wallet yang tersedia:")
    if not wallet_data_list:
        print(Fore.RED + "⚠️  Belum ada data wallet. Silakan tambahkan wallet baru.")
    
    for idx, wallet in enumerate(wallet_data_list, 1):
        print(Fore.GREEN + f"{idx}. {wallet['nama']}: {wallet['my_address']}")
    
    wallet_index = input(Fore.CYAN + "Pilih nomor wallet yang ingin Anda gunakan (tekan Enter untuk membuat baru): ")
    if wallet_index == "":
        wallet_name = input(Fore.CYAN + "Masukkan nama untuk wallet ini: ")
        my_address = input(Fore.CYAN + "Masukkan alamat wallet: ")
        private_key = input(Fore.CYAN + "Masukkan private key wallet: ")
        
        new_wallet = {
            'nama': wallet_name,
            'my_address': my_address,
            'private_key': private_key
        }
        
        wallet_data_list.append(new_wallet)
        save_data_list(wallet_file, new_wallet)
        print(Fore.GREEN + f"✔️ Wallet '{wallet_name}' berhasil ditambahkan.")
        return new_wallet
    
    wallet_index = int(wallet_index)
    return wallet_data_list[wallet_index - 1]
# Fungsi untuk menampilkan wallet yang ada
def display_wallets():
    wallet_data_list = load_all_data(wallet_file)
    
    if not wallet_data_list:
        print(Fore.RED + "⚠️  Tidak ada data wallet yang tersedia.")
        return False
    
    # Memeriksa apakah setiap item dalam wallet_data_list adalah dictionary
    for idx, wallet in enumerate(wallet_data_list, 1):
        if isinstance(wallet, dict) and 'nama' in wallet and 'my_address' in wallet:
            print(Fore.GREEN + f"{idx}. {wallet['nama']}: {wallet['my_address']}")
        else:
            print(Fore.RED + f"⚠️ Wallet data tidak valid pada indeks {idx}, pastikan formatnya benar.")
    
    return True


# Fungsi untuk menghapus wallet yang ada
def delete_wallet():
    wallet_data_list = load_all_data(wallet_file)
    
    if not wallet_data_list:
        print(Fore.RED + "⚠️  Tidak ada data wallet yang tersedia untuk dihapus.")
        return
    
    for idx, wallet in enumerate(wallet_data_list, 1):
        print(Fore.GREEN + f"{idx}. {wallet['nama']}: {wallet['my_address']}")
    
    wallet_index = int(input(Fore.CYAN + "Pilih nomor wallet yang ingin Anda hapus: "))
    
    if 1 <= wallet_index <= len(wallet_data_list):
        wallet_to_delete = wallet_data_list.pop(wallet_index - 1)
        save_data_list(wallet_file, wallet_data_list)
        print(Fore.GREEN + f"✔️ Wallet '{wallet_to_delete['nama']}' berhasil dihapus.")
    else:
        print(Fore.RED + "⚠️ Nomor wallet tidak valid.")

# Fungsi untuk memuat wallet berdasarkan indeks yang dipilih
def load_wallet_by_index(index):
    wallet_data_list = load_all_data(wallet_file)
    if 1 <= index <= len(wallet_data_list):
        return wallet_data_list[index - 1]
    else:
        print(Fore.RED + "⚠️ Nomor wallet tidak valid.")
        return None