import sys
import math
import pymem
import pymem.process
import keyboard
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QRegion, QPainterPath

# --- Bellek Adresleri (Aynı Kaldı) ---
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
        self.pm = None
        self.game_module = None
        
        self.speed = 0.0
        self.rpm = 0.0
        self.gear = "N"
        self.nos = 1.0
        
        self.start_angle = 225 
        self.sweep_angle = -270
        
        self.max_kmh = 400.0
        self.max_rpm = 10000.0
        
        self.drag_pos = None 
        self.is_fullscreen = False
        
        self.initUI()
        self.connect_game()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(16) 

    def initUI(self):
        self.resize(1000, 400)
        self.setMinimumSize(500, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.show()

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

    def connect_game(self):
        try:
            self.pm = pymem.Pymem(PROCESS_NAME)
            self.game_module = pymem.process.module_from_name(self.pm.process_handle, PROCESS_NAME).lpBaseOfDll
        except: self.pm = None

    def get_pointer_address(self, base, offsets):
        try:
            addr = self.pm.read_int(base)
            for offset in offsets[:-1]: addr = self.pm.read_int(addr + offset)
            return addr + offsets[-1]
        except: return None

    def update_all(self):
        if keyboard.is_pressed('q'): sys.exit()
        if not self.pm: self.connect_game(); self.update(); return
        try:
            raw_speed = self.pm.read_float(self.game_module + SPEED_STATIC_OFFSET)
            self.speed += (abs(raw_speed * 1.609) - self.speed) * 0.15
            
            rpm_addr = self.get_pointer_address(self.game_module + RPM_STATIC_OFFSET, RPM_OFFSETS)
            if rpm_addr:
                target_rpm = abs(self.pm.read_float(rpm_addr))
                self.rpm += (target_rpm - self.rpm) * 0.2

            gear_addr = self.get_pointer_address(self.game_module + GEAR_STATIC_OFFSET, GEAR_OFFSETS)
            if gear_addr:
                gear_raw = self.pm.read_int(gear_addr)
                self.gear = {0: "R", 1: "N"}.get(gear_raw, str(max(1, gear_raw - 1)))

            nos_addr = self.get_pointer_address(self.game_module + NOS_BASE_OFFSET, NOS_OFFSETS)
            if nos_addr:
                self.nos = self.pm.read_float(nos_addr)
                if self.nos < 0.05 or keyboard.is_pressed('0'):
                    self.pm.write_float(nos_addr, 1.0)
            self.update()
        except: self.pm = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w = self.width()
        h = self.height()
        scale = min(w / 1000, h / 400)

        # Arka plan çizimi (Kenar yumuşatma eklendi)
        painter.setBrush(QColor(12, 14, 18))
        painter.setPen(Qt.NoPen)
        
        if not self.is_fullscreen:
            # Tam ekran değilken köşeleri yuvarla (25px radyus)
            painter.drawRoundedRect(QRectF(0, 0, w, h), 25 * scale, 25 * scale)
        else:
            # Tam ekranken düz dikdörtgen
            painter.drawRect(self.rect())

        radius = 185 * scale
        rpm_center = QPointF(w * 0.22, h * 0.5) 
        speed_center = QPointF(w * 0.78, h * 0.5)

        self.draw_modern_gauge(painter, rpm_center, radius, self.rpm, self.max_rpm, "TACHOMETER", "RPM", True, scale)
        self.draw_modern_gauge(painter, speed_center, radius, self.speed, self.max_kmh, "SPEEDOMETER", "KM/H", False, scale)
        self.draw_center_console(painter, w, h, scale)

    def draw_modern_gauge(self, painter, center, radius, value, max_val, title, unit, is_rpm, scale):
        rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        painter.setPen(QPen(QColor(25, 28, 35), 14 * scale, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(rect, self.start_angle * 16, self.sweep_angle * 16)

        ratio = min(max(value, 0), max_val) / max_val
        active_span = self.sweep_angle * ratio
        
        if is_rpm:
            if value > 8500: active_color = QColor(255, 20, 50)  
            elif value > 7000: active_color = QColor(255, 180, 0) 
            else: active_color = QColor(0, 220, 255)                  
        else:
            active_color = QColor(0, 255, 150) if value < 320 else QColor(255, 50, 50)

        painter.setPen(QPen(QColor(active_color.red(), active_color.green(), active_color.blue(), 60), 22 * scale, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(rect, self.start_angle * 16, int(active_span) * 16)
        
        painter.setPen(QPen(active_color, 10 * scale, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(rect, self.start_angle * 16, int(active_span) * 16)

        step = 1000 if is_rpm else 50
        minor_step = 250 if is_rpm else 10
        
        for i in range(0, int(max_val) + 1, minor_step):
            angle_deg = self.start_angle + (i / max_val * self.sweep_angle)
            angle_rad = math.radians(-angle_deg) 
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            if i % step == 0:
                p1 = center + QPointF(cos_a * (radius - (12 * scale)), sin_a * (radius - (12 * scale)))
                p2 = center + QPointF(cos_a * (radius + (2 * scale)), sin_a * (radius + (2 * scale)))
                painter.setPen(QPen(QColor(200, 200, 200), max(1, 2 * scale)))
                painter.drawLine(p1, p2)
                
                text_radius = radius - (35 * scale)
                text_p = center + QPointF(cos_a * text_radius, sin_a * text_radius)
                painter.setFont(QFont("Segoe UI", int(11 * scale), QFont.Bold))
                display_val = str(i // 1000) if is_rpm else str(i)
                text_color = QColor(255, 80, 80) if (is_rpm and i >= 8000) or (not is_rpm and i >= 350) else QColor(220, 220, 220)
                painter.setPen(text_color)
                painter.drawText(int(text_p.x() - 20 * scale), int(text_p.y() - 10 * scale), int(40 * scale), int(20 * scale), Qt.AlignCenter, display_val)

        painter.setFont(QFont("Segoe UI", int(10 * scale), QFont.Medium))
        painter.setPen(QColor(120, 130, 140))
        painter.drawText(QRectF(center.x() - 60 * scale, center.y() - 65 * scale, 120 * scale, 20 * scale), Qt.AlignCenter, title)
        
        painter.setFont(QFont("Segoe UI Black", int(48 * scale)))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - 100 * scale, center.y() - 40 * scale, 200 * scale, 80 * scale), Qt.AlignCenter, f"{int(value)}")
        
        painter.setFont(QFont("Segoe UI", int(12 * scale), QFont.Bold))
        painter.setPen(active_color)
        painter.drawText(QRectF(center.x() - 50 * scale, center.y() + 45 * scale, 100 * scale, 25 * scale), Qt.AlignCenter, unit)

    def draw_center_console(self, painter, w, h, scale):
        center_x = w / 2
        center_y = h / 2

        # --- Vites Kutusu (Boyutlar artırıldı) ---
        gw, gh = 120 * scale, 150 * scale  # Genişlik ve yükseklik büyütüldü
        # Kutuyu biraz daha yukarı alarak merkeze oturttuk
        gear_rect = QRectF(center_x - (gw/2), center_y - (gh/2) - (20 * scale), gw, gh)
        
        # Kutu Arka Planı
        painter.setBrush(QColor(8, 10, 12))
        painter.setPen(QPen(QColor(0, 220, 255, 150), 2 * scale)) # Kenarlığa hafif bir renk katıldı
        painter.drawRoundedRect(gear_rect, 15 * scale, 15 * scale)

        # "GEAR" Yazısı
        painter.setFont(QFont("Segoe UI", int(12 * scale), QFont.Bold))
        painter.setPen(QColor(100, 110, 120))
        painter.drawText(QRectF(center_x - (gw/2), gear_rect.top() + (5 * scale), gw, 30 * scale), Qt.AlignCenter, "GEAR")

        # Vites Sayısı (Büyütüldü ve Ortalandı)
        painter.setFont(QFont("Segoe UI Black", int(85 * scale))) # Font 75'ten 85'e çıkarıldı
        gear_color = QColor(255, 50, 50) if self.gear == "R" else QColor(255, 255, 255)
        painter.setPen(gear_color)
        
        # Sayının tam kutu içinde kalması için alan hesaplaması
        # gear_rect içinde dikeyde tam ortalamak için offset verildi
        text_rect = QRectF(gear_rect.left(), gear_rect.top() + (20 * scale), gw, gh - (20 * scale))
        painter.drawText(text_rect, Qt.AlignCenter, str(self.gear))

        # --- Nitro Bölümü ---
        nos_y = gear_rect.bottom() + (10 * scale)
        painter.setFont(QFont("Segoe UI", int(10 * scale), QFont.Bold))
        painter.setPen(QColor(150, 160, 170))
        painter.drawText(QRectF(center_x - 50 * scale, nos_y, 100 * scale, 20 * scale), Qt.AlignCenter, "NITROUS")

        segment_count = 10
        segment_w = 14 * scale
        segment_h = 10 * scale
        spacing = 4 * scale
        total_w = (segment_count * segment_w) + ((segment_count - 1) * spacing)
        start_x = center_x - (total_w / 2)

        for i in range(segment_count):
            rect = QRectF(start_x + i * (segment_w + spacing), nos_y + 25 * scale, segment_w, segment_h)
            fill_threshold = i / segment_count
            if self.nos > fill_threshold:
                painter.setBrush(QColor(0, 255, 180)) 
            else:
                painter.setBrush(QColor(30, 35, 40))
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UltimateRacingDash()
    sys.exit(app.exec_())