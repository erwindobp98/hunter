#!/usr/bin/env python
import os
import random
import threading
import time
import sys
from eth_account import Account
from web3 import Web3
from colorama import Fore, Style, init

# Inisialisasi colorama
init(autoreset=True)

# Daftar RPC untuk multi-chain
RPC_ENDPOINTS = {
    "Ethereum": "https://opt-mainnet.g.alchemy.com/v2/SiRDe2sBrBR3f2vm3cbhNSYpqwnk5LwJ",
    "BNB Chain": "https://bnb-mainnet.g.alchemy.com/v2/SiRDe2sBrBR3f2vm3cbhNSYpqwnk5LwJ",
    "Polygon": "https://polygon-mainnet.g.alchemy.com/v2/SiRDe2sBrBR3f2vm3cbhNSYpqwnk5LwJ",
    "Avalanche": "https://avax-mainnet.g.alchemy.com/v2/SiRDe2sBrBR3f2vm3cbhNSYpqwnk5LwJ",
    "Hayperliquid": "https://hyperliquid-mainnet.g.alchemy.com/v2/SiRDe2sBrBR3f2vm3cbhNSYpqwnk5LwJ"
}

# Simpan Web3 untuk tiap chain
WEB3_CHAINS = {name: Web3(Web3.HTTPProvider(url)) for name, url in RPC_ENDPOINTS.items()}

# Karakter hex untuk generator PK
HEX_CHARS = "0123456789abcdef"

def loading_animation(text, duration=0.5):
    """Animasi loading singkat"""
    animation = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{Fore.CYAN}{text} {animation[i % len(animation)]}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.5)
    sys.stdout.write("\r" + " " * (len(text) + 4) + "\r")

def random_private_key():
    """Buat private key hex acak"""
    loading_animation("Generating PK")
    return "0x" + ''.join(random.choice(HEX_CHARS) for _ in range(64))

def check_wallet():
    while True:
        try:
            pk = random_private_key()
            acct = Account.from_key(pk)
            addr = acct.address

            found_balance = False
            balances = {}

            # Cek semua chain
            for chain_name, w3 in WEB3_CHAINS.items():
                try:
                    balance_wei = w3.eth.get_balance(addr)
                    balance_eth = w3.from_wei(balance_wei, 'ether')
                    balances[chain_name] = balance_eth

                    if balance_eth > 0:
                        found_balance = True
                except Exception as e:
                    balances[chain_name] = "Err"

            # Tampilan scanning ala Matrix
            chain_display = " ".join(
                f"{Fore.GREEN}{chain}:{Fore.YELLOW}{balances[chain]}"
                for chain in balances
            )

            print(f"{Fore.GREEN}[SCAN]{Style.RESET_ALL} "
                  f"{Fore.LIGHTGREEN_EX}{addr}{Style.RESET_ALL} "
                  f"| {chain_display}")

            # Simpan jika ada aset
            if found_balance:
                with open("aset.txt", "a") as f:
                    f.write(f"{addr} | {pk} | {balances}\n")
                print(f"{Fore.RED}[FOUND]{Style.RESET_ALL} "
                      f"{Fore.LIGHTGREEN_EX}{addr}{Style.RESET_ALL} "
                      f"→ Simpan ke aset.txt")

        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {e}")

def main():
    print(f"{Fore.YELLOW}=== EVM Private Key Hunter Multi-Chain (Matrix Style) ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}Chains aktif: {Fore.GREEN}{', '.join(RPC_ENDPOINTS.keys())}\n")

    # Jalankan beberapa thread scanning
    for _ in range(1):  # 10 thread agar cepat
        threading.Thread(target=check_wallet, daemon=True).start()

    # Tetap hidup
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
