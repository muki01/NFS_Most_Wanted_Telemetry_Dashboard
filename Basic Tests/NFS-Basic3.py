import pymem
import pymem.process
import time
import os
import keyboard
import sys
from colorama import init, Fore, Style

# Initialize colors
init(autoreset=True)

# Settings
PROCESS_NAME = "speed.exe"
NOS_BASE_OFFSET = 0x50D670
NOS_OFFSETS = [0x68, 0x4, 0x8, 0x10, 0xF8]
SPEED_STATIC_OFFSET = 0x514654

def get_pointer_address(pm, base, offsets):
    try:
        addr = pm.read_int(base)
        for offset in offsets[:-1]:
            addr = pm.read_int(addr + offset)
        return addr + offsets[-1]
    except:
        return None

def clear_line():
    """Completely clears the current line."""
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

def main():
    try:
        pm = pymem.Pymem(PROCESS_NAME)
        game_module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        static_addr = game_module + NOS_BASE_OFFSET
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + "="*50)
        print(Fore.YELLOW + "  NFS:MW Advanced NOS Interface")
        print(Fore.WHITE + "  [Q] Exit | Auto-Refill Active")
        print(Fore.CYAN + Style.BRIGHT + "="*50 + "\n")

        while True:
            if keyboard.is_pressed('q'): break

            try:
                final_addr = get_pointer_address(pm, static_addr, NOS_OFFSETS)
                if final_addr:
                    nos_val = pm.read_float(final_addr)
                    nos_perc = max(0.0, min(1.0, nos_val))
                    
                    # Bar design
                    bar = "█" * int(20 * nos_perc) + "░" * (20 - int(20 * nos_perc))
                    color = Fore.GREEN if nos_perc > 0.2 else Fore.RED
                    
                    # SINGLE LINE UPDATE
                    # \r moves cursor to start, end="" prevents newline
                    print(f"\r{Fore.WHITE}STATUS: [{color}{bar}{Fore.WHITE}] %{nos_perc*100:>5.1f}", end="", flush=True)

                    # NOS Refill Logic
                    if nos_perc < 0.05 or keyboard.is_pressed('0'):
                        pm.write_float(final_addr, 1.0)
                        
                        # Show message on same line instantly then return:
                        print(f"  {Fore.CYAN}<< NOS BOOSTED! >>", end="", flush=True)
                        time.sleep(0.7) # Brief pause for message visibility
                        clear_line() # Clear line so old bar doesn't linger
                
            except Exception:
                print(f"\r{Fore.RED}[!] Waiting for race...                      ", end="")
            
            time.sleep(0.01)

    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")

if __name__ == "__main__":
    main()