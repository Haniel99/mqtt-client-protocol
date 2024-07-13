import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from mqtt_client import MQTT

class LoginWidget(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Ingrese el host y puerto")
        self.label.setStyleSheet('font-size: 16pt; color: #333333')
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.label.setAlignment(Qt.AlignCenter)

        self.host = QLineEdit()
        self.host.setPlaceholderText("host")

        self.port = QLineEdit()
        self.port.setPlaceholderText("puerto")
        
        self.start = QPushButton("Iniciar")
        self.start.clicked.connect(self.handle_start)
        self.switch_to_main = switch_to_main
        
        layout.addWidget(self.label)  
        layout.addWidget(self.host)   
        layout.addWidget(self.port)   
        layout.addWidget(self.start)
        
        self.setLayout(layout)
    
    def handle_start(self):
        host = self.host.text().strip()
        port = self.port.text().strip()
        
        if not host or not port.isdigit():
            QMessageBox.warning(self, "Error", "Ingrese un host válido y un puerto numérico")
            return
        
        self.switch_to_main(host, port)

class TopicWidget(QWidget):
    def __init__(self, main, mqtt, topic):
        super().__init__()
        layout = QGridLayout()
        self.mqtt = mqtt
        self.back = QPushButton("Volver")
        self.back.clicked.connect(main)
        layout.addWidget(self.back, 0, 0)  
        
        self.message_label = QLabel('Publicaciones')
        layout.addWidget(self.message_label, 0, 1)  
        
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display, 1, 1)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText('Ingrese el mensaje')
        layout.addWidget(self.text_edit, 1, 0)
        
        self.send = QPushButton("Enviar")
        self.send.clicked.connect(self.send_message)
        layout.addWidget(self.send, 2, 0)
        
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 1)
        
        self.mqtt.on_sub(topic, self.message_display)
        self.setLayout(layout)
    
    def send_message(self):
        message = self.text_edit.toPlainText().strip()
        if message:
            self.mqtt.on_pub(message)
            self.text_edit.clear()

class MainWidget(QWidget):
    def __init__(self, switch_to_topic, host, port):
        super().__init__()
        self.host = host
        self.port = int(port)
        self.mqtt = MQTT()
        
        try:
            self.mqtt.on_start(host=self.host, port=self.port)
        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", f"No se pudo conectar al host {host}:{port}\n{e}")
            return
        
        self.grid_layout = QGridLayout()
        
    
        self.label = QLabel("Suscríbete a un tópico")
        self.label.setStyleSheet('font-size: 16pt; color: #333333')
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.label.setAlignment(Qt.AlignCenter)        
        self.topic = QLineEdit()
        self.topic.setPlaceholderText("Tópico")
        
        self.start = QPushButton("Continuar")
        self.start.clicked.connect(self.handle_start)
        self.switch_to_topic = switch_to_topic
        
        self.grid_layout.addWidget(self.label, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.topic, 1, 0, 1, 2)
        self.grid_layout.addWidget(self.start, 2, 0, 1, 2)
        
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        
        self.setLayout(self.grid_layout)
    
    def handle_start(self):
        topic = self.topic.text().strip()
        if not topic:
            QMessageBox.warning(self, "Error", "El tópico no puede estar vacío")
            return
        self.switch_to_topic(self.mqtt, topic)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MQTT app")
        self.setGeometry(100, 100, 600, 400)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.login_widget = LoginWidget(self.switch_to_main)
        self.stacked_widget.addWidget(self.login_widget)
        
        self.stacked_widget.setCurrentWidget(self.login_widget)
    
    def main(self):
        self.main_widget = MainWidget(self.switch_to_topic, self.host, self.port)
        self.stacked_widget.addWidget(self.main_widget)
        self.stacked_widget.setCurrentWidget(self.main_widget)
        
    def switch_to_main(self, host, port):
        self.host = host
        self.port = port
        self.main()
        
    def switch_to_topic(self, mqtt, topic):
        self.topic_widget = TopicWidget(self.main, mqtt, topic)
        self.stacked_widget.addWidget(self.topic_widget)
        self.stacked_widget.setCurrentWidget(self.topic_widget)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Mensaje', '¿Estás seguro de que quieres salir?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if hasattr(self, 'main_widget') and hasattr(self.main_widget, 'mqtt'):
                self.main_widget.mqtt.client.loop_stop()
                self.main_widget.mqtt.client.disconnect()
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
