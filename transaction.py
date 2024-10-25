from colorama import init, Fore, Style
from web3 import Web3
from wallet import input_or_load_wallet
from rpc import input_or_load_rpc
import time
import datetime
import threading
import json

# Inisialisasi colorama
init(autoreset=True)

# Menggunakan threading.Event untuk menghentikan bot
stop_event = threading.Event()

# Fungsi untuk menghentikan bot (menggunakan event)
def interrupt_bot():
    while not stop_event.is_set():
        time.sleep(1)

# Fungsi untuk memuat semua wallet dari file JSON (atau bisa diubah sesuai sumber data Anda)
def load_all_wallets():
    try:
        with open('wallet_data.json', 'r') as file:
            wallets = json.load(file)  # Memuat data wallet dari file JSON
        return wallets
    except FileNotFoundError:
        print(Fore.RED + "File wallet_data.json tidak ditemukan!")
        return []

# Fungsi untuk menjalankan bot pengiriman ETH multi wallet
def run_multi_wallet_bot():
    print(Fore.CYAN + "Atur Sebelum Menjalankan Transaksi Pengiriman ETH (Multi Wallet)")
    
    wallet_data_list = []  # Menyimpan data semua wallet yang dipilih
    all_wallets = load_all_wallets()  # Ambil semua wallet yang tersedia

    # Tanyakan apakah ingin menggunakan semua wallet atau memilih secara manual
    use_all_wallets = input(Fore.CYAN + "Gunakan seluruh wallet yang tersedia? (y/n): ").lower().strip()

    if use_all_wallets == 'y':
        # Gunakan seluruh wallet yang ada
        wallet_data_list = all_wallets
    else:
        while True:
            # Pilih wallet (bisa menambahkan beberapa wallet)
            wallet_data = input_or_load_wallet()
            wallet_data_list.append(wallet_data)
            more_wallets = input(Fore.CYAN + "Ingin menambahkan wallet lagi? (y/n): ").lower()
            if more_wallets != 'y':
                break

    # Pilih RPC (sama untuk semua wallet)
    rpc_data = input_or_load_rpc()

    # Prompt pengguna untuk memasukkan jumlah ETH yang ingin dikirim
    eth_amount = float(input(Fore.CYAN + "Masukkan jumlah ETH yang ingin Anda kirim per transaksi: "))

    # Prompt pengguna untuk memasukkan delay atau lewatkan jika tidak ingin delay
    delay_input = input(Fore.CYAN + "Masukkan delay (dalam detik) antar transaksi (tekan Enter untuk tanpa delay): ").strip()
    delay = None if delay_input == "" else float(delay_input)  # Tetapkan None jika delay dikosongkan

    # Menangani jumlah transaksi (unlimited jika kosong)
    num_transactions_input = input(Fore.CYAN + "Masukkan jumlah transaksi yang ingin dilakukan (tekan Enter untuk unlimited): ")
    num_transactions = None if num_transactions_input == "" else int(num_transactions_input)

    # List untuk menyimpan data user dan statistik per wallet
    user_data_list = []
    stats_list = []
    wallet_saldo_habis_count = 0  # Menghitung jumlah wallet yang kehabisan saldo

    # Menyimpan data wallet dan RPC untuk setiap user
    for wallet_data in wallet_data_list:
        user_data_list.append((wallet_data, rpc_data))
        stats_list.append({})  # Buat dict kosong untuk menyimpan statistik per wallet

    # Menjalankan transaksi untuk setiap user
    threads = []
    try:
        for idx, user_data in enumerate(user_data_list):
            wallet_data, rpc_data = user_data
            thread = threading.Thread(target=start_multi_user_bot, args=(wallet_data, rpc_data, eth_amount, delay, num_transactions, stats_list[idx]))
            threads.append(thread)
            thread.start()

        # Menunggu semua thread selesai dan menangkap interupsi di thread utama
        while any(thread.is_alive() for thread in threads):
            try:
                # Cek apakah semua wallet kehabisan saldo
                wallet_saldo_habis_count = sum(1 for stats in stats_list if stats.get('saldo_habis', False))
                if wallet_saldo_habis_count == len(user_data_list):
                    print(Fore.RED + "\n❗ Semua wallet kehabisan saldo. Menghentikan semua transaksi...\n")
                    stop_event.set()
                    break

                for thread in threads:
                    thread.join(timeout=0.1)
            except KeyboardInterrupt:
                print(Fore.RED + "\n❗ Interupsi diterima. Menghentikan semua transaksi...\n")
                stop_event.set()
                break

        # Menunggu semua thread selesai setelah interupsi
        for thread in threads:
            thread.join()  # Menunggu semua thread selesai

    except Exception as e:
        print(Fore.RED + f"Error: {e}")

    # Tampilkan pesan persiapan statistik
    print(Fore.YELLOW + "\nSedang mempersiapkan statistik...")

    # Tambahkan delay untuk memastikan semua thread menyelesaikan tugasnya
    time.sleep(2)  # Delay 2 detik untuk memastikan semua data sudah terkumpul

    # Menampilkan statistik akhir
    for idx, (wallet_data, rpc_data) in enumerate(user_data_list):
        stats = stats_list[idx]
        print(Fore.CYAN + f"Statistik untuk wallet {wallet_data['nama']}:")
        print(Fore.GREEN + f"Total transaksi sukses: {stats.get('successful_txs', 0)}")
        print(Fore.MAGENTA + f"Total gas yang digunakan: {stats.get('total_gas_used', 0)} ETH")
        print(Fore.YELLOW + f"Sisa saldo: {stats.get('saldo_akhir', 'N/A')} ETH")

def start_multi_user_bot(wallet_data, rpc_data, eth_amount, delay, num_transactions, stats):
    max_retries = 5  # Jumlah maksimum percobaan koneksi ulang
    retry_delay = 5  # Delay antar retry dalam detik

    # Coba hubungkan ke RPC dengan retry
    for attempt in range(max_retries):
        web3 = Web3(Web3.HTTPProvider(rpc_data['rpc_url']))
        if web3.is_connected():
            print(Fore.GREEN + f"✔️ Berhasil terhubung ke jaringan RPC setelah {attempt+1} percobaan.")
            break
        else:
            print(Fore.RED + f"❌ Gagal terhubung ke jaringan RPC. Percobaan ke-{attempt+1} dari {max_retries}.")
            time.sleep(retry_delay)
    else:
        # Jika masih gagal setelah max_retries, lemparkan exception
        raise Exception(Fore.RED + "❌ Tidak dapat terhubung ke jaringan RPC setelah beberapa percobaan.")

    successful_txs = 0
    total_gas_used = 0
    start_time = datetime.datetime.now()

    try:
        # Ambil nonce awal dari jaringan
        nonce = web3.eth.get_transaction_count(wallet_data['my_address'])

        while not stop_event.is_set() and (num_transactions is None or successful_txs < num_transactions):
            # Cek saldo sebelum transaksi
            saldo_sekarang = float(web3.from_wei(web3.eth.get_balance(wallet_data['my_address']), 'ether'))
            print(Fore.CYAN + f"Saldo wallet {wallet_data['nama']}: {saldo_sekarang} ETH")

            # Pastikan eth_amount juga dalam bentuk float
            eth_amount_float = float(eth_amount)

            # Generate address tujuan secara otomatis
            target_address = web3.eth.account.create().address
            print(Fore.CYAN + f"Alamat tujuan: {target_address}")

            retry_count = 0
            while retry_count < 3:
                try:
                    # Estimasi gas limit secara otomatis
                    estimated_gas_limit = web3.eth.estimate_gas({
                        'to': target_address,
                        'from': wallet_data['my_address'],
                        'value': web3.to_wei(eth_amount_float, 'ether')
                    })

                    # Ambil gas price secara otomatis dari jaringan
                    gas_price = web3.eth.gas_price

                    print(Fore.YELLOW + f"Gas yang digunakan: {estimated_gas_limit} wei, GasPrice: {gas_price} wei")

                    # Kirim transaksi dengan gas yang disesuaikan otomatis
                    tx_hash, gas_used = send_transaction(web3, wallet_data, target_address, eth_amount_float, estimated_gas_limit, gas_price, nonce)

                    if tx_hash:
                        # Tunggu receipt untuk memastikan transaksi disetujui jaringan sebelum melanjutkan
                        print(Fore.CYAN + "Menunggu receipt dari jaringan...")
                        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
                        
                        # Hanya lanjutkan jika receipt sudah diterima
                        successful_txs += 1
                        total_gas_used += gas_used
                        gas_eth = Web3.from_wei(gas_used, 'ether')
                        saldo_sekarang = float(web3.from_wei(web3.eth.get_balance(wallet_data['my_address']), 'ether'))
                        print(Fore.GREEN + f"✔️ Tx Hash: {tx_hash}")
                        print(Fore.YELLOW + f"Total Tx Sukses: {successful_txs}")
                        print(Fore.BLUE + f"Gas yang Digunakan: {gas_eth} ETH")
                        print(Fore.MAGENTA + f"Sisa Saldo: {saldo_sekarang} ETH")
                        nonce += 1  # Increment nonce setelah transaksi sukses
                        break

                except Exception as e:
                    error_message = str(e)

                    if 'replacement transaction underpriced' in error_message.lower():
                        print(Fore.RED + "❌ Transaksi underpriced, menaikkan gasPrice secara signifikan.")
                        gas_price = int(gas_price * 1.5)  # Naikkan gas price 50% untuk menghindari underpriced
                    elif 'nonce too low' in error_message.lower():
                        print(Fore.RED + "❌ Nonce terlalu rendah, memperbarui nonce.")
                        nonce = web3.eth.get_transaction_count(wallet_data['my_address'])
                    elif 'known transaction' in error_message.lower():
                        print(Fore.RED + "❌ Known transaction, incrementing nonce.")
                        nonce += 1  # Inkrementasi nonce jika transaksi sudah dikenal
                    else:
                        print(Fore.RED + f"❌ Kesalahan: {error_message}")
                    
                    retry_count += 1

            if retry_count == 3:
                print(Fore.RED + "❌ Gagal mengirim transaksi setelah 3 kali percobaan.")
            
            # Terapkan delay hanya jika ada, jika delay kosong (None) tidak ada penundaan
            if delay is not None:
                print(Fore.CYAN + f"Menunggu {delay} detik sebelum transaksi berikutnya...")
                time.sleep(delay)

    except Exception as e:
        print(Fore.RED + f"Error: {e}")

    finally:
        # Menyimpan statistik akhir
        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        stats['successful_txs'] = successful_txs
        stats['total_gas_used'] = Web3.from_wei(total_gas_used, 'ether')
        stats['saldo_akhir'] = float(web3.from_wei(web3.eth.get_balance(wallet_data['my_address']), 'ether'))
        stats['total_time'] = total_time

# Fungsi send_transaction tetap sama, tetapi sekarang gas_limit dan gas_price diambil dari estimasi otomatis
def send_transaction(web3, wallet_data, target_address, eth_amount, gas_limit, gas_price, nonce):
    my_address = wallet_data['my_address']
    private_key = wallet_data['private_key']

    try:
        eth_amount_float = float(eth_amount)

        # Ambil Chain ID dari RPC yang sedang digunakan
        chain_id = web3.eth.chain_id  # Mengambil Chain ID dari jaringan RPC yang dipilih

        # Buat transaksi dengan gas limit dan gas price yang disediakan
        transaction = {
            'to': target_address,
            'from': my_address,
            'value': web3.to_wei(eth_amount_float, 'ether'),
            'nonce': nonce,  # Nonce unik untuk setiap transaksi
            'gas': gas_limit,  # Gunakan gas limit yang disesuaikan otomatis
            'gasPrice': gas_price,  # Gunakan gas price yang disesuaikan otomatis
            'chainId': chain_id  # Sertakan Chain ID
        }

        # Tanda tangani transaksi
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return web3.to_hex(tx_hash), receipt.gasUsed

    except Exception as e:
        print(Fore.RED + f"Error saat mengirim transaksi: {e}")
        return None, None