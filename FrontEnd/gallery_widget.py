# gallery_widget.py
# (VERSÃO CORRIGIDA PARA MOSTRAR O PRIMEIRO FRAME)

import sys
import os
import cv2
import face_recognition
import pickle 
import numpy as np 
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit, QListWidget, QLabel,
                             QMessageBox, QHBoxLayout, QSlider) 
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer

from db_manager import Pessoa, Biometria, db

class GalleryWidget(QWidget):
    def __init__(self, video_path="video.mp4", parent=None):
        super().__init__(parent)
        
        self.profile_pic_dir = "rostos_conhecidos" 
        if not os.path.exists(self.profile_pic_dir):
            os.makedirs(self.profile_pic_dir)
            
        self.video_path = video_path 
        self.capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = None 
        self.is_paused = True # Começa pausado

        self.setup_ui()
        self.populate_gallery_from_db() 
        self.start_video() 

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        camera_layout = QVBoxLayout()
        self.camera_label = QLabel("Carregando Vídeo...")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background-color: black; color: white;")
        self.camera_label.setFixedSize(640, 480)
        camera_layout.addWidget(self.camera_label)

        video_controls = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_pause)
        self.play_button.setEnabled(True) # Começa habilitado (pois começa pausado)
        video_controls.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False) # Começa desabilitado
        video_controls.addWidget(self.pause_button)
        camera_layout.addLayout(video_controls)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome completo da pessoa...")
        camera_layout.addWidget(self.name_input)

        self.capture_button = QPushButton("Capturar e Salvar no Banco de Dados")
        self.capture_button.clicked.connect(self.capture_and_save_face) 
        camera_layout.addWidget(self.capture_button)

        main_layout.addLayout(camera_layout)

        gallery_layout = QVBoxLayout()
        gallery_layout.addWidget(QLabel("Pessoas Cadastradas (do Banco de Dados):"))
        self.face_list = QListWidget()
        gallery_layout.addWidget(self.face_list)
        
        self.delete_button = QPushButton("Excluir Pessoa Selecionada")
        self.delete_button.clicked.connect(self.delete_face_from_db) 
        gallery_layout.addWidget(self.delete_button)

        main_layout.addLayout(gallery_layout)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
        else:
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.update_frame() # Chama o próximo frame

    # --- (FUNÇÃO ATUALIZADA) ---
    def start_video(self):
        video_file_path = os.path.join(os.path.dirname(__file__), self.video_path)
        print(f"[Gallery] Tentando abrir vídeo: {video_file_path}")
        
        if not os.path.exists(video_file_path):
            self.camera_label.setText(f"Erro: Vídeo não encontrado!\n{self.video_path}")
            print(f"[Gallery] ERRO: Vídeo não encontrado.")
            return
        
        print(f"[Gallery] Arquivo encontrado. Tentando abrir com OpenCV...")
        try:
            self.capture = cv2.VideoCapture(video_file_path)
            
            if not self.capture or not self.capture.isOpened():
                self.camera_label.setText(f"Erro: Não foi possível abrir o vídeo.\n{self.video_path}\n(Verifique os codecs).")
                print(f"[Gallery] ERRO: OpenCV falhou ao abrir o vídeo.")
                return
                
            print(f"[Gallery] Vídeo aberto. Lendo primeiro frame...")
            
            # --- (MUDANÇA PRINCIPAL AQUI) ---
            # 1. Lemos o primeiro frame
            ret, frame = self.capture.read()
            if ret:
                # 2. Salvamos e exibimos ele imediatamente
                self.current_frame = frame.copy()
                self.display_frame(frame)
                print(f"[Gallery] Primeiro frame exibido. O vídeo está PAUSADO.")
            else:
                print(f"[Gallery] ERRO: Não foi possível ler o primeiro frame do vídeo.")
                self.camera_label.setText("Erro ao ler o primeiro frame.")
                return
            
            # 3. Só agora iniciamos o timer
            self.timer.start(40) 
            # Não precisamos mais chamar toggle_pause(), pois o estado inicial já é 'pausado'
            
        except Exception as e:
            self.camera_label.setText(f"Erro ao carregar vídeo: {e}")
            print(f"[Gallery] ERRO CRÍTICO ao carregar vídeo: {e}")

    # --- (NOVA FUNÇÃO HELPER) ---
    def display_frame(self, frame):
        """Converte um frame OpenCV (BGR) para QPixmap e exibe na label."""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_img.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)))
        except Exception as e:
            print(f"Erro ao exibir frame: {e}")

    # --- (FUNÇÃO ATUALIZADA) ---
    def update_frame(self):
        # Se estiver pausado ou sem captura, não faz nada
        if self.is_paused or not self.capture:
            return

        ret, frame = self.capture.read()
        
        # Se o vídeo acabar, reinicia
        if not ret:
            print("[Gallery] Fim do vídeo, reiniciando.")
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.capture.read()
            if not ret:
                print("[Gallery] Não foi possível reiniciar, parando timer.")
                self.timer.stop()
                return

        # Salva e exibe o frame
        self.current_frame = frame.copy() 
        self.display_frame(frame)

        # Chama o próximo frame (se não estiver pausado)
        if not self.is_paused:
            self.timer.start(40)

    # --- (FUNÇÕES ABAIXO ESTÃO IGUAIS, SEM MUDANÇAS) ---

    def capture_and_save_face(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Nome Inválado", "Por favor, digite um nome para a pessoa.")
            return

        if self.current_frame is None:
            QMessageBox.critical(self, "Erro de Captura", "Nenhum frame de vídeo disponível.")
            return

        face_locations = face_recognition.face_locations(self.current_frame)
        if len(face_locations) == 0:
            QMessageBox.warning(self, "Nenhum Rosto Detectado", "Não foi possível encontrar um rosto. Pause em um frame melhor.")
            return
        if len(face_locations) > 1:
            QMessageBox.warning(self, "Múltiplos Rostos", "Mais de um rosto detectado. Tente pausar em um frame com apenas um rosto.")
            return

        face_encodings = face_recognition.face_encodings(self.current_frame, face_locations)
        if not face_encodings:
             QMessageBox.warning(self, "Erro de Encoding", "Não foi possível calcular a biometria do rosto.")
             return
             
        encoding_data = face_encodings[0]
        
        top, right, bottom, left = face_locations[0]
        face_image = self.current_frame[top:bottom, left:right]
        safe_filename = f"{name.lower().replace(' ', '_')}.png"
        foto_path = os.path.join(self.profile_pic_dir, safe_filename)
        cv2.imwrite(foto_path, face_image)

        try:
            if db.is_closed(): db.connect(reuse_if_open=True)
            
            with db.atomic(): 
                nova_pessoa = Pessoa.create(
                    nome=name,
                    origem="Corinthians", 
                    foto_path=foto_path
                )
                
                encoding_bytes = pickle.dumps(encoding_data)
                
                Biometria.create(
                    pessoa=nova_pessoa,
                    encoding=encoding_bytes
                )
            
            QMessageBox.information(self, "Sucesso", f"Pessoa '{name}' e sua biometria facial foram salvas no banco de dados!")
            self.populate_gallery_from_db() 
            self.name_input.clear()

        except IntegrityError as e:
            QMessageBox.critical(self, "Erro de Duplicidade", f"Uma pessoa com o nome '{name}' já existe no banco de dados.")
            if os.path.exists(foto_path):
                os.remove(foto_path)
        except Exception as e:
            QMessageBox.critical(self, "Erro no Banco de Dados", f"Falha ao salvar no banco de dados: {e}")
        finally:
            if not db.is_closed(): db.close()

    def populate_gallery_from_db(self):
        self.face_list.clear()
        try:
            if db.is_closed(): db.connect(reuse_if_open=True)
            
            pessoas = Pessoa.select().order_by(Pessoa.nome)
            
            for pessoa in pessoas:
                self.face_list.addItem(pessoa.nome)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro de Leitura", f"Não foi possível ler as pessoas do banco de dados: {e}")
        finally:
            if not db.is_closed(): db.close()

    def delete_face_from_db(self):
        selected_item = self.face_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Nenhuma Seleção", "Por favor, selecione uma pessoa para excluir.")
            return
            
        name = selected_item.text()
        reply = QMessageBox.question(self, "Confirmar Exclusão",
                                     f"Tem certeza que deseja excluir '{name}' do banco de dados?\n(Isso também excluirá sua biometria e registros associados).",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db.is_closed(): db.connect(reuse_if_open=True)
                
                pessoa_para_deletar = Pessoa.get(Pessoa.nome == name)
                foto_path = pessoa_para_deletar.foto_path
                pessoa_para_deletar.delete_instance()
                
                if foto_path and os.path.exists(foto_path):
                    os.remove(foto_path)
                    
                QMessageBox.information(self, "Sucesso", f"Pessoa '{name}' foi excluída com sucesso.")
                self.populate_gallery_from_db() 
                
            except Pessoa.DoesNotExist:
                 QMessageBox.critical(self, "Erro", f"Pessoa '{name}' não encontrada no banco de dados.")
            except Exception as e:
                QMessageBox.critical(self, "Erro de Exclusão", f"Falha ao excluir pessoa: {e}")
            finally:
                if not db.is_closed(): db.close()

    def stop_camera(self):
        self.is_paused = True 
        if self.timer.isActive():
            self.timer.stop()
        if self.capture and self.capture.isOpened():
            self.capture.release()
            self.capture = None