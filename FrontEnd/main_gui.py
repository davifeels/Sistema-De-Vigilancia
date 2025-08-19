# main_gui.py (Versão SUÍTE COMPLETA - GUI Avançada)

import sys
import os
import json
import cv2
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QGridLayout,
                             QPushButton, QDialog, QLineEdit, QVBoxLayout, QListWidget,
                             QMenuBar, QTabWidget, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QUrl
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QAction, QIcon
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

# Importe os novos widgets
from detector import Detector
from gravador import Gravador
from gallery_widget import GalleryWidget
from login_dialog import LoginDialog
from auth_manager import AuthManager

# ====================================================================================
# ESTILO QSS APRIMORADO (CSS)
# ====================================================================================
QSS_STYLE = """
/* Estilo geral */
QWidget {
    background-color: #1E1E1E;
    color: #E0E0E0;
    font-family: Arial;
}
QMainWindow {
    background-color: #1E1E1E;
}

/* Abas */
QTabWidget::pane {
    border: 1px solid #444;
    border-radius: 5px;
}
QTabBar::tab {
    background-color: #2D2D2D;
    color: white;
    padding: 10px 25px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border: 1px solid #444;
}
QTabBar::tab:selected {
    background-color: #007ACC;
    border-bottom-color: #007ACC;
}
QTabBar::tab:!selected:hover {
    background-color: #3E3E3E;
}

/* Caixas de Câmera */
CameraWidget {
    background-color: #2D2D2D;
    border-radius: 10px;
}
#CameraTitle {
    background-color: #007ACC;
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 5px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
#VideoLabel {
    background-color: black;
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}

/* Galeria */
QListWidget {
    background-color: #2D2D2D;
    border-radius: 5px;
    border: 1px solid #444;
    font-size: 14px;
}
QListWidget::item {
    padding: 8px;
}
QListWidget::item:selected {
    background-color: #007ACC;
    color: white;
}
QPushButton {
    background-color: #007ACC;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #005A9E;
}

/* Diálogo de Configurações */
QDialog {
    background-color: #2D2D2D;
}
QLineEdit {
    background-color: #3E3E3E;
    color: white;
    border: 1px solid #555;
    border-radius: 5px;
    padding: 5px;
    font-size: 14px;
}
"""

# ====================================================================================
# THREAD DE PROCESSAMENTO DE CÂMERA
# ====================================================================================
class CameraThread(QThread):
    changePixmap = pyqtSignal(QImage)
    def __init__(self, camera_id, nome_camera):
        super().__init__()
        self.camera_id = camera_id; self.nome_camera = nome_camera; self.running = True
    def run(self):
        try:
            captura = cv2.VideoCapture(self.camera_id)
            w, h = 640, 360
            if not captura.isOpened(): return
            detector = Detector(); gravador = Gravador(largura=w, altura=h, prefixo_nome=f"{self.nome_camera}_")
            frames, ultima_vez_detectado, persistencia = 0, 0, 10.0
            ultimos_contornos, ultimas_poses = [], []
            while self.running:
                ret, frame_original = captura.read()
                if not ret or frame_original is None: continue
                frame = cv2.resize(frame_original, (w, h))
                if frames % 4 == 0:
                    contornos = detector.detectar_movimento(frame); poses = []
                    if contornos: poses = detector.detectar_poses(frame)
                    if contornos or poses:
                        ultima_vez_detectado = time.time()
                        ultimos_contornos = contornos; ultimas_poses = poses
                frames += 1
                no_periodo_de_persistencia = time.time() - ultima_vez_detectado < persistencia
                if no_periodo_de_persistencia:
                    status, cor = "ATIVIDADE DETECTADA", (0, 0, 255)
                    for contorno in ultimos_contornos:
                        (x, y, w_c, h_c) = cv2.boundingRect(contorno)
                        cv2.rectangle(frame, (x, y), (x + w_c, y + h_c), (0, 255, 0), 2)
                        cv2.putText(frame, "Movimento", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    for pose in ultimas_poses:
                        px = [p[0] for p in pose if p[0]>0]; py = [p[1] for p in pose if p[1]>0]
                        if px and py:
                            x_min, x_max = int(min(px)), int(max(px)); y_min, y_max = int(min(py)), int(max(py))
                            cv2.rectangle(frame, (x_min-10, y_min-10), (x_max+10, y_max+10), (255,0,0), 2)
                    gravador.iniciar_gravacao(); gravador.gravar_frame(frame)
                else:
                    status, cor = "MONITORANDO", (0, 255, 0)
                    gravador.parar_gravacao()
                cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h_i, w_i, ch = rgb_image.shape; bytes_per_line = ch * w_i
                qt_img = QImage(rgb_image.data, w_i, h_i, bytes_per_line, QImage.Format.Format_RGB888)
                self.changePixmap.emit(qt_img.scaled(640, 360, Qt.AspectRatioMode.KeepAspectRatio))
        finally:
            if 'captura' in locals() and captura.isOpened(): captura.release()
            if 'gravador' in locals(): gravador.finalizar()
    def stop(self): self.running = False; self.wait()

# ====================================================================================
# WIDGET DA CÂMERA - Agora emite um sinal de duplo-clique
# ====================================================================================
class CameraWidget(QWidget):
    doubleClicked = pyqtSignal() # Sinal para a tela cheia
    
    def __init__(self, camera_id, nome_camera, placeholder_img, parent=None):
        super(CameraWidget, self).__init__(parent)
        self.setObjectName("CameraWidget")
        self.layout = QVBoxLayout(); self.layout.setContentsMargins(0,0,0,0); self.setLayout(self.layout)
        self.label_nome = QLabel(nome_camera); self.label_nome.setObjectName("CameraTitle"); self.label_nome.setAlignment(Qt.AlignmentFlag.AlignCenter); self.layout.addWidget(self.label_nome)
        self.label_video = QLabel(self); self.label_video.setObjectName("VideoLabel"); self.layout.addWidget(self.label_video)
        
        placeholder_pixmap = QPixmap(placeholder_img)
        if placeholder_pixmap.isNull():
            placeholder_pixmap = QPixmap(640, 360); placeholder_pixmap.fill(Qt.GlobalColor.black)
            painter = QPainter(placeholder_pixmap); painter.setPen(Qt.GlobalColor.white); painter.setFont(QFont("Arial", 30, QFont.Weight.Bold)); painter.drawText(placeholder_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "SEM SINAL"); painter.end()
        self.label_video.setPixmap(placeholder_pixmap.scaled(640, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        if camera_id is not None:
            self.thread = CameraThread(camera_id, nome_camera); self.thread.changePixmap.connect(self.setImage); self.thread.start()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit() # Emite o sinal quando houver duplo-clique
        super().mouseDoubleClickEvent(event)

    def setImage(self, image):
        self.label_video.setPixmap(QPixmap.fromImage(image))
        
    def stop_thread(self):
        if hasattr(self, 'thread'): self.thread.stop()

# ====================================================================================
# ABA DA GALERIA DE GRAVAÇÕES
# ====================================================================================
class GalleryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        
        self.video_list = QListWidget()
        self.video_list.currentItemChanged.connect(self.play_video)
        self.layout.addWidget(self.video_list, 0, 0)
        
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.layout.addWidget(self.video_widget, 0, 1)

        self.refresh_button = QPushButton("Atualizar Gravações")
        self.refresh_button.clicked.connect(self.populate_videos)
        self.layout.addWidget(self.refresh_button, 1, 0)
        
        self.layout.setColumnStretch(1, 3) # Faz o vídeo ocupar mais espaço
        self.populate_videos()

    def populate_videos(self):
        self.video_list.clear()
        video_dir = "videos"
        if os.path.exists(video_dir):
            files = sorted([f for f in os.listdir(video_dir) if f.endswith(".avi")], reverse=True)
            self.video_list.addItems(files)

    def play_video(self, item):
        if item is None: return
        video_path = os.path.join("videos", item.text())
        self.media_player.setSource(QUrl.fromLocalFile(os.path.abspath(video_path)))
        self.media_player.play()

# ====================================================================================
# JANELA DE CONFIGURAÇÕES
# ====================================================================================
class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.layout = QVBoxLayout(self)
        self.line_edits = []

        for i, cam in enumerate(settings['cameras']):
            self.layout.addWidget(QLabel(f"--- Câmera {i+1} ---"))
            le_name = QLineEdit(cam['name'])
            le_id = QLineEdit(str(cam['id']) if cam['id'] is not None else "")
            le_placeholder = QLineEdit(cam['placeholder'])
            
            self.layout.addWidget(QLabel("Nome:"))
            self.layout.addWidget(le_name)
            self.layout.addWidget(QLabel("ID ou URL (deixe em branco para desativar):"))
            self.layout.addWidget(le_id)
            self.layout.addWidget(QLabel("Imagem Placeholder:"))
            self.layout.addWidget(le_placeholder)
            self.line_edits.append({'name': le_name, 'id': le_id, 'placeholder': le_placeholder})

        self.save_button = QPushButton("Salvar e Reiniciar")
        self.save_button.clicked.connect(self.accept)
        self.layout.addWidget(self.save_button)

    def get_settings(self):
        new_settings = {"cameras": []}
        for edits in self.line_edits:
            cam_id_text = edits['id'].text()
            cam_id = None
            if cam_id_text.lower().startswith(('http', 'rtsp')):
                cam_id = cam_id_text
            elif cam_id_text.isdigit():
                cam_id = int(cam_id_text)

            new_settings["cameras"].append({
                "name": edits['name'].text(),
                "id": cam_id,
                "placeholder": edits['placeholder'].text()
            })
        return new_settings

# ====================================================================================
# JANELA PRINCIPAL - O APLICATIVO EM SI
# ====================================================================================
class MainWindow(QMainWindow):
    def __init__(self, user_role="guest"): # Adiciona o papel do usuário
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle("Painel de Vigilância PRO MAX")
        self.setStyleSheet(QSS_STYLE)

        self.load_settings()
        self.init_ui()

    def load_settings(self):
        try:
            with open("config.json", "r") as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Cria um config padrão se não existir ou for inválido
            self.settings = { "cameras": [ {"id": None, "name": f"Câmera {i+1}", "placeholder": "assets/no_signal.png"} for i in range(4) ] }
            self.save_settings()
    
    def save_settings(self):
        with open("config.json", "w") as f:
            json.dump(self.settings, f, indent=2)

    def init_ui(self):
        if hasattr(self, 'tab_widget'):
            self.tab_widget.deleteLater()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Arquivo")
        settings_action = QAction("Configurações", self)
        # Habilita ou desabilita a ação de acordo com o papel do usuário
        settings_action.setEnabled(self.user_role == "admin")
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        self.camera_panel = QWidget()
        self.grid_layout = QGridLayout(self.camera_panel)
        self.grid_layout.setSpacing(15)
        self.tab_widget.addTab(self.camera_panel, "Painel de Câmeras")
        
        # Aba de Galeria de Gravações
        self.gallery_panel = GalleryWidget()
        self.tab_widget.addTab(self.gallery_panel, "Gravações")

        # ABA DE GALERIA DE ROSTOS
        self.face_gallery_panel = GalleryWidget(camera_id=0)
        self.tab_widget.addTab(self.face_gallery_panel, "Galeria de Rostos")
        
        self.camera_widgets = []
        positions = [(i, j) for i in range(2) for j in range(2)]
        
        for position, cam_config in zip(positions, self.settings['cameras']):
            widget = CameraWidget(cam_config['id'], cam_config['name'], cam_config['placeholder'])
            widget.doubleClicked.connect(lambda w=widget: self.toggle_fullscreen(w))
            self.grid_layout.addWidget(widget, position[0], position[1])
            self.camera_widgets.append(widget)
        
        self.fullscreen_widget = None

    def toggle_fullscreen(self, widget_clicked):
        if self.fullscreen_widget is None:
            self.fullscreen_widget = widget_clicked
            for widget in self.camera_widgets:
                if widget != self.fullscreen_widget:
                    widget.setVisible(False)
        else:
            for widget in self.camera_widgets:
                widget.setVisible(True)
            self.fullscreen_widget = None

    def open_settings(self):
        dialog = SettingsDialog(self.settings)
        if dialog.exec():
            self.settings = dialog.get_settings()
            self.save_settings()
            QMessageBox.information(self, "Reiniciar", "As configurações foram salvas. Por favor, reinicie o aplicativo para que elas tenham efeito.")
            self.close()

    def closeEvent(self, event):
        for widget in self.camera_widgets:
            widget.stop_thread()
        self.face_gallery_panel.stop_camera()
        super().closeEvent(event)

# --- PONTO DE PARTIDA DO APLICATIVO ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth_manager = AuthManager()

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        username = login_dialog.username_input.text()
        password = login_dialog.password_input.text()
        user = auth_manager.authenticate(username, password)

        if user:
            QMessageBox.information(None, "Login Bem-sucedido", f"Bem-vindo, {user['username']}!")
            main_window = MainWindow(user_role=user['role'])
            main_window.showMaximized()
            sys.exit(app.exec())
        else:
            QMessageBox.critical(None, "Erro de Login", "Usuário ou senha incorretos.")
            sys.exit(app.exec())
    else:
        sys.exit(0)