import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt  

# Configuration for the MQTT Broker
MQTT_BROKER = "test.mosquitto.org"  
MQTT_PORT = 1883
MQTT_TOPIC = "basura/status"
MQTT_TOPIC_LOCK = "basura/lock"

# Global variable for bin status
tacho_status = {
    "nivel": 0,
    "cerradura": "cerrado"
}

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with code {rc}")
        client.subscribe(MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC_LOCK)
    else:
        print(f"Connection error, code {rc}")

def on_message(client, userdata, msg):
    global tacho_status
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    if topic == MQTT_TOPIC:
        try:
            tacho_status["nivel"] = int(payload)
        except ValueError:
            print("Error in data format for fill level")
    elif topic == MQTT_TOPIC_LOCK:
        tacho_status["cerradura"] = payload
    update_status()

def update_status():
    nivel_label.config(text=f"Nivel de llenado: {tacho_status['nivel']}%")
    lock_label.config(text=f"Estado de la cerradura: {tacho_status['cerradura']}")

def refrescar_datos():
    client.publish("basura/refresh", "1")

def abrir_cerradura():
    client.publish(MQTT_TOPIC_LOCK, "abrir")

def cerrar_cerradura():
    client.publish(MQTT_TOPIC_LOCK, "cerrar")

def on_closing():
    if messagebox.askokcancel("Salir", "¿Deseas salir y desconectar el MQTT?"):
        client.loop_stop()
        client.disconnect()
        root.destroy()

# Connect to the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")

# GUI setup with Tkinter
root = tk.Tk()
root.title("Tacho Inteligente")

# Status Labels
nivel_label = tk.Label(root, text="Nivel de llenado: 0%", font=("Helvetica", 14))
nivel_label.pack(pady=10)

lock_label = tk.Label(root, text="Estado de la cerradura: cerrado", font=("Helvetica", 14))
lock_label.pack(pady=10)

# Buttons
refrescar_btn = tk.Button(root, text="Refrescar Datos", command=refrescar_datos, font=("Helvetica", 12))
refrescar_btn.pack(pady=5)

abrir_btn = tk.Button(root, text="Abrir Tacho", command=abrir_cerradura, font=("Helvetica", 12))
abrir_btn.pack(pady=5)

cerrar_btn = tk.Button(root, text="Cerrar Tacho", command=cerrar_cerradura, font=("Helvetica", 12))
cerrar_btn.pack(pady=5)

# Handle window close
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI
root.mainloop()
