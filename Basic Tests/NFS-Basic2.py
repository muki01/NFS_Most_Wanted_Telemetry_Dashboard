import pymem
import pymem.process
import time
import os
import keyboard

os.system('cls' if os.name == 'nt' else 'clear')

PROCESS_NAME = "speed.exe"
STATIC_PTR_OFFSET = 0x50D670
OFFSETS = [0x68, 0x4, 0x8, 0x10, 0xF8]

def get_pointer_address(pm, base, offsets):
    """Pointer zincirini takip ederek gerçek veri adresini bulur."""
    addr = pm.read_int(base)
    for offset in offsets[:-1]:
        addr = pm.read_int(addr + offset)
    return addr + offsets[-1]

def main():
    try:
        pm = pymem.Pymem(PROCESS_NAME)
        game_module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        static_addr = game_module + STATIC_PTR_OFFSET
        
        print(" NOS Doldurmak için '0' tuşuna basın. (Çıkış için 'q')")

        while True:
            try:
                final_addr = get_pointer_address(pm, static_addr, OFFSETS) # Dynamic NOS calculation
                nos_val = pm.read_float(final_addr) # Real NOS value (0.0 to 1.0)
                nos_percentage = max(0.0, min(1.0, nos_val)) * 100 # Calculate percentage and clamp between 0-100

                print(f"Mevcut NOS: %{nos_percentage:.1f}      ", end="\r") # Print current NOS percentage

                # '0' tuşuna basılırsa NOS'u %100 yap (1.0 yaz)
                if keyboard.is_pressed('0'):
                    pm.write_float(final_addr, 1.0)
                    print("\n[!] NOS Dolduruldu!          ")

                if nos_percentage <= 5.0: # NOS %5 or less, prompt user to refill
                    pm.write_float(final_addr, 1.0)
                    print("\n[!] NOS Dolduruldu!          ")

                # 'q' ile çıkış
                if keyboard.is_pressed('q'):
                    break

            except Exception:
                print("Veri okunurken hata!", end="\r")
            
            time.sleep(0.1)

    except Exception as e:
        print(f"Hata: {e}")
        print("Lütfen oyunun açık olduğundan ve yönetici olarak çalıştırdığından emin ol.")

if __name__ == "__main__":
    main()