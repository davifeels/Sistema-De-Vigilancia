# camera_stream.py

import cv2
import time
import asyncio
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage
from detector import Detector
from gravador import Gravador
from face_recognizer import FaceRecognizer
from notifier import TelegramNotifier
from db_manager import initialize_db, Event # Importa o banco de dados

# Inicializa o banco de dados
initialize_db()

class CameraThread(QThread):
    changePixmap = pyqtSignal(QImage)
    statusUpdate = pyqtSignal(str, tuple) # Sinal para o status (texto, cor)
    
    def __init__(self, camera_id, nome_camera):
        super().__init__()
        self.camera_id = camera_id
        self.nome_camera = nome_camera
        self.running = True
        self.detector = Detector()
        self.gravador = Gravador(prefixo_nome=f"{self.nome_camera}_")
        self.face_recognizer = FaceRecognizer()
        self.telegram_notifier = TelegramNotifier()
        self.last_alert_time = 0

    def run(self):
        try:
            captura = cv2.VideoCapture(self.camera_id)
            w, h = 640, 360
            if not captura.isOpened():
                self.statusUpdate.emit("ERRO: SEM SINAL", (0, 0, 255))
                return

            frames = 0
            ultima_vez_detectado = 0
            persistencia = 10.0
            
            ultimos_contornos, ultimas_poses, ultimas_faces = [], [], []

            while self.running:
                ret, frame_original = captura.read()
                if not ret or frame_original is None:
                    continue
                
                frame = cv2.resize(frame_original, (w, h))
                
                if frames % 4 == 0:
                    contornos = self.detector.detectar_movimento(frame)
                    poses = []
                    faces = []
                    
                    if contornos:
                        poses = self.detector.detectar_poses(frame)
                    
                    if poses:
                        faces = self.face_recognizer.recognize(frame)
                    
                    if contornos or poses or faces:
                        ultima_vez_detectado = time.time()
                        ultimos_contornos = contornos
                        ultimas_poses = poses
                        ultimas_faces = faces

                frames += 1
                
                no_periodo_de_persistencia = time.time() - ultima_vez_detectado < persistencia
                
                if no_periodo_de_persistencia:
                    for contorno in ultimos_contornos:
                        (x, y, w_c, h_c) = cv2.boundingRect(contorno)
                        cv2.rectangle(frame, (x, y), (x + w_c, y + h_c), (0, 255, 0), 2)
                    
                    for pose in ultimas_poses:
                        px = [p[0] for p in pose if p[0]>0]; py = [p[1] for p in pose if p[1]>0]
                        if px and py:
                            x_min, x_max = int(min(px)), int(max(px)); y_min, y_max = int(min(py)), int(max(py))
                            cv2.rectangle(frame, (x_min-10, y_min-10), (x_max+10, y_max+10), (255,0,0), 2)
                    
                    for face in ultimas_faces:
                        top, right, bottom, left = face['box']
                        name = face['name']
                        
                        cor_borda = (255, 255, 0) if name != "Desconhecido" else (0, 0, 255)
                        
                        cv2.rectangle(frame, (left, top), (right, bottom), cor_borda, 2)
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, cor_borda, 2)

                    faces_desconhecidas = [f for f in ultimas_faces if f['name'] == 'Desconhecido']
                    
                    if faces_desconhecidas or (ultimos_contornos and not ultimas_faces):
                         status_texto = "ALERTA: ATIVIDADE SUSPEITA!"
                         cor = (0, 0, 255)
                         self.gravador.iniciar_gravacao()
                         self.gravador.gravar_frame(frame)
                         
                         # NOVO: Registra o evento no banco de dados e envia notificação
                         if time.time() - self.last_alert_time > 30:
                             screenshot_path = f"assets/alerta_{self.nome_camera}.png"
                             cv2.imwrite(screenshot_path, frame)
                             message = "ALARME! Atividade suspeita detectada."
                             asyncio.run(self.telegram_notifier.send_alert(message, screenshot_path))
                             
                             # Loga no banco de dados
                             Event.create(
                                 event_type=status_texto,
                                 camera_name=self.nome_camera,
                                 image_path=screenshot_path,
                                 video_path=self.gravador.nome_arquivo if self.gravador.gravando else None
                             )
                             self.last_alert_time = time.time()
                    else:
                        status_texto = "MONITORANDO"
                        cor = (0, 255, 0)
                        self.gravador.parar_gravacao()

                else:
                    status_texto = "MONITORANDO"
                    cor = (0, 255, 0)
                    self.gravador.parar_gravacao()
                
                cv2.putText(frame, status_texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)
                
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h_i, w_i, ch = rgb_image.shape
                bytes_per_line = ch * w_i
                qt_img = QImage(rgb_image.data, w_i, h_i, bytes_per_line, QImage.Format.Format_RGB888)
                self.changePixmap.emit(qt_img.scaled(640, 360, Qt.AspectRatioMode.KeepAspectRatio))
                
        finally:
            if 'captura' in locals() and captura.isOpened():
                captura.release()
            if hasattr(self, 'gravador'):
                self.gravador.finalizar()

    def stop(self):
        self.running = False
        self.wait()