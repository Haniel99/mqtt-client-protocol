import paho.mqtt.client as mqtt
import logging

logging.basicConfig(level=logging.INFO)

class MQTT:
    def __init__(self):
        self.client = mqtt.Client()
        self.message_display = None

    def on_start(self, host, port):
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(host=host, port=port)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Error al conectar al host {host}:{port} - {e}")

    def on_sub(self, topic='', wid=None):
        self.topic = topic
        self.message_display = wid

        try:
            self.client.subscribe(f"{topic}/topic")
            logging.info(f"Suscrito al tema {topic}/topic")
        except Exception as e:
            logging.error(f"Error al suscribirse al tema {topic}/topic - {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Conectado con éxito al servidor MQTT")
        else:
            logging.error(f"Error de conexión con el código {rc}")

    def on_message(self, client, userdata, msg):
        try:
            if self.message_display:
                self.message_display.append(msg.payload.decode())
            logging.info(f"Mensaje recibido: {msg.topic} {msg.payload.decode()}")
        except Exception as e:
            logging.error(f"Error al procesar el mensaje: {e}")

    def on_pub(self, msg=''):
        try:
            self.client.publish(f"{self.topic}/topic", msg)
            logging.info(f"Mensaje publicado en {self.topic}/topic: {msg}")
        except Exception as e:
            logging.error(f"Error al publicar el mensaje: {e}")

    def stop(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logging.info("Desconectado del servidor MQTT")
        except Exception as e:
            logging.error(f"Error al desconectar del servidor MQTT: {e}")
