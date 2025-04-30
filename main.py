import os
import webview
import threading

# Cambia este puerto si ya está en uso
PORT = 8000

def start_django():
    os.system(f"python manage.py runserver {PORT}")

if __name__ == '__main__':
    threading.Thread(target=start_django, daemon=True).start()
    webview.create_window("TASAL - Control de Asistencia", f"http://127.0.0.1:{PORT}", width=1200, height=800)
