# gravador.py
# (Este arquivo foi recriado com base no seu uso em outros scripts)

import cv2
import os
import datetime

class Gravador:
    def __init__(self, largura=640, altura=360, prefixo_nome="camera_"):
        self.gravando = False
        self.largura = largura
        self.altura = altura
        self.prefixo_nome = prefixo_nome
        self.nome_arquivo = ""
        self.video_writer = None
        self.pasta_videos = "videos"

        # Garante que a pasta de vídeos exista
        if not os.path.exists(self.pasta_videos):
            os.makedirs(self.pasta_videos)

    def iniciar_gravacao(self):
        """Inicia uma nova gravação se não estiver gravando."""
        if not self.gravando:
            self.gravando = True
            agora = datetime.datetime.now()
            nome_base = f"{self.prefixo_nome}{agora.strftime('%Y-%m-%d_%H-%M-%S')}.avi"
            self.nome_arquivo = os.path.join(self.pasta_videos, nome_base)
            
            # Define o codec (XVID é amplamente compatível)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            
            # Inicializa o VideoWriter
            try:
                self.video_writer = cv2.VideoWriter(self.nome_arquivo, fourcc, 10.0, (self.largura, self.altura))
                print(f"[GRAVADOR] Iniciando gravação: {self.nome_arquivo}")
            except Exception as e:
                print(f"ERRO ao iniciar VideoWriter: {e}")
                self.gravando = False

    def gravar_frame(self, frame):
        """Grava um frame no arquivo de vídeo se estiver gravando."""
        if self.gravando and self.video_writer is not None:
            # Redimensiona o frame para garantir consistência
            frame_redimensionado = cv2.resize(frame, (self.largura, self.altura))
            self.video_writer.write(frame_redimensionado)

    def parar_gravacao(self):
        """Para a gravação e libera o arquivo."""
        if self.gravando:
            self.gravando = False
            if self.video_writer is not None:
                self.video_writer.release()
                print(f"[GRAVADOR] Gravação finalizada: {self.nome_arquivo}")
            self.video_writer = None
            self.nome_arquivo = ""

    def finalizar(self):
        """Método de limpeza para garantir que tudo seja liberado."""
        self.parar_gravacao()