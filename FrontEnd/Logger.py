# logger.py (ou adicione no db_manager.py)

from db_manager import Event, db

class Logger:
    def log_event(self, event_type, camera_name, image_path=None, video_path=None):
        """Registra um evento no banco de dados."""
        try:
            db.connect()
            Event.create(
                event_type=event_type,
                camera_name=camera_name,
                image_path=image_path,
                video_path=video_path
            )
            print(f"[LOG] Evento registrado: {event_type} na {camera_name}")
        except Exception as e:
            print(f"[ERRO LOG] Falha ao registrar evento: {e}")
        finally:
            if not db.is_closed():
                db.close()