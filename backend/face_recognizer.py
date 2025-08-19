# face_recognizer.py

import face_recognition
import os
import cv2

class FaceRecognizer:
    def __init__(self, known_faces_dir="rostos_conhecidos"):
        self.known_faces_dir = known_faces_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

    def load_known_faces(self):
        print("[INFO] Carregando rostos conhecidos...")
        if not os.path.exists(self.known_faces_dir):
            print(f"AVISO: Pasta '{self.known_faces_dir}' não encontrada. O reconhecimento facial está desativado.")
            return

        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.known_faces_dir, filename)
                try:
                    image = face_recognition.load_image_file(path)
                    encoding = face_recognition.face_encodings(image)[0]
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(os.path.splitext(filename)[0])
                    print(f"[INFO] Rosto de '{self.known_face_names[-1]}' carregado.")
                except IndexError:
                    print(f"AVISO: Nenhum rosto encontrado em {filename}. Ignorando.")

    def recognize(self, frame):
        # Redimensionar o frame para acelerar o reconhecimento
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1] # Converter de BGR para RGB

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        recognized_faces = []
        for i, face_encoding in enumerate(face_encodings):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Desconhecido"

            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]

            # Ajusta as coordenadas para o frame original
            top, right, bottom, left = [coord * 4 for coord in face_locations[i]]

            recognized_faces.append({"name": name, "box": (top, right, bottom, left)})
            
        return recognized_faces