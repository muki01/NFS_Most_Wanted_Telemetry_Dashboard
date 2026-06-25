import pymem
import pymem.process
import time
import keyboard

# --- AYARLAR ---
PROCESS_NAME = "tomb123.exe"
MODULE_NAME = "tomb2.dll" 

# Hedef Değerler
HP_VALUE = 1000
AMMO_VALUE = 950
MEDKIT_VALUE = 100
AIR_VALUE = 1800 
JUMP_FORCE = -150

# Ofsetler (Dinamik - Player Base üzerinden)
PLAYER_BASE = 0x025B23A0
HP_OFFSET = 0x22
VELOCITY_OFFSET = 0x20
Y_COORD_OFFSET = 0x1C

# Ofsetler (Statik - Modül üzerinden)
# Yeni eklenen Uzi: 0x2CA550
AMMO_OFFSETS = [0x2CA578, 0x2CA548, 0x2CA558, 0x2CA550] 
MEDKIT_OFFSETS = [0x1206D4, 0x1206D8]

# KRİTİK: Senin what writes çıktın A416'ya (A414+2) yazıyordu.
# Eğer hala azalırsa bu ofseti 0x2CA414 yaparak dene.
AIR_OFFSET = 0x2CA416 

def tomb_raider_ultimate_cheat():
    last_height = None
    try:
        pm = pymem.Pymem(PROCESS_NAME)
        module = pymem.process.module_from_name(pm.process_handle, MODULE_NAME).lpBaseOfDll
        
        print(f"--- Tomb Raider II: Ultimate Cheat Seti Aktif ---")
        print(f"[+] Silahlar: Shotgun, Uzi, Pistols ve fazlası kilitli.")
        print(f"[+] Envanter: Büyük/Küçük Medkitler kilitli.")
        print(f"[+] Nefes: Sınırsız (Adres: {hex(module + AIR_OFFSET)})")
        print(f"[+] Hareket: X = Yüksel, Z = Havada Sabitle")
        print(f"--------------------------------------------------")

        while True:
            try:
                # 1. NEFES SABİTLEME (2-Byte / Short)
                pm.write_short(module + AIR_OFFSET, AIR_VALUE)

                # 2. OYUNCU İŞLEMLERİ
                p_ptr = pm.read_longlong(module + PLAYER_BASE)
                if p_ptr > 0:
                    # Can Sabitle
                    pm.write_short(p_ptr + HP_OFFSET, HP_VALUE)

                    # X Tuşu - Yükselme
                    if keyboard.is_pressed('x'):
                        pm.write_short(p_ptr + VELOCITY_OFFSET, JUMP_FORCE)
                        last_height = None 

                    # Z Tuşu - Havada Sabitleme
                    if keyboard.is_pressed('z'):
                        if last_height is None:
                            last_height = pm.read_int(p_ptr + Y_COORD_OFFSET)
                        pm.write_int(p_ptr + Y_COORD_OFFSET, last_height)
                        pm.write_short(p_ptr + VELOCITY_OFFSET, 0)
                    else:
                        last_height = None

                # 3. MERMİLER (4-Byte / Int)
                for ammo in AMMO_OFFSETS:
                    pm.write_int(module + ammo, AMMO_VALUE)

                # 4. MEDKİTLER (2-Byte / Short)
                for med in MEDKIT_OFFSETS:
                    pm.write_short(module + med, MEDKIT_VALUE)

                # Döngü hızı
                time.sleep(0.01) 

            except Exception:
                continue

    except Exception as e:
        print(f"[-] Hata: {e}")

if __name__ == "__main__":
    tomb_raider_ultimate_cheat()