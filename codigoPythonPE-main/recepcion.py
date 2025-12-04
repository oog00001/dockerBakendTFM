
import respuestas
import socket
import threading
import time
from transformers import AutoTokenizer, AutoModel
import torch
import cargarDatos
from cornac.eval_methods import RatioSplit
from cornac.models import SVD  



# cogemos el nombre de la maquina y la ip que tenemos asignada y el puerto
hostname = socket.gethostname()        
ip_local = socket.gethostbyname(hostname)
print("IP local:", ip_local)
#HOST = ip_local
HOST = '0.0.0.0'
PORT = 5000







# recibimos el mensaje 
def receive_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError("Se perdió la conexión")
        data += more
    return data

# Recibimos el mensaje de unity, creamos la respuesta y la enviamos
def handle_client(conn, addr):
    print('Conectado por', addr)
    try:
        # Recibir mensaje de Unity
        msg_type = conn.recv(4).decode()
        if not msg_type:
            return
        size = int(conn.recv(8).decode())
        data = receive_all(conn, size)

        if msg_type == "TEXT":
            texto = data.decode()
            print("Texto recibido de Unity:", texto)
                
            # Preparar respuesta: texto + imagen
            respuesta = respuestas.realizar_accion(texto)
            partes = texto.split(':::')
            print('llega')
            if (partes[0] == '5'):
                print('Imagen por enviada')
                send_image(conn, respuesta)  # envía imagen
                print('imagen enviada')
            else:
                print('Texto por enviar')
                send_text(conn, respuesta)          # envía texto
                print('texto enviado')
            # guardar datos
            if(partes[0] == '2'):
                cargarDatos.guardar_nuevo_usuario_privado()
                cargarDatos.guardar_nuevo_user()
            if(partes[0] == '4'):
                cargarDatos.guardar_valoracion_rating()
    except Exception as e:
        print("Error en handle_client:", e)
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except:
            pass
        conn.close()
        print(f"Conexión cerrada con {addr}")

def send_text(conn, text):
    data = text.encode()
    conn.sendall(b"TEXT" + f"{len(data):08}".encode() + data)

def send_image(conn, data):
    conn.sendall(b"IMG " + f"{len(data):08}".encode() + data)

# Creamos el servidor con los datos establecidos anteriormente, la ip y el puerto e inicializamos la captura de mensajes
def empezar_programa():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("Servidor Python escuchando en", HOST, PORT)

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()



# esta funcion llama a inicializar programa
def recibir_peticion_frontend():
    #mensaje = '0:::1:::oog:::00001'
    #respuesta = respuestas.realizar_accion(mensaje)
    empezar_programa()

