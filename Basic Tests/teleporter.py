import pymem
import pymem.process
import keyboard
import time

# --- Settings ---
PROCESS_NAME = "speed.exe"
ADDR_X = 0x5386E0
ADDR_Y = 0x5386DC  # Height
ADDR_Z = 0x5386D8

# Sabit Konumlar
LOC_1 = (2105.0, 164.0, -1440.0)
LOC_2 = (1929.0, 160.0, -1866.0)

def get_current_y(pm, game_module):
    """Reads the current height from memory."""
    try:
        return pm.read_float(game_module + ADDR_Y)
    except:
        return None

def set_coords(pm, game_module, x=None, y=None, z=None):
    """Writes the specified coordinates to memory."""
    try:
        if x is not None: pm.write_float(game_module + ADDR_X, x)
        if y is not None: pm.write_float(game_module + ADDR_Y, y)
        if z is not None: pm.write_float(game_module + ADDR_Z, z)
        return True
    except:
        return False

def main():
    try:
        pm = pymem.Pymem(PROCESS_NAME)
        game_module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        print("--- NFS:MW 2005 Advanced Coordinate System ---")
        print("1: Go to Location 1")
        print("2: Go to Location 2")
        print("3: Increase Height +20 (Jump)")
        print("Q: Exit")
    except Exception as e:
        print(f"Error: Game not found! ({e})")
        return

    while True:
        event = keyboard.read_event()
        
        if event.event_type == keyboard.KEY_DOWN:
            # KONUM 1
            if event.name == '1':
                set_coords(pm, game_module, *LOC_1)
                print(f"[!] Teleported to Location 1.")

            # KONUM 2
            elif event.name == '2':
                set_coords(pm, game_module, *LOC_2)
                print(f"[!] Teleported to Location 2.")

            # HEIGHT +20 (JUMP)
            elif event.name == '3':
                current_y = get_current_y(pm, game_module)
                if current_y is not None:
                    new_y = current_y + 20.0
                    set_coords(pm, game_module, y=new_y)
                    print(f"[^] Height Increased: {current_y:.2f} -> {new_y:.2f}")

            # EXIT
            elif event.name == 'q':
                print("Shutting down...")
                break

        time.sleep(0.01)

if __name__ == "__main__":
    main()