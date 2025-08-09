#!/usr/bin/env python
import os
import random
import threading
import time
import sys
from eth_account import Account
from web3 import Web3
from colorama import Fore, Back, Style, init

# Inisialisasi colorama
init(autoreset=True)

# Daftar RPC untuk multi-chain
RPC_ENDPOINTS = {
    "Ethereum": "https://eth.merkle.io",
    "Base": "https://base.drpc.org",
    "Optimism": "https://optimism.drpc.org",
    "Arbitrum": "https://arbitrum.drpc.org",
    "Unichain": "https://0xrpc.io/uni",
    "Soneium": "https://soneium.drpc.org",
    "Zora": "https://zora.drpc.org",
    "Blast": "https://blast.drpc.org",
    "Hyperliquid": "https://hyperliquid.drpc.org",
    "BSC": "https://bsc.therpc.io",
    "Polygon": "https://polygon-rpc.com",
    "Avalanche": "https://avalanche.drpc.org",
}

# Web3 instances
WEB3_CHAINS = {name: Web3(Web3.HTTPProvider(url)) for name, url in RPC_ENDPOINTS.items()}

# Hex chars untuk generator
HEX_CHARS = "0123456789abcdef"

# Counter untuk stats
scan_count = 0
found_count = 0
start_time = time.time()

def get_terminal_width():
    """Dapatkan lebar terminal"""
    try:
        return os.get_terminal_size().columns
    except:
        return 120

def create_matrix_banner():
    """Banner Matrix style"""
    banner = f"""
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  {Fore.CYAN}EVM PRIVATE KEY HUNTER v2.0 - MULTI CHAIN MATRIX SCANNER{Fore.GREEN}                      ║
║  {Fore.YELLOW}Active Chains: {len(RPC_ENDPOINTS)} Networks{Fore.GREEN}                                                    ║
╚══════════════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    return banner

def random_private_key():
    """Generate random private key"""
    return "0x" + ''.join(random.choice(HEX_CHARS) for _ in range(64))

def matrix_effect_text(text, color=Fore.GREEN):
    """Efek teks matrix dengan karakter berubah"""
    chars = "!<>-_\\/[]{}—=+*^?#________"
    result = ""
    for char in text:
        if random.random() < 0.1:  # 10% chance untuk karakter matrix
            result += color + random.choice(chars) + Style.RESET_ALL
        else:
            result += color + char + Style.RESET_ALL
    return result

def format_balance(balance):
    """Format balance dengan warna"""
    if isinstance(balance, str) and balance == "Err":
        return f"{Fore.RED}ERR{Style.RESET_ALL}"
    elif balance == 0:
        return f"{Fore.LIGHTBLACK_EX}0.000{Style.RESET_ALL}"
    elif balance > 0:
        return f"{Fore.YELLOW}★{balance:.6f}{Style.RESET_ALL}"
    else:
        return f"{Fore.LIGHTBLACK_EX}{balance}{Style.RESET_ALL}"

def create_scrolling_display(addr, balances, pk, found_balance=False):
    """Buat display bergulir dalam satu baris"""
    global scan_count, found_count
    
    # Stats
    elapsed = time.time() - start_time
    rate = scan_count / elapsed if elapsed > 0 else 0
    
    # Status indicator
    if found_balance:
        status = f"{Back.RED}{Fore.WHITE} ★ JACKPOT ★ {Style.RESET_ALL}"
        found_count += 1
    else:
        status_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        status_char = status_chars[scan_count % len(status_chars)]
        status = f"{Fore.CYAN}{status_char} SCANNING{Style.RESET_ALL}"
    
    # Chain balances display - hanya yang penting
    chain_info = []
    for chain, balance in balances.items():
        if balance != 0 and balance != "Err":
            chain_info.append(f"{Fore.GREEN}{chain}{Fore.WHITE}:{format_balance(balance)}")
        elif len(chain_info) < 3:  # Tampilkan beberapa yang 0 juga
            chain_info.append(f"{Fore.LIGHTBLACK_EX}{chain}:{format_balance(balance)}")
    
    # Batasi chain display agar tidak terlalu panjang
    chain_display = " ".join(chain_info[:8])
    
    # Address dengan efek matrix
    addr_display = f"{Fore.LIGHTGREEN_EX}{addr[:6]}...{addr[-4:]}{Style.RESET_ALL}"
    
    # Stats info
    stats = f"{Fore.MAGENTA}[{scan_count:,}]{Fore.WHITE}|{Fore.YELLOW}[{found_count}💎]{Fore.WHITE}|{Fore.CYAN}[{rate:.1f}/s]{Style.RESET_ALL}"
    
    # Terminal width
    term_width = get_terminal_width()
    
    # Build the line
    line = f"{status} {stats} {addr_display} ║ {chain_display}"
    
    # Truncate if too long
    if len(line.encode()) > term_width - 10:  # Leave some margin
        line = line[:term_width-15] + "..."
    
    # Print dengan carriage return untuk overwrite
    print(f"\r{line}", end="", flush=True)

def check_wallet():
    """Main wallet checking function"""
    global scan_count
    
    while True:
        try:
            pk = random_private_key()
            acct = Account.from_key(pk)
            addr = acct.address
            
            found_balance = False
            balances = {}
            
            # Check all chains
            for chain_name, w3 in WEB3_CHAINS.items():
                try:
                    balance_wei = w3.eth.get_balance(addr)
                    balance_eth = w3.from_wei(balance_wei, 'ether')
                    balances[chain_name] = balance_eth
                    
                    if balance_eth > 0:
                        found_balance = True
                        
                except Exception as e:
                    balances[chain_name] = "Err"
            
            scan_count += 1
            
            # Display in scrolling format
            create_scrolling_display(addr, balances, pk, found_balance)
            
            # Save if found assets
            if found_balance:
                with open("aset.txt", "a") as f:
                    f.write(f"{addr} | {pk} | {balances}\n")
                
                # New line for found wallet
                print(f"\n{Back.GREEN}{Fore.BLACK} WALLET FOUND! {Style.RESET_ALL} {addr} → Saved to aset.txt")
                print()  # Extra space before continuing scan
            
            # Small delay untuk readability
            time.sleep(0.05)
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}[STOPPED]{Style.RESET_ALL} Scanning stopped by user")
            print(f"{Fore.CYAN}Total scanned: {scan_count:,}")
            print(f"{Fore.GREEN}Wallets found: {found_count}")
            sys.exit(0)
        except Exception as e:
            # Don't print errors in scrolling mode, just continue
            continue

def main():
    """Main function"""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Show banner
    print(create_matrix_banner())
    
    print(f"{Fore.CYAN}🌐 Active Networks: {Fore.GREEN}{', '.join(RPC_ENDPOINTS.keys())}")
    print(f"{Fore.CYAN}🔍 Scanning Mode: {Fore.YELLOW}Matrix Scroll")
    print(f"{Fore.CYAN}💾 Results saved to: {Fore.YELLOW}aset.txt")
    print(f"{Fore.CYAN}⚡ Press Ctrl+C to stop\n")
    
    print(f"{Fore.LIGHTBLACK_EX}{'='*get_terminal_width()}")
    print(f"{Fore.YELLOW}STATUS    STATS         ADDRESS      ║ CHAIN BALANCES")
    print(f"{Fore.LIGHTBLACK_EX}{'='*get_terminal_width()}")
    
    # Start scanning threads
    threads = []
    thread_count = 1  # Single thread untuk display yang clean
    
    for i in range(thread_count):
        t = threading.Thread(target=check_wallet, daemon=True)
        t.start()
        threads.append(t)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[SHUTDOWN]{Style.RESET_ALL} Matrix Hunter terminated")
        sys.exit(0)

if __name__ == "__main__":
    main()
