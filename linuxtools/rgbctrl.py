import sys
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QColorDialog, QGridLayout, QMessageBox,
                             QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, QLabel)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

class RAMLEDController(QWidget):
    def __init__(self):
        super().__init__()
        self.initOpenRGB()
        self.initUI()

    def initOpenRGB(self):
        try:
            print("Attempting to connect to OpenRGB server...")
            self.client = OpenRGBClient()
            print("Connected successfully!")
            print("Detected devices:")
            for device in self.client.devices:
                print(f"- {device.name}")
            self.devices = [device for device in self.client.devices if "Corsair" in device.name and "RAM" in device.type.name]
            if not self.devices:
                raise ValueError("No Corsair RAM found")
            print(f"Found {len(self.devices)} Corsair RAM device(s)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize OpenRGB: {str(e)}")
            sys.exit(1)

    def initUI(self):
        self.setWindowTitle('Corsair RAM LED Controller')
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left panel with RAM list
        left_panel = QVBoxLayout()
        
        # Add "Devices:" label
        devices_label = QLabel("Devices:")
        devices_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_panel.addWidget(devices_label)
        
        self.ram_list = QListWidget()
        self.ram_list.addItem("All RAM")
        for i, device in enumerate(self.devices):
            self.ram_list.addItem(f"RAM {i+1}: {device.name}")
        self.ram_list.currentRowChanged.connect(self.on_ram_selected)
        left_panel.addWidget(self.ram_list)
        main_layout.addLayout(left_panel)

        # Right panel with LED controls
        right_panel = QVBoxLayout()
        self.stacked_widget = QStackedWidget()
        all_ram_widget = self.create_device_widget(None)  # Widget for controlling all RAM
        self.stacked_widget.addWidget(all_ram_widget)
        for device in self.devices:
            device_widget = self.create_device_widget(device)
            self.stacked_widget.addWidget(device_widget)
        right_panel.addWidget(self.stacked_widget)
        main_layout.addLayout(right_panel)

        self.setGeometry(100, 100, 600, 400)
        self.show()

    def create_device_widget(self, device):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Color presets
        preset_layout = QHBoxLayout()
        presets = [('Red', Qt.red), ('Green', Qt.green), ('Blue', Qt.blue), 
                   ('White', Qt.white), ('Yellow', Qt.yellow), ('Purple', Qt.magenta)]
        for name, color in presets:
            btn = QPushButton(name)
            btn.setStyleSheet(f"background-color: {QColor(color).name()}; color: {'black' if name in ['White', 'Yellow'] else 'white'};")
            btn.clicked.connect(lambda _, c=color, d=device: self.apply_color_to_device(d, c))
            preset_layout.addWidget(btn)
        layout.addLayout(preset_layout)

        # Custom color button
        custom_color_btn = QPushButton("Custom Color")
        custom_color_btn.clicked.connect(lambda _, d=device: self.choose_custom_color(d))
        layout.addWidget(custom_color_btn)

        # LED buttons (only for individual RAM devices)
        if device is not None:
            led_layout = QGridLayout()
            for i, led in enumerate(device.leds):
                btn = QPushButton(f'LED {i+1}')
                btn.clicked.connect(lambda _, d=device, led_index=i: self.choose_color(d, led_index))
                led_layout.addWidget(btn, i // 4, i % 4)
            layout.addLayout(led_layout)

        return widget

    def on_ram_selected(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def choose_custom_color(self, device):
        color = QColorDialog.getColor()
        if color.isValid():
            self.apply_color_to_device(device, color)

    def apply_color_to_device(self, device, color):
        qcolor = QColor(color)
        rgb_color = RGBColor(qcolor.red(), qcolor.green(), qcolor.blue())
        if device is None:  # Apply to all RAM
            for dev in self.devices:
                dev.set_colors([rgb_color] * len(dev.leds))
            self.update_all_led_buttons(qcolor)
        else:  # Apply to specific RAM
            device.set_colors([rgb_color] * len(device.leds))
            self.update_led_buttons(device, qcolor)

    def choose_color(self, device, led_index):
        color = QColorDialog.getColor()
        if color.isValid():
            rgb_color = RGBColor(color.red(), color.green(), color.blue())
            new_colors = device.colors
            new_colors[led_index] = rgb_color
            device.set_colors(new_colors)
            self.update_led_buttons(device, color, led_index)

    def update_led_buttons(self, device, color, specific_led=None):
        device_index = self.devices.index(device) + 1  # +1 because "All RAM" is at index 0
        widget = self.stacked_widget.widget(device_index)
        led_layout = widget.layout().itemAt(2).layout()
        for i in range(led_layout.count()):
            if specific_led is None or i == specific_led:
                led_layout.itemAt(i).widget().setStyleSheet(f'background-color: {color.name()}')

    def update_all_led_buttons(self, color):
        for i in range(1, self.stacked_widget.count()):  # Start from 1 to skip "All RAM" widget
            widget = self.stacked_widget.widget(i)
            led_layout = widget.layout().itemAt(2).layout()
            for j in range(led_layout.count()):
                led_layout.itemAt(j).widget().setStyleSheet(f'background-color: {color.name()}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = RAMLEDController()
    sys.exit(app.exec_())
