# 🔥 Phoenix Vision – Sistema de Vigilância Inteligente

Status: ✅ **Concluído**

---

## 🎥 Demonstração Visual

Abaixo, duas demonstrações visuais do sistema em funcionamento:

- **Painel Principal com Detecção de Pose:**  
Visualização em grade 2x2 com o modelo de IA identificando pontos-chave do corpo humano em tempo real.

- **Funcionalidades Avançadas da Interface:**  
Demonstração do modo tela cheia, galeria de gravações automáticas e painel gráfico de configurações.

<table>
  <tr>
    <td><img src="https://github.com/davifeels/Sistema-De-Vigilancia/raw/main/assets/hehe.JPG" width="300"/></td>
    <td><img src="https://github.com/davifeels/Sistema-De-Vigilancia/raw/main/assets/img.camera.vigilancia.JPG" width="300"/></td>
  </tr>
</table>


---

## 📜 Sobre o Projeto

O **Phoenix Vision** é uma suíte de segurança e monitoramento de vídeo desenvolvida com Python. Ele transforma webcams USB e câmeras IP (como celulares via apps tipo DroidCam) em um sistema inteligente de vigilância, com suporte a múltiplas câmeras e análise por IA em tempo real.

Construído do zero, este sistema evoluiu de um script simples para uma aplicação desktop robusta, moderna e altamente funcional, com interface gráfica interativa.

---

## ✨ Funcionalidades Principais

🎛️ **Interface Gráfica (GUI)**  
Painel moderno com layout em grade (2x2) para até 4 câmeras.  
Tema escuro customizado com QSS (estilo CSS para PyQt).

📹 **Múltiplas Câmeras**  
Suporte a webcams e streams IP (RTSP/HTTP).

🧠 **Inteligência Artificial**  
YOLOv8-Pose: Estimação de pose com pontos-chave (cabeça, ombros, joelhos etc.).  
Detecção de Movimento: Algoritmo leve que ativa a IA e a gravação somente quando necessário.  
Sistema de Persistência Visual: Mantém desenhos e avisos na tela por tempo configurável.

🎞️ **Gravação Automática**  
Clipes de vídeo (.avi) são gravados automaticamente ao detectar movimento.

⚙️ **Recursos Interativos**  
Modo Tela Cheia: Duplo clique em uma câmera expande a visualização.  
Galeria de Gravações: Navegue e reproduza vídeos gravados diretamente pelo app.  
Painel de Configurações: Interface para adicionar/editar/remover câmeras (salvas em config.json, sem editar o código).

🚀 **Otimização de Desempenho**  
Multithreading para manter a GUI fluida.  
Detecção inteligente ativada por movimento.  
Técnicas de frame skipping para economia de CPU.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia       | Descrição                                     |
|------------------|-----------------------------------------------|
| Python 3.11      | Linguagem principal                           |
| PyQt6            | Interface gráfica                             |
| OpenCV           | Processamento de vídeo                        |
| Ultralytics YOLOv8 | Estimação de pose (modelo yolov8n-pose.pt) |
| NumPy            | Processamento numérico                        |
| JSON             | Configuração via arquivo externo              |
| Multithreading   | Processamento paralelo                        |

---

## 🚀 Como Executar o Projeto

### Clone o Repositório

```bash
git clone https://github.com/davifeels/Sistema-De-Vigilancia.git
cd Sistema-De-Vigilancia
Crie um Ambiente Virtual (opcional, mas recomendado)
bash
Copiar
Editar
python -m venv venv
.\venv\Scripts\activate  # No Windows
Instale as Dependências
bash
Copiar
Editar
pip install -r requirements.txt
Configure as Câmeras
Edite o arquivo config.json com os endereços das câmeras e nomes.
Verifique se a pasta assets/ contém imagens de placeholder (no_signal.png etc.).

Execute o Aplicativo
bash
Copiar
Editar
python main_gui.py
📁 Estrutura do Projeto
arduino
Copiar
Editar
sistema_vigilancia/
│
├── assets/
│   └── no_signal.png
│
├── videos/
│   └── (Vídeos gravados automaticamente)
│
├── .gitignore
├── config.json
├── detector.py
├── gravador.py
├── main_gui.py
└── requirements.txt
📄 Licença
Este projeto está sob a licença MIT.

💡 Créditos
Feito com ❤️ por Davi Feels
