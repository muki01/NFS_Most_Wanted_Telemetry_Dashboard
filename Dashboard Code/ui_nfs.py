import math
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush

class Ui_UltimateRacingDash(object):
    def setupUi(self, UltimateRacingDash):
        UltimateRacingDash.setObjectName("UltimateRacingDash")
        UltimateRacingDash.resize(1000, 400)
        UltimateRacingDash.setMinimumSize(500, 200)
        UltimateRacingDash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        UltimateRacingDash.setAttribute(Qt.WA_TranslucentBackground)
        
        # --- Kapatma Butonu ---
        self.closeBtn = QPushButton("✕", UltimateRacingDash)
        self.closeBtn.setObjectName("closeBtn")
        self.closeBtn.setFixedSize(40, 40)
        
        # --- Sonsuz Nitro Butonu ---
        self.nitroBtn = QPushButton("INF NITRO", UltimateRacingDash)
        self.nitroBtn.setObjectName("nitroBtn")
        self.nitroBtn.setFixedSize(120, 35)

        # Buton Stilleri (Premium Dashboard Görünümü)
        self.updateStyles(False) # Başlangıçta nitro kapalı

        # UI Constants
        self.start_angle = 225
        self.sweep_angle = -270
        self.max_kmh = 400.0
        self.max_rpm = 10000.0

    def updateStyles(self, nitro_active):
        # Kapatma Butonu Stili
        self.closeBtn.setStyleSheet("""
            QPushButton {
                background-color: rgba(20, 20, 25, 150);
                border: 1px solid rgba(255, 50, 50, 100);
                color: rgba(255, 50, 50, 200);
                font-size: 18px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 50, 50, 100);
                border: 1px solid rgba(255, 50, 50, 255);
                color: white;
            }
        """)

        # Nitro Butonu Stili (Toggle etkili)
        nitro_color = "0, 255, 180" if nitro_active else "100, 110, 120"
        bg_alpha = "80" if nitro_active else "40"
        
        self.nitroBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({nitro_color}, {bg_alpha});
                border: 2px solid rgba({nitro_color}, 150);
                color: white;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba({nitro_color}, 120);
                border: 2px solid rgba({nitro_color}, 255);
            }}
        """)

    def repositionWidgets(self, w, h, scale):
        # Butonları dinamik olarak konumlandır (Tam ekran uyumlu)
        self.closeBtn.move(w - 50, 10)
        
        # Nitro butonunu vites kutusunun hemen üzerine koy
        center_x = w / 2
        center_y = h / 2
        self.nitroBtn.move(int(center_x - (60)), int(center_y - 125 * scale))

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

    def draw_center_console(self, painter, w, h, scale, gear, nos):
        center_x = w / 2
        center_y = h / 2

        # --- Vites Kutusu ---
        gw, gh = 120 * scale, 150 * scale
        gear_rect = QRectF(center_x - (gw/2), center_y - (gh/2) - (20 * scale), gw, gh)
        
        painter.setBrush(QColor(8, 10, 12))
        painter.setPen(QPen(QColor(0, 220, 255, 150), 2 * scale))
        painter.drawRoundedRect(gear_rect, 15 * scale, 15 * scale)

        painter.setFont(QFont("Segoe UI", int(12 * scale), QFont.Bold))
        painter.setPen(QColor(100, 110, 120))
        painter.drawText(QRectF(center_x - (gw/2), gear_rect.top() + (5 * scale), gw, 30 * scale), Qt.AlignCenter, "GEAR")

        painter.setFont(QFont("Segoe UI Black", int(85 * scale)))
        gear_color = QColor(255, 50, 50) if gear == "R" else QColor(255, 255, 255)
        painter.setPen(gear_color)
        
        text_rect = QRectF(gear_rect.left(), gear_rect.top() + (20 * scale), gw, gh - (20 * scale))
        painter.drawText(text_rect, Qt.AlignCenter, str(gear))

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
            if nos > fill_threshold:
                painter.setBrush(QColor(0, 255, 180)) 
            else:
                painter.setBrush(QColor(30, 35, 40))
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)
