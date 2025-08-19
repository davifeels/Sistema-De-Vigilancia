# detector.py (Versão 3.0 - Com Estimação de Pose)

import cv2
from ultralytics import YOLO

class Detector:
    def __init__(self):
        self.frame_anterior = None
        # --- MUDANÇA PRINCIPAL: Usamos o modelo treinado para POSE ---
        # Ele será baixado automaticamente na primeira vez.
        self.modelo_ia = YOLO("yolov8n-pose.pt")

    def detectar_movimento(self, frame):
        frame_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_cinza = cv2.GaussianBlur(frame_cinza, (21, 21), 0)

        if self.frame_anterior is None:
            self.frame_anterior = frame_cinza
            return [] 

        delta = cv2.absdiff(self.frame_anterior, frame_cinza)
        self.frame_anterior = frame_cinza
        
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        contornos, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contornos_filtrados = []
        for contorno in contornos:
            if cv2.contourArea(contorno) < 1000:
                continue
            contornos_filtrados.append(contorno)
        
        return contornos_filtrados

    def detectar_poses(self, frame):
        """Nova função que detecta e retorna os pontos-chave do corpo."""
        resultados = self.modelo_ia(frame, stream=True, verbose=False)
        poses_detectadas = []
        
        for resultado in resultados:
            # Verifica se keypoints foram detectados antes de tentar acessá-los
            if resultado.keypoints and len(resultado.keypoints.xy) > 0:
                # Itera sobre cada conjunto de pontos-chave (cada pessoa detectada)
                for pontos_pessoa in resultado.keypoints.xy:
                    poses_detectadas.append(pontos_pessoa.tolist()) # Adiciona a lista de pontos [x, y] para uma pessoa

        return poses_detectadas