# gravador.py (Versão 2 - com prefixo_nome)

import cv2
import os
import datetime

class Gravador:
    # A correção está aqui: adicionamos 'prefixo_nome'
    def __init__(self, largura=640, altura=480, prefixo_nome="gravacao_"):
        self.gravando = False
        self.saida = None
        self.nome_arquivo = ""
        self.largura = largura
        self.altura = altura
        self.prefixo = prefixo_nome

        if not os.path.exists("videos"):
            os.makedirs("videos")

    def iniciar_gravacao(self):
        if not self.gravando:
            self.gravando = True
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Usamos o prefixo para criar um nome de arquivo único
            nome_final = f"{self.prefixo}{timestamp}.avi"
            self.nome_arquivo = os.path.join("videos", nome_final)
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.saida = cv2.VideoWriter(self.nome_arquivo, fourcc, 20.0, (self.largura, self.altura))
            # Removido o print para não poluir o terminal do app GUI
            # print(f"[INFO] Iniciando gravação em: {self.nome_arquivo}")

    def gravar_frame(self, frame):
        if self.gravando and self.saida is not None:
            self.saida.write(frame)

    def parar_gravacao(self):
        if self.gravando:
            self.gravando = False
            if self.saida is not None:
                self.saida.release()
                # print(f"[INFO] Gravação finalizada: {self.nome_arquivo}")
            self.saida = None

    def finalizar(self):
        self.parar_gravacao()