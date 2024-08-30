import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel, QGroupBox, QTextEdit
from PyQt5.QtCore import Qt, QTimer
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

        # Information Box
        info_group = QGroupBox("GPU Information")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

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

            button = QPushButton('Apply')
            button.clicked.connect(lambda _, s=slider, i=i: self.set_speed(s.value(), i))

            fan_layout.addLayout(slider_layout)
            fan_layout.addWidget(button)
            fan_group.setLayout(fan_layout)
            layout.addWidget(fan_group)

        self.setLayout(layout)

        # Set up timer for updating GPU information
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gpu_info)
        self.timer.start(5000)  # Update every 5 seconds

        # Initial update
        self.update_gpu_info()

    def update_label(self, value, label):
        label.setText(f'{value}%')

    def set_speed(self, speed, fan_index):
        try:
            subprocess.run(['sudo', '-E', './set_fan.sh', str(speed), str(fan_index)], check=True)
            print(f"Fan {fan_index} speed set to {speed}%")
        except subprocess.CalledProcessError as e:
            print(f"Error setting fan speed: {e}")

    def update_gpu_info(self):
        try:
            # Get GPU model, temperature, and driver version
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,temperature.gpu,driver_version', '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
            gpu_info = result.stdout.strip().split(',')
            
            # Get fan speeds
            fan_speeds = []
            for i in range(self.fan_count):
                result = subprocess.run(['nvidia-settings', '-q', f'[fan:{i}]/GPUCurrentFanSpeed', '-t'], 
                                        capture_output=True, text=True, check=True)
                fan_speeds.append(result.stdout.strip())

            # Format the information
            info = f"<b>GPU Model: {gpu_info[0]}</b><br>"
            info += f"Driver Version: {gpu_info[2]}<br>"
            info += "<br>"
            info += f"<b>Temperature: {gpu_info[1]}°C</b><br>"
            for i, speed in enumerate(fan_speeds):
                info += f"Fan {i} Speed: {speed}%<br>"

            self.info_text.setText(info)

        except subprocess.CalledProcessError as e:
            print(f"Error getting GPU information: {e}")
            self.info_text.setText("Error fetching GPU information")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FanControlApp()
    ex.show()
    sys.exit(app.exec_())