from PyQt5 import QtWidgets, QtCore
import subprocess
import sys
import threading
import os
import tempfile
import re
import requests
import shutil
import glob
import zipfile
import subprocess

class InstallerApp(QtWidgets.QWidget):
    update_output = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hyprland hello world")
        self.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(5)  # Reduce overall spacing between widgets
        layout.setContentsMargins(10, 10, 10, 10)  # Adjust margins around the layout

        # Hyprland Config
        self.checkHyprland = QtWidgets.QCheckBox("Configure Hyprland")
        self.entryHyprland = QtWidgets.QLineEdit("Input link to Hyprland config files separated by a ','")
        self.entryHyprland.installEventFilter(self)

        layout.addWidget(self.checkHyprland, 0, 0)
        layout.addWidget(self.entryHyprland, 0, 1)

        # Waybar Modules
        self.checkWaybarModule = QtWidgets.QCheckBox("Install Waybar Modules")
        self.entryWaybarModule = QtWidgets.QLineEdit("Input link to Waybar module files separated by a ','")
        self.entryWaybarModule.installEventFilter(self)

        layout.addWidget(self.checkWaybarModule, 1, 0)
        layout.addWidget(self.entryWaybarModule, 1, 1)

        # Waybar Themes (New)
        self.checkWaybarTheme = QtWidgets.QCheckBox("Install Waybar Themes")
        self.entryWaybarTheme = QtWidgets.QLineEdit("Input link to Waybar dot files separated by a ','")
        self.entryWaybarTheme.installEventFilter(self)

        layout.addWidget(self.checkWaybarTheme, 2, 0)
        layout.addWidget(self.entryWaybarTheme, 2, 1)

        # Tools
        self.tools_labels = [
        "Firefox", "Brave", "Krita", "Discord", "Spotify", "Visual Studio Code", "Kitty", "NWG Look", "Nemo", "Gnome Calculator", "GeforceNow"
        ]
        self.tools_vars = {}
        tools_label = QtWidgets.QLabel("Tools")
        tools_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(tools_label, 3, 0, 1, 1)

        # Add checkboxes without additional space
        for i, label in enumerate(self.tools_labels):
          self.tools_vars[label] = QtWidgets.QCheckBox(label)
          layout.addWidget(self.tools_vars[label], 4 + i, 0, 1, 1)

        # Themes
        self.themes_labels = [
          "Grub", "Sddm", "Rofi", "Kitty", "Qt5ct", "Gtk", "Cursor", "Icons", "Gnome Calculator"
        ]
        self.themes_vars = {}
        themes_label = QtWidgets.QLabel("Themes")
        themes_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(themes_label, 3, 1, 1, 1)

        # Add checkboxes without additional space
        for i, label in enumerate(self.themes_labels):
          self.themes_vars[label] = QtWidgets.QCheckBox(label)
          layout.addWidget(self.themes_vars[label], 4 + i, 1, 1, 1)

        # Flavor label
        flavor_label = QtWidgets.QLabel("Choose your flavor:")
        layout.addWidget(flavor_label, 25, 0)

        # Dropdown flavor
        self.flavor = ["frappe", "macchiato", "latte", "mocha"]
        self.themeFlavor = QtWidgets.QComboBox()
        self.themeFlavor.addItems(self.flavor)
        layout.addWidget(self.themeFlavor, 25, 1)

        # Install button
        self.buttonInstall = QtWidgets.QPushButton("Install")
        self.buttonInstall.clicked.connect(self.execute_commands)
        layout.addWidget(self.buttonInstall, 26, 1)

        # Output area
        self.output_area = QtWidgets.QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area, 27, 0, 1, 2)

        self.setLayout(layout)

        # Connect the signal to update_output_area method
        self.update_output.connect(self.update_output_area)

    def eventFilter(self, obj, event):
      if event.type() == QtCore.QEvent.FocusIn:
        if obj.text().startswith("Input link to"):
            obj.clear()
      elif event.type() == QtCore.QEvent.FocusOut:
        if obj.text().strip() == "":
            if obj == self.entryHyprland:
                obj.setText("Input link to Hyprland config files separated by a ','")
            elif obj == self.entryWaybarModule:
                obj.setText("Input link to Waybar module files separated by a ','")
            elif obj == self.entryWaybarTheme:
                obj.setText("Input link to Waybar dot files separated by a ','")
      return super().eventFilter(obj, event)

    def execute_commands(self):
        # Start the installation in a separate thread
        threading.Thread(target=self._execute_commands_thread, daemon=True).start()

    def _execute_commands_thread(self):
        commands = {
            "Firefox": "paru -S --noconfirm firefox",
            "Brave": "paru -S --noconfirm brave-bin",
            "Krita": "paru -S --noconfirm krita",
            "Discord": "paru -S --noconfirm discord",
            "Spotify": "paru -S --noconfirm spotify-launcher",
            "Visual Studio Code": "paru -S --noconfirm visual-studio-code-bin",
            "Kitty": "paru -S --noconfirm kitty",
            "NWG Look": "paru -S --noconfirm nwg-look",
            "Nemo": "paru -S --noconfirm nemo",
            "Gnome Calculator": "paru -S --noconfirm gnome-calculator",
            "Gtk": "paru -S --noconfirm catppuccin-gtk-theme-{selected_flavor}",
            "Cursor": "paru -S --noconfirm catppuccin-cursors-{selected_flavor}",
            "GeforceNow": "paru -S --noconfirm geforcenow-electron",
            "Icons": [
                "paru -S --noconfirm papirus-icon-theme",
                "paru -S --noconfirm papirus-folders-catppuccin-git",
                "papirus-folders -C cat-{selected_flavor}-lavender --theme Papirus-Dark"
            ],
        }

        self.update_output.emit("Starting installation...\n")
        selected_flavor = self.themeFlavor.currentText()

        # Execute commands for tools and themes
        
        for label, cmd in commands.items():
            if self.tools_vars.get(label, QtWidgets.QCheckBox()).isChecked() or \
               self.themes_vars.get(label, QtWidgets.QCheckBox()).isChecked():
                self.update_output.emit(f"Installing {label}...\n")
                try:
                    if label == "Icons":
                        for single_cmd in cmd:
                            # Substitute the selected flavor in the command if applicable
                            if '{selected_flavor}' in single_cmd:
                                single_cmd = single_cmd.format(selected_flavor=selected_flavor)
                            result = subprocess.run(single_cmd, shell=True, text=True, capture_output=True, check=True)
                            self.update_output.emit(f"Successfully executed: {single_cmd}\n")
                    else:
                        if label in ["Gtk", "Cursor"]:
                            cmd = cmd.format(selected_flavor=selected_flavor)
                    result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
                    self.update_output.emit(f"Successfully installed {label}\n")
                except subprocess.CalledProcessError as e:
                    self.update_output.emit(f"Error installing {label}: {e.stderr}\n")

        # Handle Gnome Calculator fix

        if self.themes_vars["Gnome Calculator"].isChecked():
            selected_flavor = self.themeFlavor.currentText().lower()
            self.update_output.emit("Applying Gnome Calculator fix...\n")

            try:
                # Set GTK theme
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", f"catppuccin-{selected_flavor}-lavender-standard+default"], check=True)

                # Download and extract GTK theme
                gtk_theme_url = f"https://github.com/catppuccin/gtk/releases/download/v1.0.3/catppuccin-{selected_flavor}-lavender-standard+default.zip"
                gtk_theme_zip = os.path.expanduser(f"~/catppuccin-{selected_flavor}-gtk.zip")
        
                # Download the zip file
                response = requests.get(gtk_theme_url)
                with open(gtk_theme_zip, 'wb') as f:
                    f.write(response.content)

                # Extract the zip file
                with zipfile.ZipFile(gtk_theme_zip, 'r') as zip_ref:
                    zip_ref.extractall("/tmp/catppuccin-gtk")

                # Copy files to .config/gtk-4.0
                gtk_config_dir = os.path.expanduser("~/.config/gtk-4.0")
                os.makedirs(gtk_config_dir, exist_ok=True)

                shutil.copytree("/tmp/catppuccin-gtk/catppuccin-macchiato-lavender-standard+default/gtk-4.0/assets", os.path.join(gtk_config_dir, "assets"), dirs_exist_ok=True)
                shutil.copy2("/tmp/catppuccin-gtk/catppuccin-macchiato-lavender-standard+default/gtk-4.0/gtk.css", gtk_config_dir)
                shutil.copy2("/tmp/catppuccin-gtk/catppuccin-macchiato-lavender-standard+default/gtk-4.0/gtk-dark.css", gtk_config_dir)

                # Clean up
                os.remove(gtk_theme_zip)
                shutil.rmtree("/tmp/catppuccin-gtk")

                self.update_output.emit("Gnome Calculator fix applied successfully.\n")
            except Exception as e:
                self.update_output.emit(f"Error applying Gnome Calculator fix: {str(e)}\n")

        # Handle Hyprland configuration

        if self.checkHyprland.isChecked():
            config_links = self.entryHyprland.text().split(',')
            hyprland_config_dir = os.path.expanduser("~/.config/hypr")
            os.makedirs(hyprland_config_dir, exist_ok=True)
            for link in config_links:
                self.update_output.emit(f"Downloading Hyprland config from {link}\n")
                try:
                    response = requests.get(link.strip())
                    if response.status_code == 200:
                        filename = os.path.join(hyprland_config_dir, os.path.basename(link.strip()))
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        self.update_output.emit(f"Successfully downloaded and saved {filename}\n")
                    else:
                        self.update_output.emit(f"Failed to download from {link}. Status code: {response.status_code}\n")
                except Exception as e:
                  self.update_output.emit(f"Error downloading from {link}: {str(e)}\n")
        
        # Handle polkit fix

        if self.checkHyprland.isChecked():
            self.update_output.emit("Replacing KDE Polkit with Gnome Polkit...\n")

            try:
                # Install Gnome Polkit
                subprocess.run(["paru", "-S", "--noconfirm", "polkit-gnome"], check=True)

                # Update Hyprland config files
                hyprland_config_dir = os.path.expanduser("~/.config/hypr")
                polkit_line_replaced = False

                for filename in os.listdir(hyprland_config_dir):
                    if filename.endswith(".conf"):
                        file_path = os.path.join(hyprland_config_dir, filename)
                        with open(file_path, 'r') as f:
                            content = f.read()

                        if "exec-once = /usr/lib/polkit-kde-authentication-agent-1" in content:
                            content = content.replace(
                                "exec-once = /usr/lib/polkit-kde-authentication-agent-1",
                                "exec-once = /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1"
                            )
                            polkit_line_replaced = True
                        elif not polkit_line_replaced and "exec-once = /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1" not in content:
                            content += "\nexec-once = /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1"
                            polkit_line_replaced = True

                        with open(file_path, 'w') as f:
                            f.write(content)

                if polkit_line_replaced:
                    self.update_output.emit("Polkit replaced successfully in Hyprland config.\n")
                else:
                    self.update_output.emit("Polkit line was already updated or not found in Hyprland config.\n")

            except Exception as e:
                self.update_output.emit(f"Error replacing Polkit: {str(e)}\n")

        # Handle Waybar Modules installation

        if self.checkWaybarModule.isChecked():
          module_links = self.entryWaybarModule.text().split(',')
          waybar_module_dir = os.path.expanduser("~/.config/waybar/modules")
          os.makedirs(waybar_module_dir, exist_ok=True)

          for link in module_links:
              self.update_output.emit(f"Downloading Waybar module from {link}\n")
              try:
                    response = requests.get(link.strip())
                    if response.status_code == 200:
                        filename = os.path.join(waybar_module_dir, os.path.basename(link.strip()))
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        os.chmod(filename, 0o755)
                        self.update_output.emit(f"Successfully downloaded and saved {filename}\n")
                    else:
                        self.update_output.emit(f"Failed to download from {link}. Status code: {response.status_code}\n")
              except Exception as e:
                  self.update_output.emit(f"Error downloading from {link}: {str(e)}\n")
        
        # Handle Waybar Themes installation

        if self.checkWaybarTheme.isChecked():
            theme_links = self.entryWaybarTheme.text().split(',')
            waybar_config_dir = os.path.expanduser("~/.config/waybar")
            os.makedirs(waybar_config_dir, exist_ok=True)
        
            for link in theme_links:
                self.update_output.emit(f"Downloading Waybar theme from {link}\n")
                try:
                    response = requests.get(link.strip())
                    if response.status_code == 200:
                        filename = os.path.join(waybar_config_dir, os.path.basename(link.strip()))
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        self.update_output.emit(f"Successfully downloaded and saved {filename}\n")
                    else:
                        self.update_output.emit(f"Failed to download from {link}. Status code: {response.status_code}\n")
                except Exception as e:
                    self.update_output.emit(f"Error downloading from {link}: {str(e)}\n")

        # Download and install Catppuccin Waybar theme

        if self.checkWaybarTheme.isChecked():
            selected_flavor = self.themeFlavor.currentText()
            catppuccin_url = f"https://raw.githubusercontent.com/catppuccin/waybar/main/themes/{selected_flavor}.css"
            try:
                response = requests.get(catppuccin_url)
                if response.status_code == 200:
                    filename = os.path.join(waybar_config_dir, f"{selected_flavor}.css")
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    self.update_output.emit(f"Successfully downloaded and saved Catppuccin {selected_flavor} theme for Waybar\n")
                else:
                    self.update_output.emit(f"Failed to download Catppuccin theme. Status code: {response.status_code}\n")
            except Exception as e:
                self.update_output.emit(f"Error downloading Catppuccin theme: {str(e)}\n")
        
        # GRUB theme configuration

        if self.themes_vars["Grub"].isChecked():
            selected_flavor = self.themeFlavor.currentText()
            grub_theme_dir = "/boot/grub/themes/catppuccin"
    
            self.update_output.emit("Configuring GRUB theme...\n")
    
            try:
                # Create a temporary directory
                with tempfile.TemporaryDirectory() as tmp_dir:
                    # Clone the Catppuccin GRUB theme repository
                    self.update_output.emit("Cloning Catppuccin GRUB theme repository...\n")
                    subprocess.run(["git", "clone", "https://github.com/catppuccin/grub.git", tmp_dir], check=True)

                    # Create theme directory if it doesn't exist
                    subprocess.run(["sudo", "mkdir", "-p", grub_theme_dir], check=True)
            
                    # Copy theme files
                    src_dir = os.path.join(tmp_dir, f"src/catppuccin-{selected_flavor}-grub-theme")

                    if not os.path.exists(src_dir):
                        raise FileNotFoundError(f"Directory {src_dir} not found. Check the flavor name and repository structure.")

                    self.update_output.emit(f"Copying {selected_flavor} theme files...\n")
            
                    # Get list of files to copy
                    files_to_copy = glob.glob(os.path.join(src_dir, "*"))
            
                    for file in files_to_copy:
                        subprocess.run(["sudo", "cp", "-r", file, grub_theme_dir], check=True)

                # Update GRUB configuration
                self.update_output.emit("Updating GRUB configuration...\n")
                with open('/etc/default/grub', 'r') as f:
                    grub_config = f.read()
        
                if 'GRUB_THEME=' not in grub_config:
                    grub_config += f'\nGRUB_THEME="{grub_theme_dir}/theme.txt"\n'
                else:
                    grub_config = re.sub(r'#?GRUB_THEME=.*', f'GRUB_THEME="{grub_theme_dir}/theme.txt"', grub_config)
        
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
                    tmp_file.write(grub_config)
                    tmp_file_path = tmp_file.name

                subprocess.run(["sudo", "mv", tmp_file_path, "/etc/default/grub"], check=True)
        
                # Update GRUB
                self.update_output.emit("Regenerating GRUB configuration...\n")
                subprocess.run(["sudo", "grub-mkconfig", "-o", "/boot/grub/grub.cfg"], check=True)
        
                self.update_output.emit("GRUB theme configured successfully.\n")
            except subprocess.CalledProcessError as e:
                self.update_output.emit(f"Error configuring GRUB theme: {e}\n")
                self.update_output.emit(f"Command: {e.cmd}\n")
                self.update_output.emit(f"Output: {e.output}\n")
                self.update_output.emit(f"Stderr: {e.stderr}\n")
            except Exception as e:
                self.update_output.emit(f"Unexpected error configuring GRUB theme: {str(e)}\n")
                self.update_output.emit(f"Error type: {type(e).__name__}\n")


        # SDDM theme configuration

        if self.themes_vars["Sddm"].isChecked():
            selected_flavor = self.themeFlavor.currentText()
            sddm_theme_dir = f"/usr/share/sddm/themes/"

            self.update_output.emit("Installing Catppuccin SDDM theme...\n")

            try:
                # Create a temporary directory
                with tempfile.TemporaryDirectory() as tmp_dir:
                    # Construct the URL for the release zip file based on the selected flavor
                    zip_url = f"https://github.com/catppuccin/sddm/releases/download/v1.0.0/catppuccin-{selected_flavor}.zip"
                    zip_path = os.path.join(tmp_dir, f"catppuccin-{selected_flavor}.zip")

                    # Download the zip file
                    self.update_output.emit(f"Downloading {selected_flavor} SDDM theme...\n")
                    response = requests.get(zip_url)
                    if response.status_code == 200:
                        with open(zip_path, 'wb') as file:
                            file.write(response.content)
                    else:
                        raise Exception(f"Failed to download theme. HTTP Status Code: {response.status_code}")

                    # Unzip the file
                    self.update_output.emit("Unzipping the theme...\n")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(tmp_dir)

                    # Copy theme files to the SDDM themes directory
                    self.update_output.emit(f"Copying {selected_flavor} SDDM theme files...\n")
                    subprocess.run(["sudo", "mkdir", "-p", sddm_theme_dir], check=True)
                    extracted_theme_dir = os.path.join(tmp_dir, f"catppuccin-{selected_flavor}")
                    subprocess.run(["sudo", "cp", "-r", os.path.join(extracted_theme_dir), sddm_theme_dir], check=True)

                # Update SDDM configuration
                self.update_output.emit("Updating SDDM configuration...\n")
                sddm_conf_file = "/etc/sddm.conf"

                if os.path.exists(sddm_conf_file):
                    # Read the existing SDDM configuration
                    with open(sddm_conf_file, 'r') as f:
                        sddm_conf = f.read()

                    # Update or add the current theme configuration
                    if '[Theme]' in sddm_conf:
                        sddm_conf = re.sub(r'Current=.*', f'Current=catppuccin-{selected_flavor}', sddm_conf)
                    else:
                        sddm_conf += f'\n[Theme]\nCurrent=catppuccin-{selected_flavor}\n'
                else:
                    # If the configuration file does not exist, create it
                    sddm_conf = f'[Theme]\nCurrent=catppuccin-{selected_flavor}\n'

                # Write the updated configuration
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
                    tmp_file.write(sddm_conf)
                    tmp_file_path = tmp_file.name

                # Replace the original SDDM configuration file
                subprocess.run(["sudo", "mv", tmp_file_path, sddm_conf_file], check=True)

                self.update_output.emit("Catppuccin SDDM theme installed and configured successfully.\n")

            except subprocess.CalledProcessError as e:
                self.update_output.emit(f"Error installing SDDM theme: {e}\n")
                self.update_output.emit(f"Command: {e.cmd}\n")
                self.update_output.emit(f"Output: {e.output}\n")
                self.update_output.emit(f"Stderr: {e.stderr}\n")
            except Exception as e:
                self.update_output.emit(f"Unexpected error installing SDDM theme: {str(e)}\n")
                self.update_output.emit(f"Error type: {type(e).__name__}\n")
                self.update_output.emit("Installation complete!\n")

        # Rofi theme configuration

        if self.themes_vars["Rofi"].isChecked():
            selected_flavor = self.themeFlavor.currentText()
    
            self.update_output.emit("Installing Catppuccin Rofi theme...\n")

            try:
                # Create a temporary directory
                with tempfile.TemporaryDirectory() as tmp_dir:
                    # Clone the Catppuccin Rofi theme repository
                    self.update_output.emit("Cloning Catppuccin Rofi theme repository...\n")
                    subprocess.run(["git", "clone", "https://github.com/catppuccin/rofi.git", tmp_dir], check=True)

                    # Navigate to the 'basic' folder
                    basic_dir = os.path.join(tmp_dir, "basic")
                    os.chdir(basic_dir)

                    # Run the install.sh script
                    self.update_output.emit("Running install.sh script...\n")
                    subprocess.run(["chmod", "+x", "install.sh"], check=True)  # Ensure the script is executable
                    subprocess.run(["./install.sh"], check=True)

                    # Update the config.rasi file to set the selected flavor
                    config_rasi_path = os.path.expanduser("~/.config/rofi/config.rasi")

                    if os.path.exists(config_rasi_path):
                        # Read the existing config.rasi file
                        with open(config_rasi_path, 'r') as f:
                            config_rasi_content = f.read()

                        # Update the @theme line to use the selected flavor
                        config_rasi_content = re.sub(r'@theme "catppuccin-.*"', f'@theme "catppuccin-{selected_flavor}"', config_rasi_content)

                        # Write the updated configuration back to the file
                        with open(config_rasi_path, 'w') as f:
                            f.write(config_rasi_content)

                        self.update_output.emit(f"Rofi theme updated to Catppuccin {selected_flavor} in config.rasi.\n")
                    else:
                        self.update_output.emit(f"config.rasi file not found at {config_rasi_path}. Please ensure Rofi is installed and configured.\n")

            except subprocess.CalledProcessError as e:
                self.update_output.emit(f"Error installing Rofi theme: {e}\n")
                self.update_output.emit(f"Command: {e.cmd}\n")
                self.update_output.emit(f"Output: {e.output}\n")
                self.update_output.emit(f"Stderr: {e.stderr}\n")
            except Exception as e:
                self.update_output.emit(f"Unexpected error installing Rofi theme: {str(e)}\n")
                self.update_output.emit(f"Error type: {type(e).__name__}\n")
        
        # qt5ct theme configuration

        if self.themes_vars["Qt5ct"].isChecked():
            selected_flavor = self.themeFlavor.currentText().capitalize()
            qt5ct_config_dir = os.path.expanduser("~/.config/qt5ct/colors")
            theme_file = f"Catppuccin-{selected_flavor}.conf"

            self.update_output.emit("Installing Catppuccin Qt5ct theme...\n")

            try:
                # Check and set a valid working directory
                try:
                    os.getcwd()
                except FileNotFoundError:
                    home_dir = os.path.expanduser("~")
                    os.chdir(home_dir)
                    self.update_output.emit(f"Changed working directory to: {home_dir}\n")

                # Create the target directory if it doesn't exist
                os.makedirs(qt5ct_config_dir, exist_ok=True)

                # Create a specific temporary directory for Qt5ct
                qt5ct_tmp_dir = os.path.expanduser("~/qt5ct_tmp")
                os.makedirs(qt5ct_tmp_dir, exist_ok=True)

                self.update_output.emit(f"Created temporary directory: {qt5ct_tmp_dir}\n")

                # Clone the Catppuccin Qt5ct theme repository
                self.update_output.emit("Cloning Catppuccin Qt5ct theme repository...\n")
                clone_command = ["git", "clone", "https://github.com/catppuccin/qt5ct.git", qt5ct_tmp_dir]
        
                try:
                    result = subprocess.run(clone_command, check=True, capture_output=True, text=True)
                    self.update_output.emit(f"Git clone output: {result.stdout}\n")
                except subprocess.CalledProcessError as e:
                    self.update_output.emit(f"Git clone failed. Error: {e.stderr}\n")
                    raise

                # Copy the selected flavor's .conf file to the qt5ct colors directory
                src_theme_path = os.path.join(qt5ct_tmp_dir, "themes", theme_file)
                dest_theme_path = os.path.join(qt5ct_config_dir, theme_file)

                self.update_output.emit(f"Checking for source theme file: {src_theme_path}\n")

                if os.path.exists(src_theme_path):
                    self.update_output.emit(f"Copying {theme_file} to {qt5ct_config_dir}...\n")
                    shutil.copy2(src_theme_path, dest_theme_path)
                    self.update_output.emit(f"Qt5ct theme {selected_flavor} installed successfully.\n")
                else:
                    raise FileNotFoundError(f"{theme_file} not found in the repository.")

            except Exception as e:
                self.update_output.emit(f"Error installing Qt5ct theme: {str(e)}\n")
                self.update_output.emit(f"Error type: {type(e).__name__}\n")
        
                # Safely get the current working directory
                try:
                    cwd = os.getcwd()
                    self.update_output.emit(f"Current working directory: {cwd}\n")
                except FileNotFoundError:
                    self.update_output.emit("Unable to determine current working directory.\n")

            finally:
                # Clean up: remove the temporary directory
                if os.path.exists(qt5ct_tmp_dir):
                    shutil.rmtree(qt5ct_tmp_dir)
                    self.update_output.emit(f"Removed temporary directory: {qt5ct_tmp_dir}\n")
                    
    @QtCore.pyqtSlot(str)
    def update_output_area(self, text):
        self.output_area.append(text)
        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = InstallerApp()
    ex.show()
    sys.exit(app.exec_())