# report_widget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from db_manager import Event, db

class ReportWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Data", "Câmera", "Tipo de Evento", "Imagem", "Vídeo"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        refresh_button = QPushButton("Atualizar Relatório")
        refresh_button.clicked.connect(self.populate_table)
        self.layout.addWidget(refresh_button)

        self.populate_table()

    def populate_table(self):
        """Preenche a tabela com os eventos do banco de dados."""
        try:
            db.connect()
            events = Event.select().order_by(Event.timestamp.desc())

            self.table.setRowCount(len(events))
            for row_num, event in enumerate(events):
                self.table.setItem(row_num, 0, QTableWidgetItem(str(event.timestamp.strftime("%d/%m/%Y %H:%M:%S"))))
                self.table.setItem(row_num, 1, QTableWidgetItem(event.camera_name))
                self.table.setItem(row_num, 2, QTableWidgetItem(event.event_type))
                self.table.setItem(row_num, 3, QTableWidgetItem(event.image_path if event.image_path else "N/A"))
                self.table.setItem(row_num, 4, QTableWidgetItem(event.video_path if event.video_path else "N/A"))

        except Exception as e:
            print(f"ERRO: Falha ao carregar eventos do banco de dados: {e}")
        finally:
            if not db.is_closed():
                db.close()