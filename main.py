import os
import shutil
import sys
from datetime import datetime

import dotenv
from dotenv import load_dotenv
from PySide6.QtWidgets import (QApplication, QFileDialog, QLabel, QMainWindow,
                               QListWidget, QVBoxLayout, QHBoxLayout, QWidget,
                               QPushButton)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        load_dotenv()

        self.backup_folder = os.getenv('BACKUP_FOLDER')
        self.darkest_dungeon_folder = os.getenv('DARKEST_DUNGEON_FOLDER')
        self.selected_folder = None

        self.setWindowTitle("Darkest Dungeon Save Manager")

        self.label = QLabel(f"DARKEST_DUNGEON_FOLDER: {os.getenv('DARKEST_DUNGEON_FOLDER', 'Not Set')}")

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)

        self.button_save = QPushButton("Save")
        self.button_load = QPushButton("Load")
        self.button_delete = QPushButton("Delete")
        self.button_set_dd_location = QPushButton("Choose Darkest Dungeon File Location")

        self.button_load.setEnabled(False)
        self.button_delete.setEnabled(False)

        self.button_save.clicked.connect(self.on_button_save_clicked)
        self.button_load.clicked.connect(self.on_button_load_clicked)
        self.button_delete.clicked.connect(self.on_button_delete_clicked)
        self.button_set_dd_location.clicked.connect(self.on_button_set_dd_location_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_save)
        button_layout.addWidget(self.button_load)
        button_layout.addWidget(self.button_delete)
        button_layout.addWidget(self.button_set_dd_location)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.open_folder()

    def closeEvent(self, event):
        self.update_env_on_close()
        event.accept()  # Accept the event to close the window

    def open_folder(self):
        print(os.getenv('BACKUP_FOLDER'))
        desktop_path = os.getenv('BACKUP_FOLDER')
        self.load_files(desktop_path)

    def load_files(self, folder_path):
        self.list_widget.clear()
        for file_name in os.listdir(folder_path):
            self.list_widget.addItem(file_name)

    def on_item_clicked(self, item):
        self.selected_folder = item.text()
        print(f"Selected item: {item.text()}")
        self.button_load.setEnabled(True)
        self.button_delete.setEnabled(True)

    def on_button_save_clicked(self):
        print("Button 1 clicked")
        folder_path = self.create_date_folder()
        self.open_folder()
        self.save_backup_files(folder_path)

    def create_date_folder(self):
        # Get today's date in YYYY-MM-DD format
        today_date = datetime.today().strftime('%Y-%m-%d_%H-%M')
        # Create the full path for the new folder
        folder_path = os.path.join(os.getenv('BACKUP_FOLDER'), today_date)
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def save_backup_files(self, folder_path):
        for root, dirs, files in os.walk(self.darkest_dungeon_folder):
            # Create corresponding directory structure in the backup folder
            relative_path = os.path.relpath(root, self.darkest_dungeon_folder)
            backup_root = os.path.join(folder_path, relative_path)
            if not os.path.exists(backup_root):
                os.makedirs(backup_root)

            for file_name in files:
                file_path = os.path.join(root, file_name)
                new_file_path = os.path.join(backup_root, file_name)
                with open(file_path, 'rb') as file:
                    with open(new_file_path, 'wb') as new_file:
                        new_file.write(file.read())


    def on_button_load_clicked(self):
        if self.selected_folder is not None:
            print(f"Button load clicked: {self.selected_folder}")
            self.overwrite_dd_files()

    def overwrite_dd_files(self):
        source_folder = os.path.join(os.getenv('BACKUP_FOLDER'), self.selected_folder)
        destination_folder = self.darkest_dungeon_folder

        # Remove all existing files and directories in the destination folder
        for root, dirs, files in os.walk(destination_folder):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))

        # Copy all files and directories from the source folder to the destination folder
        for item in os.listdir(source_folder):
            s = os.path.join(source_folder, item)
            d = os.path.join(destination_folder, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    def on_button_delete_clicked(self):
        if self.selected_folder is not None:
            folder_to_delete = os.path.join(os.getenv('BACKUP_FOLDER'), self.selected_folder)
            if os.path.exists(folder_to_delete):
                shutil.rmtree(folder_to_delete)
                print(f"Deleted folder: {folder_to_delete}")
                self.open_folder()  # Refresh the list widget
            else:
                print(f"Folder does not exist: {folder_to_delete}")
        else:
            print("No folder selected")

    def on_button_set_dd_location_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            print(f"Selected folder: {folder_path}")
            self.darkest_dungeon_folder = folder_path
            self.label.setText(f"DARKEST_DUNGEON_FOLDER: {self.darkest_dungeon_folder}")
            self.label.adjustSize()

    def update_env_on_close(self):
        dotenv.set_key('.env', 'DARKEST_DUNGEON_FOLDER', self.darkest_dungeon_folder)
        dotenv.set_key('.env', 'BACKUP_FOLDER', self.backup_folder)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())