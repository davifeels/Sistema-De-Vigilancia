# gallery_widget.py

import sys
import os
import cv2
import face_recognition
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit, QListWidget, QLabel,
                             QMessageBox, QHBoxLayout)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer

# A classe FaceRecognizer deve ser importada daqui
from face_recognizer import FaceRecognizer

class GalleryWidget(QWidget):
    def __init__(self, camera_id=0, parent=None):
        super().__init__(parent)
        self.face_recognizer = FaceRecognizer()
        self.camera_id = camera_id
        self.capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.setup_ui()
        self.populate_gallery()
        self.start_camera()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Layout da Câmera e Captura
        camera_layout = QVBoxLayout()
        self.camera_label = QLabel("Visualização da Câmera")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background-color: black; color: white;")
        self.camera_label.setFixedSize(640, 480)
        camera_layout.addWidget(self.camera_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome do rosto a ser cadastrado...")
        camera_layout.addWidget(self.name_input)

        self.capture_button = QPushButton("Capturar Rosto")
        self.capture_button.clicked.connect(self.capture_face)
        camera_layout.addWidget(self.capture_button)

        main_layout.addLayout(camera_layout)

        # Layout da Galeria
        gallery_layout = QVBoxLayout()
        self.face_list = QListWidget()
        gallery_layout.addWidget(self.face_list)
        
        self.delete_button = QPushButton("Excluir Rosto Selecionado")
        self.delete_button.clicked.connect(self.delete_face)
        gallery_layout.addWidget(self.delete_button)

        main_layout.addLayout(gallery_layout)

    def start_camera(self):
        self.capture = cv2.VideoCapture(self.camera_id)
        if not self.capture.isOpened():
            self.camera_label.setText("Erro: Câmera não disponível.")
            return
        self.timer.start(30)  # Atualiza a cada 30 ms

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_img.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)))

    def capture_face(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Nome Inválido", "Por favor, digite um nome para o rosto.")
            return

        ret, frame = self.capture.read()
        if not ret:
            QMessageBox.critical(self, "Erro de Câmera", "Não foi possível capturar o frame.")
            return

        # Tenta encontrar um rosto no frame
        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) == 0:
            QMessageBox.warning(self, "Nenhum Rosto Detectado", "Não foi possível encontrar um rosto. Tente novamente.")
            return

        # Pega a localização do primeiro rosto
        top, right, bottom, left = face_locations[0]
        face_image = frame[top:bottom, left:right]

        filename = os.path.join(self.face_recognizer.known_faces_dir, f"{name}.png")
        cv2.imwrite(filename, face_image)
        QMessageBox.information(self, "Sucesso", f"Rosto de {name} cadastrado com sucesso!")

        self.face_recognizer.load_known_faces()  # Recarrega os rostos na memória
        self.populate_gallery()
        self.name_input.clear()

    def populate_gallery(self):
        self.face_list.clear()
        for name in self.face_recognizer.known_face_names:
            self.face_list.addItem(name)

    def delete_face(self):
        selected_item = self.face_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Nenhuma Seleção", "Por favor, selecione um rosto para excluir.")
            return
            
        name = selected_item.text()
        file_to_delete = os.path.join(self.face_recognizer.known_faces_dir, f"{name}.png")
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
            QMessageBox.information(self, "Sucesso", f"Rosto de {name} excluído com sucesso.")
            self.face_recognizer.load_known_faces()
            self.populate_gallery()

    def stop_camera(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.capture and self.capture.isOpened():
            self.capture.release()