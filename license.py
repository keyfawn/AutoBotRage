import base64
import os
import subprocess
import sys
from datetime import datetime, timedelta

from Crypto.Cipher import AES
from PyQt6 import QtCore


def resource_path(relative_path) -> str:
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return str(os.path.join(base_path, relative_path))


class License:
    def __init__(self, path_key):
        self.path_file = f'C:\\Users\\{os.environ["username"]}\\Documents\\RAGERAID\\license.rageraid'
        self.path_dir = f'C:\\Users\\{os.environ["username"]}\\Documents\\RAGERAID'

        with open(path_key, 'r') as file:
            encoded_key = file.read().strip()
        self.key = bytes.fromhex(encoded_key)

        self.hwid = str(
            str(subprocess.check_output(
                'wmic csproduct get uuid')).strip().replace(r"\r", "").split(r"\n")[1].strip())

    def decrypt(self, text: bytes) -> str:
        cipher = AES.new(self.key, AES.MODE_ECB)
        decrypted_script = cipher.decrypt(text).decode().rstrip()
        return decrypted_script

    def encrypt(self, text: str) -> bytes:
        while len(text) % 16 != 0:
            text += ' '
        cipher = AES.new(self.key, AES.MODE_ECB)
        encrypted_script = cipher.encrypt(text.encode('utf-8'))
        return encrypted_script

    def create_file(self):
        if not os.path.isdir(self.path_dir):
            os.mkdir(self.path_dir)
            subprocess.check_call(["attrib", "+H", self.path_dir])

        self.date = datetime.now()
        subprocess.check_call(["attrib", "-H", self.path_file])
        with open(self.path_file, 'wb') as file:
            file.writelines([self.encrypt(i) for i in [self.date.strftime("%d/%m/%Y, %H:%M:%S")]])
        subprocess.check_call(["attrib", "+H", self.path_file])

    def delete_file(self):
        os.remove(self.path_file)

    def check_file(self):
        if os.path.isdir(self.path_dir):
            if os.path.isfile(self.path_file):
                return True
        return False

    def get_data(self) -> int:
        # -- check file --
        if not self.check_file():
            return 404

        with open(self.path_file, 'rb') as f_r:
            self.date = datetime.strptime(self.decrypt(f_r.read()), "%d/%m/%Y, %H:%M:%S")

        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)
        self.secret_key = settings.value('secret_key')
        if self.decode_secret(self.secret_key):
            return 4044

        return 0

    def decode_secret(self, text):
        try:
            self.your_hwid, self.days, random = base64.b64decode(text).decode("utf-8").split(':')
            return 0
        except Exception as e:
            return 404

    def check_license(self) -> int:
        # -- check date --
        if datetime.now() > self.date + timedelta(days=int(self.days)):
            self.delete_file()
            return 504

        # -- check hwid --
        if self.decode_secret(self.secret_key):
            return 404

        if self.your_hwid != self.hwid:
            return 401

        return 0

    def print(self):
        print(f'data: {self.date}')
        print(f'hwid: {self.hwid}')
        print(f'key: {self.key}')
