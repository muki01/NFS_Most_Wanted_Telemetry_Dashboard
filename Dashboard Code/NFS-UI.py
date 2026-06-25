import sys
import math
import pymem
import pymem.process
import keyboard
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush

# UI Sınıfını içe aktar
from ui_nfs import Ui_UltimateRacingDash

# --- Bellek Adresleri ---
PROCESS_NAME = "speed.exe"
SPEED_STATIC_OFFSET = 0x514654
RPM_STATIC_OFFSET = 0x50D670
RPM_OFFSETS = [0x4, 0x4, 0x6C, 0x12C]
GEAR_STATIC_OFFSET = 0x50D670
GEAR_OFFSETS = [0x68, 0x4, 0x8, 0x10, 0x84]
NOS_BASE_OFFSET = 0x50D670
NOS_OFFSETS = [0x68, 0x4, 0x8, 0x10, 0xF8]

class UltimateRacingDash(QWidget):
    def __init__(self):
        super().__init__()
        
        # UI Kurulumu (QtDesigner tarzı)
        self.ui = Ui_UltimateRacingDash()
        self.ui.setupUi(self)
        
        # Değişkenler
        self.pm = None
        self.game_module = None
        self.speed = 0.0
        self.rpm = 0.0
        self.gear = "N"
        self.nos = 1.0
        self.nitro_hack_enabled = False # Yeni: Nitro hilesi durumu
        
        self.drag_pos = None 
        self.is_fullscreen = False
        
        # Buton Bağlantıları
        self.ui.closeBtn.clicked.connect(self.close)
        self.ui.nitroBtn.clicked.connect(self.toggle_nitro_hack)

        self.connect_game()
        
        # Güncelleme Zamanlayıcısı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(16) 

    def toggle_nitro_hack(self):
        self.nitro_hack_enabled = not self.nitro_hack_enabled
        self.ui.updateStyles(self.nitro_hack_enabled)
        # Eğer aktifse hemen full yap
        if self.nitro_hack_enabled:
            self.nos = 1.0

    # Pencere boyutu değiştikçe butonları yerleştir
    def resizeEvent(self, event):
        w, h = self.width(), self.height()
        scale = min(w / 1000, h / 400)
        self.ui.repositionWidgets(w, h, scale)
        super().resizeEvent(event)

    # --- Olay İşleyiciler (Event Handlers) ---
    def mouseDoubleClickEvent(self, event):
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    # --- Oyun Mantığı (Game Logic) ---
    def connect_game(self):
        try:
            self.pm = pymem.Pymem(PROCESS_NAME)
            self.game_module = pymem.process.module_from_name(self.pm.process_handle, PROCESS_NAME).lpBaseOfDll
        except: 
            self.pm = None

    def get_pointer_address(self, base, offsets):
        try:
            addr = self.pm.read_int(base)
            for offset in offsets[:-1]: 
                addr = self.pm.read_int(addr + offset)
            return addr + offsets[-1]
        except: 
            return None

    def update_all(self):
        if keyboard.is_pressed('q'): sys.exit()
        if not self.pm: 
            self.connect_game()
            self.update()
            return
            
        try:
            # Hız Okuma
            raw_speed = self.pm.read_float(self.game_module + SPEED_STATIC_OFFSET)
            self.speed += (abs(raw_speed * 1.609) - self.speed) * 0.15
            
            # RPM Okuma
            rpm_addr = self.get_pointer_address(self.game_module + RPM_STATIC_OFFSET, RPM_OFFSETS)
            if rpm_addr:
                target_rpm = abs(self.pm.read_float(rpm_addr))
                self.rpm += (target_rpm - self.rpm) * 0.2

            # Vites Okuma
            gear_addr = self.get_pointer_address(self.game_module + GEAR_STATIC_OFFSET, GEAR_OFFSETS)
            if gear_addr:
                gear_raw = self.pm.read_int(gear_addr)
                self.gear = {0: "R", 1: "N"}.get(gear_raw, str(max(1, gear_raw - 1)))

            # Nitro Okuma/Yazma
            nos_addr = self.get_pointer_address(self.game_module + NOS_BASE_OFFSET, NOS_OFFSETS)
            if nos_addr:
                if self.nitro_hack_enabled or keyboard.is_pressed('0'):
                    self.pm.write_float(nos_addr, 1.0)
                    self.nos = 1.0
                else:
                    self.nos = self.pm.read_float(nos_addr)
            
            self.update() # paintEvent'i tetikler
        except: 
            self.pm = None

    # --- Çizim Mantığı (UI Rendering) ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w, h = self.width(), self.height()
        scale = min(w / 1000, h / 400)

        # Arka Plan
        painter.setBrush(QColor(12, 14, 18))
        painter.setPen(Qt.NoPen)
        if not self.is_fullscreen:
            painter.drawRoundedRect(QRectF(0, 0, w, h), 25 * scale, 25 * scale)
        else:
            painter.drawRect(self.rect())

        # UI Çizimi (ui_nfs.py'den gelen metodlar)
        radius = 185 * scale
        rpm_center = QPointF(w * 0.22, h * 0.5) 
        speed_center = QPointF(w * 0.78, h * 0.5)

        self.ui.draw_modern_gauge(painter, rpm_center, radius, self.rpm, self.ui.max_rpm, "TACHOMETER", "RPM", True, scale)
        self.ui.draw_modern_gauge(painter, speed_center, radius, self.speed, self.ui.max_kmh, "SPEEDOMETER", "KM/H", False, scale)
        self.ui.draw_center_console(painter, w, h, scale, self.gear, self.nos)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UltimateRacingDash()
    ex.show()
    sys.exit(app.exec_())