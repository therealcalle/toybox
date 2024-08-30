import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel, QGroupBox, QTextEdit, QComboBox, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
import subprocess

class FanControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.fan_count = self.get_fan_count()
        self.profiles = self.load_profiles()
        self.current_profile = "Manual"
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

    def load_profiles(self):
        try:
            with open('fan_profiles.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"Manual": {}, "Automatic": {}}

    def save_profiles(self):
        with open('fan_profiles.json', 'w') as f:
            json.dump(self.profiles, f)

    def initUI(self):
        self.setWindowTitle('GPU Fan Control')
        layout = QVBoxLayout()

        # Profile selection
        profile_layout = QHBoxLayout()
        self.profile_combo = QComboBox()

        unique_profiles = list(set(["Manual", "Automatic"] + list(self.profiles.keys())))
        self.profile_combo.addItems(unique_profiles)

        # self.profile_combo.addItems(["Manual", "Automatic"] + list(self.profiles.keys()))

        self.profile_combo.currentTextChanged.connect(self.change_profile)
        profile_layout.addWidget(QLabel("Profile:"))
        profile_layout.addWidget(self.profile_combo)
        save_profile_btn = QPushButton("Save Profile")
        save_profile_btn.clicked.connect(self.save_profile)
        profile_layout.addWidget(save_profile_btn)
        delete_profile_btn = QPushButton("Delete Profile")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_layout.addWidget(delete_profile_btn)
        layout.addLayout(profile_layout)

        # Information Box
        info_group = QGroupBox("GPU Information")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Fan controls
        self.fan_sliders = []
        for i in range(self.fan_count):
            fan_group = QGroupBox(f"Fan {i}")
            fan_layout = QVBoxLayout()

            slider_layout = QHBoxLayout()
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(30)
            slider.setMaximum(100)
            slider.setValue(50)
            self.fan_sliders.append(slider)
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

            # Automatic mode
            if self.current_profile == "Automatic":
                self.adjust_fan_speed_auto(int(gpu_info[1]))

        except subprocess.CalledProcessError as e:
            print(f"Error getting GPU information: {e}")
            self.info_text.setText("Error fetching GPU information")

    """ def adjust_fan_speed_auto(self, temp):
        if temp < 50:
            speed = 30
        elif temp < 70:
            speed = 50
        else:
            speed = 80
        
        for i in range(self.fan_count):
            self.set_speed(speed, i)
            self.fan_sliders[i].setValue(speed) """
    
    def adjust_fan_speed_auto(self, temp):
        if temp < 50:
            desired_speed = 30
        elif temp < 70:
            desired_speed = 50
        else:
            desired_speed = 80

        for i in range(self.fan_count):
            try:
                # Get current fan speed
                result = subprocess.run(['nvidia-settings', '-q', f'[fan:{i}]/GPUCurrentFanSpeed', '-t'], capture_output=True, text=True, check=True)
                current_speed = int(result.stdout.strip())
            except subprocess.CalledProcessError as e:
                print(f"Error fetching current fan speed for fan {i}: {e}")
                continue

            # Only update if the desired speed is different from the current speed
            if current_speed != desired_speed:
                self.set_speed(desired_speed, i)
                self.fan_sliders[i].setValue(desired_speed)


    def change_profile(self, profile_name):
        self.current_profile = profile_name
        if profile_name in self.profiles:
            for i, speed in enumerate(self.profiles[profile_name]):
                if i < self.fan_count:
                    self.fan_sliders[i].setValue(speed)
                    self.set_speed(speed, i)

    def save_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if ok and name:
            self.profiles[name] = [slider.value() for slider in self.fan_sliders]
            self.save_profiles()
            if not any(name == self.profile_combo.itemText(i) for i in range(self.profile_combo.count())):
                self.profile_combo.addItem(name)
            QMessageBox.information(self, "Profile Saved", f"Profile '{name}' has been saved.")

    def delete_profile(self):
        name = self.profile_combo.currentText()
        if name not in ["Manual", "Automatic"]:
            del self.profiles[name]
            self.save_profiles()
            self.profile_combo.removeItem(self.profile_combo.findText(name))
            QMessageBox.information(self, "Profile Deleted", f"Profile '{name}' has been deleted.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FanControlApp()
    ex.show()
    sys.exit(app.exec_())