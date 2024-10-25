from colorama import init, Fore, Back
from transaction import run_multi_wallet_bot
from wallet import input_or_load_wallet, delete_wallet, display_wallets
from rpc import input_or_load_rpc, delete_rpc, display_rpcs

# Inisialisasi colorama
init(autoreset=True)

def main_menu():
    while True:
        print(Fore.CYAN + Back.BLACK + "\n--- Menu Utama ---")
        print(Fore.GREEN + "1. 📝 Pengisian data")
        print(Fore.YELLOW + "2. 🚀 Menjalankan bot pengiriman ETH (Multi Wallet)")
        print(Fore.RED + "3. ❌ Keluar")
        pilihan = input(Fore.CYAN + "Pilih opsi: ")

        if pilihan == '1':
            menu_pengisian_data()
        elif pilihan == '2':
            run_multi_wallet_bot()  # Memanggil fungsi bot multi wallet
        elif pilihan == '3':
            print(Fore.RED + "Keluar dari program.")
            break
        else:
            print(Fore.RED + "Pilihan tidak valid. Silakan coba lagi.")

def menu_pengisian_data():
    print(Fore.CYAN + "\n--- Pengisian Data ---")

    print(Fore.GREEN + "Daftar wallet yang tersedia:")
    if not display_wallets():
        print(Fore.RED + "Belum ada data wallet.\n")

    print(Fore.GREEN + "Daftar RPC yang tersedia:")
    if not display_rpcs():
        print(Fore.RED + "Belum ada data RPC.\n")

    while True:
        print(Fore.YELLOW + "\nTentukan pilihan anda:")
        print("1. ➕ isi data wallet baru")
        print("2. 🗑️ hapus data wallet yang sudah ada")
        print("3. ➕ isi data rpc baru")
        print("4. 🗑️ hapus data rpc yang sudah ada")
        print("5. 🔙 Kembali ke menu utama")
        pilihan = input(Fore.CYAN + "Tentukan pilihan anda: ")

        if pilihan == '1':
            input_or_load_wallet()
        elif pilihan == '2':
            delete_wallet()
        elif pilihan == '3':
            input_or_load_rpc()
        elif pilihan == '4':
            delete_rpc()
        elif pilihan == '5':
            break
        else:
            print(Fore.RED + "Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main_menu()
