import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel, QGroupBox
from PyQt5.QtCore import Qt
import subprocess

class FanControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.fan_count = self.get_fan_count()
        self.initUI()

    def get_fan_count(self):
        try:
            result = subprocess.run(['nvidia-settings', '-q', 'fans'], capture_output=True, text=True, check=True)
            output = result.stdout
            fan_count = output.count('[fan:')
            return max(fan_count, 1)
        except subprocess.CalledProcessError as e:
            print(f"Error getting fan count: {e}")
            return 1

    def initUI(self):
        self.setWindowTitle('GPU Fan Control')
        layout = QVBoxLayout()

        for i in range(self.fan_count):
            fan_group = QGroupBox(f"Fan {i}")
            fan_layout = QVBoxLayout()

            slider_layout = QHBoxLayout()
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(30)
            slider.setMaximum(100)
            slider.setValue(50)
            slider_label = QLabel('50%')
            slider.valueChanged.connect(lambda value, label=slider_label: self.update_label(value, label))
            slider_layout.addWidget(QLabel('Speed:'))
            slider_layout.addWidget(slider)
            slider_layout.addWidget(slider_label)

            button = QPushButton('Set Speed')
            button.clicked.connect(lambda _, s=slider, i=i: self.set_speed(s.value(), i))

            fan_layout.addLayout(slider_layout)
            fan_layout.addWidget(button)
            fan_group.setLayout(fan_layout)
            layout.addWidget(fan_group)

        self.setLayout(layout)

    def update_label(self, value, label):
        label.setText(f'{value}%')

    def set_speed(self, speed, fan_index):
        try:
            subprocess.run(['sudo', '-E', './set_fan.sh', str(speed), str(fan_index)], check=True)
            print(f"Fan {fan_index} speed set to {speed}%")
        except subprocess.CalledProcessError as e:
            print(f"Error setting fan speed: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FanControlApp()
    ex.show()
    sys.exit(app.exec_())