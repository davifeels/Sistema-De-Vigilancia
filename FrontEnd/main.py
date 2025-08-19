# main.py (Versão FINAL "POSE" - Com Detecção de Partes do Corpo)

import cv2
import threading
import time 
from detector import Detector
from gravador import Gravador

def processar_camera(camera_id, nome_camera):
    print(f"[INFO] Iniciando {nome_camera}...")
    print(f"[INFO] Conectando ao stream: {camera_id}")
    
    captura = cv2.VideoCapture(camera_id)
    largura_processamento, altura_processamento = 640, 360
    
    if not captura.isOpened():
        print(f"ERRO: Não foi possível abrir o stream da {nome_camera}.")
        return

    detector = Detector()
    gravador = Gravador(largura=largura_processamento, altura=altura_processamento, prefixo_nome=f"{nome_camera}_")

    # --- Variáveis de Memória ---
    contador_frames = 0
    ultima_vez_detectado = 0
    tempo_de_persistencia = 10.0
    
    ultimos_contornos_movimento = []
    ultimas_poses_detectadas = []

    # --- DICIONÁRIO DE PONTOS-CHAVE (Corpo Humano) ---
    # Estes são os índices dos pontos que o modelo YOLOv8-Pose reconhece
    PONTOS = {
        'nariz': 0, 'olho_esq': 1, 'olho_dir': 2, 'orelha_esq': 3, 'orelha_dir': 4,
        'ombro_esq': 5, 'ombro_dir': 6, 'cotovelo_esq': 7, 'cotovelo_dir': 8,
        'pulso_esq': 9, 'pulso_dir': 10
    }

    while True:
        ret, frame_original = captura.read()
        if not ret or frame_original is None:
            break

        frame = cv2.resize(frame_original, (largura_processamento, altura_processamento))
        
        if contador_frames % 4 == 0:
            contornos_movimento = detector.detectar_movimento(frame)
            poses = []
            
            if contornos_movimento:
                poses = detector.detectar_poses(frame)

            if contornos_movimento or poses:
                ultima_vez_detectado = time.time()
                ultimos_contornos_movimento = contornos_movimento
                ultimas_poses_detectadas = poses
        
        contador_frames += 1

        # --- LÓGICA DE DESENHO PERSISTENTE ---
        no_periodo_de_persistencia = time.time() - ultima_vez_detectado < tempo_de_persistencia

        if no_periodo_de_persistencia:
            status_texto = "STATUS: ATIVIDADE DETECTADA"
            cor_texto = (0, 0, 255)
            
            # Desenha os contornos de movimento gerais
            for contorno in ultimos_contornos_movimento:
                (x, y, w, h) = cv2.boundingRect(contorno)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Movimento", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Desenha os pontos-chave das poses detectadas
            for pose in ultimas_poses_detectadas:
                # Desenha o ombro esquerdo
                ponto_ombro_esq = pose[PONTOS['ombro_esq']]
                x, y = int(ponto_ombro_esq[0]), int(ponto_ombro_esq[1])
                cv2.circle(frame, (x, y), 5, (255, 0, 0), -1) # Círculo azul

                # Desenha o ombro direito
                ponto_ombro_dir = pose[PONTOS['ombro_dir']]
                x, y = int(ponto_ombro_dir[0]), int(ponto_ombro_dir[1])
                cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)

                # Desenha a cabeça (usando o nariz como referência)
                ponto_nariz = pose[PONTOS['nariz']]
                x, y = int(ponto_nariz[0]), int(ponto_nariz[1])
                cv2.circle(frame, (x, y), 7, (0, 255, 255), -1) # Círculo amarelo
                cv2.putText(frame, "Cabeca", (x - 20, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)


            gravador.iniciar_gravacao()
            gravador.gravar_frame(frame)
        else:
            status_texto = "STATUS: MONITORANDO"
            cor_texto = (0, 255, 0)
            gravador.parar_gravacao()
            
        cv2.putText(frame, status_texto, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_texto, 2)
        cv2.imshow(nome_camera, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    captura.release()
    gravador.finalizar()
    cv2.destroyWindow(nome_camera)

if __name__ == "__main__":
    url_da_sua_camera = "http://192.168.1.3:4747/video" 
    cameras_a_monitorar = [(url_da_sua_camera, "Sistema de Pose")]
    threads = []
    for cam_id, cam_nome in cameras_a_monitorar:
        thread = threading.Thread(target=processar_camera, args=(cam_id, cam_nome), daemon=True)
        threads.append(thread)
        thread.start()
    print("[INFO] Sistema de Estimação de Pose iniciado. Pressione 'q' para fechar.")
    for thread in threads:
        thread.join()
    print("[INFO] Sistema encerrado.")