import pymem
import pymem.process
import time
import os
import keyboard

# Clear console
os.system('cls' if os.name == 'nt' else 'clear')

# --- GAME SETTINGS ---
PROCESS_NAME = "speed.exe"

SPEED_STATIC_OFFSET = 0x514654

NOS_STATIC_OFFSET = 0x50D670
NOS_OFFSETS = [0x68, 0x4, 0x8, 0x10, 0xF8]

GEAR_STATIC_OFFSET = 0x50D670
GEAR_OFFSETS = [0x68, 0x4, 0x8, 0x10, 0x84]

RPM_STATIC_OFFSET = 0x50D670
RPM_OFFSETS = [0x4, 0x4, 0x6C, 0x12C]
#RPM_OFFSETS = [0x10, 0x4, 0x6C, 0x12C]
#RPM_OFFSETS = [0x4, 0x4, 0x14, 0x90, 0x12C]

# 10 4 24 1C
# 4 4 24 1c
# 18

# 68 0 24 84 15C
#      34 60
# 74 28 f8 15c

def get_pointer_address(pm, base, offsets):
    """Follows the pointer chain to find the actual data address."""
    try:
        addr = pm.read_int(base)
        for offset in offsets[:-1]:
            addr = pm.read_int(addr + offset)
        return addr + offsets[-1]
    except Exception:
        return None

def main():
    try:
        # Connect to game
        pm = pymem.Pymem(PROCESS_NAME)
        game_module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        
        nos_base_addr = game_module + NOS_STATIC_OFFSET
        gear_base_addr = game_module + GEAR_STATIC_OFFSET
        rpm_base_addr = game_module + RPM_STATIC_OFFSET 
        speed = game_module + SPEED_STATIC_OFFSET
        
        print("=== SPEED.EXE TRAINER ACTIVE ===")
        print("[-] NOS auto-refills when below 5%.")
        print("[-] Press '0' to manually refill NOS.")
        print("[-] Press 'q' to exit the program.\n")

        while True:
            # Check addresses every loop
            final_nos_addr = get_pointer_address(pm, nos_base_addr, NOS_OFFSETS)
            final_gear_addr = get_pointer_address(pm, gear_base_addr, GEAR_OFFSETS)
            final_rpm_addr = get_pointer_address(pm, rpm_base_addr, RPM_OFFSETS)


            if final_nos_addr and final_gear_addr:
                try:
                    # NOS OKUMA (Float)
                    nos_val = pm.read_float(final_nos_addr)
                    nos_percentage = max(0.0, min(1.0, nos_val)) * 100
                    
                    # GEAR READ (Integer)
                    current_gear = pm.read_int(final_gear_addr)
                    
                    # RPM OKUMA (Float)
                    current_rpm = pm.read_float(final_rpm_addr)
                    
                    speed_val = pm.read_float(speed)
                    


                    # --- NEW GEAR LOGIC ---
                    if current_gear == 0:
                        gear_display = "R"
                    elif current_gear == 1:
                        gear_display = "N"
                    else:
                        gear_display = str(current_gear - 1) 
                    # --------------------------

                    print(f"Speed: {speed_val:.0f} |RPM: {current_rpm:.0f} |Gear: {gear_display} | NOS: %{nos_percentage:.1f}      ", end="\r")

                    # Cheat Operations
                    if nos_percentage <= 5.0 or keyboard.is_pressed('0'):
                        pm.write_float(final_nos_addr, 1.0)
                if keyboard.is_pressed('0'):
                     print("\n[!] NOS Refilled!          ")
                    
                    if keyboard.is_pressed('e'):
                        pm.write_float(final_rpm_addr, 100000.0)
                        print("\n[!] RPM 5000!          ")

                except Exception:
                    pass

            if keyboard.is_pressed('q'):
                break
            
            time.sleep(0.05)

    except Exception as e:
        print(f"\nError: {e}")
        print("Don't forget to run as administrator.")

if __name__ == "__main__":
    main()