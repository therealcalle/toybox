import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel
from PyQt5.QtCore import Qt
import subprocess

class FanControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('GPU Fan Control')
        layout = QVBoxLayout()

        # Slider
        slider_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(30)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider_label = QLabel('50%')
        self.slider.valueChanged.connect(self.update_label)
        slider_layout.addWidget(QLabel('GPU Fan Speed:'))
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.slider_label)

        # Button
        self.button = QPushButton('Set Speed')
        self.button.clicked.connect(self.set_speed)

        layout.addLayout(slider_layout)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def update_label(self, value):
        self.slider_label.setText(f'{value}%')

    def set_speed(self):
        speed = self.slider.value()
        try:
            subprocess.run(['sudo', '-E', './set_fan.sh', str(speed)], check=True)
            print(f"Fan speed set to {speed}%")
        except subprocess.CalledProcessError as e:
            print(f"Error setting fan speed: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FanControlApp()
    ex.show()
    sys.exit(app.exec_())