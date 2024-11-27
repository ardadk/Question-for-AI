import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame, QLabel, QFileDialog, QDialog, QDialogButtonBox, QMessageBox, QListWidget, QListWidgetItem
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import os
import time
import torch
from TTS.api import TTS
import subprocess
import cv2
import google.generativeai as genai

# JSON dosya adları
DATABASE_FILE = "characters.json"
CONFIG_FILE = "config.json"  # API key ve diğer ayarlar için
folder_path=os.getcwd()

class APIKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API-Key Ayarları")
        self.setGeometry(400, 200, 400, 200)

        # Layouts
        layout = QVBoxLayout(self)

        # API-Key Input
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Gemini API-Key'inizi girin")
        layout.addWidget(self.api_key_input)

        # Not
        note_label = QLabel("Gemini API-Key için: https://ai.google.dev/gemini-api/docs/api-key?hl=tr")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        # Kaydet ve İptal Butonları
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_api_key)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # API key'i mevcut dosyadan yükle (eğer varsa)
        self.load_existing_api_key()

    def load_existing_api_key(self):
        """Mevcut API-Key'i config.json'dan yükle."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                api_key = config.get("api_key", "")
                self.api_key_input.setText(api_key)

    def save_api_key(self):
        api_key = self.api_key_input.text().strip()
        if api_key:
            try:
                # API anahtarını kaydet
                with open(CONFIG_FILE, "w") as file:
                    json.dump({"api_key": api_key}, file)

                # Google Generative AI yapılandırmasını ayarla
                genai.configure(api_key=api_key)

                QMessageBox.information(self, "Başarılı", "API-Key başarıyla kaydedildi.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"API-Key ayarlanamadı: {str(e)}")
        else:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen geçerli bir API-Key girin.")


class AddCharacterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yeni Karakter Ekle")
        self.setGeometry(400, 200, 400, 200)

        # Layouts
        layout = QVBoxLayout(self)

        # Karakter Adı
        self.character_name_input = QLineEdit()
        self.character_name_input.setPlaceholderText("Karakter Adı")
        layout.addWidget(self.character_name_input)

        # Fotoğraf Seçme Butonu
        self.photo_path = ""
        self.photo_button = QPushButton("Fotoğraf seç")
        self.photo_button.clicked.connect(self.select_photo)
        layout.addWidget(self.photo_button)

        # Ses Dosyası Seçme Butonu
        self.audio_path = ""
        self.audio_button = QPushButton("Klonlanacak ses dosyasını seç")
        self.audio_button.clicked.connect(self.select_audio)
        layout.addWidget(self.audio_button)

        # Ekleme ve İptal Butonları
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_inputs)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_photo(self):
        photo_file, _ = QFileDialog.getOpenFileName(self, "Fotoğraf seç", "", "Images (*.png *.jpg *.jpeg)")
        if photo_file:
            self.photo_path = photo_file
            self.photo_button.setText(f"Seçildi: {os.path.basename(photo_file)}")

    def select_audio(self):
        audio_file, _ = QFileDialog.getOpenFileName(self, "Klonlanacak ses dosyasını seç", "", "Audio Files (*.wav)")
        if audio_file:
            self.audio_path = audio_file
            self.audio_button.setText(f"Seçildi: {os.path.basename(audio_file)}")

    def validate_inputs(self):
        if not self.character_name_input.text() or not self.photo_path or not self.audio_path:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen tüm alanları doldurunuz.")
        else:
            self.accept()

    def get_inputs(self):
        return self.character_name_input.text(), self.photo_path, self.audio_path


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Question for AI")
        self.setGeometry(100, 100, 1000, 600)
        self.generated_text = ""
        self.i = 0

        # Ana dikey düzen (tüm widget'ları içerir)
        main_layout = QVBoxLayout()

        # Sağ taraf: Liste ve butonlar için frame
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setFixedWidth(200)
        right_layout = QVBoxLayout(right_frame)  # Liste ve butonlar için dikey düzen

        # Karakter Listesi
        self.character_list = QListWidget()
        right_layout.addWidget(self.character_list)

        # Yeni karakter eklemek için buton oluştur ve en alta ekle
        self.add_character_button = QPushButton("Karakter Ekle")
        self.add_character_button.clicked.connect(self.add_character)
        right_layout.addWidget(self.add_character_button)

        # Karakter Silme Butonu
        self.delete_character_button = QPushButton("Karakter Sil")
        self.delete_character_button.clicked.connect(self.delete_character)
        right_layout.addWidget(self.delete_character_button)

        # API-Key Butonu
        self.api_key_button = QPushButton("API-Key")
        self.api_key_button.clicked.connect(self.open_api_key_dialog)
        right_layout.addWidget(self.api_key_button)

        # Sağdaki listeyi ve videoyu yan yana yerleştirmek için yatay düzen
        top_layout = QHBoxLayout()

        # Video oynatıcı için QLabel
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.video_label, 4)  # Video ekranı sol tarafta olacak
        top_layout.addWidget(right_frame, 1)  # Liste ve butonlar sağ tarafta olacak

        self.cap = cv2.VideoCapture("QfAI.mp4")
        # Timer ayarı: Her kareyi belirli aralıklarla güncellemek için
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 ms aralıkla kareyi güncelle (yaklaşık 30 fps)

        # Input alanını alta yerleştir
        input_layout = QHBoxLayout()  # Input için yatay düzen
        self.input = QLineEdit()
        self.input.setFixedHeight(50)
        input_layout.addWidget(QLabel("Prompt :"))  # Bir label ekliyoruz
        input_layout.addWidget(self.input)

        # Çalıştır Butonu
        self.run_button = QPushButton("Çalıştır")
        self.run_button.clicked.connect(self.run_selected_character)
        input_layout.addWidget(self.run_button)

        # Ana layout'a yerleştir
        main_layout.addLayout(top_layout)  # Video ve liste üstte
        main_layout.addLayout(input_layout)  # Input alanı ve Çalıştır butonu altta

        # Ana layout'u pencereye ayarla
        self.setLayout(main_layout)

        # Karakterleri saklamak için bir sözlük
        self.characters = {}

        # Veritabanını yükle
        self.load_database()

        # API key'i yükle
        self.load_api_key()

    def load_api_key(self):
        """API key'i config.json'dan yükler ve Google Generative AI'yı yapılandırır."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                api_key = config.get("api_key", "")
                if api_key:
                    genai.configure(api_key=api_key)

    def update_frame(self):
        ret, frame = self.cap.read()
        # Video dosyasından kare al
        if ret:
            # OpenCV BGR formatını, PyQt5'te kullanılmak üzere RGB formatına dönüştür
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qImg))
        else:
            # Video bittiğinde tekrar başlat
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def open_api_key_dialog(self):
        dialog = APIKeyDialog(self)
        dialog.exec_()

    def add_character(self):
        # Karakter ekleme penceresi oluşturma ve gösterme
        dialog = AddCharacterDialog()
        if dialog.exec_() == QDialog.Accepted:
            character_name, image_file, audio_file = dialog.get_inputs()
            if character_name and image_file and audio_file:
                # Karakteri listeye ekleme
                list_item = QListWidgetItem(character_name)
                self.character_list.addItem(list_item)
                self.characters[character_name] = {"image": image_file, "audio": audio_file}

                # .bat dosyası oluşturma
                self.create_bat_file(character_name, image_file, audio_file)

                # JSON veritabanını güncelle
                self.save_database()

    def create_bat_file(self, character_name, image_file, audio_file):
        bat_content = f"""@echo off
cd  {folder_path}       
call conda activate uc
start /b python inference.py --checkpoint_path "checkpoints/wav2lip.pth" --face "{image_file}" --audio "{character_name.replace(" ", "_")}_output.wav" --outfile "{character_name.replace(" ", "_")}_lip.mp4"
exit"""

        bat_filename = f"{character_name.replace(' ', '_')}.bat"
        with open(bat_filename, "w") as bat_file:
            bat_file.write(bat_content)
        print(f"{bat_filename} dosyası başarıyla oluşturuldu.")

    def run_selected_character(self):
        selected_item = self.character_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Karakter Seçimi Eksik", "Lütfen bir karakter seçin.")
            return

        character_name = selected_item.text()
        prompt_text = self.input.text().strip()

        if not prompt_text:
            QMessageBox.warning(self, "Prompt Eksik", "Lütfen bir prompt girin.")
            return

        # Gemini API'ye prompt gönderme
        input_text = self.input.text()
        if input_text:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content(input_text)
            self.generated_text = response.text
            print(self.generated_text)

        # Yanıtı TTS ile sese dönüştürme
        self.generate_tts_audio(character_name, self.generated_text)
        self.play_character_audio(character_name)

    def generate_tts_audio(self, character_name, text):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        speaker_wav = self.characters[character_name]["audio"]
        output_file = f"{character_name.replace(' ', '_')}_output.wav"
        tts.tts_to_file(text=text, speaker_wav=speaker_wav, language="tr", file_path=output_file)
        print(f"{output_file} başarıyla oluşturuldu.")

    def play_character_audio(self, character_name):
        try:
            bat_file = f"{character_name.replace(' ', '_')}.bat"
            lip_path=f"{folder_path}"+"/outputs"
            target_file = f"{character_name}_lip.mp4"
            os.system(f'start "" "{bat_file}"')
            while True:
                if target_file in os.listdir(lip_path):
                    time.sleep(5)
                    os.system(f'start "" "{target_file}"')
                    print("oynatılıyor")
                    break
                else:
                    time.sleep(1)
        except Exception as e:
            print(f"{character_name} oynatma sırasında bir hata oluştu: {str(e)}")

    def delete_character(self):
        selected_item = self.character_list.currentItem()
        if selected_item:
            character_name = selected_item.text()
            self.character_list.takeItem(self.character_list.row(selected_item))
            if character_name in self.characters:
                del self.characters[character_name]
                self.save_database()
                print(f"{character_name} başarıyla silindi.")
            else:
                print(f"{character_name} bulunamadı.")

    def load_database(self):
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as file:
                self.characters = json.load(file)
                for character_name, data in self.characters.items():
                    list_item = QListWidgetItem(character_name)
                    self.character_list.addItem(list_item)

    def save_database(self):
        with open(DATABASE_FILE, "w") as file:
            json.dump(self.characters, file)
        print(f"{DATABASE_FILE} başarıyla güncellendi.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())
